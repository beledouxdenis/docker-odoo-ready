#!/usr/bin/env python3
import os
import select
import socket
import sys
import termios
import tty


SOCKET = os.environ.get("PODMAN_BROKER_SOCKET", "/broker/docker-odoo.sock")


def main():
    old = termios.tcgetattr(sys.stdin) if sys.stdin.isatty() else None
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as broker:
        broker.connect(SOCKET)
        broker.sendall("\0".join(sys.argv[1:]).encode() + b"\n")
        inputs = [broker, *([sys.stdin.buffer] if old else [])]
        try:
            if old:
                tty.setraw(sys.stdin)
            while True:
                for ready in select.select(inputs, [], [])[0]:
                    if ready is broker:
                        data = broker.recv(65536)
                        if not data:
                            return
                        sys.stdout.buffer.write(data)
                        sys.stdout.buffer.flush()
                    else:
                        data = os.read(sys.stdin.fileno(), 65536)
                        if not data:
                            return
                        broker.sendall(data)
        finally:
            if old:
                termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old)


if __name__ == "__main__":
    main()
