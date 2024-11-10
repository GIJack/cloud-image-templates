OpenVPN-Server
==============
Be your own VPN. Provides a OpenVPN access point you control.

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
gen\_cloud\_template.sh init-image
gen\_cloud\_tempalte.sh compile-template
```

Harbor-Wave Payloads
--------------------
TODO - auto-generate payload file from OpenSSL certs

openvpn.payload - blank payload file
