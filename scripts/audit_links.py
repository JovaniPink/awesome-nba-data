#!/usr/bin/env python3
"""Manually audit catalog URL transport; responses do not establish content quality."""

from __future__ import annotations

import argparse
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import hashlib
import http.client
import io
import ipaddress
import json
import math
from pathlib import Path
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
TIMEOUT = 20
RESOURCE_DEADLINE_SECONDS = 20
MAX_BODY_BYTES = 65536
TRANSIENT_STATUS = {500, 502, 503, 504}
USER_AGENT = "CatalogLinkAudit/1.0 (manual resource availability review)"


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def host(url: str) -> str:
    return (urllib.parse.urlsplit(url).hostname or "").lower().removeprefix("www.")


class UnsafeDestination(ValueError):
    """A request refused locally, before sending HTTP to its destination."""


def validate_url(url: str) -> None:
    # Reject syntax that URL parsers, DNS, and HTTP could interpret differently.
    if any(ord(char) <= 32 or ord(char) >= 127 for char in url):
        raise UnsafeDestination("URL must use printable ASCII without whitespace")
    try:
        parsed = urllib.parse.urlsplit(url)
        if (
            parsed.scheme != "https"
            or not parsed.hostname
            or parsed.username is not None
            or parsed.password is not None
            or parsed.port not in (None, 443)
            or "%" in parsed.netloc
            or "\\" in parsed.netloc
        ):
            raise UnsafeDestination("Only credential-free HTTPS on port 443 is allowed")
    except ValueError as error:
        raise UnsafeDestination(str(error)) from error


def is_public_address(value: str) -> bool:
    address = ipaddress.ip_address(value)
    if not address.is_global or address.is_multicast or address.is_reserved:
        return False
    # Keep conservative behavior across Python 3.11/3.14 registry differences.
    if address.version == 4:
        return not any(address in ipaddress.ip_network(net) for net in (
            "192.0.0.0/24", "192.88.99.0/24",
        ))
    # Exclude mapped, translation, transition, scoped and special-purpose IPv6.
    return (
        "%" not in value
        and address in ipaddress.ip_network("2000::/3")
        and not any(address in ipaddress.ip_network(net) for net in (
            "2001::/23", "2002::/16", "3fff::/20",
        ))
    )


def public_connection(address, timeout=TIMEOUT, source_address=None):
    hostname, port = address
    if port != 443:
        raise UnsafeDestination("Only port 443 is allowed")
    resolved = socket.getaddrinfo(hostname, port, type=socket.SOCK_STREAM)
    if not resolved:
        raise OSError("DNS returned no addresses")
    # Validate the entire answer before opening any socket, including mixed A/AAAA.
    for family, socktype, protocol, _, sockaddr in resolved:
        if family not in (socket.AF_INET, socket.AF_INET6) or not is_public_address(sockaddr[0]):
            raise UnsafeDestination("Destination resolves to a non-public address")
    last_error = None
    for family, socktype, protocol, _, sockaddr in resolved:
        sock = None
        try:
            sock = socket.socket(family, socktype, protocol)
            sock.settimeout(timeout)
            if source_address:
                sock.bind(source_address)
            # Numeric sockaddr from the checked DNS answer: no second lookup.
            sock.connect(sockaddr)
            return sock
        except OSError as error:
            last_error = error
            if sock is not None:
                sock.close()
    raise last_error


class PublicHTTPSConnection(http.client.HTTPSConnection):
    def connect(self):
        if self._tunnel_host:
            raise UnsafeDestination("Proxy tunnels are disabled")
        self._create_connection = public_connection
        # Retains standard certificate verification and original-host TLS SNI.
        super().connect()


class PublicHTTPSHandler(urllib.request.HTTPSHandler):
    def https_open(self, req):
        return self.do_open(PublicHTTPSConnection, req)


