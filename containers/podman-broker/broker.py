#!/usr/bin/env python3
import argparse
import os
import pty
import select
import signal
import socketserver
import subprocess
from pathlib import Path


SOCKET = Path("/broker/docker-odoo.sock")
REPO = os.environ["PODMAN_BROKER_REPO"]
PARSER = argparse.ArgumentParser(add_help=False)
PARSER.add_argument("--volume", "-v", action="append")
PARSER.add_argument("--image", action="append")
PARSER.add_argument("--build", action="store_true")


class Handler(socketserver.BaseRequestHandler):
    def handle(self):
        argv = self.request.makefile("rb").readline().rstrip(b"\n").decode().split("\0")
        if any(vars(PARSER.parse_known_args(argv)[0]).values()):
            self.request.sendall(f"denied docker-odoo {' '.join(argv)}\n".encode())
            return
        self.run(argv)

    def run(self, argv):
        master, slave = pty.openpty()
        process = subprocess.Popen(["./docker-odoo", *argv], cwd=REPO, stdin=slave, stdout=slave, stderr=slave, start_new_session=True)
        os.close(slave)
        try:
            while process.poll() is None:
                for ready in select.select([self.request, master], [], [])[0]:
                    if ready is self.request:
                        data = self.request.recv(65536)
                        if not data:
                            process.terminate()
                            return
                        os.write(master, data)
                    else:
                        try:
                            data = os.read(master, 65536)
                        except OSError:
                            return
                        if not data:
                            return
                        self.request.sendall(data)
        finally:
            os.close(master)
            if process.poll() is None:
                os.killpg(process.pid, signal.SIGTERM)


if __name__ == "__main__":
    SOCKET.parent.mkdir(parents=True, exist_ok=True)
    SOCKET.unlink(missing_ok=True)
    with socketserver.ThreadingUnixStreamServer(str(SOCKET), Handler) as server:
        SOCKET.chmod(0o666)
        print(f"docker-odoo broker listening on {SOCKET}; repo: {REPO}", flush=True)
        server.serve_forever()
