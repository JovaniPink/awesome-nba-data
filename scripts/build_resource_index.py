#!/usr/bin/env python3
"""Build the public knowledge-contract resource projection from README.md."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any, Final

ROOT: Final[Path] = Path(__file__).resolve().parents[1]
README_PATH: Final[Path] = ROOT / "README.md"
CONFIG_PATH: Final[Path] = ROOT / "catalog" / "resource-index.config.json"
OUTPUT_PATH: Final[Path] = ROOT / "catalog" / "resources.v1.json"
HEADING_RE: Final[re.Pattern[str]] = re.compile(r"^##\s+(.+?)\s*$")
RESOURCE_RE: Final[re.Pattern[str]] = re.compile(
    r"^- \[([^]]+)]\((https://[^)]+)\) - (.+\.)$"
)


def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def _access_status(description: str) -> str:
    normalized = description.lower()
    if any(term in normalized for term in ("restricted", "limited to active")):
        return "restricted"
    if any(
        term in normalized
        for term in ("paid", "subscription", "commercial", "licensed")
    ):
        return "licensed"
    if any(
        term in normalized
        for term in ("api key", "registration", "registered", "requires an account")
    ):
        return "registration-required"
    return "open-access"


def _resource_object(
    *,
    project_id: str,
    domains: list[str],
    projection_date: str,
    section: str,
    name: str,
    url: str,
    description: str,
) -> dict[str, Any]:
    resource_key = hashlib.sha256(url.encode("utf-8")).hexdigest()[:16]
    return {
        "schemaVersion": "1.0",
        "id": f"{project_id}:source:r-{resource_key}",
        "projectId": project_id,
        "legacyIds": [],
        "kind": "source",
        "title": name,
        "summary": description,
        "dates": {"createdAt": projection_date},
        "provenance": {"sourceIds": [], "methodIds": []},
        "semantics": {
            "domains": domains,
            "topics": [_slug(section)],
            "tags": ["catalog-resource"],
            "entities": [],
        },
        "evidenceStatus": "unreviewed",
        "editorialStatus": "published",
        "visibility": "public",
        "limitations": [
            "Catalog inclusion is curation, not endorsement, permission, maintenance proof, or model fitness proof.",
            "This record does not establish a dataset vintage, retrieval snapshot, license grant, or current availability.",
        ],
        "relationships": [],
        "corrections": [],
        "source": {
            "canonicalUrl": url,
            "publisher": name,
            "authorityRole": "secondary-source",
            "accessStatus": _access_status(description),
            "license": "Resource-specific terms apply; catalog inclusion grants no license.",
            "methodologyWarnings": [
                "Review the publisher methodology, access conditions, license, retrieval date, review date, and as-of meaning before use."
            ],
        },
    }


def build_projection() -> dict[str, Any]:
    config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    project_id = config["projectId"]
    domains = config["domains"]
    projection_date = config["projectionDate"]
    section = ""
    resources: list[dict[str, Any]] = []

    for line in README_PATH.read_text(encoding="utf-8").splitlines():
        heading = HEADING_RE.fullmatch(line)
        if heading:
            section = heading.group(1)
            continue
        resource = RESOURCE_RE.fullmatch(line)
        if not resource:
            continue
        if not section:
            raise ValueError("Resource entry appears before a level-two section.")
        name, url, description = resource.groups()
        resources.append(
            _resource_object(
                project_id=project_id,
                domains=domains,
                projection_date=projection_date,
                section=section,
                name=name,
                url=url,
                description=description,
            )
        )

    identifiers = [resource["id"] for resource in resources]
    if not resources:
        raise ValueError("No catalog resources were found.")
    if len(identifiers) != len(set(identifiers)):
        raise ValueError("Resource identifiers are not unique.")

    return {
        "schemaVersion": "1.0",
        "projectId": project_id,
        "generatedFrom": "README.md",
        "projectionDate": projection_date,
        "curationBoundary": (
            "Catalog inclusion is curation, not endorsement, permission, "
            "maintenance proof, or model fitness proof."
        ),
        "resources": resources,
    }


def render_projection() -> str:
    return json.dumps(build_projection(), indent=2, sort_keys=True) + "\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="Fail when the committed projection differs from README.md.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    rendered = render_projection()
    if args.check:
        if not OUTPUT_PATH.is_file():
            print(f"ERROR: missing {OUTPUT_PATH.relative_to(ROOT)}", file=sys.stderr)
            return 1
        if OUTPUT_PATH.read_text(encoding="utf-8") != rendered:
            print(
                "ERROR: catalog/resources.v1.json is out of sync; run "
                "python3 scripts/build_resource_index.py",
                file=sys.stderr,
            )
            return 1
        print(f"Resource projection is current: {len(build_projection()['resources'])} records")
        return 0

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(rendered, encoding="utf-8")
    print(f"Wrote {OUTPUT_PATH.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
