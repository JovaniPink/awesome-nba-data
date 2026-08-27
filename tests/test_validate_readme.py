from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from typing import Final, TypeAlias, TypedDict

from scripts.validate_readme import (
    RESOURCE_ENTRY_RE,
    github_anchor,
    validate_document,
    validate_source_audit,
)

CatalogEntry: TypeAlias = tuple[str, str, str]


class ReleaseSourceContract(TypedDict):
    name: str
    url: str
    section: str
    readme_phrases: tuple[str, ...]
    forbidden_readme_phrases: tuple[str, ...]
    audit_category: str
    audit_authority: str
    audit_access: str
    audit_result: str
    audit_reviewed_at: str
    audit_note_phrases: tuple[str, ...]
    matrix_phrases: tuple[str, ...]


VALID_README = """# Awesome Test [![Awesome](https://awesome.re/badge.svg)](https://awesome.re)

> A focused catalog.

Catalog structure reviewed: August 2026.

## Contents

- [Official & League Data](#official--league-data)

## Official & League Data

- [Example](https://example.com/) - Example primary source.

## Contributing

See the contribution guide.
"""

PUBLISHABLE_TEXT_FILES: Final[tuple[str, ...]] = (
    ".github/workflows/validate.yml",
    "AGENTS.md",
    "LICENSE",
    "README.md",
    "code-of-conduct.md",
    "contributing.md",
    "docs/source-audit.tsv",
    "docs/source-matrix.md",
    "scripts/validate_readme.py",
    "tests/test_validate_readme.py",
)

RELEASE_SOURCE_CONTRACTS: Final[tuple[ReleaseSourceContract, ...]] = (
    {
        "name": "NBA Injury Report: 2025-26 Season",
        "url": "https://official.nba.com/nba-injury-report-2025-26-season/",
        "section": "Official & League Data",
        "readme_phrases": (
            "season-specific reports",
            "update throughout reporting windows",
            "not a historical bulk-data API",
        ),
        "forbidden_readme_phrases": ("is a historical bulk-data API",),
        "audit_category": "Official & League Data",
        "audit_authority": "official",
        "audit_access": "public-restricted",
        "audit_result": "403-anti-bot",
        "audit_reviewed_at": "2026-08-27",
        "audit_note_phrases": (
            "Browser-visible season page",
            "automated request blocked",
            "no historical bulk API",
        ),
        "matrix_phrases": (
            "Season-specific public page",
            "no documented supported bulk export",
            "public access does not establish redistribution permission",
            "**Not approved**",
        ),
    },
    {
        "name": "NBA Player Transactions",
        "url": "https://www.nba.com/players/transactions",
        "section": "Official & League Data",
        "readme_phrases": (
            "Official filterable transaction reference",
            "does not establish a documented bulk-data license",
        ),
        "forbidden_readme_phrases": (
            "establishes a documented bulk-data license",
        ),
        "audit_category": "Official & League Data",
        "audit_authority": "official",
        "audit_access": "public-restricted",
        "audit_result": "403-anti-bot",
        "audit_reviewed_at": "2026-08-27",
        "audit_note_phrases": (
            "Browser-visible dynamic page",
            "automated request blocked",
            "no documented bulk-data license",
        ),
        "matrix_phrases": (
            "Public web interface with dynamically loaded results",
            "no documented supported bulk export",
            "public access does not establish redistribution permission",
            "**Not approved**",
        ),
    },
)


def _catalog_entries_by_url(text: str) -> dict[str, CatalogEntry]:
    entries: dict[str, CatalogEntry] = {}
    section = ""
    for line in text.splitlines():
        if line.startswith("## "):
            section = line.removeprefix("## ")
            continue
        match = RESOURCE_ENTRY_RE.fullmatch(line)
        if match and match.group(3):
            entries[match.group(2)] = (match.group(1), section, match.group(3))
    return entries


