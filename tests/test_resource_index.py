from __future__ import annotations

import json
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


if __name__ == "__main__":
    unittest.main()
