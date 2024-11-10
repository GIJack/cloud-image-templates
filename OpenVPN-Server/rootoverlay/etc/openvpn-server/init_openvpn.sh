#!/usr/bin/env bash
help_and_exit(){
  cat 1>&2 << EOF
init_openvpn.sh:

Initialize per-instance files for OpenVPN. Run this once
1. Generate DH Parms
2. Generate TA key
3. Ensure Dir for Certs Exists

    USAGE
    /etc/openvpn/init_openvpn.sh
    
If any parameters are specified, this script help and exits
EOF
  exit 4
}

### CONFIG
DH_BITS=2048
OUT_DIR="/etc/openvpn/server/"
OPENVPN_LOG="/var/log/openvpn/openvpn-status.log"
### /CONFIG

### CONSTANTS
OPENVPN_LOG_DIR="$(dirname ${OPENVPN_LOG})"
### /CONSTANTS

message(){
  echo "init_openvpn.sh: ${@}"
  logger -i -p user.notice "init_openvpn.sh: ${@}"
}
exit_with_error(){
  echo 1>&2 "init_openvpn.sh: ERROR: ${2}"
  logger -i -p user.err "init_openvpn.sh: ERROR: ${2}"
  exit ${1}
}
warn(){
  echo 1>&2 "init_openvpn.sh: WARN: ${@}"
  logger -i -p user.warning "init_openvpn.sh: WARN: ${@}"
}
submsg(){
  echo "[+]	${@}"
  logger -i -p user.notice "init_openvpn.sh: ${@}"
}


gen_dh_parms(){
  openssl dhparam -out "${OUT_DIR}/dh.pem" ${DH_BITS} || return 1
}

gen_ta_key(){
  openvpn --genkey secret "${OUT_DIR}/ta.key" || return 1
}

set_dir_perms(){
  mkdir -p "${OUT_DIR}" || exit_with_error 2 "Could not create ${OUT_DIR}"
  chmod 700 "${OUT_DIR}" || warn "Could not set permissions for ${OUT_DIR}"
}

main(){
  [ ! -z "${1}" ] && help_and_exit
  message "Initializing OpenVPN files"
  
  submsg "Initializing directory"
  set_dir_perms
  
  submsg "Generating dh.pem"
  gen_dh_parms || exit_with_error 1 "Could Not Generate dh.pem"
  
  submsg "Generating ta.key"
  gen_ta_key || exit_with_error 2 "Could Not Generate ta.key"
  
  message "Done"
}

main "${@}"
