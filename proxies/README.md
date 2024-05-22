This folder holds explanation and basic configuration files
on how to run common web server proxies for Odoo
with podman.

To be able to use port 80 without root privileges (podman being rootless),
you must first add `net.ipv4.ip_unprivileged_port_start=80` to `/etc/sysctl.conf`,
then do `sudo sysctl -p`.
