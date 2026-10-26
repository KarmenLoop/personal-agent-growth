# Copyright (C) 2026 KARMENLOOP Official Team
# SPDX-License-Identifier: AGPL-3.0-only
"""Real filesystem checks for distribution safety; these are not Agent trials."""
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
import zipfile

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from build_delivery import build_delivery
from check_delivery import check
from local_install import install, uninstall
from read_experience import read


class DeliveryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.storage = tempfile.TemporaryDirectory(prefix="growth-delivery-tests-")
        cls.root = Path(cls.storage.name)
        result = build_delivery(cls.root / "build")
        cls.archive = Path(result["archive"])
        with zipfile.ZipFile(cls.archive) as archive:
            archive.extractall(cls.root / "unpacked")
        cls.bundle = next((cls.root / "unpacked").iterdir())

    @classmethod
    def tearDownClass(cls):
        cls.storage.cleanup()

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=self.root)
        self.addCleanup(self.temp.cleanup)
        self.area = Path(self.temp.name)

    def test_reproducible_archive(self):
        again = build_delivery(self.area / "build")
        self.assertEqual(self.archive.read_bytes(), Path(again["archive"]).read_bytes())

    def test_existing_root_is_preserved(self):
        root = self.area / "existing"
        root.mkdir()
        (root / "keep.txt").write_text("existing memory")
        with self.assertRaises(FileExistsError):
            install(self.bundle, root)
        self.assertEqual(list(root.iterdir()), [root / "keep.txt"])
        self.assertEqual((root / "keep.txt").read_text(), "existing memory")

    def test_tampered_delivery_never_installs(self):
        bundle = self.area / "tampered"
        shutil.copytree(self.bundle, bundle)
        (bundle / "SKILL.md").write_text("changed")
        root = self.area / "target"
        with self.assertRaisesRegex(ValueError, "differ"):
            install(bundle, root)
        self.assertFalse(root.exists())

    def test_uninstall_retains_memory_and_rejects_extra_file(self):
        root = self.area / "Knowledge 中文 & space"
        install(self.bundle, root)
        (root / "tasks/user-note.txt").write_text("preserve")
        before = (root / "experience/index.json").read_bytes()
        extra = root / "skills/personal-agent-growth/DELIVERY-MANIFEST.json"
        extra.write_text("user work")
        with self.assertRaisesRegex(ValueError, "Skill changed"):
            uninstall(root)
        self.assertTrue(extra.exists())
        extra.unlink()
        uninstall(root)
        self.assertFalse((root / "skills/personal-agent-growth").exists())
        self.assertEqual(before, (root / "experience/index.json").read_bytes())
        self.assertEqual((root / "tasks/user-note.txt").read_text(), "preserve")

    def test_moved_library_and_tampered_profile(self):
        library = self.area / "seed"
        shutil.copytree(self.bundle / "examples/experience-seed", library)
        moved = self.area / "moved 中文"
        library.rename(moved)
        result = read(moved, "meta:cross-domain-evidence")
        self.assertEqual(result["selection"]["revision"], 1)
        self.assertTrue(result["records"][0]["reflection"]["lessons"])
        # Windows may resolve the runner's 8.3 temp path to its long name.
        # Compare the actual indexed directory, not a textual path prefix.
        expected_profile = moved / result["selection"]["active"]["path"]
        self.assertTrue(Path(result["profile"]).samefile(expected_profile))
        (Path(result["profile"]) / "SKILL.md").write_text("tampered")
        with self.assertRaisesRegex(ValueError, "snapshot has changed"):
            read(moved, "meta:cross-domain-evidence")

    def test_symlink_and_extra_content_are_rejected(self):
        bundle = self.area / "extra"
        shutil.copytree(self.bundle, bundle)
        (bundle / "unexpected.txt").write_text("unexpected")
        with self.assertRaisesRegex(ValueError, "differ"):
            check(bundle)
        (bundle / "unexpected.txt").unlink()
        if sys.platform != "win32":
            (bundle / "link").symlink_to(bundle / "LICENSE")
            with self.assertRaisesRegex(ValueError, "symlink"):
                check(bundle)


if __name__ == "__main__":
    unittest.main()
