```sh
podman run --rm --name caddy -p 80:80 -p 443:443 -v ./caddy.conf:/etc/caddy/Caddyfile:ro -v ./.certs:/etc/caddy/ssl/:ro docker.io/library/caddy:latest
```
