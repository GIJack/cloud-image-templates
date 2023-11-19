Basic Icecast Server
====================

Icecast is a FOSS "internet radio" audio streaming server.

This profile lets you set admin user, password, stream password and set ports
with the payload. See options below

Payload
=======

payload items and defaults. Payload items should be seperated by a newline
or a ;, and item/value seperated by a =

default:

port=8000;
tls_port=8443;
admin_user=admin;
admin_password=password;
source_password=password;
relay_password=password;

see auth_icecast.payload for working payload file
