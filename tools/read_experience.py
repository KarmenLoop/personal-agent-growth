#!/usr/bin/env python3
# Copyright (C) 2026 KARMENLOOP Official Team
# SPDX-License-Identifier: AGPL-3.0-only
"""Read the selected profile and indexed lessons; do not launch an Agent."""
import argparse
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import compare_trials as gate


def read(library, domain):
    selected = gate.select(library, domain)
    active = selected["active"]
    gate.require(active is not None, "No matching profile; use the coordinator skill for this task")
    profile = gate.local(library, active["path"])
    texts = {name: (profile / name).read_text(encoding="utf-8")
             for name in ("SKILL.md", "strategy.md") if (profile / name).is_file()}
    return {"library": str(library.resolve()), "selection": selected, "profile": str(profile.resolve()),
            "profile_text": texts,
            "records": [gate.read_json(gate.local(library, e["path"])) for e in selected["experiences"]],
            "observations": [gate.read_json(gate.local(library, e["path"])) for e in selected["observations"]],
            "path_mapping": "The historical strategy/ prefix denotes this selected profile. Resolve task inputs against the new task directory. A seed has no private task state to resume.",
            "scope": "Actual file read and hash verification; no model execution, scheduling or performance claim"}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--library", type=Path, required=True)
    parser.add_argument("--domain", required=True)
    args = parser.parse_args()
    print(json.dumps(read(args.library.resolve(), args.domain), ensure_ascii=False, indent=2))
