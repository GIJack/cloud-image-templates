#!/usr/bin/env bash

CONFIG=/etc/tinyproxy/tinyproxy.conf

IPTABLES_CONFIG=/etc/iptables/iptables.rules
IP6TABLES_CONFIG=//etc/iptables/ip6tables.rules

help_and_exit(){
  cat 1>&2 << EOF
Set Port for Tinyproxy before first run.

init_proxy.sh (port)

If port is blank, it will be prompted.

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
  local port="${1}"
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
  [ -z ${3} ] && read -r -p "Proxy port(default: 8888): " portinput
  
  # Sanity Check, make sure we do in fact have a username and password
  [ -z ${port} ] && port=8888
  
  # Update iptables config
  iptables_line="-A INPUT -m multiport -p tcp -s 0.0.0.0/0 --dports ${port} -j ACCEPT # Proxy Server(tiny proxy)"
  ip6tables_line="-A INPUT -m multiport -p tcp --dports ${port} -j ACCEPT # Proxy Server(tiny proxy)"
  sed -ie "s/.*# Proxy Server(tiny proxy)$/${iptables_line}" "${IPTABLES_CONFIG}"
  sed -ie "s/.*# Proxy Server(tiny proxy)$/${ip6tables_line}" "${IP6TABLES_CONFIG}"
  
  # enable and start tinyproxy
  systemct restart iptables ip6tables || exit+=1
  systemctl restart tinyproxy || exit_code+=1
  systemctl enable tinyproxy || exit_code+=1
  
  if [ exit_code -ge 0 ];then
    exit_with_error 1 "Script threw a code, setup is NOT complete"
   else
    echo "Tinyproxy Port set to ${port} complete."
    exit 0
  fi
}

main "${@}"
