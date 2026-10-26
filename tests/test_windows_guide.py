"""Guide adaptation checks; actual PowerShell behavior stays in Windows CI."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('windows_guide', ROOT / 'tools/check_windows_install.py')
guide = importlib.util.module_from_spec(spec)
spec.loader.exec_module(guide)


class WindowsGuideTests(unittest.TestCase):
    def test_future_release_uses_its_manifest_and_preserves_nontransport_commands(self):
        version = '9.8.7'
        current = json.loads((ROOT / 'publication.json').read_text(encoding="utf-8"))['version']
        en = (ROOT / 'docs/install.md').read_text(encoding="utf-8").replace(current, version)
        zh = (ROOT / 'docs/install.zh-CN.md').read_text(encoding="utf-8").replace(current, version)
        network, uninstall = guide.prepare_guides(en, zh, version)
        with tempfile.TemporaryDirectory() as temporary:
            local = Path(temporary)
            name = 'personal-agent-growth-' + version + '.zip'
            (local / 'manifest.json').write_text(json.dumps({'declared_version': version, 'archive': {'name': name}}))
            adapted, remove = guide.prepare_guides(en, zh, version, local)
            self.assertEqual(remove, uninstall)
            self.assertNotIn('Invoke-WebRequest', adapted)
            self.assertIn(str((local / name).resolve()).replace("'", "''"), adapted)
            net = [line for line in network.splitlines() if 'Invoke-WebRequest' not in line]
            saved = [line for line in adapted.splitlines() if 'Copy-Item' not in line]
            self.assertEqual(saved, net)
            self.assertIn("downloads\\" + version, adapted)

    def test_old_manifest_or_mismatched_language_cannot_substitute_another_release(self):
        version = json.loads((ROOT / 'publication.json').read_text(encoding="utf-8"))['version']
        en = (ROOT / 'docs/install.md').read_text(encoding="utf-8")
        zh = (ROOT / 'docs/install.zh-CN.md').read_text(encoding="utf-8")
        with tempfile.TemporaryDirectory() as temporary:
            local = Path(temporary)
            (local / 'manifest.json').write_text(json.dumps({'declared_version': '0.0.1', 'archive': {'name': 'personal-agent-growth-0.0.1.zip'}}))
            with self.assertRaises(ValueError):
                guide.prepare_guides(en, zh, version, local)
        with self.assertRaises(ValueError):
            guide.prepare_guides(en, zh.replace('downloads\\' + version, 'downloads\\0.0.1'), version)
