#!/usr/bin/env bash

# Because this is run on firstrun
source /etc/environment

help_and_exit(){
  cat 1>&2 << EOF
do_certbot.sh

Runonce that runs certbot, and generates single file .pem for icecast

Has work arounds for aggressive IPtables rules. Needs to be run as root

    USAGE:
    ./do_certbot [firstrun|renew|help]
EOF
  exit 4
}
### VARIABLES
# Edit this before use. This is what email your LETS ENCRYPT! certs are registered to
readonly LETSENCRYPT_EMAIL="postmaster@example.com"

### /VARIABLES

### CONSTANTS
readonly FQDN="$(hostname).${HARBORWAVE_DOMAIN}"
readonly ENCRYPTION_KEY="/etc/letsencrypt/live/${FQDN}/privkey.pem"
readonly ENCRYPTION_CERT="/etc/letsencrypt/live/${FQDN}/fullchain.pem"
readonly ICECAST_CERT="/usr/share/icecast/icecast.pem"
readonly PORT=80
readonly SERVICES="icecast"
### /CONSTANTS

message(){
  echo "do_certbot.sh: ${@}"
  logger "do_certbot.sh: ${@}"
}

submsg(){
  echo "[+] ${@}"
  logger "do_certbot.sh: ${@}"
}

warn(){
  echo 1>&2 "do_certbot.sh: WARN: ${2}"
  logger "do_certbot.sh:WARN: ${2}"
}

exit_with_error(){
  echo 1>&2 "do_certbot.sh: ERROR: ${2}"
  logger "do_certbot.sh:ERROR: ${2}"
  exit ${1}
}

init_certbot(){
  local -i error_code=0
  local iptables_string="INPUT -m tcp -p tcp --dport ${PORT} -j ACCEPT"
  iptables -I ${iptables_string} || return 9
 
  certbot certonly --standalone --domains "${FQDN}" -n --agree-tos --email "${LETSENCRYPT_EMAIL}" || error_code=${?}
 
  iptables -D ${iptables_string} || warn "IPTables rule for certbot left open. Please correct this mantually"
  return ${error_code}
}

gen_icecast_file(){
   local return_code=0
   cat "${ENCRYPTION_KEY}" "${ENCRYPTION_CERT}" > "${ICECAST_CERT}"
   if [ ${?} -ne 0 ];then
     warn "Could not generate combined .pem for icecast"
     return 1
    else
     return 0
   fi
}

renew_certbot(){
  local -i error_code=0
  local iptables_string="INPUT -m tcp -p tcp --dport ${PORT} -j ACCEPT"
  submsg "Opening firewall hole"
  iptables -I ${iptables_string} || return 9
  submsg "Stopping Services"
  for service in ${SERVICES};do
    systemctl stop ${service} || warn "Could not stop ${item}"
  done
  submsg "Updating Lets Encrypt via certbot"

  certbot certonly --standalone --domains "${FQDN}" -n --agree-tos --email "${LETSENCRYPT_EMAIL}" || error_code=${?}
 
  submsg "Closing Firewall hole"
  iptables -D ${iptables_string} || warn "IPTables rule for certbot left open. Please correct this mantually"
  submsg "Restarting Services"
  for item in ${SERVICES};do
    systemctl restart "${item}" || warn "Could not start ${item}"
  done
  return ${error_code}
}

main(){
  declare -i ERRORS=0
  local command="${1}"
  [ -z "${HARBORWAVE_DOMAIN}" ] && exit_with_error 2 "No Domain set, no qualified for a Lets Encrypt! cert"
  [ ${EUID} -ne 0 ] && exit_with_error 2 "This script needs to be run as root."
  
  case ${command} in
    firstrun)
      message "Initializing..."
      submsg "Registering with Lets Encrypt via certbot"
      init_certbot || ERRORS+=1
      ;;
    renew)
      message "Updating Certs"
      renew_certbot || ERRORS+=1
      ;;
    *)
      help_and_exit
      ;;
  esac
  
  submsg "Updating icecast .pem cert"
  gen_icecast_file || ERRORS+=1

  case ${ERRORS} in
    0)
     message "Done"
     exit 0
     ;;
    1)
     message "Done, but with 1 error"
     exit 1
     ;;
    *)
     message "Done, but with ${ERRORS} errors"
     exit 1
     ;;
  esac
  
}

main "${@}"
