```sh
podman run --rm --name lighttpd -p 80:80 -p 443:443 -v ./lighttpd.conf:/etc/lighttpd/lighttpd.conf:ro -v ./.certs:/etc/lighttpd/ssl/:ro docker.io/jitesoft/lighttpd:latest
```
