# Copyright (C) 2026 KARMENLOOP Official Team
# SPDX-License-Identifier: AGPL-3.0-only
"""Exercise the real CLI with independently constructed, controlled archives."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import warnings
import zipfile

ROOT = Path(__file__).resolve().parents[1]
CHECKER = ROOT / "scripts" / "verify_handoff.py"


def sha(data):
    return hashlib.sha256(data).hexdigest()


class HandoffTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.archive = self.root / "sample.zip"
        self.manifest = self.root / "manifest.json"
        self.files = {"SKILL.md": b"# Example\n", "references/check.md": b"Review\n"}
        self.write_zip(list(self.files.items()))
        records = {
            name: {"bytes": len(data), "sha256": sha(data)}
            for name, data in self.files.items()
        }
        self.data = {
            "name": "sample",
            "declared_version": "1.0.0",
            "files": records,
            "content_hash_rule": "SHA256 of sorted compact JSON for the files object",
            "content_sha256": sha(
                json.dumps(records, sort_keys=True, separators=(",", ":")).encode()
            ),
            "archive": {"name": self.archive.name, "sha256": sha(self.archive.read_bytes())},
        }
        self.write_manifest()

    def write_zip(self, entries):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning)
            with zipfile.ZipFile(self.archive, "w") as archive:
                for name, value in entries:
                    archive.writestr("sample/" + name, value)

    def write_manifest(self, refresh_archive=False):
        if refresh_archive:
            self.data["archive"]["sha256"] = sha(self.archive.read_bytes())
        self.manifest.write_text(json.dumps(self.data), encoding="utf-8")

    def run_check(self, expected):
        run = subprocess.run(
            [sys.executable, str(CHECKER), "--archive", str(self.archive),
             "--manifest", str(self.manifest)],
            capture_output=True, text=True, timeout=20,
        )
        self.assertEqual(run.returncode, expected, run.stdout + run.stderr)
        result = json.loads(run.stdout)
        self.assertEqual(result["status"], {0: "PASS", 1: "REJECT", 2: "INCOMPLETE"}[expected])
        self.assertFalse(result["publisher_authenticated"])
        return result

    def test_original_package(self):
        result = self.run_check(0)
        self.assertEqual(result["stage"], "completed_inspection")
        self.assertEqual(result["inputs"]["archive"]["sha256"], sha(self.archive.read_bytes()))
        self.assertTrue(all(check["passed"] for check in result["checks"]))

    def test_file_tampering_after_archive_hash_refresh(self):
        changed = dict(self.files, **{"SKILL.md": b"# Changed\n"})
        self.write_zip(list(changed.items()))
        self.write_manifest(refresh_archive=True)
        result = self.run_check(1)
        self.assertNotIn("archive_sha256", result["failed_checks"])
        self.assertTrue(any(name.endswith(":sha256") for name in result["failed_checks"]))

    def test_archive_identity_changed(self):
        self.write_zip(list(self.files.items()) + [("extra.md", b"Extra")])
        self.assertIn("archive_sha256", self.run_check(1)["failed_checks"])

    def test_extra_member(self):
        self.write_zip(list(self.files.items()) + [("extra.md", b"Extra")])
        self.write_manifest(refresh_archive=True)
        self.assertIn("exact_member_list", self.run_check(1)["failed_checks"])

    def test_missing_member(self):
        self.write_zip([("SKILL.md", self.files["SKILL.md"])])
        self.write_manifest(refresh_archive=True)
        self.assertIn("exact_member_list", self.run_check(1)["failed_checks"])

    def test_duplicate_member(self):
        self.write_zip(list(self.files.items()) + [("SKILL.md", self.files["SKILL.md"])])
        self.write_manifest(refresh_archive=True)
        self.assertIn("unique_members", self.run_check(1)["failed_checks"])

    def test_unsafe_member(self):
        self.write_zip(list(self.files.items()) + [("../escape.md", b"Escape")])
        self.write_manifest(refresh_archive=True)
        self.assertIn("safe_member_paths", self.run_check(1)["failed_checks"])
        self.assertFalse((self.root / "escape.md").exists())

    def test_archive_filename_mismatch(self):
        self.data["archive"]["name"] = "different.zip"
        self.write_manifest()
        self.assertIn("archive_name", self.run_check(1)["failed_checks"])

    def test_duplicate_manifest_key(self):
        self.manifest.write_text('{"name":"sample","name":"other"}', encoding="utf-8")
        self.assertEqual(self.run_check(2)["stage"], "validate_manifest")

    def test_inconsistent_manifest_file_map(self):
        self.data["files"]["SKILL.md"]["bytes"] += 1
        self.write_manifest()
        self.assertEqual(self.run_check(2)["stage"], "validate_manifest")

    def test_missing_input(self):
        self.archive.unlink()
        self.assertEqual(self.run_check(2)["stage"], "read_archive")

    def test_invalid_zip(self):
        self.archive.write_bytes(b"Not a ZIP archive")
        self.write_manifest(refresh_archive=True)
        self.assertIn("zip_structure_or_crc", self.run_check(1)["failed_checks"])

    def test_release_archive(self):
        output = self.root / "release"
        build = subprocess.run(
            [sys.executable, str(ROOT / "tools" / "build_release.py"), "--output", str(output)],
            capture_output=True, text=True, timeout=20,
        )
        self.assertEqual(build.returncode, 0, build.stderr)
        built = json.loads(build.stdout)
        self.archive = Path(built["archive"])
        self.manifest = Path(built["manifest"])
        self.run_check(0)
        with zipfile.ZipFile(self.archive) as archive:
            names = set(archive.namelist())
            self.assertIn("personal-agent-growth/LICENSE", names)
            self.assertIn("personal-agent-growth/NOTICE", names)
            self.assertEqual(len(names), 59)
            self.assertIn("personal-agent-growth/scripts/host.py", names)
            self.assertIn("personal-agent-growth/scripts/host_support.py", names)
            self.assertIn("personal-agent-growth/README.zh-CN.md", names)
            self.assertIn("personal-agent-growth/docs/tutorial.en.md", names)
            for language in ("en", "zh-CN"):
                for kind in ("daily", "weekly", "consolidation", "memory", "context", "node",
                             "summary", "project-experience", "experience", "profile", "behavior",
                             "tags", "preview", "index", "policy", "research"):
                    self.assertIn(f"personal-agent-growth/templates/learning/{language}/{kind}.md", names)
            self.assertIn("personal-agent-growth/scripts/compare_trials.py", names)
            self.assertIn("personal-agent-growth/references/markdown-learning.en.md", names)
            text = archive.read("personal-agent-growth/README.md").decode("utf-8")
            self.assertIn("https://github.com/KarmenLoop/personal-agent-growth/blob/v0.4.1/docs/architecture.en.md", text)
            self.assertNotIn("](docs/architecture.en.md)", text)


if __name__ == "__main__":
    unittest.main()