def build_public_opener(redirects):
    # Neither environment nor system proxies may resolve destinations for us.
    return urllib.request.build_opener(
        urllib.request.ProxyHandler({}), PublicHTTPSHandler(), redirects
    )


class RedirectRecorder(urllib.request.HTTPRedirectHandler):
    max_redirections = 5
    max_repeats = 1

    def __init__(self) -> None:
        self.chain: list[dict] = []

    def http_error_302(self, req, fp, code, msg, headers):
        # urllib normally drains the entire redirect body before following it.
        # Close it instead: redirect metadata is sufficient for this audit.
        fp.close()
        return super().http_error_302(req, io.BytesIO(), code, msg, headers)

    http_error_301 = http_error_303 = http_error_307 = http_error_308 = http_error_302

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        self.chain.append({"status": code, "from": req.full_url, "to": newurl})
        validate_url(newurl)
        redirected = super().redirect_request(req, fp, code, msg, headers, newurl)
        # Python 3.11's handler defaults redirected HEAD requests to GET.
        # Preserve HEAD so body limits and the reported method stay accurate.
        if redirected is not None and req.get_method() == "HEAD":
            redirected.method = "HEAD"
        return redirected


def request(url: str, method: str, opener_factory=build_public_opener) -> dict:
    redirects = RedirectRecorder()
    result = {
        "method": method,
        "observedAt": now(),
        "httpStatus": None,
        "finalUrl": url,
        "redirectChain": redirects.chain,
        "error": None,
    }
    try:
        validate_url(url)
        req = urllib.request.Request(url, method=method, headers={"User-Agent": USER_AGENT})
        with opener_factory(redirects).open(req, timeout=TIMEOUT) as response:
            result.update(httpStatus=response.status, finalUrl=response.geturl())
            if method == "GET":
                # Never download full datasets just to check a catalog link.
                result["sampleBytes"] = len(response.read(MAX_BODY_BYTES))
    except UnsafeDestination as error:
        result.update(error=str(error), securityBlocked=True)
        if redirects.chain:
            result["finalUrl"] = redirects.chain[-1]["to"]
    except urllib.error.HTTPError as error:
        result.update(
            httpStatus=error.code, finalUrl=error.geturl(), error=str(error.reason)
        )
        error.close()
    except (
        urllib.error.URLError,
        OSError,
        ValueError,
        http.client.HTTPException,
    ) as error:
        result["error"] = str(error)
        reason = error.reason if isinstance(error, urllib.error.URLError) else error
        result["timedOut"] = isinstance(reason, TimeoutError)
        result["transient"] = isinstance(
            error,
            (TimeoutError, socket.timeout, ConnectionError, http.client.HTTPException),
        ) or (
            isinstance(error, urllib.error.URLError)
            and isinstance(
                error.reason, (TimeoutError, socket.timeout, ConnectionError)
            )
        )
        if redirects.chain:
            result["finalUrl"] = redirects.chain[-1]["to"]
    return result


def classify(attempt: dict) -> str:
    if attempt.get("deadlineExceeded"):
        return "deadline-exceeded"
    if attempt.get("workerFailed"):
        return "worker-error"
    if attempt.get("securityBlocked"):
        return "security-blocked"
    status = attempt["httpStatus"]
    if status is None or (status < 300 and attempt["error"]):
        return "transport-error"
    if 200 <= status < 300:
        return "redirected" if attempt["redirectChain"] else "reachable"
    if status in (401, 403, 407, 451):
        return "blocked/authentication-required"
    if status == 429:
        return "rate-limited"
    if status in (404, 410):
        return "missing"
    if 500 <= status < 600:
        return "server-error"
    if 300 <= status < 400:
        return "redirect-error"
    return "http-error"


