OpenVPN-Server
==============
Be your own VPN. Provides a OpenVPN access point you control.

Requires you provide server certificates (cert,key,ca) for OpenVPN, and you
have a client setup for the same Certificate Authority(CA).

Certificates are specified in PAYLOAD

Debian Base

This makes extensive use of harbor-wave for start variables

Based on
- iptables
- dnsmasq
- openvpn
- some clever scripts

Compile
-------
```
gen_cloud_template.sh init-image
gen_cloud_tempalte.sh compile-template
```

Harbor-Wave Payloads
--------------------

openvpn.payload - blank payload file

This payload uses JSON and takes three keys for the VPN's Crypto

ca	- Cert file for the Certificate authority
cert	- Cert file for the server's certificate
key	- Key file for the server's certificate
ta	- Additional TLS key. This is static and used by both client and server
see https://openvpn.net/community-resources/how-to/

All of these will be the contents of a text file using x.509 certs as known to
work with OpenVPN. There is a yet to be written script that will generate
payloads from files

Erata
-----

tun0.conf	- OpenVPN client template

TODO
----

* Add some more variables, such as protocol and port
