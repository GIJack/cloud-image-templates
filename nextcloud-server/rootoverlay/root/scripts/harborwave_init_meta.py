#!/usr/bin/env python
# exit codes 0-success, 1-operation error, 2-condition error
prog_desc='''
Download initialize harbor-wave data from Digital Ocean's API, so its available
for the system
'''

import sys,os
import json
import subprocess
import urllib.request
from http.client import responses as http_responses
from datetime import datetime

config = {
    'host'            : '169.254.169.254',
    'path'            : '/metadata/v1/user-data',
    'timeout'         : 3, # timeout, in seconds, for URL query
    'logfile'         : "/var/log/harbor-wave-init.log",
    'app-dir'         : '/opt/harborwave',
    'done-file'       : '/opt/harborwave/done',
    'reload-services' : ['redis','nginx','mysqld','php7.4-fpm'] # systemd units
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

def proc_environment(data):
    '''Write config, and set permissions'''
    error_code = 0
    # write env file
    env_file = '/etc/environment'
    out_lines  = "HARBORWAVE_SEQEUNCE=" + str(data['sequence']) + "\n"
    out_lines += "HARBORWAVE_BASENAME=" + data['base-name'] + "\n"
    out_lines += "HARBORWAVE_DOMAIN="   + data['domain'] + "\n"
    try:
        file_obj = open(env_file,'a')
        file_obj.write(out_lines)
        file_obj.close()
    except:
        warn("Could not write to " + env_file)
        error_code +=1
    # Gen, variables
    FQDN = data['base-name'] + data['sequence'] + "." + data['domain']
    # apply variables to nginx config
    nextcloud_config="/etc/nginx/sites-available/nextcloud.conf"
    redis_config="/etc/redis/redis.conf"
    try:
        file_obj      = open(nextcloud_config,"r")
        file_contents = file_obj.read()
        file_obj.close()
    except:
        warn("Could not read nextcloud config file!")
        error_code +=1
    file_contents = file_contents.replace("+FQDN+",FQDN)
    try:
        file_obj = open(nextcloud_config,"w")
        file_obj.write(file_contents)
        file_obj.close()
    except:
        warn("Could not write nextcloud config")
        error_code +=1
    #Set reddis config
    reddis_add_lines="\nunixsocket /var/run/redis/redis-server.sock\nunixsocketperm 770\n"
    try:
        file_obj   = open(redis_config,"a")
        file_obj.write(reddis_add_lines)
        file_obj.close()
    except:
        warn("Could not write redis config")
        error_code +=1
    # set permissions and groups
    error_code += subproccess.check_call(['usermod','-aG','redis','www-data'])
    
    if error_code != 0:
        return 1
    else:
        return 0

def setup_lets_encrypt(data):
    '''run certbot, and configure Lets Encrypt! for this host'''
    return False #TODO
    
def proc_payload(data):
    '''Proccess payload from harbor-wave command line'''
    #TODO figure out what payload should be
    return False
    
def reload_services():
    '''reload restart services with systemd that have modified configs. Takes no parameters'''
    error_code = 0
    for item in config['restart-services']:
        error_code += subprocess.check_call(['systemctl','restart',item])

    if error_code != 0:
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
    
    submsg("Writing Config Files")
    WARNS += proc_environment(data)
    
    submsg("Processing Command Line payload")
    WARNS += proc_payload(data)
    
    submsg("Reloading Services")
    WARNS += reload_services()
    
    submsg("Writing donefile")
    WARNS += write_done()
    
    if WARNS > 0:
        message("Done, but with " + WARNS + " warning(s)")
        sys.exit(1)
    else:
        message("Done")

if __name__ == "__main__":
    main()
