#!/usr/bin/env bash

CONFIG=/etc/tinyproxy/tinyproxy.conf

IPTABLES_CONFIG=/etc/iptables/iptables.rules
IP6TABLES_CONFIG=/etc/iptables/ip6tables.rules

help_and_exit(){
  cat 1>&2 << EOF
Initilize tinyproxy before first run.

init_proxy.sh <username> <password> (port)

If either username,password, or port is blank, they will be prompted.

default port: 8888

error codes 0-success, 1-operation error, 2-invalid input, 4-help

EOF
  exit 4
}

exit_with_error(){
  echo 1>&2 "init_proxy.sh: ERROR: ${2}"
  exit ${1}
}

main() {
  local -i exit_code=0
  local proxyuser="${1}"
  local password="${2}"
  local port="${3}"
  local authline=""
  local iptables_line=""
  local ip6tables_line=""

  # Check help.
  if [[ ${1} = *help* ]];then
    help_and_exit
  fi
  
  # This needs to be run as root
  [[ $UID -ne  0 ]] && exit_with_error 1 "This script needs to be run as root"

  #Bannner
  "Initializing tinyproxy authenication, see --help for more info"
  # Get username and password:
  [ -z ${1} ] && read -r -p "Proxy User(default: proxyuser): " proxyuser
  [ -z ${2} ] && read -rs -p "Proxy Password(default: proxypass): " password
  [ -z ${3} ] && read -r -p "Proxy port(default: 8888): " portinput
  
  # Sanity Check, make sure we do in fact have a username and password
  [ -z "${proxyuser}" ] && proxyuser="proxyuser"
  [ -z "${password}" ] && password="proxypass"
  [ -z "${port}" ] && port=8888
  
  # Generate new config line
  authline="BasicAuth ${proxyuser} ${password}"
  portline="Port ${port}"
  # update tinyproxy config
  echo "${authline}" >> "${CONFIG}" || exit_code+=1
  echo "${porline}" >> "${CONFIG}" || exit_code+=1
  
  # Update iptables config
  iptables_line="-A INPUT -m multiport -p tcp -s 0.0.0.0/0 --dports ${port} -j ACCEPT # Proxy Server(tiny proxy)"
  ip6tables_line="-A INPUT -m multiport -p tcp --dports ${port} -j ACCEPT # Proxy Server(tiny proxy)"
  echo "${iptables_line}" >> "${IPTABLES_CONFIG}"
  echo "${ip6tables_line}" >> "${IP6TABLES_CONFIG}"
  
  # enable and start tinyproxy
  systemctl restart iptables ip6tables || exit_code+=1
  systemctl restart tinyproxy || exit_code+=1
  systemctl enable tinyproxy || exit_code+=1
  
  if [ exit_code -ge 0 ];then
    exit_with_error 1 "Script threw a code, setup is NOT complete"
   else
    echo "Tinyproxy setup complete. Listening on port ${port}"
    exit 0
  fi
}

main "${@}"
