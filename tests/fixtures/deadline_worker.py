"""Controlled, offline transport for the deadline supervisor's process tests."""

from pathlib import Path
import socket
import ssl
import sys
import threading
import time
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
import audit_links as audit

mode = sys.argv[1]
if mode == "crash":
    raise SystemExit(3)

PUBLIC = "93.184.216.34"
calls = 0


def resolve(*args, **kwargs):
    if mode == "dns" or (mode == "fallback-dns" and calls > 0):
        time.sleep(4)
    return [(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP, "", (PUBLIC, 443))]


class Transport:
    def __init__(self, *args):
        global calls
        calls += 1
        self.number = calls
        self.reader, self.writer = socket.socketpair()

    def settimeout(self, timeout):
        self.reader.settimeout(timeout)

    def setsockopt(self, *args):
        pass

    def connect(self, address):
        assert address == (PUBLIC, 443)
        if mode == "connect":
            time.sleep(4)

    def sendall(self, data):
        def send():
            try:
                if mode == "headers":
                    for byte in b"HTTP/1.1 200 OK\r\n":
                        self.writer.sendall(bytes([byte]))
                        time.sleep(.08)
                elif mode in ("body", "fallback-dns") and self.number == 1:
                    self.writer.sendall(b"HTTP/1.1 405 Test\r\nContent-Length: 0\r\n\r\n")
                elif mode == "body":
                    self.writer.sendall(b"HTTP/1.1 200 OK\r\nContent-Length: 1000\r\n\r\n")
                    for _ in range(50):
                        self.writer.sendall(b"x")
                        time.sleep(.08)
                elif mode == "backoff":
                    self.writer.sendall(b"HTTP/1.1 503 Test\r\nContent-Length: 0\r\n\r\n")
                else:
                    self.writer.sendall(b"HTTP/1.1 200 OK\r\nContent-Length: 0\r\n\r\n")
            except OSError:
                pass
            finally:
                self.writer.close()
        threading.Thread(target=send, daemon=True).start()

    def makefile(self, *args):
        return self.reader.makefile(*args)

    def close(self):
        self.reader.close()


def tls(context, sock, *, server_hostname):
    assert context.check_hostname and context.verify_mode == ssl.CERT_REQUIRED
    assert server_hostname == "publisher.example"
    if mode == "tls":
        time.sleep(4)
    return sock


# The socketpair is local IPC; no public/private TCP destination is contacted.
real_socket = socket.socket
def transport(*args):
    with patch.object(socket, "socket", real_socket):
        return Transport(*args)

audit.TIMEOUT = .2
if mode == "backoff":
    engine = audit._audit_resource
    def slow_backoff(resource, **kwargs):
        return engine(resource, sleep=lambda _: time.sleep(4), **kwargs)
    audit._audit_resource = slow_backoff
with patch.object(socket, "getaddrinfo", resolve), patch.object(socket, "socket", transport), patch.object(ssl.SSLContext, "wrap_socket", tls):
    raise SystemExit(audit._worker_main())
