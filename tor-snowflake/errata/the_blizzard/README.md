THE BLIZZARD
============
```
A single snowflake by itself is beautiful, harmless, and unique. Alone it is 
small and fragile. Never a snowflake by itself. It is always working with
other snowflakes in the form of snow. A massive amount of snow is both beautiful
awe inspiring, and capable of shutting down entire counties and sometimes
states. It has stopped armies, humbled the heartiest of men, stopped conquests
and crushed ambitions.

A blizzard, a large amount of snow....
```

WHAT
----
Automation script for the tor-snowflake image. 

This script runs from a cron job, and then automaticly rotates through
tor snowflake nodes, to prevent finger printing. It makes all nodes ephermedal

It will spawn some, and then destroy more snowflake images on your digital ocean
cloud.

HOW TO
------
This script assumes
1. you build the tor-snowflake profile, see above directory with disk-image-scripts
2. you've installed the tor-snowflake custom image into a digital ocean account
3. You generated a digital ocean API key, and setup harbor-wave.
4. You setup harbor-wave on a server, or at least always on computer with internet access

edit the_blizzard.cron for username that has harbor-wave setup. Install the scripts
to the correct paths.
```
/etc/cron.d/the_blizzard.cron
/usr/local/bin/the_blizzard.sh
```
You can use provided Makefile with:

```
make install
```