def _audit_rows_by_url(text: str) -> dict[str, dict[str, str]]:
    lines = text.splitlines()
    if not lines:
        return {}
    headings = lines[0].split("\t")
    rows: dict[str, dict[str, str]] = {}
    for line in lines[1:]:
        values = line.split("\t")
        row = dict(zip(headings, values, strict=True))
        rows[row["url"]] = row
    return rows


def _release_source_contract_errors(
    readme_text: str, audit_text: str, matrix_text: str
) -> tuple[str, ...]:
    errors: list[str] = []
    entries = _catalog_entries_by_url(readme_text)
    audit_rows = _audit_rows_by_url(audit_text)
    matrix_lines = matrix_text.splitlines()

    for contract in RELEASE_SOURCE_CONTRACTS:
        url = contract["url"]
        entry = entries.get(url)
        if entry is None:
            errors.append(f"missing release source URL: {url}")
            continue
        name, section, description = entry
        if name != contract["name"]:
            errors.append(f"unexpected README name for {url}: {name}")
        if section != contract["section"]:
            errors.append(f"unexpected README section for {url}: {section}")
        for phrase in contract["readme_phrases"]:
            if phrase not in description:
                errors.append(f"missing README phrase for {url}: {phrase}")
        for phrase in contract["forbidden_readme_phrases"]:
            if phrase in description:
                errors.append(f"forbidden README phrase for {url}: {phrase}")

        audit_row = audit_rows.get(url)
        if audit_row is None:
            errors.append(f"missing audit row for {url}")
        else:
            expected_audit_fields = {
                "name": contract["name"],
                "category": contract["audit_category"],
                "authority": contract["audit_authority"],
                "access": contract["audit_access"],
                "result": contract["audit_result"],
                "reviewed_at": contract["audit_reviewed_at"],
            }
            for field, expected in expected_audit_fields.items():
                if audit_row[field] != expected:
                    errors.append(
                        f"unexpected audit {field} for {url}: {audit_row[field]}"
                    )
            for phrase in contract["audit_note_phrases"]:
                if phrase not in audit_row["note"]:
                    errors.append(f"missing audit note phrase for {url}: {phrase}")

        matrix_prefix = f"| {contract['name']} |"
        matrix_row = next(
            (line for line in matrix_lines if line.startswith(matrix_prefix)), None
        )
        if matrix_row is None:
            errors.append(f"missing source matrix row for {url}")
        else:
            for phrase in contract["matrix_phrases"]:
                if phrase not in matrix_row:
                    errors.append(f"missing matrix phrase for {url}: {phrase}")

    return tuple(errors)


class GithubAnchorTests(unittest.TestCase):
    def test_matches_github_heading_style(self) -> None:
        self.assertEqual(github_anchor("Official & League Data"), "official--league-data")


class DocumentValidationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_directory = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_directory.name)
        for filename in ("LICENSE", "code-of-conduct.md", "contributing.md"):
            (self.root / filename).touch()

    def tearDown(self) -> None:
        self.temp_directory.cleanup()

    def test_accepts_the_catalog_contract(self) -> None:
        result = validate_document(VALID_README, self.root)

        self.assertEqual(result.errors, ())
        self.assertEqual(result.resource_count, 1)
        self.assertEqual(result.contents_count, 1)

    def test_reports_contents_and_resource_format_errors(self) -> None:
        invalid = VALID_README.replace(
            "- [Official & League Data](#official--league-data)",
            "- [Contributing](#contributing)",
        ).replace(
            "- [Example](https://example.com/) - Example primary source.",
            "- [Example](http://example.com/) - lowercase description",
        )

        result = validate_document(invalid, self.root)

        self.assertTrue(any("Contents entries must match" in error for error in result.errors))
        self.assertTrue(any("must use HTTPS" in error for error in result.errors))
        self.assertTrue(any("start uppercase" in error for error in result.errors))
        self.assertTrue(any("end with a period" in error for error in result.errors))

    def test_reports_malformed_and_duplicate_resources(self) -> None:
        invalid = VALID_README.replace(
            "- [Example](https://example.com/) - Example primary source.",
            "- [Example](https://example.com/) - Example primary source.\n"
            "- [Malformed](https://malformed.example/) / "
            "[Second](https://second.example/) - Combined entry.\n"
            "- [Duplicate](https://example.com/) - Duplicate source.",
        )

        result = validate_document(invalid, self.root)

        self.assertTrue(any("must match" in error for error in result.errors))
        self.assertTrue(any("duplicate resource URL" in error for error in result.errors))

    def test_reports_missing_relative_links(self) -> None:
        invalid = VALID_README + "\n[Missing](docs/missing.md)\n"

        result = validate_document(invalid, self.root)

        self.assertIn(
            "relative link for 'Missing' points to missing file: docs/missing.md",
            result.errors,
        )

    def test_reports_non_ascii_characters(self) -> None:
        invalid = VALID_README.replace("focused", f"foc{chr(0x016B)}sed")

        result = validate_document(invalid, self.root)

        self.assertIn(
            "line 3: document must use ASCII characters; found U+016B",
            result.errors,
        )

    def test_empty_document_reports_errors_instead_of_crashing(self) -> None:
        result = validate_document("", self.root)

        self.assertTrue(result.errors)
        self.assertEqual(result.resource_count, 0)

    def test_source_audit_covers_every_catalog_resource_exactly_once(self) -> None:
        audit = (
            "name\turl\tcategory\tauthority\taccess\tresult\treviewed_at\tnote\n"
            "Example\thttps://example.com/\tOfficial & League Data\tprimary\tpublic"
            "\t200\t2026-08-13\tReviewed source\n"
        )

        self.assertEqual(validate_source_audit(VALID_README, audit), ())

    def test_source_audit_rejects_missing_and_extra_rows(self) -> None:
        audit = (
            "name\turl\tcategory\tauthority\taccess\tresult\treviewed_at\tnote\n"
            "Extra\thttps://extra.example/\tOther\tunknown\tunknown"
            "\t200\t2026-08-13\tNot in catalog\n"
        )

        errors = validate_source_audit(VALID_README, audit)

        self.assertTrue(any("missing README URLs" in error for error in errors))
        self.assertTrue(any("non-catalog URLs" in error for error in errors))


class ReleaseSourceContractTests(unittest.TestCase):
    def setUp(self) -> None:
        repository_root = Path(__file__).resolve().parents[1]
        self.readme = (repository_root / "README.md").read_text(encoding="utf-8")
        self.audit = (repository_root / "docs/source-audit.tsv").read_text(
            encoding="utf-8"
        )
        self.matrix = (repository_root / "docs/source-matrix.md").read_text(
            encoding="utf-8"
        )

    def test_release_sources_match_reviewed_evidence(self) -> None:
        self.assertEqual(
            _release_source_contract_errors(self.readme, self.audit, self.matrix), ()
        )

    def test_release_source_contract_rejects_boundary_mutations(self) -> None:
        readme = self.readme.replace(
            "not a historical bulk-data API", "is a historical bulk-data API"
        )
        audit = self.audit.replace(
            "\t403-anti-bot\t2026-08-27", "\t200\t2026-08-27", 1
        )
        matrix = self.matrix.replace(
            "public access does not establish redistribution permission",
            "public access establishes redistribution permission",
            1,
        )

        errors = _release_source_contract_errors(readme, audit, matrix)

        self.assertTrue(any("forbidden README phrase" in error for error in errors))
        self.assertTrue(any("unexpected audit result" in error for error in errors))
        self.assertTrue(any("missing matrix phrase" in error for error in errors))


class RepositoryTextContractTests(unittest.TestCase):
    def test_publishable_text_files_are_ascii(self) -> None:
        repository_root = Path(__file__).resolve().parents[1]

        for relative_path in PUBLISHABLE_TEXT_FILES:
            with self.subTest(path=relative_path):
                contents = (repository_root / relative_path).read_bytes()
                self.assertTrue(
                    contents.isascii(), f"{relative_path} must contain only ASCII"
                )


if __name__ == "__main__":
    unittest.main()
