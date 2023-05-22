#!/usr/bin/env bash

help_and_exit(){
  cat 1>&2 << EOF
do_certbot.sh

Runonce that runs certbot, and the updates stunnel with Lets Encrypt! certs, so
it works with LE certs.

    USAGE:
    ./certbot_znc_update.sh [firstrun|renew|help]
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
### /CONSTANTS

message(){
  echo "do_certbot.sh: ${@}"
  logger "do_certbot.sh: ${@}"
}

submsg(){
  echo "[+] ${@}"
  logger "do_certbot.sh: ${@}"
}

exit_with_error(){
  echo 1>&2 "do_certbot.sh:ERROR: ${2}"
  logger "do_certbot.sh: ERROR: ${2}"
  exit ${1}
}

init_certbot(){
  certbot certonly --standalone --domains "${FQDN}" -n --agree-tos --email "${LETSENCRYPT_EMAIL}" || errors+=1
  return ${?}
}

renew_certbot(){
  /usr/bin/certbot -q renew
  return ${?}
}

main(){
  declare -i ERRORS=0
  local command="${1}"
  [ -z "${HARBORWAVE_DOMAIN}" ] && exit_with_error 2 "No Domain set, no qualified for a Lets Encrypt! cert"

  case ${command} in
    firstrun)
      message "Initializing..."
      submsg "Registering with Lets Encrypt via certbot"
      init_certbot || ERRORS+=1
      ;;
    renew)
      message "Updating Certs"
      submsg "Updating Lets Encrypt via certbot"
      renew_certbot || ERRORS+=1
      ;;
    *)
      help_and_exit
      ;;
  esac
  
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
