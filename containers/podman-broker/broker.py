#!/usr/bin/env python3
import argparse
import logging
import os
import pty
import re
import select
import signal
import socketserver
import subprocess
import uuid
from pathlib import Path

SOCKET = Path("/broker/podman-compose.sock")
REPO = os.environ["PODMAN_BROKER_REPO"]
ODOO_SRC = Path(os.environ["ODOO_SRC"])
ODOO_IMAGES_DIR = Path(REPO) / "containers" / "odoo" / "images"
COMMUNITY = ODOO_SRC / "odoo"

IMAGES = [(18.0, "noble"), (14.0, "jammy"), (6.1, "bionic")]


class DeniedCommand(Exception):
    pass


class StrictArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        raise DeniedCommand(message)


EXEC_PARSER = StrictArgumentParser(add_help=False)
EXEC_PARSER.add_argument("--detach", action="store_true")
EXEC_PARSER.add_argument("--env", action="append")
EXEC_PARSER.add_argument("--user")
EXEC_PARSER.add_argument("--workdir")
COMPOSE_RUN_PARSER = StrictArgumentParser(prog="podman-compose run", add_help=False)
COMPOSE_RUN_PARSER.add_argument("--rm", action="store_true")
COMPOSE_RUN_PARSER.add_argument("--no-TTY", "-T", action="store_true")
COMPOSE_RUN_PARSER.add_argument("--env", "-e", action="append", default=[])
COMPOSE_RUN_PARSER.add_argument("service", choices=("odoo", "nginx"))
COMPOSE_RUN_PARSER.add_argument("command", nargs=argparse.REMAINDER)
ODOO_PARSER = StrictArgumentParser(add_help=False)
ODOO_PARSER.add_argument("--branch", "-b", required=True)

ACTIVE_CONTAINERS = {}
UPSTREAM_HOST_RE = re.compile(r"[A-Za-z0-9](?:[A-Za-z0-9_.-]{0,251}[A-Za-z0-9])?")
LOGGER = logging.getLogger(__name__)


def prepare_command(argv, requested_image=None):
    if not argv:
        raise DeniedCommand
    if argv[0] == "exec":
        if requested_image or len(argv) < 3 or ACTIVE_CONTAINERS.get(argv[1]) != "odoo":
            raise DeniedCommand
        _, command = EXEC_PARSER.parse_known_args(argv[2:])
        if not command or command[0].startswith("-"):
            raise DeniedCommand
        return ["podman", *argv], None, None, False, None
    if argv[0] == "inspect":
        if requested_image or len(argv) != 2 or argv[1] not in ACTIVE_CONTAINERS:
            raise DeniedCommand
        return ["podman", *argv], None, None, False, None
    if argv[0] != "run":
        raise DeniedCommand

    args = COMPOSE_RUN_PARSER.parse_args(argv[1:])
    environment = None
    if args.service == "odoo":
        if args.env or not args.command or args.command[0] != "odoo":
            raise DeniedCommand
        odoo_args, _extra_args = ODOO_PARSER.parse_known_args(args.command[1:])
        branch_path = (COMMUNITY / odoo_args.branch).resolve()
        if not branch_path.is_relative_to(COMMUNITY.resolve()) or not branch_path.is_dir():
            raise DeniedCommand
        available_images = {containerfile.parent.name for containerfile in ODOO_IMAGES_DIR.glob("*/Containerfile")}
        if requested_image and requested_image not in available_images:
            raise DeniedCommand
        if requested_image:
            docker_file = requested_image
        else:
            odoo_path = COMMUNITY / odoo_args.branch
            odoo_release_file = next(
                path / "release.py"
                for path in [odoo_path / "odoo", odoo_path / "openerp"]
                if path.exists()
            )
            odoo_version = re.search(r"version_info = \((.*)\)", odoo_release_file.read_text())
            odoo_version = float(
                ".".join(re.findall(r"\d+", "".join(odoo_version.groups()[0].split(",")[:2])))
            )
            docker_file = next(image for version, image in IMAGES if odoo_version >= version)
        environment = {"DOCKERFILE": docker_file}
    else:
        if requested_image:
            raise DeniedCommand
        if args.command or len(args.env) > 1:
            raise DeniedCommand
        if args.env:
            variable, separator, target = args.env[0].partition("=")
            if (
                separator != "="
                or variable != "ODOO_UPSTREAM_HOST"
                or UPSTREAM_HOST_RE.fullmatch(target) is None
            ):
                raise DeniedCommand
    normalized = list(argv)
    if not args.rm:
        normalized.insert(1, "--rm")
    container_name = f"broker-{args.service}-{uuid.uuid4().hex}"
    normalized[1:1] = ["--name", container_name]
    return ["podman-compose", *normalized], args.service, container_name, True, environment


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
        requested_image = self._read_line() or None
        argv = self._read_line().split("\0")
        try:
            command, service, container_name, stream, environment = prepare_command(argv, requested_image)
        except DeniedCommand:
            self.request.sendall(f"denied podman-compose {' '.join(argv)}\n".encode())
            return
        self.run(
            command,
            service=service,
            container_name=container_name,
            stdin_is_tty=stdin_is_tty,
            stream=stream,
            environment=environment,
        )

    def run(self, command, service, container_name, stdin_is_tty, stream, environment):
        if not stream:
            process = subprocess.run(
                command,
                cwd=REPO,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                check=False,
            )
            self.request.sendall(process.stdout)
            return
        master, slave = pty.openpty() if stdin_is_tty else (None, None)
        process = subprocess.Popen(
            command,
            cwd=REPO,
            env=dict(os.environ, **environment) if environment else None,
            stdin=slave if stdin_is_tty else subprocess.PIPE,
            stdout=slave if stdin_is_tty else subprocess.PIPE,
            stderr=slave if stdin_is_tty else subprocess.STDOUT,
            start_new_session=True,
        )
        if stdin_is_tty:
            os.close(slave)
        try:
            if container_name:
                ACTIVE_CONTAINERS[container_name] = service
                self.request.sendall(f"broker container name: {container_name}\n".encode())
            output = master if stdin_is_tty else process.stdout.fileno()
            stdin_open = True
            readers = [self.request, output]
            while output in readers:
                for ready in select.select(readers, [], [])[0]:
                    if ready is self.request:
                        data = self.request.recv(65536)
                        if not data:
                            if stdin_is_tty:
                                process.terminate()
                                return
                            if stdin_open:
                                process.stdin.close()
                                stdin_open = False
                            readers.remove(self.request)
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
                            readers.remove(output)
                            continue
                        self.request.sendall(data)
        finally:
            if container_name:
                ACTIVE_CONTAINERS.pop(container_name, None)
            if process.poll() is None:
                os.killpg(process.pid, signal.SIGINT)
                process.wait(timeout=15)
            if stdin_is_tty:
                os.close(master)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    SOCKET.parent.mkdir(parents=True, exist_ok=True)
    SOCKET.unlink(missing_ok=True)
    with socketserver.ThreadingUnixStreamServer(str(SOCKET), Handler) as server:
        SOCKET.chmod(0o666)
        LOGGER.info("podman-compose broker listening on %s; repo: %s", SOCKET, REPO)
        server.serve_forever()
