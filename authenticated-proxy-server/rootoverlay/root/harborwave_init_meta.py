#!/usr/bin/env python
# exit codes 0-success, 1-operation error, 2-condition error
prog_desc='''
Download initialize harbor-wave data from Digital Ocean's API, so its available
for the system.

Modified for authenticated-proxy-server. configs tinyproxy and iptables info
from init_proxy.sh
'''

import sys,os
import json
import urllib.request
import subprocess, platform
from http.client import responses as http_responses
from datetime import datetime

config = {
    'host'             : '169.254.169.254',
    'path'             : '/metadata/v1/user-data',
    'timeout'          : 30, # timeout, in seconds, for URL query
    'logfile'          : "/var/log/harbor-wave-init.log",
    'app-dir'          : '/opt/harborwave',
    'done-file'        : '/opt/harborwave/done',
    'tinyproxy-config' : '/etc/tinyproxy/tinyproxy.conf',
    'stunnel-config'   : '/etc/stunnel/stunnel.conf',
    'iptables-file'    : '/etc/iptables/iptables.rules',
    'ip6tables-file'   : '/etc/iptables/ip6tables.rules',
    'certbot-script'   : "/root/do_certbot.sh"
    'snakeoil-script'  : "/root/do_snakeoil.sh"
}

defaults = {
    'user'     : 'proxyuser',
    'pass'     : 'proxypass',
    'port'     : '8888',
    'tls_port' : '8443'
}

def message(message):
    print_message = "harborwave_initlization: " + message
    print(print_message)
    do_log(print_message)

def exit_with_error(error,message):
    print_message = "harborwave_initlization ¡ERROR!: " + message
    print(print_message, file=sys.stderr)
    do_log(print_message)
    sys.exit(error)

def submsg(message):
    print_message = "[+]\t" + message
    print(print_message)
    do_log(print_message)
        
def warn(message):
    print_message="harborwave_initlization: ¡WARN!: " + message
    print(print_message, file=sys.stderr)
    do_log(print_message)

def do_log(message):
    time_obj   = datetime.now()
    time_stamp = time_obj.ctime()
    out_message = time_stamp + "\t" + message + "\n"
    log_obj = open(config['logfile'],'a')
    log_obj.write(out_message)
    log_obj.close()

def strip_comments(in_file):
    '''Strip comments from a text file. Takes one var, a  string, returns a string with comments stripped'''
    comment="#"
    out_lines = []
    in_lines  = in_file.split("\n")
    for line in in_lines:
        if line == "" or line.startswith(comment):
            continue
        line = line.split(comment)
        if line[0] != "":
            out_lines.append(line[0])
    out_file = " ".join(out_lines)
    return out_file

def get_data(config):
    '''get the data and return it as a dict, takes the config array'''
    get_url     = "http://" + config['host'] + config['path']
    
    # do URL call, and check for errors, both in fetching and any codes from
    # the server
    try:
        response = urllib.request.urlopen(get_url,timeout=config['timeout'])
    except:
        exit_with_error(1,"Could not retrieve data from API!")
    if response.code != 200:
        exit_with_error(1,"HTTP Error " + response.code + ": " + http_responses[response.code])
    
    # now, get a python dict from the response
    raw_data    = response.read()
    output_data = raw_data.decode()
    try:
        output_data = json.loads(output_data)
    except:
        exit_with_error(9,"Data isn't in the JSON format, are you sure this is a harbor-wave VM?")
    
    # check to make sure all fields are there
    needed_keys = ['sequence', 'base-name', 'payload', 'payload-filename','domain','total_vms']
    data_keys = output_data.keys()
    missing_keys = []
    for item in needed_keys:
        if item not in data_keys:
            missing_keys.appennd(item)
    if missing_keys != []:
        missing_keys = ",".join(missing_keys)
        error_line = "Missing JSON items " + missing_keys + ": are you sure this is a harbor-wave VM?"
        exit_with_error(9,error_line)
    
    return output_data

