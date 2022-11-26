TOR-Snowflake
=============

Runs a TOR Snowflake node using docker-compose ontop of Debian. TOR snowflake
is a proxy to anonymize TOR usage to evade censorship. You can read more about
it here:

https://snowflake.torproject.org/

Compile
-------
To compile.
```
gen_cloud_template.sh init-image
gen_cloud_template.sh compile-template
```

You may now upload this to digital-ocean or cloud provider of choice.

Payload
-------
There are no payload options for this. One size fits all.
