```sh
podman run --rm --name caddy -p 80:80 -v ./caddy.conf:/etc/caddy/Caddyfile:ro docker.io/library/caddy:latest
```
