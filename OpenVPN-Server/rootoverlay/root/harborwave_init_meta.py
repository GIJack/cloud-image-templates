#!/usr/bin/env python
# exit codes 0-success, 1-operation error, 2-condition error
prog_desc='''
Download initialization harbor-wave data from Digital Ocean's API.

Modified for OpenVPN-Server.
'''

import sys,os
import json
import urllib.request
from http.client import responses as http_responses
from datetime import datetime

config = {
    'host'      : '169.254.169.254',
    'path'      : '/metadata/v1/user-data',
    'timeout'   : 3, # timeout, in seconds, for URL query
    'logfile'   : "/var/log/harbor-wave-init.log",
    'app-dir'   : '/opt/harborwave',
    'done-file' : '/opt/harborwave/done',
    'openvpn-dir' : '/etc/openvpn/server/',
}

openvpn_file = {
    'ca'   : '/etc/openvpn/server/ca.crt',
    'cert' : '/etc/openvpn/server/server.crt',
    'key'  : '/etc/openvpn/server/server.key',
    'ta'   : '/etc/openvpn/server/ta.key',
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

def openvpn_runonce():
    errors = 0
    
    # Make directory
    try:
        os.makedirs(config['openvpn-dir'],0o700,exit_ok=True)
        os.chmod(config['openvpn-dir'],0o700)
    except:
        warn_line = "Dir %s does not exist and cannot be created" % config['openvpn-dir']
        warn(warn_line)
        return 1
    
    # Create dh.pem
    dh_file = config['openvpn-dir'] + "dh.pem"
    dh_bits = 2048
    errors += subprocess.check_call(['openssl', 'dhparam', '-out', dh_file, dh_bits])

def process_payload(data):
    '''Process payload. Write OpenVPN Cert and Key Files from Payload.'''
    warns = 0
    # decode the JSON
    try:
        payload_dict = json.loads(data)
    except:
        warn("Invalid JSON, OpenVPN remains unconfigured")
        return 1
    
    json_key_list = ['ca','cert','key','ta']

    # preflight checks.
    for key in json_key_list:
        if key not in payload_dict:
            warn_line = "%s not found in payload, aborting" %s key
            warn(warn_line)
            return 1
    
    # write to the files
    for item in json_key_list:
        try:
            file_obj = open(openvpn_file[item],"w")
            file_obj.write(payload_dict[item])
            file_obj.close()
            os.chmod(openvpn_file[item],0o400)
        except:
            warn_line = "Could Not Write %s" % file
            warn(warn_line)
            warns += 1
            
    return(warns)

def start_enable_openvpn():
    exit_code = 0
    service = "openvpn-server@tun0"
    try:
        exit_code += subprocess.check_call(['systemctl', 'restart', service])
    except:
        warn("Could Not Restart Service: " + item)
        exit_code += 1
    try:
        exit_code += subprocess.check_call(['systemctl', 'enable', service])
    except:
        warn("Could Not Enable Service: " + item)
        exit_code += 1

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
    
    submsg("Generating dh.pem")
    WARNS += openvpn_runonce()
    
    submsg("Processing payload")
    WARNS += process_payload(data)
    
    submsg("Start/Enable OpenVPN")
    WARNS += start_enable_openvpn()
    
    submsg("Writing donefile")
    WARNS += write_done()
    
    if WARNS > 0:
        message("Done, but with " + WARNS + " warning(s)")
        sys.exit(1)
    else:
        message("Done")

if __name__ == "__main__":
    main()
