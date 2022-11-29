#!/usr/bin/env bash

# Initializing snowflake. Runonce. Will disabled itself if it succeedes

message() {
  echo "init_snowflake.sh: ${@}"
}
exit_with_error(){
  echo 1>&2 "init_snowflake.sh: ERROR: ${2}"
  exit ${1}
}

main() {
  # code goes here
  ERROR=0
  message "Spawning TOR-Snowflake docker containers"
  
  cd /root
  docker-compose up -d snowflake-proxy || ERROR+=1
  
  if [ ${ERROR} -ne 0 ];then
    exit_with_error 1 "Docker-compose for snowflake-proxy FAILED!"
   else
    message "Done. TOR snowflake setup"
    systemctl disable harborwave-runonce
    exit 0
  fi
}

main "${@}"