def _audit_resource(resource: dict, requester=request, sleep=time.sleep, emit=None) -> dict:
    """HTTP engine, run only in the supervised child (or offline unit fixtures)."""
    url = resource["source"]["canonicalUrl"]
    attempts = []
    retry_remaining = True
    method = "HEAD"
    while True:
        if emit:
            emit({"type": "phase", "phase": "request", "method": method})
        attempt = requester(url, method)
        attempts.append(attempt)
        if emit:
            emit({"type": "attempt", "attempt": attempt})
        status = attempt["httpStatus"]
        if retry_remaining and (status in TRANSIENT_STATUS or attempt.get("transient")):
            retry_remaining = False
            if emit:
                emit({"type": "phase", "phase": "retry-backoff", "method": method})
            sleep(1)
            continue
        # Some publishers time out or return 5xx for HEAD while GET works.
        # Keep the existing retry budget shared across both methods.
        if method == "HEAD" and (
            status in (403, 404, 405, 410)
            or (status is not None and 500 <= status < 600)
            or attempt.get("timedOut")
        ):
            method = "GET"
            continue
        break
    return _resource_result(resource, attempts)


def _resource_result(resource: dict, attempts: list[dict]) -> dict:
    attempt = attempts[-1]
    result = {
        "resourceId": resource["id"],
        "url": resource["source"]["canonicalUrl"],
        "observedAt": attempt["observedAt"],
        "method": attempt["method"],
        "httpStatus": attempt["httpStatus"],
        "finalUrl": attempt["finalUrl"],
        "redirectChain": attempt["redirectChain"],
        "error": attempt["error"],
        "classification": classify(attempt),
        "crossDomainRedirect": any(
            host(hop["from"]) != host(hop["to"])
            for item in attempts
            for hop in item["redirectChain"]
        ),
        "contentReview": "not-performed",
        "attempts": attempts,
    }
    return result


def _worker_main() -> int:
    """Private JSON-lines protocol; never execute anything supplied by the URL."""
    def emit(event):
        print(json.dumps(event, ensure_ascii=True), flush=True)
    resource = json.load(sys.stdin)
    result = _audit_resource(resource, emit=emit)
    emit({"type": "result", "result": result})
    return 0


def _incomplete_attempt(resource, method, phase, error, *, expired=False):
    return {
        "method": method, "observedAt": now(), "httpStatus": None,
        "finalUrl": resource["source"]["canonicalUrl"], "redirectChain": [],
        "error": error, "deadlineExceeded": expired, "workerFailed": not expired,
        "timedOut": expired, "incomplete": True, "phase": phase,
    }


def _supervise_resource(resource: dict, command: list[str], deadline_seconds: float) -> dict:
    """Stop and reap DNS/HTTP work rather than abandoning a timed-out thread."""
    if not math.isfinite(deadline_seconds) or deadline_seconds <= 0:
        raise ValueError("Resource deadline must be finite and positive")
    expires = time.monotonic() + deadline_seconds
    expired = False
    try:
        process = subprocess.Popen(
            command, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL, text=True, encoding="utf-8",
        )
    except OSError as error:
        return _resource_result(resource, [_incomplete_attempt(
            resource, "HEAD", "startup", f"Audit worker could not start (OS error {error.errno})",
        )])
    try:
        try:
            output, _ = process.communicate(
                json.dumps(resource, ensure_ascii=True),
                timeout=max(0, expires - time.monotonic()),
            )
            expired = time.monotonic() >= expires
        except subprocess.TimeoutExpired:
            expired = True
            process.kill()
            output, _ = process.communicate()
    finally:
        # Includes interruption/error paths; no detached DNS/reader thread survives.
        if process.poll() is None:
            process.kill()
        process.wait()
        for stream in (process.stdin, process.stdout):
            if stream is not None:
                stream.close()

    attempts = []
    phase, method = "startup", "HEAD"
    result = None
    for line in output.splitlines():
        try:
            event = json.loads(line)
        except (ValueError, TypeError):
            continue  # A killed process may leave one incomplete final line.
        if event.get("type") == "attempt":
            attempts.append(event["attempt"])
        elif event.get("type") == "phase":
            phase, method = event["phase"], event["method"]
        elif event.get("type") == "result":
            result = event["result"]
    if not expired and process.returncode == 0 and result is not None:
        return result

    # Preserve completed attempts, without inventing a response or redirect target
    # for an interrupted request. No retry or GET fallback follows this result.
    attempts.append(_incomplete_attempt(
        resource, method, phase,
        (f"Overall resource deadline exceeded ({deadline_seconds:g}s)"
         if expired else "Audit worker failed before completing a result"),
        expired=expired,
    ))
    return _resource_result(resource, attempts)


