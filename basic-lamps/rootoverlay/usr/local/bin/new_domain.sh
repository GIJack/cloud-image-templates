#!/usr/bin/env/bash

help_and_exit(){
  cat 1>&2 << EOF
new_domain.sh:

Adds a new virtual domain into apache web server, and adds domain with
Lets Encrypt! using certbot.

If domain is blank, it is prompted.

DNS needs to be configured or certbot will fail.

	USAGE:
new_domain.sh <domain.tld>

exit codes 0-success, 1-execution error, 2-bad input, 4-help

EOF
  exit 4
}

exit_with_error(){
  echo 1>&2 "new_domain.sh: ERROR: ${2}"
  exit ${1}
}

main() {
  local domain=${1}
  # Check and validate inputs
  [ -z ${domain} ] && read -p "Enter new domain: " domain
  [ -z ${domain} ] && exit_with_error 2 "Invalid domain"
  
  echo "Setting up new domain ${domain}, using Apache and Certbot"
  # generate new vhost config file
  local new_conf_file="/etc/httpd/conf/vhosts/${domain}.conf"
  local new_web_root="/var/www/${domain}"
  cat /usr/local/share/apache/header_comments.txt > ${new_conf_file}
  cat /usr/local/share/apache/vhost_reg_template.conf >> ${new_conf_file}
  sed -i "s/example.com/${domain}/g" ${new_conf_file}

  # make base dir and put a placeholder file
  mkdir -p ${new_web_root}/
  mkdir -p ${new_web_root}/.well_known
  cp /usr/local/share/apache/example_index.html ${new_web_root}/index.html
  
  # restart apache for new changes to take effect
  systemct restart httpd || exit_with_error 1 "could not restart apache, check configuration and error logs!"
  
  # get new cert with certbot
  certbot -d ${domain} --webroot --webroot-path ${new_web_root} certonly || \
   exit_with_error 1 "Certbot failed, cannot continue!"
  
  # add TLS config
  cat /usr/local/share/apache/vhost_tls_template.conf >> ${new_conf_file}
  
  # restart apache again
  systemctl restart httpd || exit_with_error 1 "could not restart apache, check configuration and error logs!"
  
  echo "Done! https://${domain} should be valid"
}

main "${@}"
