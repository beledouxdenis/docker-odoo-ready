#!/usr/bin/env python3
import argparse
import os
import pty
import re
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
CONTAINER_NAME_RE = re.compile(r"odoo-[0-9a-f]{7}")
EXEC_PARSER = argparse.ArgumentParser(add_help=False)
EXEC_PARSER.add_argument("--detach", action="store_true")
EXEC_PARSER.add_argument("--env", action="append")
EXEC_PARSER.add_argument("--user")
EXEC_PARSER.add_argument("--workdir")


def is_codex_odoo_container(name):
    return bool(CONTAINER_NAME_RE.fullmatch(name))


def is_allowed_exec(argv):
    if len(argv) < 3 or not is_codex_odoo_container(argv[1]):
        return False
    try:
        _, command = EXEC_PARSER.parse_known_args(argv[2:])
    except SystemExit:
        return False
    return bool(command) and not command[0].startswith("-")


def is_allowed_inspect(argv):
    return len(argv) == 2 and is_codex_odoo_container(argv[1])


PODMAN_COMMANDS = {
    "exec": is_allowed_exec,
    "inspect": is_allowed_inspect,
}


class Handler(socketserver.BaseRequestHandler):
    def _read_line(self):
        data = bytearray()
        while True:
            chunk = self.request.recv(1)
            if not chunk or chunk == b"\n":
                break
            data.extend(chunk)
        return data.decode()

    def handle(self):
        stdin_is_tty = self._read_line() == "1"
        argv = self._read_line().split("\0")
        if argv and argv[0] in PODMAN_COMMANDS:
            if PODMAN_COMMANDS[argv[0]](argv):
                process = subprocess.run(["podman", *argv], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                self.request.sendall(process.stdout)
            else:
                self.request.sendall(f"denied docker-odoo {' '.join(argv)}\n".encode())
            return
        if any(vars(PARSER.parse_known_args(argv)[0]).values()):
            self.request.sendall(f"denied docker-odoo {' '.join(argv)}\n".encode())
            return
        self.run(argv, stdin_is_tty=stdin_is_tty)

    def run(self, argv, stdin_is_tty):
        master, slave = pty.openpty() if stdin_is_tty else (None, None)
        process = subprocess.Popen(
            ["./docker-odoo", "--internal-url", *argv],
            cwd=REPO,
            stdin=slave if stdin_is_tty else subprocess.PIPE,
            stdout=slave if stdin_is_tty else subprocess.PIPE,
            stderr=slave if stdin_is_tty else subprocess.STDOUT,
            start_new_session=True,
        )
        if stdin_is_tty:
            os.close(slave)
        try:
            output = master if stdin_is_tty else process.stdout.fileno()
            stdin_open = True
            while process.poll() is None:
                for ready in select.select([self.request, output], [], [])[0]:
                    if ready is self.request:
                        data = self.request.recv(65536)
                        if not data:
                            if stdin_is_tty:
                                process.terminate()
                                return
                            elif stdin_open:
                                process.stdin.close()
                                stdin_open = False
                            continue
                        if stdin_is_tty:
                            os.write(master, data)
                        elif stdin_open:
                            process.stdin.write(data)
                            process.stdin.flush()
                    else:
                        try:
                            data = os.read(output, 65536)
                        except OSError:
                            return
                        if not data:
                            return
                        self.request.sendall(data)
        finally:
            if process.poll() is None:
                os.killpg(process.pid, signal.SIGINT)
                process.wait(timeout=15)
            if stdin_is_tty:
                os.close(master)


if __name__ == "__main__":
    SOCKET.parent.mkdir(parents=True, exist_ok=True)
    SOCKET.unlink(missing_ok=True)
    with socketserver.ThreadingUnixStreamServer(str(SOCKET), Handler) as server:
        SOCKET.chmod(0o666)
        print(f"docker-odoo broker listening on {SOCKET}; repo: {REPO}", flush=True)
        server.serve_forever()
