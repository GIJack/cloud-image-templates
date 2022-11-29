#!/usr/bin/env bash
# Exit codes
# 0-success, 4-help
# 2-bad config. Check variables and ensure harbor-wave is setup correctly
# 9-spawn failed, 17-destroy failed, 25-spawn and destroy failed

### VARIABLES
# FILL THIS OUT. SCRIPT WILL FAIL IF THIS IS NOT FILLED OUT
TEMPLATE_ID="" # tor-snowflake template-id. get this from "harbor-wave list templates".

HARBOR_WAVE_SIZE="s-1vcpu-1gb" # from "harbor-wave list sizes"
FLIGHT_SIZE=10 # how many machines do we spawn per flight
FLIGHTS=(red green blue) #names of the flights. Needs to be exactly three.
DATES=(7 14 21) # Days of the month for rotation points. Needs to be exactly three
EMAIL="" # Optional, If this is set, this script will email the report to the address given
### /VARIABLES

help_and_exit(){
  cat 1>&2 << EOF
the_blizzard.sh:
A single snowflake by itself is beautiful, harmless, and unique. Alone it is 
small and fragile. Never a snowflake by itself. It is always working with
other snowflakes in the form of snow. A massive amount of snow is both beautiful
awe inspiring, and capable of shutting down entire counties and sometimes
states. It has stopped armies, humbled the heartiest of men, stopped conquests
and crushed ambitions.

A blizzard, a large amount of snow....

    USE:
    
    the_blizard.sh run

EOF
  exit 4
}
message(){
  echo "the_blizzard.sh: ${@}"
  logger "the_blizzard.sh ${@}"
  echo "${@}" >> "${MAIL_FILE}"
}
submsg(){
  echo "[+]	${@}"
  logger "the_blizzard.sh ${@}"
  echo "[+]	${@}" >> "${MAIL_FILE}"
}
exit_with_error(){
  echo 1>&2 "the_blizzard.sh: ERROR: ${2}"
  logger "the_blizzard.sh ERROR: ${2}"
  exit ${1}
}
warn(){
  echo 1>&2 "the_blizzard.sh: WARN: ${@}"
  logger "the_blizzard.sh WARN: ${@}"
  echo "WARN: ${@}" >> "${MAIL_FILE}"
}

### CONSTANTS
DATE=$(date "+%B %d, %Y")
HARBOR_WAVE_API_CHECK=$(harbor-wave get api-key)
HARBOR_WAVE_SSH_KEY_N=$(harbor-wave get ssh-key-n)
HARBOR_WAVE_REIGON_LIST=($(harbor-wave list regions -T |cut -d "," -f 1) )
HARBOR_WAVE_TEMPLATE_LIST=$(harbor-wave list templates -T | cut -d "," -f 1)
HARBOR_WAVE_SIZE_LIST=$(harbor-wave list sizes -T | cut -d "," -f 1)
DAY_OF_MONTH=$(date +%d)
### /CONSTANTS

send_email(){
  # email the results
  local fqdn=$(hostname -f)
  local sender="the_blizzard@${fqdn}"
  local subject="${fqdn}: the_blizard.sh report. Date: ${DATE}"
  
  mail -r "${sender}" -s "${subject}" "${EMAIL}" < "${MAIL_FILE}"
}

