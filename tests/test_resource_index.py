from __future__ import annotations

import json
import importlib.util
import subprocess
import sys
import unittest
from tempfile import TemporaryDirectory
from unittest.mock import patch
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX_PATH = ROOT / "catalog" / "resources.v1.json"


class ResourceIndexTests(unittest.TestCase):
    def setUp(self) -> None:
        self.index = json.loads(INDEX_PATH.read_text(encoding="utf-8"))

    def test_projection_is_current(self) -> None:
        result = subprocess.run(
            [sys.executable, "scripts/build_resource_index.py", "--check"],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_identifiers_are_stable_and_unique(self) -> None:
        resources = self.index["resources"]
        identifiers = [resource["id"] for resource in resources]
        self.assertEqual(len(identifiers), len(set(identifiers)))
        self.assertTrue(
            all(identifier.startswith(f"{self.index['projectId']}:source:r-") for identifier in identifiers)
        )

    def test_projection_preserves_the_public_boundary(self) -> None:
        for resource in self.index["resources"]:
            self.assertEqual(resource["evidenceStatus"], "unreviewed")
            self.assertEqual(resource["visibility"], "public")
            self.assertNotIn("retrievedAt", resource["dates"])
            self.assertIn("grants no license", resource["source"]["license"])
            self.assertIn("not endorsement", resource["limitations"][0])

    def test_unreviewed_description_cannot_assert_source_assessments(self) -> None:
        spec = importlib.util.spec_from_file_location("resource_builder", ROOT / "scripts/build_resource_index.py")
        self.assertIsNotNone(spec)
        assert spec is not None and spec.loader is not None
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        identifiers = []
        for description in ("Provides example data.", "Official open data.", "Paid commercial data.", "Requires an account."):
            with self.subTest(description=description):
                resource = module._resource_object(project_id=self.index["projectId"], domains=["sports"], projection_date="2026-08-30", section="Data", name="Example", url="https://example.com/data", description=description)
                identifiers.append(resource["id"])
                self.assertEqual(resource["source"]["accessStatus"], "unknown")
                self.assertEqual(resource["source"]["authorityRole"], "unknown")
                self.assertEqual(resource["schemaVersion"], "1.1")
                self.assertEqual(resource["summary"], description)
        self.assertEqual(len(set(identifiers)), 1)

    def test_all_projected_assessments_remain_unknown(self) -> None:
        self.assertEqual(self.index["schemaVersion"], "1.1")
        for resource in self.index["resources"]:
            self.assertEqual(resource["source"]["authorityRole"], "unknown")
            self.assertEqual(resource["source"]["accessStatus"], "unknown")

    def build_fixture(self, creation_dates):
        spec = importlib.util.spec_from_file_location("resource_builder", ROOT / "scripts/build_resource_index.py")
        assert spec is not None and spec.loader is not None
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        with TemporaryDirectory() as directory:
            root = Path(directory)
            readme = root / "README.md"
            config = root / "config.json"
            readme.write_text("## Data\n- [Old](https://example.com/old) - Original data.\n- [New](https://example.com/new) - New data.\n", encoding="utf-8")
            settings = {"projectId": "example", "domains": ["sports"], "projectionDate": "2026-08-30"}
            if creation_dates is not None:
                settings["creationDates"] = creation_dates
            config.write_text(json.dumps(settings), encoding="utf-8")
            with patch.object(module, "README_PATH", readme), patch.object(module, "CONFIG_PATH", config):
                return module.build_projection()

    def test_creation_dates_are_explicit_and_independent_of_projection_date(self) -> None:
        result = self.build_fixture({"https://example.com/old": "2026-08-30", "https://example.com/new": "2026-10-09"})
        self.assertEqual(result["projectionDate"], "2026-08-30")
        self.assertEqual([r["dates"]["createdAt"] for r in result["resources"]], ["2026-08-30", "2026-10-09"])

    def test_new_identity_date_cannot_change_existing_identity(self) -> None:
        before = self.build_fixture({"https://example.com/old": "2026-08-30", "https://example.com/new": "2026-10-09"})
        after = self.build_fixture({"https://example.com/old": "2026-08-30", "https://example.com/new": "2026-10-10"})
        self.assertEqual(before["resources"][0], after["resources"][0])
        self.assertEqual(before["resources"][1]["id"], after["resources"][1]["id"])

    def test_missing_creation_date_configuration_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "creationDates"):
            self.build_fixture(None)

    def test_non_mapping_creation_dates_are_rejected(self) -> None:
        for value in ([], "2026-10-09", 42):
            with self.subTest(value=value), self.assertRaisesRegex(ValueError, "creationDates"):
                self.build_fixture(value)

    def test_missing_resource_creation_date_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "Missing explicit catalog creation date"):
            self.build_fixture({"https://example.com/old": "2026-08-30"})

    def test_invalid_resource_creation_dates_are_rejected(self) -> None:
        for value in (None, 20261009, "20261009", "2026-10-09T00:00:00", "2026-02-30", "2026-1-9", "invalid"):
            with self.subTest(value=value), self.assertRaisesRegex(ValueError, "Invalid catalog creation date"):
                self.build_fixture({"https://example.com/old": "2026-08-30", "https://example.com/new": value})

    def test_contributor_entries_have_explicit_creation_dates(self) -> None:
        config = json.loads((ROOT / "catalog/resource-index.config.json").read_text(encoding="utf-8"))
        urls = {"https://ultimatebigboard.com/nba/2027/methodology/", "https://www.realtimesportsapi.com/apis/nba"}
        added = [r for r in self.index["resources"] if r["source"]["canonicalUrl"] in urls]
        self.assertEqual(len(added), 2)
        for resource in added:
            self.assertEqual(resource["dates"]["createdAt"], "2026-10-09")
            self.assertEqual(resource["dates"]["createdAt"], config["creationDates"][resource["source"]["canonicalUrl"]])


if __name__ == "__main__":
    unittest.main()
