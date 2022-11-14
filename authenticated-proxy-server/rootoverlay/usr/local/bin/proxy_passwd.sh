#!/usr/bin/env bash

# 
CONFIG=/etc/tinyproxy/tinyproxy.conf

help_and_exit(){
  cat 1>&2 << EOF
This script changes the password of tinyproxy

proxy_passwd.sh <password>

If password is empty it will be prompted

error codes 0-success, 1-operation error, 2-invalid input, 4-help
EOF
  exit 4
}

main() {
  local exit_code=0
  local password="${1}"
  local proxyuser=""
  echo "Changing Tinyproxy password:"
  
  # Get username from config
  proxyuser=$(grep -e "^BasicAuth.*" "${CONFIG}"|cut -d " " -f 2) || exit_code+=1
  
  # get new password
  [ -z ${1} ] && read -rs -p "Proxy Password: " password
  # Check to make sure password exists
  [ -z ${password} ] && exit_with_error 2 "Password is blank, try again!"
  
  # Generate new config line
  authline="BasicAuth ${proxyuser} ${password}"
  # update tinyproxy config
  sed -ie "s/^BasicAuth.*/${authline}/" "${CONFIG}" || exit_code+=1
  
  if [ exit_code -ge 0 ];then
    exit_with_error 1 "Script threw a code, password change did not work"
   else
    echo "Password Changed"
    exit 0
  fi
}

main "${@}"
