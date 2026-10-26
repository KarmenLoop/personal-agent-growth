#!/usr/bin/env python3
# Copyright (C) 2026 KARMENLOOP Official Team
# SPDX-License-Identifier: AGPL-3.0-only
"""Verify exact delivery contents against the included consistency manifest."""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath


def inventory(root, exclude_manifest=True):
    files = {}
    for path in sorted(root.rglob("*")):
        if path.is_symlink():
            raise ValueError("Delivery contains a symlink")
        if path.is_file() and not (exclude_manifest and path.relative_to(root).as_posix() == "DELIVERY-MANIFEST.json"):
            data = path.read_bytes()
            files[path.relative_to(root).as_posix()] = {"bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}
    return files


def check(root):
    if root.is_symlink() or (root / "DELIVERY-MANIFEST.json").is_symlink():
        raise ValueError("Delivery root or manifest is a symlink")
    manifest = json.loads((root / "DELIVERY-MANIFEST.json").read_text(encoding="utf-8"))
    for name in manifest["files"]:
        if not name or "\\" in name or ":" in name or PurePosixPath(name).is_absolute() or any(p in ("", ".", "..") for p in name.split("/")):
            raise ValueError("Unsafe manifest path")
    actual = inventory(root)
    if actual != manifest["files"]:
        raise ValueError("Delivery files differ from the manifest")
    return {"status": "PASS", "files": len(actual), "build_id": manifest["build_id"],
            "scope": "Content consistency only; not publisher authentication or Agent acceptance"}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    try:
        print(json.dumps(check(args.root), indent=2))
    except (OSError, ValueError, KeyError) as error:
        print(json.dumps({"status": "REJECT", "error": str(error)}))
        raise SystemExit(1)