def audit_resource(resource: dict) -> dict:
    # Isolated Python ignores caller PYTHONPATH/startup customization. The worker
    # executes this trusted file, never a command or path taken from a catalog.
    return _supervise_resource(
        resource, [sys.executable, "-I", str(Path(__file__).resolve()), "--_worker"],
        RESOURCE_DEADLINE_SECONDS,
    )


def load_catalog(path: Path) -> dict:
    catalog = json.loads(path.read_text(encoding="utf-8"))
    resources = catalog["resources"]
    if not isinstance(resources, list) or not resources:
        raise ValueError("Catalog must contain a nonempty resources list")
    identifiers = set()
    for resource in resources:
        identifier = resource["id"]
        url = urllib.parse.urlsplit(resource["source"]["canonicalUrl"])
        if not isinstance(identifier, str) or identifier in identifiers:
            raise ValueError("Resource identifiers must be unique strings")
        if url.scheme != "https" or not url.hostname or url.username or url.password:
            raise ValueError("Canonical URLs must be HTTPS without credentials")
        identifiers.add(identifier)
    return catalog


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--catalog", type=Path, default=ROOT / "catalog/resources.v1.json"
    )
    parser.add_argument(
        "--output",
        type=Path,
        required=True,
        help="Destination for versioned JSON report",
    )
    args = parser.parse_args(argv)
    try:
        if args.output.resolve() == args.catalog.resolve():
            raise ValueError("Report must not overwrite its input catalog")
        catalog = load_catalog(args.catalog)
        catalog_hash = hashlib.sha256(args.catalog.read_bytes()).hexdigest()
        started = now()
        with ThreadPoolExecutor(max_workers=4) as pool:
            results = list(pool.map(audit_resource, catalog["resources"]))
        counts = dict(sorted(Counter(r["classification"] for r in results).items()))
        report = {
            "schemaVersion": "1.2",
            "projectId": catalog["projectId"],
            "catalogSha256": catalog_hash,
            "startedAt": started,
            "completedAt": now(),
            "boundary": "Transport observations only; HTTP success does not establish relevant content, rights, freshness, completeness, or quality.",
            "settings": {
                "workers": 4,
                "timeoutSeconds": TIMEOUT,
                "resourceDeadlineSeconds": RESOURCE_DEADLINE_SECONDS,
                "deadlineScope": "per resource; startup, DNS, connect, TLS, redirects, reads, retries and backoff",
                "transientRetries": 1,
                "maxGetBytes": MAX_BODY_BYTES,
                "destinationPolicy": "public-addresses-only; HTTPS port 443; no proxies",
            },
            "summary": counts,
            "resources": results,
        }
        args.output.write_text(
            json.dumps(report, indent=2, ensure_ascii=True) + "\n", encoding="utf-8"
        )
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(f"Audit failed: {error}", file=sys.stderr)
        return 1
    print(
        f"Audited {len(results)} resources: "
        + ", ".join(f"{k}={v}" for k, v in counts.items())
    )
    for result in results:
        if result["classification"] != "reachable" or result["crossDomainRedirect"]:
            print(
                f"{result['classification']}: {result['url']} -> {result['finalUrl']}"
            )
    print(
        f"Report: {args.output}. Content review was not performed; inspect redirects and failures."
    )
    return 0


if __name__ == "__main__":
    if sys.argv[1:] == ["--_worker"]:
        raise SystemExit(_worker_main())
    raise SystemExit(main())
