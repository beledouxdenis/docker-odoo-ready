```sh
podman run --rm --name traefik -p 80:80 -p 443:443 -v ./traefik.toml:/etc/traefik/traefik.toml:ro -v ./dynamic_conf.toml:/etc/traefik/traefik_provider.toml:ro -v ./.certs:/etc/traefik/certs/:ro docker.io/library/traefik:latest
```
