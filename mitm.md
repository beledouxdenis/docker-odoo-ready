# Interactive HTTPS Proxy (Burpsuite like)

```sh
podman run --rm -it -v ~/.mitmproxy:/home/mitmproxy/.mitmproxy -p 8080:8080 -p 127.0.0.1:8081:8081 docker.io/mitmproxy/mitmproxy mitmweb --web-host 0.0.0.0
```
Note: The -v for volume mount is optional. It allows to persist and reuse the generated CA certificates between runs, and for you to access them. Without it, a new root CA would be generated on each container restart.

In your browser, you can access the web interface with http://localhost:8081.
It requires a password, look in the logs in the terminal after the above command.

Then you need to configure your OS or browser proxy to http://localhost:8080

For HTTPS interception, you need to make accept the CA certificate of the proxy by your operating system or browser.
Go to [mitm.it](http://mitm.it/) and follow the instructions.
mitm.it points to a website locally hosted in the podman container you spawned above.
