#!/usr/bin/env python3
"""Validate the structural contract for the Awesome NBA catalog."""

from __future__ import annotations

import argparse
import csv
import io
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Final, TypeAlias

Section: TypeAlias = tuple[str, int]
ContentsEntry: TypeAlias = tuple[str, str]

AWESOME_BADGE: Final[str] = (
    "[![Awesome](https://awesome.re/badge.svg)](https://awesome.re)"
)
EXCLUDED_CONTENTS_SECTIONS: Final[frozenset[str]] = frozenset(
    {"Contribute", "Contributing", "Footnotes"}
)
REQUIRED_FILES: Final[tuple[str, ...]] = (
    "LICENSE",
    "code-of-conduct.md",
    "contributing.md",
)
HEADING_RE: Final[re.Pattern[str]] = re.compile(
    r"^(#{1,6})\s+(.+?)\s*$", re.MULTILINE
)
CONTENTS_ENTRY_RE: Final[re.Pattern[str]] = re.compile(
    r"^- \[([^]]+)]\(#([^)]+)\)$"
)
MARKDOWN_LINK_RE: Final[re.Pattern[str]] = re.compile(
    r"(?<!!)\[([^]]+)]\(([^)]+)\)"
)
RESOURCE_BULLET_RE: Final[re.Pattern[str]] = re.compile(
    r"^\s*- \[[^]]+]\(https?://"
)
RESOURCE_ENTRY_RE: Final[re.Pattern[str]] = re.compile(
    r"^\s*- \[([^]]+)]\((https?://[^)]+)\)(?:\s+-\s+(.+))?$"
)
STRUCTURE_REVIEW_RE: Final[re.Pattern[str]] = re.compile(
    r"^Catalog structure reviewed: "
    r"(January|February|March|April|May|June|July|August|September|October|November|December) "
    r"\d{4}\.$",
    re.MULTILINE,
)
AUDIT_COLUMNS: Final[tuple[str, ...]] = (
    "name",
    "url",
    "category",
    "authority",
    "access",
    "result",
    "reviewed_at",
    "note",
)
AUDIT_DATE_RE: Final[re.Pattern[str]] = re.compile(r"^\d{4}-\d{2}-\d{2}$")


@dataclass(frozen=True)
class ValidationResult:
    errors: tuple[str, ...]
    resource_count: int
    contents_count: int


def github_anchor(heading: str) -> str:
    """Return the anchor GitHub generates for the headings used in this README."""

    normalized = heading.strip().lower()
    normalized = re.sub(r"[^\w\s-]", "", normalized)
    return re.sub(r"\s", "-", normalized)


def _level_two_sections(text: str) -> list[Section]:
    return [
        (title, match.start())
        for match in HEADING_RE.finditer(text)
        if len(match.group(1)) == 2
        for title in [match.group(2)]
    ]


def _non_ascii_code_points(text: str) -> tuple[str, ...]:
    """Return sorted Unicode code points for non-ASCII characters in text."""

    return tuple(
        f"U+{ord(character):04X}"
        for character in sorted(set(text))
        if not character.isascii()
    )