harbor_wave_spawn() {
  # runs harbor-wave spawn, takes a variable, the name of the flight
  local basename="${1}"
  
  # Pick a random reigon to spawn VMs
  local -i n=$(( ${RANDOM} % ${#HARBOR_WAVE_REIGON_LIST[*]} )) # random number for index of reigon list
  local reigon=${HARBOR_WAVE_REIGON_LIST[n]} #random reigon
  
  harbor-wave spawn ${FLIGHT_SIZE} -r "${reigon}" -n "${basname}" -s "${HARBOR_WAVE_SIZE}" --no-wait || return ${?}
}

rotate_flights() {
  # Stand up one, and bring down another
  local standup="${1}"
  local bringdown="${2}"
  submsg "Standing up ${standup}"
  harbor_wave_spawn "${standup}" || SPAWN_ERRORS+=1
  submsg "Standing Down ${bringdown}"
  harbor-wave destroy -n "${bringdown}" || DESTROY_ERRORS+=1
}

main(){
  SPAWN_ERRORS=0
  DESTROY_ERRORS=0
  local -i activated=0
  # pre-flight checks
  [ "${HARBOR_WAVE_API_CHECK}" != "HIDDEN" ] && exit_with_error 2 "No API key set with harbor-wave, see harbor-wave --help"
  [ -z "${HARBOR_WAVE_SSH_KEY_N}" ] && exit_with_error 2 "SSH key not set with harbor-wave, see harbor-wave --help"
  [ ${HARBOR_WAVE_SIZE_LIST} = *${HARBOR_WAVE_SIZE}* ] || exit_with_error 2 "Invalid template size. Ensure that the size code is actually on digital ocean. see habor-wave list sizes"
  [ ${HARBOR_WAVE_TEMPLATE_LIST} = *${TEMPLATE_ID}* ] || exit_with_error 2 "Invalid template. Ensure that your template is actually on digital ocean. see habor-wave list templates"
  [ ${#HARBOR_WAVE_REIGON_LIST[*]} -lt 1 ] && exit_with_error 3 "No Digital Ocean Reigons found? Check your setup!"
  
  # Run command goes, anything else: help_and exit
  [ "${1}" != "run" ] && help_and_exit
  
  ### Lets Go...
  # set up temp file with email message
  MAIL_FILE=$(mktemp)
  echo "The_blizard.sh Daily report $(date)" > "${MAIL_FILE}"
  echo "" >> "${MAIL_FILE}"
  # Wait a random number of seconds from 0 to 32768. This script should be run by cron, daily....
  # Run at random offset
  WAIT_TIME=${RANDOM}
  message "ITS COMMING DOWN! SSSSH. Sleeping ${WAIT_TIME} second(s)."
  sleep ${WAIT_TIME}
  message "I LIVE. GET YOUR GOLASHES, HERE COMES THE SNOW!"
  
  # The logic. Yes, this could probably be factored more for abritrary number of
  # dates. That is going to get dicey in shell tho
  if [ ${DAY_OF_MONTH} == ${DATES[0]} ];then
    rotate_flights "${FLIGHTS[0]}" "${FLIGHTS[1]}"
    activated=1
   elif [ ${DAY_OF_MONTH} == ${DATES[1]} ];then
    rotate_flights "${FLIGHTS[1]}" "${FLIGHTS[2]}"
    activated=1
   elif [ ${DAY_OF_MONTH} == ${DATES[2]} ];then
    rotate_flights "${FLIGHTS[2]}" "${FLIGHTS[0]}"
    activated=1
   else
    message "Today is not the day. Going back to Sleep. Zzzz"
    activated=0
  fi

  # Get financial data:
  local harbor_wave_money=$(harbor-wave list money-left -T)
  local money_left=$(cut -d "," -f "1" <<< ${harbor_wave_money})
  local burn_rate=$(cut -d "," -f "2" <<< ${harbor_wave_money})
  message "There is \$${money_left} money in your digital ocean account. Harbor-wave Burn rate is \$${burn_rate}/hour"

  # Summary and generate exit_code
  EXIT_CODE=0
  if [[ ${SPAWN_ERRORS} -eq 0 && ${DESTROY_ERRORS} -eq 0 ]];then
    message "DONE. No Errors. Goodbye until nextime..."
    EXIT_CODE=0
   elif [[ ${SPAWN_ERRORS} -ne 0 && ${DESTROY_ERRORS} -ne 0 ]];then
    mesage "Done, but rotation completed FAILED. Spawn and destroy both"
    EXIT_CODE=25
   elif [[ ${SPAWN_ERRORS} -ne 0 ]];then
    message "Done, but spawn failed. Could not stand up new snowflakes"
    EXIT_CODE=9
   elif [[ ${DESTROY_ERRORS} -ne 0 ]];then
    message "DONE, but could not get rid of stale snowflakes. This could be the first time in the monthly cycle and they don't exist yet."
    EXIT_CODE=17
  fi
  
  # if email is set, and it appears to be an addres(has a @ char), email the
  # results to said email address
  email_domain=$(cut -f "2" -d "@")
  if [ ! -z "${email_domain}" ];then
    send_email
  fi
  
  # Cleanup and exit
  rm -f "${MAIL_FILE}"
  exit ${EXIT_CODE}
}

main "${@}"
