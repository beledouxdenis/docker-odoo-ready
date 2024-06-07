This folder holds explanation and basic configuration files
on how to run common web server proxies for Odoo
with podman.

To generate the SSL certificates and make it trusted by Chrome, you can run (Restart Google Chrome after):
```sh
# Having a self signed certificate is not enough if you want the browser to fully trust `https://localhost`.
# You need to add your certificate to the browser trusted certificates database.
# The snakeoil certificates which are installed by default with `ssl-certificate` could be used
# but they work only for your machine name (hostname).
# Generate a new one to support multiple domains: `localhost`, your host name and `odoo.local`
mkdir .certs
openssl req -x509 -nodes -days 730 -newkey rsa:2048 -keyout .certs/localhost.key -out .certs/localhost.pem \
    -subj "/CN=localhost" -addext "subjectAltName=DNS:localhost,DNS:`hostname`,DNS:odoo.local"
sudo apt install -y libnss3-tools
# Add the certificate to Google Chrome's trusted certificates
certutil -d sql:$HOME/.pki/nssdb -A -t "P,," -n "Localhost" -i .certs/localhost.pem
```

To be able to use port 80 without root privileges (podman being rootless),
you must first add `net.ipv4.ip_unprivileged_port_start=80` to `/etc/sysctl.conf`,
then do `sudo sysctl -p`.
