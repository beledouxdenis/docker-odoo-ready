```sh
podman run --rm --name nginx -p 80:80 -v ./nginx.conf:/etc/nginx/nginx.conf:ro docker.io/library/nginx:latest
```
