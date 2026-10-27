#!/usr/bin/env python3
"""Validate bilingual docs, local links/anchors, templates, and rendered media."""
import hashlib
import json
from pathlib import Path
import re
import sys
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]


def prose(text):
    lines = []
    fenced = False
    for line in text.splitlines():
        if line.lstrip().startswith(("```", "~~~")):
            fenced = not fenced
            lines.append("")
        else:
            lines.append("" if fenced else line)
    return "\n".join(lines)


def anchors(text):
    found = set(re.findall(r'<a\s+(?:id|name)=["\']([^"\']+)', text))
    counts = {}
    for title in re.findall(r'^#{1,6}\s+(.+?)\s*#*$', prose(text), re.M):
        title = re.sub(r'\[([^]]+)\]\([^)]*\)', r'\1', title)
        slug = re.sub(r'[^\w\- ]', '', title.lower()).replace(' ', '-')
        number = counts.get(slug, 0)
        counts[slug] = number + 1
        found.add(slug + ('-' + str(number) if number else ''))
    return found


def validate(root=ROOT):
    data = json.loads((root / 'publication.json').read_text(encoding='utf-8'))
    errors = []
    paths = set(root.glob('*.md'))
    for folder in ('docs', 'references', 'templates'):
        paths.update((root / folder).rglob('*.md'))
    link_count = 0
    for path in sorted(paths):
        text = path.read_text(encoding='utf-8')
        relative = path.relative_to(root).as_posix()
        if re.search(r'^(<<<<<<< |=======\s*$|>>>>>>> )', text, re.M):
            errors.append('Merge marker: ' + relative)
        if relative in data['documents'] and data['version'] not in text:
            errors.append('Missing version: ' + relative)
        for raw in re.findall(r'\]\(([^)\n]+)\)', prose(text)):
            link = raw.strip().strip('<>')
            if urlsplit(link).scheme:
                continue
            parsed = urlsplit(link)
            target = (path.parent / unquote(parsed.path)).resolve() if parsed.path else path
            link_count += 1
            if not target.is_relative_to(root.resolve()) or not target.exists():
                errors.append('Broken local link: ' + relative + ' -> ' + link)
            elif parsed.fragment and target.suffix == '.md':
                if unquote(parsed.fragment) not in anchors(target.read_text(encoding='utf-8')):
                    errors.append('Broken anchor: ' + relative + ' -> ' + link)
    for name in data['documents']:
        if not (root / name).is_file():
            errors.append('Missing document: ' + name)
    for kind in ('media_files', 'source_files'):
        for name, expected in data[kind].items():
            path = root / name
            if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != expected:
                errors.append('Identity drift: ' + name)
    for english, chinese in data['language_pairs']:
        for name in (english, chinese):
            if not (root / name).is_file():
                errors.append('Missing language counterpart: ' + name)
    kinds = set(data['template_types'])
    for language in ('en', 'zh-CN'):
        folder = root / 'templates/learning' / language
        if {p.stem for p in folder.glob('*.md')} != kinds:
            errors.append('Template types differ: ' + language)
        for kind in kinds:
            path = folder / (kind + '.md')
            if not path.exists():
                continue
            text = path.read_text(encoding='utf-8')
            front = re.match(r'^---\n(.*?)\n---', text, re.S)
            if not front or any(not re.search(r'^' + key + r':', front[1], re.M)
                                for key in ('id','type','project','tags','status','created','updated','sources','revision','template')):
                errors.append('Incomplete template metadata: ' + str(path.relative_to(root)))
            if '\ntemplate: true\n' not in text or not re.search(r'^## ', text, re.M):
                errors.append('Invalid blank template: ' + str(path.relative_to(root)))
    render = json.loads((root / 'docs/diagrams/render-manifest.json').read_text(encoding='utf-8'))
    outputs = [item['output'] for item in render['diagrams']]
    expected = {Path(name).name for name in data['media_files']
                if name.startswith('docs/diagrams/') and name.endswith('.svg')}
    actual = {path.name for path in (root / 'docs/diagrams').glob('*.svg')}
    if not expected or set(outputs) != expected or actual != expected:
        errors.append('Diagram inventory differs between files, publication, and render receipts')
    if len(outputs) != len(set(outputs)):
        errors.append('Duplicate diagram render record')
    for item in render['diagrams']:
        for field, hashfield in [('source', 'source_sha256'), ('output', 'output_sha256')]:
            p = root / 'docs/diagrams' / item[field]
            if not p.is_file() or hashlib.sha256(p.read_bytes()).hexdigest() != item[hashfield]:
                errors.append('Diagram render drift: ' + item[field])
        if item['labels'] <= 0 or item['width'] <= 0 or item['height'] <= 0:
            errors.append('Empty rendered diagram: ' + item['output'])
        if '&amp;quot;' in (root / 'docs/diagrams' / item['output']).read_text(encoding='utf-8'):
            errors.append('Escaped quote label in diagram: ' + item['output'])
    for name in data['documents'] + list(data['media_files']):
        if ' ' in name:
            errors.append('Space in publication filename: ' + name)
    return {'ok': not errors, 'version': data['version'], 'documents_checked': len(paths),
            'local_links_checked': link_count, 'language_pairs': len(data['language_pairs']),
            'templates': len(kinds) * 2, 'rendered_diagrams': len(render['diagrams']),
            'errors': errors, 'scope': 'Documentation, source/media identity, templates and render receipts; no new Agent behavior claim'}


if __name__ == '__main__':
    result = validate()
    print(json.dumps(result, indent=2, ensure_ascii=False))
    sys.exit(not result['ok'])
