"""Exercise real process cancellation with offline DNS and drip transports."""

from concurrent.futures import ThreadPoolExecutor
from contextlib import redirect_stdout
import errno
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import audit_links as audit

RESOURCE = {"id": "deadline-test", "source": {"canonicalUrl": "https://publisher.example/data"}}
FIXTURE = Path(__file__).resolve().parent / "fixtures/deadline_worker.py"


class OverallDeadlineTests(unittest.TestCase):
    def supervise(self, mode, seconds=.8):
        command = [sys.executable, "-I", str(FIXTURE), mode]
        children = []
        create = subprocess.Popen
        def start(*args, **kwargs):
            child = create(*args, **kwargs)
            children.append(child)
            return child
        started = time.monotonic()
        with patch.object(subprocess, "Popen", start):
            result = audit._supervise_resource(RESOURCE, command, seconds)
        elapsed = time.monotonic() - started
        self.assertTrue(children)
        self.assertTrue(all(child.poll() is not None for child in children), "Child must be reaped")
        return result, elapsed

    def test_slow_dns_is_stopped_and_worker_reaped(self):
        result, elapsed = self.supervise("dns")
        self.assertEqual(result["classification"], "deadline-exceeded")
        self.assertLess(elapsed, 3)
        self.assertIsNone(result["httpStatus"])

    def test_slow_drip_body_is_stopped_and_head_evidence_survives(self):
        result, elapsed = self.supervise("body")
        self.assertEqual(result["classification"], "deadline-exceeded")
        self.assertLess(elapsed, 3)
        self.assertEqual(result["attempts"][0]["httpStatus"], 405)
        self.assertEqual(result["method"], "GET")
        self.assertTrue(result["attempts"][-1]["deadlineExceeded"])
        self.assertEqual(len(result["attempts"]), 2)

    def test_retry_backoff_and_fallback_dns_share_the_original_deadline(self):
        for mode, phase, status in (("backoff", "retry-backoff", 503), ("fallback-dns", "request", 405)):
            with self.subTest(mode=mode):
                result, elapsed = self.supervise(mode)
                self.assertEqual(result["classification"], "deadline-exceeded")
                self.assertLess(elapsed, 3)
                self.assertEqual(result["attempts"][0]["httpStatus"], status)
                self.assertEqual(result["attempts"][-1]["phase"], phase)
                self.assertEqual(len(result["attempts"]), 2)

    def test_slow_headers_connect_and_tls_are_also_stopped(self):
        for mode in ("headers", "connect", "tls"):
            with self.subTest(mode=mode):
                result, elapsed = self.supervise(mode)
                self.assertEqual(result["classification"], "deadline-exceeded")
                self.assertLess(elapsed, 3)

    def test_success_and_worker_failure_are_distinct(self):
        result, _ = self.supervise("fast", 3)
        self.assertEqual(result["classification"], "reachable")
        result, _ = self.supervise("crash", 3)
        self.assertEqual(result["classification"], "worker-error")
        self.assertIsNone(result["httpStatus"])

    def test_parallel_deadlines_do_not_cancel_successful_resource(self):
        with ThreadPoolExecutor(max_workers=2) as pool:
            slow = pool.submit(audit._supervise_resource, RESOURCE, [sys.executable, "-I", str(FIXTURE), "dns"], .8)
            # Each supervisor uses a process, with no process-wide alarm handler.
            fast = pool.submit(audit._supervise_resource, RESOURCE, [sys.executable, "-I", str(FIXTURE), "fast"], 3)
            self.assertEqual(fast.result()["classification"], "reachable")
            self.assertEqual(slow.result()["classification"], "deadline-exceeded")

    def test_production_worker_command_is_fixed_and_isolated(self):
        with patch.object(audit, "_supervise_resource", return_value={}) as supervise:
            audit.audit_resource(RESOURCE)
        supervise.assert_called_once_with(RESOURCE, [sys.executable, "-I", str(Path(audit.__file__).resolve()), "--_worker"], 20)

    def test_invalid_deadlines_do_not_start_a_worker(self):
        for deadline in (0, -1, float("inf"), float("nan")):
            with self.subTest(deadline=deadline), patch.object(subprocess, "Popen") as start:
                with self.assertRaises(ValueError):
                    audit._supervise_resource(RESOURCE, [], deadline)
                start.assert_not_called()

    def test_interrupt_kills_and_reaps_the_worker(self):
        with patch.object(subprocess, "Popen") as start:
            child = start.return_value
            child.communicate.side_effect = KeyboardInterrupt
            child.poll.return_value = None
            with self.assertRaises(KeyboardInterrupt):
                audit._supervise_resource(RESOURCE, [], 1)
            child.kill.assert_called_once()
            child.wait.assert_called_once()
            child.stdin.close.assert_called_once()
            child.stdout.close.assert_called_once()

    def test_launch_failure_is_a_resource_error_without_network_fallback(self):
        with patch.object(subprocess, "Popen", side_effect=OSError(errno.EMFILE, "file descriptor limit")) as start:
            result = audit.audit_resource(RESOURCE)
        self.assertEqual(result["classification"], "worker-error")
        self.assertIsNone(result["httpStatus"])
        self.assertEqual(result["attempts"][-1]["phase"], "startup")
        self.assertTrue(result["attempts"][-1]["incomplete"])
        start.assert_called_once()

    def test_launch_failure_does_not_discard_other_resource_observations(self):
        create = subprocess.Popen
        lock = threading.Lock()
        first = True
        def fail_one(*args, **kwargs):
            nonlocal first
            with lock:
                if first:
                    first = False
                    raise OSError(errno.EMFILE, "file descriptor limit")
            return create(*args, **kwargs)
        with tempfile.TemporaryDirectory() as directory:
            catalog, output = Path(directory) / "catalog.json", Path(directory) / "report.json"
            resources = [{"id": str(i), "source": {"canonicalUrl": "https://publisher.example:8443/"}} for i in range(2)]
            catalog.write_text(json.dumps({"projectId": "test", "resources": resources}))
            with patch.object(subprocess, "Popen", fail_one), redirect_stdout(io.StringIO()):
                self.assertEqual(audit.main(["--catalog", str(catalog), "--output", str(output)]), 0)
            report = json.loads(output.read_text())
            self.assertEqual(report["summary"], {"security-blocked": 1, "worker-error": 1})
            self.assertEqual({r["resourceId"] for r in report["resources"]}, {"0", "1"})

    def test_cli_uses_supervision_and_versioned_deadline_settings(self):
        with tempfile.TemporaryDirectory() as directory:
            catalog = Path(directory) / "catalog.json"
            output = Path(directory) / "report.json"
            # Syntax refusal happens before DNS; this fixture needs no network.
            blocked = {"id": "blocked", "source": {"canonicalUrl": "https://publisher.example:8443/"}}
            catalog.write_text(json.dumps({"projectId": "test", "resources": [blocked]}))
            completed = subprocess.run([sys.executable, "-I", str(audit.__file__), "--catalog", str(catalog), "--output", str(output)], capture_output=True, text=True, timeout=10)
            self.assertEqual(completed.returncode, 0, completed.stderr)
            report = json.loads(output.read_text())
            self.assertEqual(report["schemaVersion"], "1.2")
            self.assertEqual(report["settings"]["resourceDeadlineSeconds"], 20)
            self.assertEqual(report["resources"][0]["classification"], "security-blocked")


if __name__ == "__main__":
    unittest.main()
