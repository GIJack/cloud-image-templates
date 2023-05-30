#!/usr/bin/env bash

# Generate a snakeoil cert. Takes no parameters
SSL_DIR="/etc/ssl"
CERTNAME="server"
BITS=4096
DAYS=3650

openssl req -x509 -sha256 -nodes -days ${DAYS} -newkey rsa:${BITS} -keyout "${SSL_DIR}/${CERTNAME}.key" -out "${SSL_DIR}/${CERTNAME}.crt"
