#!/usr/bin/env python3
# Copyright (C) 2026 KARMENLOOP Official Team
# SPDX-License-Identifier: AGPL-3.0-only
"""Install a verified delivery into a fresh root; remove only unchanged skill files.

Discovery links are managed explicitly by the user. Memory, task records and
the distribution copy are always retained on uninstall.
"""
import argparse
import json
from pathlib import Path
import shutil
import sys
import zipfile

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
from check_delivery import check, inventory
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from verify_handoff import verify


def install(bundle, root):
    check(bundle)
    manifest = json.loads((bundle / "downloads/manifest.json").read_text(encoding="utf-8"))
    archive = bundle / "downloads" / manifest["archive"]["name"]
    result, code = verify(archive, bundle / "downloads/manifest.json")
    if code != 0:
        raise ValueError("Inner skill archive failed verification: " + result["status"])
    if root.is_symlink() or root.exists():
        raise FileExistsError("Install root already exists; choose a new root and preserve existing memory")
    if root.resolve().is_relative_to(bundle.resolve()):
        raise ValueError("Install outside the delivery directory")
    root.mkdir(parents=True, exist_ok=False)
    shutil.copytree(bundle, root / "distribution")
    skills = root / "skills"
    skills.mkdir()
    with zipfile.ZipFile(archive) as package:
        package.extractall(skills)  # verify() checked the exact safe member names above.
    shutil.copytree(bundle / "examples/experience-seed", root / "experience")
    (root / "tasks").mkdir()
    record = {"schema": 1, "status": "installed", "skill_version": manifest["declared_version"],
              "skill_files": inventory(skills / "personal-agent-growth", exclude_manifest=False),
              "memory": "experience", "tasks": "tasks", "discovery_created": False}
    (root / "installation.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    return {"status": "INSTALLED", "root": str(root.resolve()), "skill": str(skills / "personal-agent-growth"),
            "memory": str(root / "experience"), "discovery_created": False}


def uninstall(root):
    if root.is_symlink() or (root / "installation.json").is_symlink():
        raise ValueError("Unexpected installation symlink")
    path = root / "installation.json"
    record = json.loads(path.read_text(encoding="utf-8"))
    if record["status"] != "installed":
        raise ValueError("Installation is not active")
    skill = root / "skills/personal-agent-growth"
    if (root / "skills").is_symlink() or skill.is_symlink() or inventory(skill, exclude_manifest=False) != record["skill_files"]:
        raise ValueError("Skill changed; preserve and review it before removal")
    shutil.rmtree(skill)
    record["status"] = "removed_memory_retained"
    path.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    return {"status": record["status"], "retained": ["experience", "tasks", "distribution", "installation.json"]}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["install", "uninstall"])
    parser.add_argument("--root", required=True, type=Path)
    parser.add_argument("--bundle", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    try:
        result = install(args.bundle, args.root) if args.action == "install" else uninstall(args.root)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except (OSError, ValueError, KeyError) as error:
        print(json.dumps({"status": "STOPPED", "error": str(error)}, ensure_ascii=False))
        raise SystemExit(1)
