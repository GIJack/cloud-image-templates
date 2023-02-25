# cloud-image-templates
Example cloud template image profiles for disk-image-scripts.

[Disk Image Scripts](https://github.com/GIJack/disk-image-scripts)

Some of these can utilize harbor-wave features such as payload or sequence/name.

Harbor-wave only works with the Digital Ocean API, and works on their cloud.

[harbor-wave](https://github.com/gijack/harbor-wave)

Here are some example profiles that can be compiled with gen\_cloud\_template.sh
from disk-image scripts, then used with a cloud provider as VM templates.

See relevant man pages for description of formats and commands

Needs Disk-Image Scripts 1.2 or later.

To build profiles:

perform base install
```
gen_cloud_template.sh init-image
```
Compile final image for export to cloud provider
```
gen_cloud_template.sh compile-template
```

EXAMPLES:
---------
**basic-proxy-server** : Basic Anonymous web proxy using tinyproxy

**authenticated-proxy-server** : Tinyproxy server with BasicAuth

**basic-lamps** : Linux Apache MySQL PHP OpenSSL Application server.

**basic-tor-node** : Run an onion router middle node, with no in or outputs.
This can be used to expand the network if spawned in serial with harbor-wave
and in great numbers

**tor-snowflake** : Generate a node running TOR's snowflake proxy. For more
information see: https://snowflake.torproject.org/

**nextcloud-server** : a nextcloud instance. see https://nextcloud.com
