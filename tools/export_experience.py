#!/usr/bin/env python3
# Copyright (C) 2026 KARMENLOOP Official Team
# SPDX-License-Identifier: AGPL-3.0-only
"""Export reviewed lessons and portable derivatives without private raw traces.

This is a seed import, not another Agent trial or a copy of the source ledger.
Review exported text before distribution; schema projection is not redaction
of arbitrary prose supplied by an untrusted or unrelated library.
"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import compare_trials as gate

DOMAINS = ("offline-package-check", "meta:cross-domain-evidence")


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def export(source, output):
    before = gate.tree_hashes(source.parent, source.name)
    index = gate.load_library(source)
    selections = {domain: gate.select(source, domain) for domain in DOMAINS}
    gate.require(all(s["active"] for s in selections.values()), "Both source profiles are required")
    output.mkdir(parents=True, exist_ok=False)
    target = {"schema": 1, "revision": 1, "profiles": {}, "records": {}, "observations": {}}
    provenance = {"kind": "portable_seed_derivative", "source_revision": index["revision"],
                  "source_index_sha256": gate.file_hash(source, "index.json"),
                  "scope": "Reviewed lesson excerpts and profile derivatives; private raw Agent events are omitted. Import does not constitute new adoption or Agent acceptance.",
                  "profiles": {}}
    for domain, selection in selections.items():
        original = selection["active"]
        staging = output / "profile-staging"
        shutil.copytree(gate.local(source, original["path"]), staging)
        changes = []
        loader = staging / "scripts/context_loader.py"
        if loader.exists():
            text = loader.read_text(encoding="utf-8")
            old = "library=(a.library or Path(location['library'])).resolve()"
            gate.require(text.count(old) == 1, "Unexpected loader: review portability change")
            text = text.replace(old, "library=(a.library or (strategy / location['library'])).resolve()")
            text = text.replace(".read_text()", ".read_text(encoding='utf-8')")
            loader.write_text(text, encoding="utf-8")
            save(staging / "memory-location.json", {"library": "../..", "relative_to": "profile_directory"})
            changes = ["memory-location.json", "scripts/context_loader.py"]
        version = gate.digest(gate.canonical(gate.tree_hashes(output, "profile-staging")))
        relative = "versions/" + version
        (output / "versions").mkdir(exist_ok=True)
        staging.rename(output / relative)
        seed_id = "seed-" + original["experiment_id"]
        target["profiles"][domain] = {"path": relative, "sha256": version, "experiment_id": seed_id,
                                       "source": "imported_seed", "source_sha256": original["sha256"]}
        provenance["profiles"][domain] = {"source_sha256": original["sha256"],
                                           "export_sha256": version, "changed_files": changes}
        for entry in selection["experiences"]:
            original_card = gate.read_json(gate.local(source, entry["path"]))
            card = {"kind": "imported_lesson_excerpt", "adopted": None, "previous": None,
                    "source_adopted": original_card.get("adopted"), "source_card_sha256": entry["sha256"],
                    "generalization": original_card["generalization"],
                    "reflection": {"lessons": [{k: v for k, v in lesson.items() if k != "evidence"}
                                  for lesson in original_card.get("reflection", {}).get("lessons", [])]},
                    "evidence_scope": "Historical lessons; see the bundled trial reports. Raw source traces are not distributed and imported profiles need validation in their new host."}
            card_id = "seed-" + Path(entry["path"]).stem
            path = "records/" + card_id + ".json"
            save(output / path, card)
            target["records"][card_id] = {"domain": domain, "path": path,
                                          "sha256": gate.file_hash(output, path), "adopted": None, "eligible": []}
        for entry in selection["observations"]:
            original_observation = gate.read_json(gate.local(source, entry["path"]))
            observation = {k: original_observation[k] for k in ("lesson", "limitations", "next_probe")}
            observation.update(kind="imported_review_excerpt", domain=domain, active_sha256=version,
                               source_observation_sha256=entry["sha256"],
                               source_active_sha256=entry["active_sha256"],
                               raw_evidence_distributed=False)
            observation_id = "seed-" + original_observation["observation_id"]
            observation["observation_id"] = observation_id
            path = "observations/" + observation_id + ".json"
            save(output / path, observation)
            target["observations"][observation_id] = {"domain": domain, "path": path,
                "sha256": gate.file_hash(output, path), "active_sha256": version}
    save(output / "index.json", target)
    save(output / "export-provenance.json", provenance)
    for domain in DOMAINS:
        gate.select(output, domain)
    gate.require(before == gate.tree_hashes(source.parent, source.name), "Source library changed during export")
    return provenance


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--library", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    print(json.dumps(export(args.library.resolve(), args.output.absolute()), indent=2))