def write_environment(data):
    '''Add sequence and base-name to /etc/environment.'''
    env_file = '/etc/environment'
    out_lines  = "HARBORWAVE_SEQEUNCE="  + str(data['sequence']) + "\n"
    out_lines += "HARBORWAVE_TOTAL_VMS=" + str(data['total_vms']) + "\n"
    out_lines += "HARBORWAVE_BASENAME="  + data['base-name'] + "\n"
    out_lines += "HARBORWAVE_DOMAIN="    + data['domain'] + "\n"
    try:
        file_obj = open(env_file,'a')
        file_obj.write(out_lines)
        file_obj.close()
    except:
        warn("Could not write to " + env_file)
        return 1
        
    return 0

def proc_payload(data):
    '''proccess payload file for proxy config'''
    write_errors = 0
    read_errors  = 0
    config_file    = config['tinyproxy-config']
    iptables_file  = config['iptables-file']
    ip6tables_file = config['ip6tables-file']
    
    # Start with defaults
    user     = defaults['user']
    password = defaults['pass']
    port     = defaults['port']
    tls_port = defaults['tls_port']
    fqdn     = platform.node() + "." + data['domain']
    
    line_seperator  = ";"
    field_seperator = "="
    # Get payload from data
    payload = data['payload']
    payload = strip_comments(payload)
    payload = payload.split(line_seperator)
    data_dict = {}
    for item in payload:
        item = item.strip()
        item = item.split(field_seperator)
        # If there is no value, skip
        if len(item) < 2:
            continue
        # Get user items from payload
        if item[0] == "user":
            user = item[1]
        elif item[0] == "pass":
            password = item[1]
        elif item[0] == "port":
            port = item[1]
        elif item[0] == "tls_port":
            tls_port = item[1]
        else:
            continue
    
    ## Generate config lines for TinyProxy
    add_lines  = "BasicAuth " + user + " " + password + "\n"
    add_lines += "Port " + port + "\n"
    # WORKAROUND FOR BUG: https://bugs.archlinux.org/task/66616
    add_lines += "PidFile \"/run/tinyproxy/tinyproxy.pid\"" + "\n"
    # Now write
    payload_file = config['tinyproxy-config']
    try:
        file_obj = open(payload_file,"a")
        file_obj.write(add_lines)
        file_obj.close()
    except:
        warn("Could not write TinyProxy config to " + payload_file)
        write_errors += 1

    ## Do Stunnel config
    # read
    stunnel_conf_file = config['stunnel-config']
    try:
        file_obj     = open(stunnel_conf_file,"r")
        stunnel_conf = file_obj.read()
        file_obj.close()
    except:
        warn("Could not read Stunnel config: " + stunnel_conf_file)
        read_errors += 1
        
    # replace variables with their values
    stunnel_conf = stunnel_conf.replace("%TLS_PORT%",tls_port)
    stunnel_conf = stunnel_conf.replace("%PORT%",port)
    stunnel_conf = stunnel_conf.replace("%FQDN%",fqdn)
    # write
    try:
        file_obj   = open(stunnel_conf_file,"w")
        file_obj.write(stunnel_conf)
        file_obj.close()
    except:
        warn("Could not write Stunnel config: " + stunnel_conf_file)
        write_errors += 1
    
    ## Do IPTables config
    
    # First, load configs into file
    iptables_config  = None
    ip6tables_config = None
    try:
        file_obj = open(iptables_file,"r")
        iptables_config = file_obj.read()
        file_obj.close()
    except:
        warn("Could not read iptables config")
        read_errors += 1
        
    try:
        file_obj = open(ip6tables_file,"r")
        ip6tables_config = file_obj.read()
        file_obj.close()
    except:
        warn("Could not read ip6tables config")
        read_errors += 1
    
    if iptables_config != None:
        iptables_config = iptables_config.replace("%PORT%",port)
        iptables_config = iptables_config.replace("%TLS_PORT%",tls_port)
        try:
            file_obj = open(iptables_file,"w")
            file_obj.write(iptables_config)
            file_obj.close()
        except:
            warn("Could not write iptables config")
            write_errors += 1

    if ip6tables_config != None:
        ip6tables_config = ip6tables_config.replace("%PORT%",port)
        ip6tables_config = ip6tables_config.replace("%TLS_PORT%",tls_port)
        try:
            file_obj = open(ip6tables_file,"w")
            file_obj.write(ip6tables_config)
            file_obj.close()
        except:
            warn("Could not write ip6tables config")
            write_errors += 1            
    
    if write_errors >= 1 or read_errors >= 1:
        return read_errors,write_errors
    else:
        return 0,0

