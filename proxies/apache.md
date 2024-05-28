```sh
podman run --rm --name apache -p 80:80 -p 443:443 -v ./apache.conf:/usr/local/apache2/conf/httpd.conf:ro -v ./.certs/:/etc/apache2/ssl/:ro docker.io/httpd:latest
```
