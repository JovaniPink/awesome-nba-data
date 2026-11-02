"""Offline HTTP scenarios exercise urllib redirects and audit classifications."""

from contextlib import redirect_stdout
from email.message import Message
import io
import json
import socket
import ssl
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
import urllib.error
import urllib.request
import urllib.response

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import audit_links as audit

URL = "https://publisher.example/data"
RESOURCE = {"id": "test:source:one", "source": {"canonicalUrl": URL}}


class CountedBody(io.BytesIO):
    def __init__(self, contents):
        super().__init__(contents)
        self.bytes_read = 0

    def read(self, size=-1):
        result = super().read(size)
        self.bytes_read += len(result)
        return result


class Scenario(urllib.request.HTTPSHandler):
    def __init__(self, routes):
        super().__init__()
        self.routes = routes
        self.calls = []
        self.bodies = []

    def https_open(self, req):
        self.calls.append((req.get_method(), req.full_url))
        outcomes = self.routes[(req.get_method(), req.full_url)]
        outcome = outcomes.pop(0) if len(outcomes) > 1 else outcomes[0]
        if isinstance(outcome, Exception):
            raise outcome
        code, destination = outcome
        headers = Message()
        if destination:
            headers["Location"] = destination
        body = CountedBody(b"x" * (audit.MAX_BODY_BYTES + 100))
        self.bodies.append(body)
        response = urllib.response.addinfourl(body, headers, req.full_url, code)
        response.msg = "Scenario response"
        return response

    def request(self, url, method):
        return audit.request(
            url, method, lambda recorder: urllib.request.build_opener(self, recorder)
        )


