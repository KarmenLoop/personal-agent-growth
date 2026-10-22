#!/usr/bin/env python3
# Copyright (C) 2026 KARMENLOOP Official Team
# SPDX-License-Identifier: AGPL-3.0-only
"""Build the installable skill and its consistency manifest using stdlib."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import zipfile

ROOT = Path(__file__).resolve().parents[1]
NAME = "personal-agent-growth"
FILES = (
    "SKILL.md",
    "references/task-record.md",
    "references/learning-and-contact.md",
    "references/autonomous-continuation.md",
    "references/shared-memory.md",
    "scripts/verify_handoff.py",
    "LICENSE",
    "NOTICE",
    "README.md",
    "README.zh-CN.md",
    "docs/tutorial.en.md",
    "docs/tutorial.zh-CN.md",
    "docs/images/workflow-v0.3.3.svg",
)


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
            data = (ROOT / name).read_bytes()
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