def enable_restart_services(use_fqdn=False):
    '''Restart and enable systemd units'''
    services = [ "tinyproxy", "iptables", "ip6tables", "stunnel" ]
    fqdn_service = "certbot-renew-custom.timer"
    exit_code = 0
    for item in services:
        try:
            exit_code += subprocess.check_call(['systemctl', 'restart', item])
        except:
            warn("Could Not Restart Service: " + item)
            exit_code += 1
        try:
            exit_code += subprocess.check_call(['systemctl', 'enable', item])
        except:
            warn("Could Not Enable Service: " + item)
            exit_code += 1
    
    if use_fqdn == True:
        try:
            exit_code += subprocess.check_call('systemctl', 'enable', fqdn_service)
        except:
            exit_code += 1
        
    if exit_code > 0:
        return 1
    else:
        return 0

def run_certbot_script(script_file):
    try:
        subprocess.call(["/usr/bin/bash",script_file,"firstrun"])
    except:
        warn("Certbot failed, without certs stunnel will not work")
        return 1

    return 0

def write_done():
    '''Touch /opt/harbor-wave/done so we know this script ran already'''
    done_file = config['done-file']
    try:
        file_obj = open(done_file,"w")
        file_obj.write("\n")
        file_obj.close()
    except:
        warn("Could not write donefile, the script will repeat!")
        return 1

    return 0

def main():
    message("Getting and parsing Harbor-Wave data from Digital Ocean API")
    WARNS = 0
    # Check if this script ran already
    if os.path.exists(config['done-file']) == True:
        warn("Script ran already, doing nothing and exiting")
        sys.exit(0)
    
    # ensure directory is available
    os.makedirs(config['app-dir'],mode=0o755,exist_ok=True)
    
    
    submsg("Retrieving Data")
    data = get_data(config)
    
    submsg("Writing to Environment File")
    WARNS += write_environment(data)
    
    submsg("Configuring TinyProxy, Stunnel, and IPTables")
    READ_ERRORS,WRITE_ERRORS = proc_payload(data)
    
    WARNS += read_errors + write_errors
    
    # Lets Encrypt! only works if there is a FQDN
    if data['domain'] != "":
        use_fqdn = True
        submsg("Getting TLS Certs from Lets Encrypt!")
        WARNS += run_certbot_script(config['certbot-script'])
    else:
        use_fqdn = False
        submsg("No FQDN, writing snakeoil cert")
        WARNS += run_certbot_script(config['snakeoil-script'])
    
    if READ_ERRORS == 0 and WRITE_ERRORS == 0:
        submsg("Restarting Daemons")
        WARNS += enable_restart_services(use_fqdn=use_fqdn)
    else:
        submsg("There were errors processing the config files, NOT restarting services. READ:" + READ_ERRORS + " WRITE:" + WRITE_ERRORS)

    submsg("Writing Donefile")
    WARNS += write_done()
    
    if WARNS > 0:
        message("Done, but with " + WARNS + " warning(s)")
        sys.exit(1)
    else:
        message("Done")

if __name__ == "__main__":
    main()
