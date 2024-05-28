This folder holds explanation and basic configuration files
on how to run common web server proxies for Odoo
with podman.

To generate the SSL certificates and make it trusted by Chrome, you can run (Restart Google Chrome after):
```sh
# Having a self signed certificate is not enough if you want the browser to fully trust https://localhost
# You need to install locally your own CA and sign your SSL certificates with this CA
mkdir .certs .ca
openssl genrsa -out .ca/rootCA.key 2048
openssl req -x509 -new -nodes -key .ca/rootCA.key -sha256 -days 1024 -out .ca/rootCA.pem -subj "/C=US/ST=State/L=City/O=Organization/OU=OrgUnit/CN=RootCA"
openssl genrsa -out .certs/localhost.key 2048
openssl req -new -key .certs/localhost.key -out .certs/localhost.csr -subj "/C=US/ST=State/L=City/O=Organization/OU=OrgUnit/CN=localhost"
cat <<EOL > .certs/localhost.ext
authorityKeyIdentifier=keyid,issuer
basicConstraints=CA:FALSE
keyUsage = digitalSignature, nonRepudiation, keyEncipherment, dataEncipherment
extendedKeyUsage = serverAuth
subjectAltName = @alt_names

[alt_names]
DNS.1 = localhost
EOL
openssl x509 -req -in .certs/localhost.csr -CA .ca/rootCA.pem -CAkey .ca/rootCA.key -CAcreateserial -out .certs/localhost.crt -days 500 -sha256 -extfile .certs/localhost.ext
cat .certs/localhost.crt .certs/localhost.key > .certs/localhost.pem
# Add the Root CA to the NSS database of Google Chrome
sudo apt install -y libnss3-tools
certutil -d sql:$HOME/.pki/nssdb -A -t "C,," -n "RootCA" -i .ca/rootCA.pem
```

To be able to use port 80 without root privileges (podman being rootless),
you must first add `net.ipv4.ip_unprivileged_port_start=80` to `/etc/sysctl.conf`,
then do `sudo sysctl -p`.
