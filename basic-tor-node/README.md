Basic TOR Node
==============
This profile is for the disk-image-scripts/harbor-wave stack. It is a simple
TOR(https://www.torproject.org/) Node, that does nothing but act as a middle
node to quickly spin up capacity as a guard against DDoS attacks. It is NOT
intended for use as an entry or exit node, and does not listen for network
connections.

based on Debian, so needs debian 

PAYLOAD
-------
This uses harbor-wave payloads. whatever payload will be put at the end of the
torrc file.

HOW TO
----------

1. Compile with disk-image-scripts

```
gen_template_image.sh init-image
gen_template_image.sh compile-image
```

2. Upload to Digital Ocean's Cloud

3. Set Harbor-wave
Get the template ID number with list templates, and then use set template

```
harbor-wave list templates
harbor-wave set template <id number>

```

these really don't need to be that big. You can likely get away with
s-1vcpu-512mb-10gb. Besides its better to spawn more nodes than bigger nodes
```
harbor-wave set size s-1vcpu-512mb-10gb
```
You don't care about waiting for an IP. If you are using the latest git that has
this feature:
```
harbor-wave set wait false
```
If you have any additional parameters for torrc you want to use. Save them to
a file. These will be appended to the end of torrc on the machines
```
harbor-wave set payload "FILE:<path_to_torrc_options>"
```

4. Spawn

Spawn N amount of extra TOR nodes

```
harbor-wave spawn <N>
```

5. OPTIONAL - set timezone
under  template.rc you can change TIMEZONE away from UTC to local time. It
effects nothing

OPERATIONS
----------

If the machines come under attack the best bet is to recycle them with
```
harbor-wave destroy
harbor-wave spawn
```

iptables firewalls are set to allow incomming SSH and the bare min for TOR to
function.
