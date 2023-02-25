Nextcloud disk-image-scripts/harbor-wave profile
================================================

WORK IN PROGRESS

This is a Disk-Image-Scripts Nextcloud profile for use with Harbor-Wave. This
is for spawning a nextcloud instance with habor-wave. Next cloud is an all in
one cloud application stack written in php using an SQL database. It was
designed around the old school LAMPS stack.

This example builds on LEMP(Linux \[E\]nginx MariaDB PHP) on Debian Stable.

\-\-\use\-dns or the 'use-dns' config option must be set to True, otherwise
this will not work. Nextcloud will need DNS set correctly to work.

\-\-use\-dns was implemented in version 0.3

Nextcloud
---------

https://nextcloud.com

The base nextcloud app is a PHP file storage and sharing with web interface
similar to 1-drive. It has calendar, addressbook, office, video confrencing
and other plugins that do many of the functions of google apps. It has a sharing
API for sharing files between users and also implements an OpenID service
provider. It can backend storage to a wide variety of of options from NFS,
SMB/CIFS, AWS S3 compatible buckets, and SFTP.

Documentation is here: https://docs.nextcloud.com/server/latest/admin_manual/

Payload
--------

TBD
