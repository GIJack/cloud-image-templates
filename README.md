# cloud-image-templates
Example cloud template image profiles for disk-image-scripts

[Disk Image Scripts](https://github.com/GIJack/disk-image-scripts)

Here are some example profiles that can be compiled with gen_cloud_template.sh
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
