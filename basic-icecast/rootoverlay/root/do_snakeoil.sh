#!/usr/bin/env bash

# Generate a snakeoil cert. Takes no parameters

### VARIABLES
SSL_DIR="/etc/ssl"
CERTNAME="server"
BITS=4096
DAYS=3650
ICECAST_CERT="/usr/share/icecast/icecast.pem"
### /VARIABLES

main() {
   local errors=0

   # Gen Cert
   openssl req -x509 -sha256 -nodes -days ${DAYS} -newkey rsa:${BITS} -keyout "${SSL_DIR}/${CERTNAME}.key" -out "${SSL_DIR}/${CERTNAME}.crt" || errors+=1
   # Combined file for icecast
   cat "${SSL_DIR}/${CERTNAME}.key"  "${SSL_DIR}/${CERTNAME}.crt" > "${ICECAST_CERT}" || errors+=1
   if [ ${ERRORS} -gt 0 ];then
     echo "do_snakeoil.sh: script threw an error, see above"
     exit 1
    else
     exit 0
   fi
}

main "${@}"
