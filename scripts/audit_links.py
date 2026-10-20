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
import json
from pathlib import Path
import socket
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
TIMEOUT = 20
MAX_BODY_BYTES = 65536
TRANSIENT_STATUS = {500, 502, 503, 504}
USER_AGENT = "CatalogLinkAudit/1.0 (manual resource availability review)"


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def host(url: str) -> str:
    return (urllib.parse.urlsplit(url).hostname or "").lower().removeprefix("www.")


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
        parsed = urllib.parse.urlsplit(newurl)
        if parsed.scheme != "https" or parsed.username or parsed.password:
            raise urllib.error.HTTPError(
                req.full_url,
                code,
                "Refusing non-HTTPS or credential-bearing redirect",
                headers,
                fp,
            )
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def request(url: str, method: str, opener_factory=urllib.request.build_opener) -> dict:
    redirects = RedirectRecorder()
    result = {
        "method": method,
        "observedAt": now(),
        "httpStatus": None,
        "finalUrl": url,
        "redirectChain": redirects.chain,
        "error": None,
    }
    req = urllib.request.Request(url, method=method, headers={"User-Agent": USER_AGENT})
    try:
        with opener_factory(redirects).open(req, timeout=TIMEOUT) as response:
            result.update(httpStatus=response.status, finalUrl=response.geturl())
            if method == "GET":
                # Never download full datasets just to check a catalog link.
                result["sampleBytes"] = len(response.read(MAX_BODY_BYTES))
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


def audit_resource(resource: dict, requester=request, sleep=time.sleep) -> dict:
    url = resource["source"]["canonicalUrl"]
    attempts = []
    retry_remaining = True
    method = "HEAD"
    while True:
        attempt = requester(url, method)
        attempts.append(attempt)
        status = attempt["httpStatus"]
        if retry_remaining and (status in TRANSIENT_STATUS or attempt.get("transient")):
            retry_remaining = False
            sleep(1)
            continue
        if method == "HEAD" and status in (403, 404, 405, 410, 501):
            method = "GET"
            continue
        break
    result = {
        "resourceId": resource["id"],
        "url": url,
        "observedAt": attempt["observedAt"],
        "method": method,
        "httpStatus": status,
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
            "schemaVersion": "1.0",
            "projectId": catalog["projectId"],
            "catalogSha256": catalog_hash,
            "startedAt": started,
            "completedAt": now(),
            "boundary": "Transport observations only; HTTP success does not establish relevant content, rights, freshness, completeness, or quality.",
            "settings": {
                "workers": 4,
                "timeoutSeconds": TIMEOUT,
                "transientRetries": 1,
                "maxGetBytes": MAX_BODY_BYTES,
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
    raise SystemExit(main())