class LinkAuditTests(unittest.TestCase):
    def run_scenario(self, routes):
        scenario = Scenario(routes)
        result = audit.audit_resource(
            RESOURCE, requester=scenario.request, sleep=lambda _: None
        )
        return result, scenario

    def test_reachable_does_not_claim_content_review(self):
        result, _ = self.run_scenario({("HEAD", URL): [(200, None)]})
        self.assertEqual(result["classification"], "reachable")
        self.assertEqual(result["contentReview"], "not-performed")

    def test_unrelated_successful_redirect_is_flagged(self):
        target = "https://unrelated.example/politics"
        result, _ = self.run_scenario(
            {("HEAD", URL): [(301, target)], ("HEAD", target): [(200, None)]}
        )
        self.assertEqual(result["classification"], "redirected")
        self.assertEqual(result["finalUrl"], target)
        self.assertTrue(result["crossDomainRedirect"])
        self.assertEqual(
            result["redirectChain"], [{"from": URL, "to": target, "status": 301}]
        )

    def test_redirects_preserve_method_and_bound_body_reads(self):
        target = "https://publisher.example/new"
        for method in ("HEAD", "GET"):
            for status in (301, 302, 303, 307, 308):
                with self.subTest(method=method, status=status):
                    scenario = Scenario(
                        {
                            (method, URL): [(status, target)],
                            (method, target): [(200, None)],
                        }
                    )
                    result = scenario.request(URL, method)
                    self.assertEqual(result["httpStatus"], 200)
                    self.assertEqual(scenario.calls, [(method, URL), (method, target)])
                    self.assertEqual(scenario.bodies[0].bytes_read, 0)
                    self.assertEqual(
                        scenario.bodies[1].bytes_read,
                        audit.MAX_BODY_BYTES if method == "GET" else 0,
                    )
                    self.assertTrue(all(body.closed for body in scenario.bodies))

    def test_head_rejection_falls_back_to_bounded_get(self):
        result, scenario = self.run_scenario(
            {("HEAD", URL): [(405, None)], ("GET", URL): [(200, None)]}
        )
        self.assertEqual(scenario.calls, [("HEAD", URL), ("GET", URL)])
        self.assertEqual(result["classification"], "reachable")
        self.assertEqual(result["attempts"][-1]["sampleBytes"], audit.MAX_BODY_BYTES)
        self.assertTrue(all(body.closed for body in scenario.bodies))

    def test_blocked_is_not_missing(self):
        result, _ = self.run_scenario(
            {("HEAD", URL): [(403, None)], ("GET", URL): [(403, None)]}
        )
        self.assertEqual(result["classification"], "blocked/authentication-required")
        self.assertEqual(result["httpStatus"], 403)

    def test_status_categories(self):
        for code, expected in [
            (401, "blocked/authentication-required"),
            (429, "rate-limited"),
            (404, "missing"),
            (410, "missing"),
            (503, "server-error"),
        ]:
            with self.subTest(status=code):
                result, scenario = self.run_scenario(
                    {("HEAD", URL): [(code, None)], ("GET", URL): [(code, None)]}
                )
                self.assertEqual(result["classification"], expected)
                self.assertEqual(
                    len(scenario.calls), 3 if code == 503 else 2 if code in (404, 410) else 1
                )

    def test_head_404_does_not_override_successful_get(self):
        result, scenario = self.run_scenario(
            {("HEAD", URL): [(404, None)], ("GET", URL): [(200, None)]}
        )
        self.assertEqual(result["classification"], "reachable")
        self.assertEqual(result["method"], "GET")
        self.assertEqual(len(scenario.calls), 2)

    def test_timeout_retries_once_then_get_preserves_all_errors(self):
        result, scenario = self.run_scenario({
            ("HEAD", URL): [TimeoutError("HEAD timed out")],
            ("GET", URL): [TimeoutError("GET timed out")],
        })
        self.assertEqual(result["classification"], "transport-error")
        self.assertEqual(scenario.calls, [("HEAD", URL), ("HEAD", URL), ("GET", URL)])
        self.assertIn("GET timed out", result["error"])
        self.assertEqual(len(result["attempts"]), 3)
        self.assertIn("HEAD timed out", result["attempts"][0]["error"])

    def test_exhausted_head_timeouts_fall_back_to_bounded_get(self):
        for error in (TimeoutError("read timed out"), urllib.error.URLError(TimeoutError("connect timed out"))):
            with self.subTest(error=error):
                result, scenario = self.run_scenario({
                    ("HEAD", URL): [error], ("GET", URL): [(200, None)],
                })
                self.assertEqual(scenario.calls, [("HEAD", URL), ("HEAD", URL), ("GET", URL)])
                self.assertEqual(result["classification"], "reachable")
                self.assertEqual(result["method"], "GET")
                self.assertTrue(all(a["timedOut"] for a in result["attempts"][:2]))
                self.assertEqual(result["attempts"][-1]["sampleBytes"], audit.MAX_BODY_BYTES)
                self.assertEqual(scenario.bodies[-1].bytes_read, audit.MAX_BODY_BYTES)
                self.assertTrue(scenario.bodies[-1].closed)

    def test_head_server_errors_fall_back_after_applicable_retry(self):
        for status in (500, 501, 502, 503, 504, 505, 599):
            with self.subTest(status=status):
                result, scenario = self.run_scenario({
                    ("HEAD", URL): [(status, None)], ("GET", URL): [(200, None)],
                })
                head_count = 2 if status in audit.TRANSIENT_STATUS else 1
                self.assertEqual(scenario.calls, [("HEAD", URL)] * head_count + [("GET", URL)])
                self.assertEqual([a["httpStatus"] for a in result["attempts"]], [status] * head_count + [200])
                self.assertEqual(result["classification"], "reachable")
                self.assertEqual(scenario.bodies[-1].bytes_read, audit.MAX_BODY_BYTES)
                self.assertTrue(all(body.closed for body in scenario.bodies))

    def test_get_failure_does_not_reset_consumed_retry_budget(self):
        for outcome, expected in (
            ((503, None), "server-error"),
            ((404, None), "missing"),
            ((429, None), "rate-limited"),
            (TimeoutError("GET timed out"), "transport-error"),
        ):
            with self.subTest(outcome=outcome):
                result, scenario = self.run_scenario({
                    ("HEAD", URL): [(503, None)], ("GET", URL): [outcome],
                })
                self.assertEqual(scenario.calls, [("HEAD", URL), ("HEAD", URL), ("GET", URL)])
                self.assertEqual(result["classification"], expected)
                self.assertEqual(result["method"], "GET")
                self.assertEqual(len(result["attempts"]), 3)

    def test_unused_retry_budget_can_recover_get_timeout(self):
        result, scenario = self.run_scenario({
            ("HEAD", URL): [(505, None)],
            ("GET", URL): [TimeoutError("GET timed out"), (200, None)],
        })
        self.assertEqual(scenario.calls, [("HEAD", URL), ("GET", URL), ("GET", URL)])
        self.assertEqual(result["classification"], "reachable")
        self.assertTrue(result["attempts"][1]["timedOut"])

    def test_non_timeout_transport_errors_do_not_trigger_get(self):
        for error, attempts in (
            (urllib.error.URLError(socket.gaierror("DNS failure")), 1),
            (urllib.error.URLError(ssl.SSLCertVerificationError("bad certificate")), 1),
            (ConnectionResetError("connection reset"), 2),
            (urllib.error.URLError("timed out"), 1),
        ):
            with self.subTest(error=error):
                result, scenario = self.run_scenario({("HEAD", URL): [error]})
                self.assertEqual(result["classification"], "transport-error")
                self.assertEqual(scenario.calls, [("HEAD", URL)] * attempts)
                self.assertFalse(any(a.get("timedOut") for a in result["attempts"]))

    def test_timeout_fallback_preserves_failed_redirect_evidence(self):
        target = "https://other.example/data"
        result, scenario = self.run_scenario({
            ("HEAD", URL): [(302, target)],
            ("HEAD", target): [TimeoutError("redirect target timed out")],
            ("GET", URL): [(200, None)],
        })
        self.assertEqual(result["classification"], "reachable")
        self.assertEqual(result["finalUrl"], URL)
        self.assertTrue(result["crossDomainRedirect"])
        self.assertEqual(result["attempts"][0]["finalUrl"], target)
        self.assertEqual(len(result["attempts"][0]["redirectChain"]), 1)
        self.assertEqual(scenario.calls[-1], ("GET", URL))

    def test_transient_recovery_retains_failed_attempt(self):
        result, _ = self.run_scenario({("HEAD", URL): [(503, None), (200, None)]})
        self.assertEqual(result["classification"], "reachable")
        self.assertEqual([a["httpStatus"] for a in result["attempts"]], [503, 200])

    def test_redirect_loop_is_bounded(self):
        target = "https://publisher.example/loop"
        result, scenario = self.run_scenario(
            {("HEAD", URL): [(302, target)], ("HEAD", target): [(302, URL)]}
        )
        self.assertEqual(result["classification"], "redirect-error")
        self.assertLessEqual(len(scenario.calls), 5)
        self.assertTrue(result["error"])

    def test_redirect_bodies_are_closed_without_downloading(self):
        target = "https://publisher.example/new"
        result, scenario = self.run_scenario(
            {("HEAD", URL): [(302, target)], ("HEAD", target): [(200, None)]}
        )
        self.assertEqual(result["classification"], "redirected")
        self.assertEqual(scenario.bodies[0].bytes_read, 0)
        self.assertTrue(all(body.closed for body in scenario.bodies))

    def test_insecure_redirect_is_not_followed(self):
        result, scenario = self.run_scenario(
            {("HEAD", URL): [(302, "http://publisher.example/data")]}
        )
        self.assertEqual(result["classification"], "security-blocked")
        self.assertEqual(len(scenario.calls), 1)

    def test_cross_domain_hop_is_flagged_even_if_it_returns(self):
        other = "https://other.example/redirect"
        final = "https://publisher.example/new"
        result, _ = self.run_scenario(
            {
                ("HEAD", URL): [(302, other)],
                ("HEAD", other): [(302, final)],
                ("HEAD", final): [(200, None)],
            }
        )
        self.assertTrue(result["crossDomainRedirect"])
        self.assertEqual(len(result["redirectChain"]), 2)

    def test_cli_report_is_separate_and_does_not_mutate_catalog(self):
        with tempfile.TemporaryDirectory() as directory:
            catalog = Path(directory) / "catalog.json"
            output = Path(directory) / "report.json"
            original = json.dumps({"projectId": "test", "resources": [RESOURCE]})
            catalog.write_text(original)
            result, _ = self.run_scenario({("HEAD", URL): [(200, None)]})
            with (
                patch.object(audit, "audit_resource", return_value=result),
                redirect_stdout(io.StringIO()),
            ):
                self.assertEqual(
                    audit.main(["--catalog", str(catalog), "--output", str(output)]), 0
                )
            report = json.loads(output.read_text())
            self.assertEqual(report["schemaVersion"], "1.1")
            self.assertEqual(report["summary"], {"reachable": 1})
            self.assertEqual(catalog.read_text(), original)

    def test_catalog_rejects_duplicate_ids_and_credential_urls(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "catalog.json"
            for resources in [
                [RESOURCE, RESOURCE],
                [
                    {
                        "id": "x",
                        "source": {"canonicalUrl": "https://user:password@example.com"},
                    }
                ],
            ]:
                path.write_text(json.dumps({"resources": resources}))
                with self.assertRaises(ValueError):
                    audit.load_catalog(path)


if __name__ == "__main__":
    unittest.main()
