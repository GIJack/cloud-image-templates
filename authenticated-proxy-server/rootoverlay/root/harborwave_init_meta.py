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
import subprocess
from http.client import responses as http_responses
from datetime import datetime

config = {
    'host'      : '169.254.169.254',
    'path'      : '/metadata/v1/user-data',
    'timeout'   : 3, # timeout, in seconds, for URL query
    'logfile'   : "/var/log/harbor-wave-init.log",
    'app-dir'   : '/opt/harborwave',
    'done-file' : '/opt/harborwave/done',
    'tinyproxy-config' : '/etc/tinyproxy/tinyproxy.conf',
    'iptables-file'    : '/etc/iptables/iptables.rules',
    'ip6tables-file'   : '/etc/iptables/ip6tables.rules'
}

defaults = {
    'pass' : 'proxypass',
    'user' : 'proxyuser',
    'port' : '8888'
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

def strip_commmens(in_file):
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
    needed_keys = ['sequence', 'base-name', 'payload','payload-filename']
    data_keys = output_data.keys()
    missing_keys = []
    for item in needed_keys:
        if item not in data_keys:
            missing_keys.appennd(item)
    if missing_keys != []:
        missing_keys = " ".join(missing_keys)
        exit_with_error(9,"Missing JSON items, are you sure this is a harbor-wave VM?")
    
    return output_data

def write_environment(data):
    '''Add sequence and base-name to /etc/environment.'''
    env_file = '/etc/environment'
    out_lines  = "HARBORWAVE_SEQEUNCE=" + str(data['sequence']) + "\n"
    out_lines += "HARBORWAVE_BASENAME=" + data['base-name'] + "\n"
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
    config_file   = config['tinyproxy-config']
    iptables_file = config['iptables-file']
    ip6tables_file = config['ip6tables-file']
    
    # Start with defaults
    user     = defaults['user']
    password = defaults['pass']
    port     = defaults['port']
    
    # Get data from payload
    line_seperator  = ";"
    field_seperator = "="
    data = strip_comments(data)
    data = data.split(line_seperator)
    data_dict = {}
    for item in data:
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
        else:
            continue
    
    # Generate config lines
    add_lines  = "BasicAuth " + user + " " + password + "\n"
    add_lines += "Port " + port + "\n"
    
    ## Now write
    payload_file = config['tinyproxy-config']
    try:
        file_obj = open(payload_file,"a")
        file_obj.write(add_lines)
        file_obj.close()
    except:
        warn("Could not write payload to " + payload_file)
        return 1
    
    iptables_line  = "-A INPUT -m multiport -p tcp -s 0.0.0.0/0 --dports " + port + " -j ACCEPT # Proxy Server(tiny proxy)"
    ip6tables_line = "-A INPUT -m multiport -p tcp --dports " + port + " -j ACCEPT # Proxy Server(tiny proxy)"
    
    iptables_errors = 0
    try:
        file_obj = open(iptables_file,"a")
        file_obj.write(iptables_line)
        file_obj.close()
    except:
        warn("Could not write iptables file")
        iptables_errors += 1
    try:
        file_obj = open(ip6tables_file,"a")
        file_obj.write(ip6ables_line)
        file_obj.close()
    except:
        warn("Could not write ip6tables file")
        iptables_errors += 1
    
    if iptables_errors >= 1:
        return 1

    return 0

def enable_restart_services():
    '''Restart and enable systemd units'''
    services = [ "tinyproxy", "iptables", "ip6tables"]
    exit_code = 0
    for item in services:
        exit_code += subprocess.check_call(['systemctl', 'restart', item])
        exit_code += subprocess.check_call(['systemctl', 'enable', item])
        
    if exit_code > 0:
        return 1
    else:
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
    
    submsg("Writing to environment file")
    WARNS += write_environment(data)
    
    submsg("Configuring TinyProxy and setting iptables listen")
    WARNS += proc_payload(data)
    
    submsg("restarting daemons")
    WARNS += enable_restart_services()
    
    submsg("Writing donefile")
    WARNS += write_done()
    
    if WARNS > 0:
        message("Done, but with " + WARNS + " warning(s)")
        sys.exit(1)
    else:
        message("Done")

if __name__ == "__main__":
    main()
