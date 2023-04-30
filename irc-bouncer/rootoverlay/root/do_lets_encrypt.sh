#!/usr/bin/env bash

help_and_exit(){
  cat 1>&2 << EOF
do_lets_encrypt.sh

Runonce that runs certbot, and the updates znc with Lets Encrypt! certs, so
it works with LE certs
EOF
  exit 4
}

message(){
  echo "do_lets_encrypt.sh: ${@}"
}

submsg(){
  echo "	${@}"
}

exit_with_error(){
  echo 1>&2 "do_lets_encrypt.sh: ERROR: ${2}"
  exit ${1}
}

warn(){
  echo 1>&2 "do_lets_encrypt.sh: WARN: ${@}"
}

main(){
  true
}

main "${@}"
