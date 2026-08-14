from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from scripts.validate_readme import (
    github_anchor,
    validate_document,
    validate_source_audit,
)


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


if __name__ == "__main__":
    unittest.main()
