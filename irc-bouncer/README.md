IRC Bouncer
===========

A Bouncer image that features the ZNC IRC Bouncer. If you have a FQDN, then
certbot will run automaticly, pull Lets Encrypt! certs, and then update the ZNC
config to run authenticated certificates

Payload
-------
Payload has connect info.
user, pass for the bouncer, IRC networks. You can specify IRC network. One
variable per line

= seperate key and value
; end line
\# comment

**Bouncer Login**
admin_user	- user of administration for setup
admin_pass	- password for admin user
user		- unprivledged user
pass		- unprivledged user's password
port		- port to connect to the bouncer
no_tls		- set this to 1, yes, or true to disable TLS connecting to the
bouncer

**IRC stuff**
nick		- IRC "nickname". A an alternative can be specified after a : for
a backup alt in case your main is not available. format: nick=network:nick:altnick
full_name	- What to put in the IRC "Real Name" field.
chan_list	- List of channels to connect to, seperated by comma(,). Can be
blank. format chan_list=network:#chan1,#chan2,etcc

server		- IRC network to connect to format: server=network:server:nick:password
		If password
		
cert_file	- If authenticating with a keypair using SASL, the location of
the local .pem file. THis will be uploaded and installed automaticly. format:
cert_file=network:file location
