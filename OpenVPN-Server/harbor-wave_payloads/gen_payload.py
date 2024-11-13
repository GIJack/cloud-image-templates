#!/usr/bin/env python3

banner='''This script will generate a payload file for harbor-wave with the
\'OpenVPN-Server\' template from the cloud-image-templates repo.

You need to setup a CA and client and server for OpenVPN, as well as the
additional TLS authentication using ta.key. You will be asked for file locations
for the CA certificate, and Server Certificate and key, as well as the ta.key.

OpenVPN Guide:
https://openvpn.net/community-resources/how-to/#setting-up-your-own-certificate-authority-ca-and-generating-certificates-and-keys-for-an-openvpn-server-and-multiple-clients

You can also use XCA, which has a nice GUI
https://hohnstaedt.de/xca/

For generating a ta.key file:
https://openvpn.net/community-resources/how-to/#hardening-openvpn-security

Port and Protocol can be left blank and defaults will be used.

    USAGE:
    ./gen_payload <filename>

    FILENAME:
    If a filename is specified, then that will be used, otherwise will write to
    harbor-wave-openvpn-server.payload
'''

import json
import os,sys

default = {
    'proto' : 'udp',
    'port'  : 1194,
}

blank_out_dict = {
  "_rev"  : 1.0,
  "_meta" : "OpenVPN payload for harbor-wave VM",
  "ca"  : "",
  "cert": "",
  "key" : "",
  "ta"  : "",
  "port"  : "1194",
  "proto" : "udp"
}

def _check_port(port):
    '''Check if port is a valid TCP Port number. Takes one parameter, the port, returns bool(True/False)'''
    # ports are intergers
    try:
        port = int(port)
    except:
        return False
    #between 1 and 65535, or 2^16 - 1
    if 1 <= port <= 65535:
        return True
    else:
        return False
        
def get_port_and_protocol():
    '''use input and prompt for a port and protocol, return tuple of port,proto . int for port, str for proto'''
    
    # Get the port
    prompt = 'Port(%s) ' % default['port']
    port   = input(prompt)
    if port == "":
        port = default['port']
    while _check_port(port) != True:
        warn_line = "Invalid Port: %s. Valid ports are from 1-65535" % port
        print(warn_line)
        port      = input(prompt)
        if port == "":
            port = default['port']
    port = int(port)
    
    # Get the protocol
    valid_protocols = ('tcp','udp')
    prompt = "Protocol(%s) " % default['proto']
    proto  = input(prompt)
    if proto == "":
        proto = default['proto']
    while proto not in valid_protocols:
        warn_line = "Invalid Protocol: %s. Valid protocols are %s" % (proto,", ".join(valid_protocols))
        print(warn_line)
        proto     = input(prompt)
        if proto == "":
            proto = default['proto']
            
    #if we made it this far, return
    return port,proto
    
def get_cert_file_names():
    '''Get certificate file name and location for ca, cert, key, and ta, return them as a tupple'''
    certs = { 'ca':'CA Certificate', 'cert':'Server Certificate', 'key':'Server Key', 'ta':'TLS Keyfile, ta.key' }
    results = []
    
    for file in certs:
        prompt   = "File Location for %s: " % certs[file]
        filename = input(prompt)
        while os.path.isfile(filename) == False:
            warn_line = "%s: No such file: %s" % (certs[file],filename)
            print(warn_line)
            filename  = input(prompt)
        results.append(filename)
    
    results = tuple(results)
    return results
    
def get_file_contents(filenames):
    '''takes a tupple of file names (ca_file, cert_file, key_file, ta_file), and returns a tupple with the content of those files.'''
    output = []
    
    for file in filenames:
        file_obj = open(file,"r")
        contents = file_obj.read()
        file_obj.close()
        output.append(contents)
    
    return output
    
def write_output(output,file):
    '''Write output to file. needs to be a string.'''
    file_obj = open(file,"w")
    file_obj.write(output)
    file_obj.close()

def main():
    # yeaaah, didn't feel like using argparse or getopts for a single input var
    if len(sys.argv) < 2:
        out_file = "harbor-wave-openvpn-server.payload"
    else:
        out_file = sys.argv[1]
    
    # start with the headers and we can keep adding to it
    out_dict = blank_out_dict 
    
    print(banner)

    port,proto     = get_port_and_protocol()
    
    #ca_file, cert_file, key_file, ta_file
    filenames      = get_cert_file_names()
    
    # read from the files
    ca,cert,key,ta = get_file_contents(filenames)
    
    # compile final config dict{}
    out_dict['port']  = port
    out_dict['proto'] = proto
    out_dict['ca']    = ca
    out_dict['cert']  = cert
    out_dict['key']   = key
    out_dict['ta']    = ta
    
    # Make it json
    output = json.dumps(out_dict,indent=2)
    
    #Write
    write_output(output,out_file)

main()
