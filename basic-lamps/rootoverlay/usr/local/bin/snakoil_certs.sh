#!/usr/bin/env bash

help_and_exit(){
  cat 1>&2 << EOF
snakeoil_cert.sh:

Generate snakeoil cert pairs with openssl. NOTE: live domains will be setup
with Lets Encrypt! using certbot. This is for things not internet facing and
defaults

	USAGE:
snakeoil_cert.sh (hostname) (key length in bits) (days 'till expiration)

exit codes 0-success, 1-execution error, 2-bad input, 4-help

EOF
  exit 4
}

[ ${1} == "--help" ] && help_and_exit

#Grab variables and set defaults of blank
CERTNAME="${1}"
BITS="${2}"
DAYS="${3}"
[ -z $1 ] && CERTNAME="server"
[ -z $2 ] && BITS=4096
[ -z $3 ] && DAYS=3650

echo "Generating Snakeoil TLS cert. You should use certbot to get a Lets Encrypt! cert for an internet facing domain"
openssl req -x509 -sha256 -nodes -days ${DAYS} -newkey rsa:${BITS} -keyout "${CERTNAME}.key" -out "${CERTNAME}.crt"
