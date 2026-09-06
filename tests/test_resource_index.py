from __future__ import annotations

import json
import importlib.util
import subprocess
import sys
import unittest
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


if __name__ == "__main__":
    unittest.main()
