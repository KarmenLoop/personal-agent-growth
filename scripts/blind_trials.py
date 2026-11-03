#!/usr/bin/env python3
# Copyright (C) 2026 KARMENLOOP Official Team
# SPDX-License-Identifier: AGPL-3.0-only
"""Freeze strategies before releasing targets and generate a blocked run order.

Markdown is the record. This helper does not start an Agent, hide files from a
privileged executor, certify novelty, or accept a candidate's own quality claim.
"""
import argparse
import json
from pathlib import Path
import random
import sys

import capability_ledger as store


def inventory(root, relative):
    folder = store.local(root, relative)
    store.require(folder.is_dir(), "Missing strategy or target directory")
    result, total = {}, 0
    for path in sorted(folder.rglob("*")):
        store.require(not path.is_symlink(), "Blind snapshot contains a symlink")
        if not path.is_file():
            continue
        size = path.stat().st_size
        total += size
        store.require(len(result) < 2048 and size <= 32 * 1024 * 1024 and total <= 64 * 1024 * 1024,
                      "Blind snapshot exceeds bounded inventory")
        result[path.relative_to(folder).as_posix()] = store.sha(path.read_bytes())
    store.require(bool(result), "Empty blind snapshot")
    return result


def write_new(path, metadata, body):
    data = store.encode(metadata, body)
    store.require(len(data) <= 1024 * 1024, "Blind record exceeds readable size")
    store.publish(path, data)
    return {"path": str(path), "sha256": store.sha(data), "record": metadata}


def folder_for(root, run_id):
    store.identifier(run_id)
    return store.local(root, "blind-trials/" + run_id)


def freeze(root, plan_md):
    root = store.root_path(root)
    plan, body, digest = store.read_md(Path(plan_md))
    keys = {"id", "type", "arms", "model_config", "repetitions", "seed", "deadline_seconds", "metric"}
    store.require(set(plan) == keys and plan["type"] == "blind-plan", "Invalid blind plan fields")
    folder = folder_for(root, plan["id"])
    arms = plan["arms"]
    store.require(isinstance(arms, dict) and 2 <= len(arms) <= 8 and "baseline" in arms, "Invalid blind arms")
    for arm in arms:
        store.identifier(arm)
    store.require(len(set(arms.values())) == len(arms), "Arms need distinct strategy roots")
    config = plan["model_config"]
    store.require(isinstance(config, dict) and config.get("model") and config.get("training") is False,
                  "Frozen visible model configuration required")
    store.require(type(plan["repetitions"]) is int and 1 <= plan["repetitions"] <= 30, "Invalid repetitions")
    store.require(type(plan["seed"]) is int and 0 <= plan["seed"] < 2**63, "Invalid seed")
    store.require(store.number(plan["deadline_seconds"]) and 0 < plan["deadline_seconds"] <= 86400,
                  "Invalid task deadline")
    store.require(plan["metric"] in ("native_tokens", "complete_task_seconds"), "Unsupported trial metric")
    store.require(plan["metric"] != "complete_task_seconds" or plan["repetitions"] >= 3,
                  "Timing comparison needs at least three repetitions")
    snapshots = {arm: inventory(root, relative) for arm, relative in arms.items()}
    folder.mkdir(parents=True, exist_ok=True)
    with store.writer(folder):
        return write_new(folder / "frozen.md", {"id": plan["id"], "type": "blind-freeze",
                         "created_at": store.clock().isoformat(), "plan_sha256": digest,
                         "plan": plan, "strategies": snapshots,
                         "scope": "Content freeze before declared target release, not proof of OS isolation or task novelty"}, body)


def read_freeze(root, run_id):
    folder = folder_for(root, run_id)
    item, _, digest = store.read_md(folder / "frozen.md")
    store.require(item.get("type") == "blind-freeze" and item.get("id") == run_id, "Wrong blind experiment")
    for arm, relative in item["plan"]["arms"].items():
        store.require(inventory(root, relative) == item["strategies"][arm], "Frozen strategy changed: " + arm)
    return folder, item, digest


def release(root, run_id, task_md):
    root = store.root_path(root)
    folder, frozen, freeze_hash = read_freeze(root, run_id)
    task, body, task_hash = store.read_md(Path(task_md))
    keys = {"id", "type", "domain", "role", "public_dir", "evaluator", "provenance"}
    store.require(set(task) == keys and task["type"] == "blind-task", "Invalid target fields")
    store.identifier(task["id"]); store.text(task["domain"], "domain", 200)
    store.require(task["role"] in ("holdout", "development", "regression"), "Invalid exposure role")
    public = inventory(root, task["public_dir"])
    store.artifacts(root, [task["evaluator"], task["provenance"]], True)
    evaluator = store.local(root, task["evaluator"]["path"])
    public_root = store.local(root, task["public_dir"])
    store.require(not evaluator.is_relative_to(public_root) and task["evaluator"]["sha256"] not in public.values(),
                  "Evaluator is exposed inside target workspace")
    tasks = folder / "tasks"; tasks.mkdir(exist_ok=True)
    with store.writer(folder):
        read_freeze(root, run_id)
        return write_new(tasks / (task["id"] + ".md"), {"id": task["id"], "type": "released-blind-task",
                         "released_at": store.clock().isoformat(), "frozen_sha256": freeze_hash,
                         "task_sha256": task_hash, "task": task, "public_inventory": public,
                         "novelty_status": "Host-declared; no hidden-answer or prior-exposure certification"}, body)


def schedule(root, run_id):
    root = store.root_path(root)
    folder, frozen, freeze_hash = read_freeze(root, run_id)
    tasks_dir = folder / "tasks"
    tasks = []
    if tasks_dir.exists():
        files = sorted(tasks_dir.glob("*.md"))
        store.require(len(files) <= 100, "Too many blind targets")
        for file in files:
            record, _, _ = store.read_md(file)
            store.require(record.get("frozen_sha256") == freeze_hash, "Task bound to another freeze")
            task = record["task"]
            store.require(inventory(root, task["public_dir"]) == record["public_inventory"], "Released target changed")
            store.artifacts(root, [task["evaluator"], task["provenance"]], True)
            tasks.append(task)
    rng = random.Random(frozen["plan"]["seed"])
    blocks = [(task, repeat) for task in tasks for repeat in range(1, frozen["plan"]["repetitions"] + 1)]
    rng.shuffle(blocks)
    runs = []
    for task, repeat in blocks:
        arms = sorted(frozen["plan"]["arms"]); rng.shuffle(arms)
        for arm in arms:
            runs.append({"id": f'{task["id"]}-r{repeat}-{arm}', "task_id": task["id"],
                         "domain": task["domain"], "role": task["role"], "replicate": repeat, "arm": arm,
                         "public_dir": task["public_dir"]})
    return {"id": run_id, "frozen_sha256": freeze_hash, "model_config": frozen["plan"]["model_config"],
            "runs": runs, "scope": "Seeded order within task/repetition blocks; not Agent execution or evidence of improvement"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("freeze", "release", "schedule"))
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--id")
    parser.add_argument("--file", type=Path)
    args = parser.parse_args()
    try:
        if args.action == "freeze": result = freeze(args.root, args.file)
        elif args.action == "release": result = release(args.root, args.id, args.file)
        else: result = schedule(args.root, args.id)
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(json.dumps({"status": "error", "error": str(error)})); return 2
    print(json.dumps(result, ensure_ascii=False)); return 0


if __name__ == "__main__": sys.exit(main())
