```sh
podman run --rm --name apache -p 80:80 -v ./apache.conf:/usr/local/apache2/conf/httpd.conf:ro docker.io/httpd:latest
```
