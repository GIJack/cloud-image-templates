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


admin_user	- user of administration for setup
admin_pass	- password for admin user

user		- unprivledged user
pass		- unprivledged user's password

port		- port to connect to the bouncer
no_tls		- set this to 1, yes, or true to disable TLS connecting to the
bouncer

server		- IRC network to connect to format: server=network:server:nick:password
