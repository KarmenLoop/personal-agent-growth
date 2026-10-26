#!/usr/bin/env python3
# Copyright (C) 2026 KARMENLOOP Official Team
# SPDX-License-Identifier: AGPL-3.0-only
"""Build the installable skill and its consistency manifest using stdlib."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import posixpath
from urllib.parse import quote
import zipfile

ROOT = Path(__file__).resolve().parents[1]
NAME = "personal-agent-growth"
FILES = (
    "SKILL.md",
    "SKILL.en.md",
    "references/task-record.md",
    "references/learning-and-contact.md",
    "references/autonomous-continuation.md",
    "references/shared-memory.md",
    "references/recursive-improvement.md",
    "scripts/compare_trials.py",
    "scripts/verify_handoff.py",
    "scripts/host.py",
    "scripts/host_support.py",
    "LICENSE",
    "NOTICE",
    "README.md",
    "README.zh-CN.md",
    "docs/tutorial.en.md",
    "docs/tutorial.zh-CN.md",
    "docs/markdown-learning.en.md",
    "docs/markdown-learning.zh-CN.md",
    "templates/learning/README.md",
)
FILES += tuple("references/" + name + ".en.md" for name in (
    "task-record", "learning-and-contact", "autonomous-continuation",
    "shared-memory", "recursive-improvement", "markdown-learning"))
FILES += ("references/markdown-learning.md",)
FILES += tuple("templates/learning/" + language + "/" + name + ".md"
               for language in ("en", "zh-CN")
               for name in ("daily", "weekly", "consolidation", "memory", "context",
                            "node", "summary", "project-experience", "experience",
                            "profile", "behavior", "tags", "preview", "index", "policy", "research"))


def package_text(name, version):
    """Keep runtime references local; bind omitted long-form docs to the release tag."""
    text = (ROOT / name).read_text(encoding="utf-8")
    lines = []
    fence = False
    def rewrite(match):
        target = match.group(1)
        if "://" in target or target.startswith(("#", "mailto:")):
            return match.group(0)
        file, sep, fragment = target.partition("#")
        relative = posixpath.normpath(posixpath.join(posixpath.dirname(name), file))
        if relative in FILES:
            return match.group(0)
        if relative.startswith("../") or not (ROOT / relative).exists():
            raise ValueError("Unresolved package document link: " + name + " -> " + target)
        url = "https://github.com/KarmenLoop/personal-agent-growth/blob/v" + version + "/" + quote(relative)
        return "](" + url + ("#" + fragment if sep else "") + ")"
    for line in text.splitlines(keepends=True):
        if line.lstrip().startswith("```"):
            fence = not fence
        lines.append(line if fence else re.sub(r"\]\(([^)]+)\)", rewrite, line))
    return "".join(lines).encode("utf-8")


def build(output):
    version = re.search(
        r'^  version: "([0-9]+\.[0-9]+\.[0-9]+)"$',
        (ROOT / "SKILL.md").read_text(encoding="utf-8"),
        re.MULTILINE,
    ).group(1)
    output.mkdir(parents=True, exist_ok=True)
    archive_path = output / f"{NAME}-{version}.zip"
    files = {}
    with zipfile.ZipFile(archive_path, "w", zipfile.ZIP_DEFLATED) as archive:
        for name in sorted(FILES):
            data = package_text(name, version) if name.endswith(".md") else (ROOT / name).read_bytes()
            files[name] = {
                "bytes": len(data),
                "sha256": hashlib.sha256(data).hexdigest(),
            }
            info = zipfile.ZipInfo(f"{NAME}/{name}", date_time=(2026, 10, 21, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            archive.writestr(info, data)
    manifest = {
        "name": NAME,
        "declared_version": version,
        "files": files,
        "content_hash_rule": "SHA256 of sorted compact JSON for the files object",
        "content_sha256": hashlib.sha256(
            json.dumps(files, sort_keys=True, separators=(",", ":")).encode("utf-8")
        ).hexdigest(),
        "archive": {
            "name": archive_path.name,
            "sha256": hashlib.sha256(archive_path.read_bytes()).hexdigest(),
        },
    }
    manifest_path = output / "manifest.json"
    with manifest_path.open("w", encoding="utf-8", newline="\n") as stream:
        stream.write(json.dumps(manifest, indent=2) + "\n")
    return archive_path, manifest_path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("dist"))
    args = parser.parse_args()
    archive, manifest = build(args.output)
    print(json.dumps({"archive": str(archive), "manifest": str(manifest)}))


if __name__ == "__main__":
    main()
