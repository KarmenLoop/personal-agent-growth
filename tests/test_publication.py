"""Publication gates reject broken reading paths and stale rendered artifacts."""
import importlib.util
import hashlib
import json
from pathlib import Path
import shutil
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('publication_check', ROOT / 'scripts/check_publication.py')
publication = importlib.util.module_from_spec(spec)
spec.loader.exec_module(publication)


class PublicationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / 'publication'
        shutil.copytree(ROOT, self.root, ignore=shutil.ignore_patterns('.git', 'dist', '__pycache__', '.venv'))

    def test_broken_anchor_is_not_hidden_by_existing_file(self):
        with (self.root / 'README.md').open('a', encoding='utf-8') as out:
            out.write('\n[Broken section](docs/architecture.en.md#not-a-real-section)\n')
        result = publication.validate(self.root)
        self.assertTrue(any('Broken anchor' in e for e in result['errors']))

    def test_diagram_source_change_requires_new_render(self):
        with (self.root / 'docs/diagrams/system.en.mmd').open('a') as out:
            out.write('\n    Changed branch\n')
        self.assertTrue(any('Diagram render drift' in e for e in publication.validate(self.root)['errors']))

    def test_missing_translation_and_template_are_reported(self):
        (self.root / 'docs/architecture.zh-CN.md').unlink()
        (self.root / 'templates/learning/zh-CN/node.md').unlink()
        errors = publication.validate(self.root)['errors']
        self.assertTrue(any('Missing language counterpart' in e for e in errors))
        self.assertTrue(any('Template types differ' in e for e in errors))

    def test_published_diagram_requires_a_render_receipt(self):
        relative = 'docs/diagrams/unrendered.svg'
        data = (self.root / 'docs/diagrams/system.en.svg').read_bytes()
        (self.root / relative).write_bytes(data)
        manifest = self.root / 'publication.json'
        publication_data = json.loads(manifest.read_text())
        publication_data['media_files'][relative] = hashlib.sha256(data).hexdigest()
        manifest.write_text(json.dumps(publication_data))
        errors = publication.validate(self.root)['errors']
        self.assertTrue(any('Diagram inventory differs' in e for e in errors))

    def test_duplicate_render_receipt_does_not_cover_another_diagram(self):
        manifest = self.root / 'docs/diagrams/render-manifest.json'
        render = json.loads(manifest.read_text())
        render['diagrams'][1] = dict(render['diagrams'][0])
        manifest.write_text(json.dumps(render))
        errors = publication.validate(self.root)['errors']
        self.assertTrue(any('Duplicate diagram render record' in e for e in errors))


if __name__ == '__main__':
    unittest.main()