def validate_document(text: str, repository_root: Path) -> ValidationResult:
    errors: list[str] = []
    lines = text.splitlines()
    headings = list(HEADING_RE.finditer(text))
    h1_titles = [match.group(2) for match in headings if len(match.group(1)) == 1]
    sections = _level_two_sections(text)
    section_titles = [title for title, _ in sections]

    for line_number, line in enumerate(lines, start=1):
        non_ascii_code_points = _non_ascii_code_points(line)
        if non_ascii_code_points:
            errors.append(
                f"line {line_number}: document must use ASCII characters; found "
                f"{', '.join(non_ascii_code_points)}"
            )

    if len(h1_titles) != 1:
        errors.append(f"expected exactly one level-one heading, found {len(h1_titles)}")
    if not lines or AWESOME_BADGE not in lines[0]:
        errors.append("the level-one heading must contain the canonical Awesome badge")
    if not STRUCTURE_REVIEW_RE.search(text):
        errors.append("missing 'Catalog structure reviewed: Month YYYY.' metadata")

    if not sections or sections[0][0] != "Contents":
        errors.append("Contents must be the first level-two section")

    duplicates = sorted({title for title in section_titles if section_titles.count(title) > 1})
    if duplicates:
        errors.append(f"duplicate level-two sections: {', '.join(duplicates)}")

    contents_entries: list[ContentsEntry] = []
    if sections and sections[0][0] == "Contents":
        contents_start = sections[0][1]
        contents_end = sections[1][1] if len(sections) > 1 else len(text)
        for line in text[contents_start:contents_end].splitlines():
            match = CONTENTS_ENTRY_RE.fullmatch(line)
            if match:
                contents_entries.append((match.group(1), match.group(2)))

    expected_contents = [
        title for title in section_titles[1:] if title not in EXCLUDED_CONTENTS_SECTIONS
    ]
    actual_contents = [title for title, _ in contents_entries]
    if actual_contents != expected_contents:
        errors.append(
            "Contents entries must match catalog sections in order "
            f"(expected {expected_contents!r}, found {actual_contents!r})"
        )

    for title, anchor in contents_entries:
        expected_anchor = github_anchor(title)
        if anchor != expected_anchor:
            errors.append(
                f"Contents anchor for '{title}' must be '#{expected_anchor}', found '#{anchor}'"
            )

    resource_count = 0
    seen_urls: dict[str, int] = {}
    for line_number, line in enumerate(lines, start=1):
        match = RESOURCE_ENTRY_RE.fullmatch(line)
        if not match:
            if RESOURCE_BULLET_RE.match(line):
                errors.append(
                    f"line {line_number}: resource entry must match "
                    "'- [Name](URL) - Description.'"
                )
            continue

        resource_count += 1
        url = match.group(2)
        description = match.group(3)
        if not url.startswith("https://"):
            errors.append(f"line {line_number}: resource URL must use HTTPS: {url}")
        if url in seen_urls:
            errors.append(
                f"line {line_number}: duplicate resource URL first used on line {seen_urls[url]}: "
                f"{url}"
            )
        else:
            seen_urls[url] = line_number
        if not description:
            errors.append(f"line {line_number}: resource entry must include a description")
            continue
        if description[0].isalpha() and not description[0].isupper():
            errors.append(f"line {line_number}: resource description must start uppercase")
        if not description.endswith("."):
            errors.append(f"line {line_number}: resource description must end with a period")

    if resource_count == 0:
        errors.append("expected at least one external resource entry")

    for label, target in MARKDOWN_LINK_RE.findall(text):
        if target.startswith(("https://", "http://", "mailto:", "#")):
            continue
        path = target.split("#", 1)[0]
        if path and not (repository_root / path).is_file():
            errors.append(f"relative link for '{label}' points to missing file: {path}")

    for required_file in REQUIRED_FILES:
        if not (repository_root / required_file).is_file():
            errors.append(f"required repository file is missing: {required_file}")

    return ValidationResult(
        errors=tuple(errors),
        resource_count=resource_count,
        contents_count=len(contents_entries),
    )


def validate_source_audit(readme_text: str, audit_text: str) -> tuple[str, ...]:
    """Require one dated audit row for every external resource in the README."""

    errors: list[str] = []
    resources = {
        match.group(2): match.group(1)
        for line in readme_text.splitlines()
        if (match := RESOURCE_ENTRY_RE.fullmatch(line))
    }
    reader = csv.DictReader(io.StringIO(audit_text), delimiter="\t")
    if tuple(reader.fieldnames or ()) != AUDIT_COLUMNS:
        return (
            "source audit columns must be exactly " + ", ".join(AUDIT_COLUMNS),
        )

    audited: dict[str, str] = {}
    for row_number, row in enumerate(reader, start=2):
        url = row["url"].strip()
        name = row["name"].strip()
        if not url.startswith("https://"):
            errors.append(f"source audit row {row_number}: URL must use HTTPS: {url}")
        if url in audited:
            errors.append(f"source audit row {row_number}: duplicate URL: {url}")
        audited[url] = name
        if not AUDIT_DATE_RE.fullmatch(row["reviewed_at"].strip()):
            errors.append(
                f"source audit row {row_number}: reviewed_at must use YYYY-MM-DD"
            )
        for field in ("category", "authority", "access", "result", "note"):
            if not row[field].strip():
                errors.append(f"source audit row {row_number}: {field} must not be empty")

    missing = sorted(set(resources) - set(audited))
    extra = sorted(set(audited) - set(resources))
    if missing:
        errors.append("source audit is missing README URLs: " + ", ".join(missing))
    if extra:
        errors.append("source audit contains non-catalog URLs: " + ", ".join(extra))
    for url in sorted(set(resources) & set(audited)):
        if resources[url] != audited[url]:
            errors.append(
                f"source audit name for {url!r} must be {resources[url]!r}, "
                f"found {audited[url]!r}"
            )

    return tuple(errors)


def validate_readme(readme_path: Path) -> ValidationResult:
    text = readme_path.read_text(encoding="utf-8")
    result = validate_document(text, readme_path.parent)
    audit_path = readme_path.parent / "docs" / "source-audit.tsv"
    audit_errors: tuple[str, ...]
    if audit_path.is_file():
        audit_errors = validate_source_audit(
            text, audit_path.read_text(encoding="utf-8")
        )
    else:
        audit_errors = ("required source audit is missing: docs/source-audit.tsv",)
    return ValidationResult(
        errors=result.errors + audit_errors,
        resource_count=result.resource_count,
        contents_count=result.contents_count,
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("readme", nargs="?", default="README.md", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    result = validate_readme(args.readme)
    if result.errors:
        for error in result.errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    print(
        "README validation passed: "
        f"{result.resource_count} resource entries, "
        f"{result.contents_count} Contents entries"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
