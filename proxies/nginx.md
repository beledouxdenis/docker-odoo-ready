```sh
podman run --rm --name nginx -p 80:80 -p 443:443 -v ./nginx.conf:/etc/nginx/nginx.conf:ro -v ./.certs:/etc/nginx/ssl/:ro docker.io/library/nginx:latest
```
