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

gen_payload.py  - python script for generating payloads based on prompts

This payload uses JSON and takes three keys for the VPN's Crypto

ca	- Cert file for the Certificate authority
cert	- Cert file for the server's certificate
key	- Key file for the server's certificate
ta	- Additional TLS key. This is static and used by both client and server
see https://openvpn.net/community-resources/how-to/

All of these will be the contents of a text file using x.509 certs as known to
work with OpenVPN. There is a yet to be written script that will generate
payloads from files

port	- port number for the VPN server to listen on. may be any valid tcp/udp
port number(1-65535)
proto	- protocol to use. Either udp or tcp

Erata
-----

tun0.conf	- OpenVPN client template

Setting up OpenVPN for Certificate Authentication:
--------------------------------------------------

This only works with Certificate authentication. You need to setup a CA, and then
generate client and server keys and certs. for the payload you will need the CA
cert, the server key and cert, you will also need an additiona TLS key, known
as ta.key.

OpenVPN Guide:
https://openvpn.net/community-resources/how-to/#setting-up-your-own-certificate-authority-ca-and-generating-certificates-and-keys-for-an-openvpn-server-and-multiple-clients

You can also use XCA, which has a nice GUI
https://hohnstaedt.de/xca/

For Generating ta.key see this:
https://openvpn.net/community-resources/how-to/#hardening-openvpn-security
