#!/usr/bin/env bash

### CONFIG
TINYPROXY_CONF_FILE=/etc/tinyproxy/tinyproxy.conf
### /CONFIG

help_and_exit(){
  cat 1>&2 << EOF
This script changes the password of tinyproxy. It edits the config file and
then restarts the service

proxy_passwd.sh <password>

If password is empty it will be prompted

error codes 0-success, 1-operation error, 2-invalid input, 4-help
EOF
  exit 4
}

exit_with_error(){
  echo 1>&2 "proxy_password.sh: ERROR: ${2}"
  exit ${1}
}

main() {
  local exit_code=0
  local password="${1}"
  local confirm_password=""
  local proxyuser=""
  
  [ "${1}" == "--help" ] && help_and_exit
  
  echo "Changing Tinyproxy password..."
  
  # Get username from config
  proxyuser=$(grep -e "^BasicAuth.*" "${TINYPROXY_CONF_FILE}"|cut -d " " -f 2) || exit_code+=1
  
  # get new password. If one wasn't provided, prompt for one. Then ask for
  # confirmation
  if [ -z "${password}" ];then
    while [ -z "${password}" ];do
      read -rs -p "New Proxy Password: " password
      echo ""
    done
    while [ -z "${confirm_password}" ];do
      read -rs -p "Confirm New Password: " confirm_password
      echo ""
    done
    [ "${password}" != "${confirm_password}" ] && exit_with_error 2 "Entries did not match, not changing password"
  fi
  
  # Generate new config line
  authline="BasicAuth ${proxyuser} ${password}"
  # update tinyproxy config
  sed -ie "s/^BasicAuth.*/${authline}/" "${TINYPROXY_CONF_FILE}" || exit_code+=1
  
  # Restart to apply
  systemctl restart tinyproxy || exit_code+=1
  
  if [ ${exit_code} -gt 0 ];then
    exit_with_error 1 "Script threw a code, password change did not work"
   else
    echo "Password Changed"
    exit 0
  fi
}

main "${@}"
