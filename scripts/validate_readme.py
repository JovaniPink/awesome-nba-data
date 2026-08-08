#!/usr/bin/env python3
"""Validate the structural contract for the Awesome NBA catalog."""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path

AWESOME_BADGE = "[![Awesome](https://awesome.re/badge.svg)](https://awesome.re)"
EXCLUDED_CONTENTS_SECTIONS = {"Contribute", "Contributing", "Footnotes"}
HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$", re.MULTILINE)
CONTENTS_ENTRY_RE = re.compile(r"^- \[([^]]+)]\(#([^)]+)\)$")
MARKDOWN_LINK_RE = re.compile(r"(?<!!)\[([^]]+)]\(([^)]+)\)")
RESOURCE_BULLET_RE = re.compile(r"^\s*- \[[^]]+]\(https?://")
RESOURCE_ENTRY_RE = re.compile(
    r"^\s*- \[([^]]+)]\((https?://[^)]+)\)(?:\s+-\s+(.+))?$"
)
STRUCTURE_REVIEW_RE = re.compile(
    r"^Catalog structure reviewed: "
    r"(January|February|March|April|May|June|July|August|September|October|November|December) "
    r"\d{4}\.$",
    re.MULTILINE,
)


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


def _level_two_sections(text: str) -> list[tuple[str, int]]:
    return [
        (title, match.start())
        for match in HEADING_RE.finditer(text)
        if len(match.group(1)) == 2
        for title in [match.group(2)]
    ]


def validate_document(text: str, repository_root: Path) -> ValidationResult:
    errors: list[str] = []
    lines = text.splitlines()
    headings = list(HEADING_RE.finditer(text))
    h1_titles = [match.group(2) for match in headings if len(match.group(1)) == 1]
    sections = _level_two_sections(text)
    section_titles = [title for title, _ in sections]

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

    contents_entries: list[tuple[str, str]] = []
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

    for required_file in ("LICENSE", "code-of-conduct.md", "contributing.md"):
        if not (repository_root / required_file).is_file():
            errors.append(f"required repository file is missing: {required_file}")

    return ValidationResult(
        errors=tuple(errors),
        resource_count=resource_count,
        contents_count=len(contents_entries),
    )


def validate_readme(readme_path: Path) -> ValidationResult:
    return validate_document(readme_path.read_text(encoding="utf-8"), readme_path.parent)


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
