"""Exercise the production opener with controlled DNS, sockets and TLS; no network."""

import errno
import io
import os
from pathlib import Path
import socket
import ssl
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import audit_links as audit

URL = "https://publisher.example/data"
PUBLIC = "93.184.216.34"
PUBLIC_V6 = "2606:4700:4700::1111"


def answer(ip):
    family = socket.AF_INET6 if ":" in ip else socket.AF_INET
    address = (ip, 443, 0, 0) if family == socket.AF_INET6 else (ip, 443)
    return (family, socket.SOCK_STREAM, socket.IPPROTO_TCP, "", address)


def response(status=200, location=None):
    headers = f"HTTP/1.1 {status} Test\r\nContent-Length: 0\r\n"
    if location:
        headers += f"Location: {location}\r\n"
    return (headers + "\r\n").encode("ascii")


class FakeSocket:
    def __init__(self, reply):
        self.reply = reply
        self.connected = None
        self.sent = b""
        self.closed = False

    def settimeout(self, timeout):
        self.timeout = timeout

    def setsockopt(self, *args):
        pass

    def connect(self, address):
        self.connected = address

    def sendall(self, data):
        self.sent += data

    def makefile(self, *args):
        return io.BytesIO(self.reply)

    def close(self):
        self.closed = True


class DestinationSecurityTests(unittest.TestCase):
    def setUp(self):
        # Unconfigured DNS/socket access fails instead of leaking out of the test.
        self.dns = self.enterContext(patch.object(audit.socket, "getaddrinfo"))
        self.sockets = self.enterContext(patch.object(audit.socket, "socket"))
        self.sockets.side_effect = AssertionError("Unexpected socket creation")
        self.dns.side_effect = AssertionError("Unexpected DNS lookup")
        self.tls_hosts = []
        def wrap(context, sock, *, server_hostname):
            self.assertTrue(context.check_hostname)
            self.assertEqual(context.verify_mode, ssl.CERT_REQUIRED)
            self.tls_hosts.append(server_hostname)
            return sock
        self.enterContext(patch.object(ssl.SSLContext, "wrap_socket", wrap))

    def audit_url(self, url=URL):
        return audit.audit_resource(
            {"id": "test", "source": {"canonicalUrl": url}},
            sleep=lambda _: self.fail("Policy failures must not be retried"),
        )

    def test_non_public_addresses_never_open_a_socket(self):
        for ip in (
            "127.0.0.1", "10.0.0.1", "172.16.0.1", "192.168.1.1",
            "169.254.169.254", "0.0.0.0", "100.64.0.1", "224.0.0.1",
            "240.0.0.1", "192.0.0.8", "192.88.99.1", "192.0.2.1",
            "::", "::1", "fc00::1", "fe80::1", "ff02::1",
            "::ffff:127.0.0.1", "64:ff9b::7f00:1", "2002:7f00:1::",
            "2001::1", "2001:db8::1", "3fff::1",
        ):
            with self.subTest(ip=ip):
                self.dns.side_effect = None
                self.dns.return_value = [answer(ip)]
                result = self.audit_url()
                self.assertEqual(result["classification"], "security-blocked")
                self.assertEqual(len(result["attempts"]), 1)
                self.assertIsNone(result["httpStatus"])
                self.sockets.assert_not_called()

    def test_literal_and_obfuscated_loopback_forms_are_resolved_and_blocked(self):
        for authority in ("127.0.0.1", "127.1", "2130706433", "0x7f000001", "0177.0.0.1", "[::1]", "localhost"):
            with self.subTest(authority=authority):
                self.dns.side_effect = None
                self.dns.return_value = [answer("127.0.0.1")]
                result = self.audit_url(f"https://{authority}/")
                self.assertEqual(result["classification"], "security-blocked")
                self.sockets.assert_not_called()

    def test_mixed_public_private_answers_fail_before_connect(self):
        for addresses in ([PUBLIC, "10.0.0.1"], [PUBLIC, "::1"], ["10.0.0.1", PUBLIC_V6]):
            with self.subTest(addresses=addresses):
                self.dns.side_effect = None
                self.dns.return_value = [answer(ip) for ip in addresses]
                self.assertEqual(self.audit_url()["classification"], "security-blocked")
                self.sockets.assert_not_called()

    def test_public_ipv4_ipv6_preserve_host_and_verified_tls(self):
        for ip in (PUBLIC, PUBLIC_V6):
            with self.subTest(ip=ip):
                sock = FakeSocket(response())
                self.dns.side_effect = None
                self.dns.return_value = [answer(ip)]
                self.sockets.side_effect = None
                self.sockets.return_value = sock
                result = self.audit_url()
                self.assertEqual(result["classification"], "reachable")
                self.assertEqual(sock.connected, answer(ip)[4])
                self.assertIn(b"Host: publisher.example\r\n", sock.sent)
                self.assertEqual(self.tls_hosts[-1], "publisher.example")
                self.assertTrue(sock.closed)

    def test_dns_rebinding_cannot_replace_the_validated_address(self):
        sock = FakeSocket(response())
        self.dns.side_effect = [[answer(PUBLIC)], [answer("127.0.0.1")]]
        self.sockets.side_effect = None
        self.sockets.return_value = sock
        self.assertEqual(self.audit_url()["classification"], "reachable")
        self.dns.assert_called_once()
        self.assertEqual(sock.connected, (PUBLIC, 443))

    def test_redirects_revalidate_dns_including_same_host(self):
        for target in ("https://internal.example/", "https://127.0.0.1/", "https://[::1]/", URL + "?next=1"):
            for status in (301, 302, 303, 307, 308):
                with self.subTest(target=target, status=status):
                    sock = FakeSocket(response(status, target))
                    self.dns.side_effect = [[answer(PUBLIC)], [answer("127.0.0.1")]]
                    self.sockets.reset_mock()
                    self.sockets.side_effect = [sock]
                    result = self.audit_url()
                    self.assertEqual(result["classification"], "security-blocked")
                    self.assertEqual(result["finalUrl"], target)
                    self.assertEqual(len(result["redirectChain"]), 1)
                    self.sockets.assert_called_once()
                    self.assertTrue(sock.closed)

    def test_fallback_and_retry_revalidate_before_a_second_connection(self):
        for status in (405, 503):
            with self.subTest(status=status):
                sock = FakeSocket(response(status))
                self.dns.side_effect = [[answer(PUBLIC)], [answer("10.0.0.1")]]
                self.sockets.reset_mock()
                self.sockets.side_effect = [sock]
                result = audit.audit_resource(
                    {"id": "test", "source": {"canonicalUrl": URL}},
                    sleep=lambda _: None,
                )
                self.assertEqual(result["classification"], "security-blocked")
                self.assertEqual(len(result["attempts"]), 2)
                self.sockets.assert_called_once()
                self.assertTrue(sock.closed)

    def test_get_after_exhausted_head_failure_revalidates_private_dns(self):
        for timeout in (False, True):
            with self.subTest(timeout=timeout):
                first = FakeSocket(response(503))
                second = FakeSocket(response(503))
                if timeout:
                    class TimeoutBody(io.BytesIO):
                        def readline(self, *args):
                            raise TimeoutError("HEAD timed out")
                    first.makefile = second.makefile = lambda *args: TimeoutBody()
                self.dns.side_effect = [[answer(PUBLIC)], [answer(PUBLIC)], [answer("169.254.169.254")]]
                self.sockets.reset_mock()
                self.sockets.side_effect = [first, second]
                result = audit.audit_resource(
                    {"id": "test", "source": {"canonicalUrl": URL}}, sleep=lambda _: None,
                )
                self.assertEqual(result["classification"], "security-blocked")
                self.assertEqual([a["method"] for a in result["attempts"]], ["HEAD", "HEAD", "GET"])
                self.assertEqual(self.sockets.call_count, 2)
                self.assertTrue(first.closed and second.closed)

    def test_failed_connect_closes_socket_before_public_address_fallback(self):
        first = FakeSocket(response())
        second = FakeSocket(response())
        self.dns.side_effect = None
        self.dns.return_value = [answer(PUBLIC), answer(PUBLIC_V6)]
        self.sockets.side_effect = [first, second]
        with patch.object(first, "connect", side_effect=ConnectionRefusedError("refused")):
            self.assertEqual(self.audit_url()["classification"], "reachable")
        self.assertTrue(first.closed)
        self.assertTrue(second.closed)
        self.assertEqual(second.connected, answer(PUBLIC_V6)[4])

    def test_socket_creation_failure_tries_remaining_public_address(self):
        sock = FakeSocket(response())
        self.dns.side_effect = None
        self.dns.return_value = [answer(PUBLIC_V6), answer(PUBLIC)]
        self.sockets.side_effect = [
            OSError(errno.EAFNOSUPPORT, "IPv6 unavailable"), sock,
        ]
        result = self.audit_url()
        self.assertEqual(result["classification"], "reachable")
        self.assertEqual(sock.connected, (PUBLIC, 443))
        self.assertEqual(self.sockets.call_count, 2)
        self.dns.assert_called_once()
        self.assertTrue(sock.closed)
        self.assertEqual(self.tls_hosts, ["publisher.example"])

    def test_all_socket_creation_failures_return_transport_error(self):
        self.dns.side_effect = None
        self.dns.return_value = [answer(PUBLIC_V6), answer(PUBLIC)]
        self.sockets.side_effect = [
            OSError(errno.EAFNOSUPPORT, "IPv6 unavailable"),
            OSError(errno.EMFILE, "Socket limit reached"),
        ]
        result = self.audit_url()
        self.assertEqual(result["classification"], "transport-error")
        self.assertIn("Socket limit reached", result["error"])
        self.assertEqual(self.sockets.call_count, 2)
        self.dns.assert_called_once()
        self.assertEqual(self.tls_hosts, [])

    def test_proxy_tunnel_is_rejected_before_dns(self):
        connection = audit.PublicHTTPSConnection("proxy.example")
        connection.set_tunnel("publisher.example", 443)
        with self.assertRaises(audit.UnsafeDestination):
            connection.connect()
        self.dns.assert_not_called()
        self.sockets.assert_not_called()

    def test_public_redirect_still_works(self):
        first = FakeSocket(response(302, "https://other.example/new"))
        second = FakeSocket(response())
        self.dns.side_effect = [[answer(PUBLIC)], [answer(PUBLIC_V6)]]
        self.sockets.side_effect = [first, second]
        result = self.audit_url()
        self.assertEqual(result["classification"], "redirected")
        self.assertTrue(result["crossDomainRedirect"])
        self.assertEqual(self.tls_hosts, ["publisher.example", "other.example"])
        self.assertIn(b"HEAD /new HTTP/1.1", second.sent)

    def test_invalid_urls_are_refused_before_dns(self):
        for url in (
            "http://publisher.example/", "file:///etc/passwd",
            "https://user:secret@publisher.example/", "https://@publisher.example/",
            "https://publisher.example:8443/", "https://publisher.example:invalid/",
            "https://127.0.0.1%2f.example/", "https://[fe80::1%25en0]/",
            "https://publisher.example\\@localhost/", "https://publisher.example/\n",
        ):
            with self.subTest(url=url):
                self.assertEqual(self.audit_url(url)["classification"], "security-blocked")
                self.dns.assert_not_called()
                self.sockets.assert_not_called()

    def test_proxy_environment_and_system_settings_are_not_used(self):
        sock = FakeSocket(response())
        self.dns.side_effect = None
        self.dns.return_value = [answer(PUBLIC)]
        self.sockets.side_effect = None
        self.sockets.return_value = sock
        with patch.dict(os.environ, {"HTTPS_PROXY": "http://127.0.0.1:8080", "https_proxy": "http://127.0.0.1:8080"}), patch.object(audit.urllib.request, "getproxies", side_effect=AssertionError("Proxy discovery called")):
            self.assertEqual(self.audit_url()["classification"], "reachable")
        self.assertEqual(self.dns.call_args.args[:2], ("publisher.example", 443))
        self.assertNotIn(b"CONNECT", sock.sent)

    def test_dns_failure_remains_transport_error(self):
        self.dns.side_effect = socket.gaierror("name not found")
        result = self.audit_url()
        self.assertEqual(result["classification"], "transport-error")
        self.sockets.assert_not_called()

    def test_tls_verification_failure_is_not_bypassed(self):
        sock = FakeSocket(response())
        self.dns.side_effect = None
        self.dns.return_value = [answer(PUBLIC)]
        self.sockets.side_effect = None
        self.sockets.return_value = sock
        with patch.object(ssl.SSLContext, "wrap_socket", side_effect=ssl.SSLCertVerificationError("certificate mismatch")):
            self.assertEqual(self.audit_url()["classification"], "transport-error")
        self.assertEqual(sock.sent, b"")
        self.assertTrue(sock.closed)


if __name__ == "__main__":
    unittest.main()
