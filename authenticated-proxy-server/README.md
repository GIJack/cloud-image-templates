Authenticated Proxy Server
==================
This is a basic tinyproxy based HTTP Proxy server.

features:
- scripts for intialization and password change. See MOTD
- harbor-wave intergration
- iptables firewall configuration blocking all other traffic
- Uses basic auth
- has an https proxy with stunnel and letsencrypt

Harbor Wave Payload
===================
uses a config with four items: user, pass, port and tls_port. item and value are
seperated with "="(colon), items/lines are seperated with ";"(semi-colon) and
uses a "#"(pound) for a comment.

Example
```
harbor-wave spawn --payload "user=jack;pass=mypass12345;port=8888;tls_port=8443;"
```

Example using payload file
```
harbor-wave spawn --payload "FILE:payload_files/proxy_harborwave.payload"
```

Defaults
========
Default Username, Password, Port, and tls_port.


User **proxyuser** 

Pass **proxypass**

port **8888**

tls_port **8443**
