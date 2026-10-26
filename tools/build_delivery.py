#!/usr/bin/env python3
# Copyright (C) 2026 KARMENLOOP Official Team
# SPDX-License-Identifier: AGPL-3.0-only
"""Build a complete offline delivery, including source, docs and a reviewed seed."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import sys
import tempfile
import zipfile

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_release import build, ROOT
from check_delivery import check, inventory

BUILD_ID = "0.4.2-bundle.1"
TOP_FILES = ("SKILL.md", "SKILL.en.md", "README.md", "README.zh-CN.md", "START-HERE.md", "开始使用.md", "LICENSE", "NOTICE", "TEAM.md", "TEAM.zh-CN.md", "CONTRIBUTING.md", "CHANGELOG.md", "publication.json", ".gitignore")
FOLDERS = ("references", "scripts", "tools", "tests", "docs", "templates", ".github", "examples/experience-seed")


def build_delivery(output):
    output.mkdir(parents=True, exist_ok=True)
    archive = output / ("personal-agent-growth-delivery-" + BUILD_ID + ".zip")
    if archive.exists():
        raise FileExistsError("Choose a fresh output directory; prior bundles are retained")
    with tempfile.TemporaryDirectory(prefix="growth-delivery-") as temporary:
        staging = Path(temporary) / ("personal-agent-growth-delivery-" + BUILD_ID)
        staging.mkdir()
        paths = [ROOT / name for name in TOP_FILES]
        for folder in FOLDERS:
            paths.extend(p for p in (ROOT / folder).rglob("*") if p.is_file())
        for source in sorted(paths):
            relative = source.relative_to(ROOT)
            if "__pycache__" in relative.parts or source.name == ".DS_Store" or source.suffix == ".pyc":
                continue
            if source.is_symlink() or not source.is_file():
                raise ValueError("Expected regular source file: " + str(relative))
            target = staging / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, target)
        if not (staging / "examples/experience-seed/index.json").is_file():
            raise ValueError("Reviewed portable experience seed missing")
        build(staging / "downloads")
        manifest = {"schema": 1, "build_id": BUILD_ID, "skill_version": "0.4.2",
                    "status": "release_distribution", "files": inventory(staging)}
        (staging / "DELIVERY-MANIFEST.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        result = check(staging)
        with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as bundle:
            for path in sorted(staging.rglob("*")):
                if path.is_file():
                    info = zipfile.ZipInfo(path.relative_to(staging.parent).as_posix(), date_time=(2026, 10, 23, 0, 0, 0))
                    info.compress_type = zipfile.ZIP_DEFLATED
                    info.create_system = 3
                    info.external_attr = 0o100644 << 16
                    bundle.writestr(info, path.read_bytes())
    sha = hashlib.sha256(archive.read_bytes()).hexdigest()
    (output / "SHA256SUMS.txt").write_text(sha + "  " + archive.name + "\n", encoding="utf-8")
    return {**result, "archive": str(archive), "sha256": sha, "bytes": archive.stat().st_size}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(build_delivery(args.output), indent=2))
