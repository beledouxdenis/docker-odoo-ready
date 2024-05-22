```sh
podman run --rm --name lighttpd -p 80:80 -v ./lighttpd.conf:/etc/lighttpd/lighttpd.conf:ro docker.io/jitesoft/lighttpd:latest
```
