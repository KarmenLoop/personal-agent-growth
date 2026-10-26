#!/usr/bin/env python3
# Copyright (C) 2026 KARMENLOOP Official Team
# SPDX-License-Identifier: AGPL-3.0-only
"""Freeze, compare and retain real-agent experiments; never launch or impersonate agents.

This is an evidence-consistency gate, not a security boundary or semantic judge.
The host must protect the evaluator and independently inspect the raw receipts.
"""
import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import re
import shutil
import statistics
import sys
from datetime import datetime, timezone

ARMS = ("baseline", "general", "domain")


def require(ok, message):
    if not ok:
        raise ValueError(message)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, allow_nan=False,
                      separators=(",", ":")).encode("utf-8")


def read_json(path):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            require(key not in result, "Duplicate JSON key: " + key)
            result[key] = value
        return result
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique)


def local(root, relative):
    require(isinstance(relative, str) and bool(relative), "Expected relative path")
    parts = relative.split("/")
    require(all(p not in ("", ".", "..") for p in parts)
            and "\\" not in relative and ":" not in relative,
            "Unsafe relative path: " + relative)
    path = root
    for part in parts:
        path = path / part
        require(not path.is_symlink(), "Symlink is not a frozen artifact: " + relative)
    require(path.resolve().is_relative_to(root.resolve()), "Path escapes experiment")
    return path


def file_hash(root, relative):
    path = local(root, relative)
    require(path.is_file() and path.stat().st_size > 0, "Missing or empty file: " + relative)
    return digest(path.read_bytes())


def tree_hashes(root, relative):
    folder = local(root, relative)
    require(folder.is_dir(), "Missing snapshot: " + relative)
    files = {}
    for path in sorted(folder.rglob("*")):
        require(not path.is_symlink(), "Snapshot contains a symlink")
        if path.is_file():
            files[path.relative_to(folder).as_posix()] = digest(path.read_bytes())
    require(bool(files), "Empty snapshot: " + relative)
    return files


def number(value):
    try:
        return type(value) in (int, float) and math.isfinite(value) and value >= 0
    except OverflowError:
        return False


def inventory(root):
    plan = read_json(root / "plan.json")
    for key in ("experiment_id", "task_id", "domain", "metric"):
        require(isinstance(plan.get(key), str) and bool(plan[key]), "Missing " + key)
    require(re.fullmatch(r"[a-zA-Z0-9][a-zA-Z0-9._-]{0,95}", plan["experiment_id"]),
            "Invalid experiment_id")
    model = plan.get("model_config")
    require(isinstance(model, dict) and model.get("training") is False
            and bool(model.get("model")), "Frozen, visible model configuration required")
    checks = plan.get("quality_checks")
    require(isinstance(checks, list) and checks and all(isinstance(x, str) and x for x in checks)
            and len(checks) == len(set(checks)), "Unique quality checks required")
    require(number(plan.get("min_relative_gain")) and 0 < plan["min_relative_gain"] <= 1,
            "min_relative_gain must be in (0, 1]")
    require(type(plan.get("samples")) is int and plan["samples"] >= 1, "Invalid samples")
    require(plan["metric"] != "wall_seconds" or plan["samples"] >= 3,
            "Timing comparisons require at least three samples")
    require(number(plan.get("max_candidate_cost")), "Candidate cost ceiling required")
    guards = plan.get("performance_guards", {})
    require(isinstance(guards, dict) and all(isinstance(k, str) and k and number(v)
            for k, v in guards.items()), "Invalid performance guards")
    require(not any("wall_seconds" in k for k in guards) or plan["samples"] >= 3,
            "Timing guards require at least three samples")
    layer = plan.get("layer", "task")
    require(layer in ("task", "harnessing"), "Unknown recursion layer")
    if layer == "harnessing":
        portfolio = plan.get("portfolio", [])
        require(isinstance(portfolio, list) and len(portfolio) >= 2 and
                all(isinstance(p, dict) and p.get("task_id") and p.get("domain") and
                    p.get("role") in ("development", "transfer", "regression") for p in portfolio),
                "Harnessing changes require a task portfolio")
        require(len({p["task_id"] for p in portfolio}) == len(portfolio) and
                {"transfer", "regression"}.issubset({p["role"] for p in portfolio}),
                "Portfolio needs distinct transfer and regression tasks")
        if plan.get("promotion") == "cross-domain":
            require(len({p["domain"] for p in portfolio}) >= 2,
                    "Cross-domain promotion needs at least two domains")
    inputs = plan.get("inputs")
    require(isinstance(inputs, list) and inputs and len(inputs) == len(set(inputs)),
            "Input files required")
    return {
        "plan_sha256": file_hash(root, "plan.json"),
        "inputs": {p: file_hash(root, p) for p in inputs},
        "evaluator": {plan["evaluator"]: file_hash(root, plan["evaluator"])},
        "proposals": {a: file_hash(root, "proposals/" + a + ".md") for a in ARMS[1:]},
        "snapshots": {a: tree_hashes(root, "arms/" + a) for a in ARMS},
    }


def write_new(path, value):
    with path.open("x", encoding="utf-8") as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2, allow_nan=False)
        stream.write("\n")


def freeze(root):
    require(not (root / "frozen.json").exists(), "Already frozen; start a new experiment")
    require(not (root / "evaluation.json").exists() and
            not any((root / "runs").glob("*/run.json")),
            "Cannot freeze after run records exist")
    value = {"schema": 1, "created_at": datetime.now(timezone.utc).isoformat(),
             "inventory": inventory(root)}
    write_new(root / "frozen.json", value)
    return {"frozen_sha256": digest((root / "frozen.json").read_bytes())}


def guard_medians(plan, row):
    """Keep whole-task resource dimensions separate instead of hiding regressions."""
    guards = plan.get("performance_guards", {})
    samples = row.get("guard_samples", {})
    require(isinstance(samples, dict) and set(samples) == set(guards),
            "Missing or unexpected performance guard measurements")
    result = {}
    for key in guards:
        values = samples[key]
        require(isinstance(values, list) and len(values) == plan["samples"] and
                all(v is None or number(v) for v in values), "Invalid measured guard samples: " + key)
        result[key] = None if any(v is None for v in values) else statistics.median(values)
    return result


def guard_failures(plan, candidate, baseline):
    return [key for key, allowance in plan.get("performance_guards", {}).items()
            if candidate[key] is None or baseline[key] is None or
            candidate[key] > baseline[key] * (1 + allowance)]


def compare_probes(root):
    frozen = read_json(root / "frozen.json")
    require(frozen["inventory"] == inventory(root), "Frozen input, proposal, evaluator or snapshot drift")
    seal = digest((root / "frozen.json").read_bytes())
    plan = read_json(root / "plan.json")
    evaluation = read_json(root / "evaluation.json")
    require(evaluation.get("frozen_sha256") == seal, "Evaluation belongs to another experiment")
    require(isinstance(evaluation.get("reviewer"), str) and evaluation["reviewer"], "Reviewer required")
    require("optimization_cost" in evaluation, "Record optimization cost, or null if unknown")
    require(evaluation["optimization_cost"] is None or number(evaluation["optimization_cost"]),
            "Invalid optimization cost")
    result = {"experiment_id": plan["experiment_id"], "task_id": plan["task_id"],
              "domain": plan["domain"], "frozen_sha256": seal, "metric": plan["metric"],
              "layer": plan.get("layer", "task"), "portfolio": plan.get("portfolio", []),
              "optimization_cost": evaluation["optimization_cost"],
              "scope": "Recorded constraints and specified metric only; no overall efficiency claim",
              "arms": {}, "eligible": []}
    for arm in ARMS:
        run_path = "runs/" + arm + "/run.json"
        run = read_json(local(root, run_path))
        require(run.get("model_config") == plan["model_config"], "Model configuration drift: " + arm)
        require(run.get("frozen_sha256") == seal, "Run belongs to another experiment: " + arm)
        executor = run.get("executor", {})
        require(executor.get("kind") == "agent" and executor.get("host") and executor.get("session_id"),
                "Actual Agent identity required: " + arm)
        require(evaluation["reviewer"] != executor["session_id"], "Executor cannot self-accept: " + arm)
        evidence = {p: file_hash(root, p) for p in (run["trace"], run["host_receipt"])}
        require(isinstance(run.get("artifacts"), list) and run["artifacts"], "Artifacts required: " + arm)
        evidence.update({p: file_hash(root, p) for p in run["artifacts"]})
        row = evaluation["arms"][arm]
        require(row["run_sha256"] == file_hash(root, run_path), "Assessment/run mismatch: " + arm)
        require(row.get("evidence_sha256") == evidence, "Raw evidence changed or is unbound: " + arm)
        file_hash(root, row["evidence"])
        checks = row["checks"]
        require(set(checks) == set(plan["quality_checks"]) and
                all(v is True or v is False or v is None for v in checks.values()),
                "Missing or invalid quality checks: " + arm)
        values = row["metric_samples"]
        require(isinstance(values, list) and len(values) == plan["samples"]
                and all(number(v) for v in values), "Missing measured samples: " + arm)
        cost = statistics.median(values)
        result["arms"][arm] = {"quality_pass": all(v is True for v in checks.values()),
                               "checks": checks, "cost": cost,
                               "guard_medians": guard_medians(plan, row),
                               "snapshot_sha256": digest(canonical(frozen["inventory"]["snapshots"][arm]))}
    base = result["arms"]["baseline"]
    for arm in ARMS[1:]:
        row = result["arms"][arm]
        gain = (base["cost"] - row["cost"]) / base["cost"] if base["cost"] else 0.0
        row["relative_metric_gain"] = gain
        row["guard_failures"] = guard_failures(plan, row["guard_medians"], base["guard_medians"])
        if row["snapshot_sha256"] == base["snapshot_sha256"]:
            reason = "no_component_change"
        elif not row["quality_pass"]:
            reason = "quality_failed_or_unknown"
        elif row["cost"] > plan["max_candidate_cost"]:
            reason = "cost_ceiling_exceeded"
        elif any(row["guard_medians"][key] is None or base["guard_medians"][key] is None
                 for key in plan.get("performance_guards", {})):
            reason = "resource_evidence_unknown"
        elif row["guard_failures"]:
            reason = "whole_task_resource_regression"
        elif any(v is False for v in base["checks"].values()):
            reason = "quality_repair"
        elif not base["quality_pass"]:
            reason = "baseline_quality_unknown"
        elif gain >= plan["min_relative_gain"]:
            reason = "measured_metric_gain"
        else:
            reason = "no_demonstrated_gain"
        row["reason"] = reason
        if reason in ("quality_repair", "measured_metric_gain"):
            result["eligible"].append(arm)
    result["recommendation"] = (min(result["eligible"], key=lambda a: result["arms"][a]["cost"])
                                 if result["eligible"] else "baseline")
    return result


def composition_inventory(root):
    """Bind composition to completed probes and their original evidence."""
    compare_probes(root)
    plan = read_json(root / "compose-plan.json")
    decisions = plan.get("decisions")
    require(isinstance(decisions, list) and decisions, "Composition decisions required")
    paths = {"evaluation.json", "frozen.json", "compose-plan.json", plan["evaluator"]}
    evaluation = read_json(root / "evaluation.json")
    observed = set()
    for arm in ARMS:
        run_path = "runs/" + arm + "/run.json"
        run = read_json(local(root, run_path))
        observed.update([run_path, run["trace"], run["host_receipt"], *run["artifacts"],
                         evaluation["arms"][arm]["evidence"]])
    for decision in decisions:
        require(decision.get("source") in (*ARMS, "new") and
                decision.get("action") in ("keep", "drop", "rewrite") and
                decision.get("component") and decision.get("reason"),
                "Incomplete component decision")
        require(isinstance(decision.get("evidence"), list) and decision["evidence"] and
                all(p in observed for p in decision["evidence"]),
                "Composition must cite actual probe evidence")
    paths.update(observed)
    return {"files": {p: file_hash(root, p) for p in sorted(paths)},
            "snapshot": tree_hashes(root, "arms/composed")}


def freeze_compose(root):
    require(not (root / "compose-frozen.json").exists(), "Composition already frozen")
    require(not (root / "runs/composed/run.json").exists() and
            not (root / "composition-evaluation.json").exists(),
            "Cannot freeze composition after execution")
    value = {"schema": 1, "created_at": datetime.now(timezone.utc).isoformat(),
             "inventory": composition_inventory(root)}
    write_new(root / "compose-frozen.json", value)
    return {"composition_sha256": file_hash(root, "compose-frozen.json")}


def compare(root):
    result = compare_probes(root)
    if not (root / "compose-frozen.json").exists():
        return result
    frozen = read_json(root / "compose-frozen.json")
    require(frozen["inventory"] == composition_inventory(root), "Composition or probe evidence drift")
    seal = file_hash(root, "compose-frozen.json")
    plan = read_json(root / "plan.json")
    run = read_json(root / "runs/composed/run.json")
    evaluation = read_json(root / "composition-evaluation.json")
    require(run.get("composition_sha256") == seal and evaluation.get("composition_sha256") == seal,
            "Composition run/evaluation is not bound to its frozen snapshot")
    require(run.get("model_config") == plan["model_config"] and
            run.get("frozen_sha256") == result["frozen_sha256"], "Composition model/input drift")
    executor = run.get("executor", {})
    require(executor.get("kind") == "agent" and executor.get("host") and executor.get("session_id"),
            "Actual composition Agent identity required")
    require(evaluation.get("reviewer") and evaluation["reviewer"] != executor["session_id"],
            "Composition executor cannot self-accept")
    require(evaluation.get("frozen_sha256") == result["frozen_sha256"], "Composition input seal mismatch")
    require(isinstance(run.get("artifacts"), list) and run["artifacts"], "Composition artifacts required")
    paths = [run["trace"], run["host_receipt"], *run["artifacts"]]
    row = evaluation["arms"]["composed"]
    require(row["run_sha256"] == file_hash(root, "runs/composed/run.json") and
            row["evidence_sha256"] == {p: file_hash(root, p) for p in paths},
            "Composition raw evidence changed or is unbound")
    file_hash(root, row["evidence"])
    checks = row["checks"]
    require(set(checks) == set(plan["quality_checks"]) and
            all(v is True or v is False or v is None for v in checks.values()),
            "Composition quality criteria changed")
    values = row["metric_samples"]
    require(isinstance(values, list) and len(values) == plan["samples"] and
            all(number(v) for v in values), "Missing composition measurements")
    cost = statistics.median(values)
    base = result["arms"]["baseline"]
    gain = (base["cost"] - cost) / base["cost"] if base["cost"] else 0.0
    version = digest(canonical(frozen["inventory"]["snapshot"]))
    guards = guard_medians(plan, row)
    failed_guards = guard_failures(plan, guards, base["guard_medians"])
    best = min((result["arms"][a]["cost"] for a in result["eligible"]), default=base["cost"])
    if not all(v is True for v in checks.values()):
        reason = "quality_failed_or_unknown"
    elif version == base["snapshot_sha256"]:
        reason = "no_component_change"
    elif cost > plan["max_candidate_cost"] or cost > best:
        reason = "composition_regressed"
    elif any(guards[key] is None or base["guard_medians"][key] is None
             for key in plan.get("performance_guards", {})):
        reason = "resource_evidence_unknown"
    elif failed_guards:
        reason = "whole_task_resource_regression"
    elif any(v is False for v in base["checks"].values()):
        reason = "quality_repair"
    elif not base["quality_pass"]:
        reason = "baseline_quality_unknown"
    elif gain >= plan["min_relative_gain"]:
        reason = "measured_metric_gain"
    else:
        reason = "no_demonstrated_gain"
    result["arms"]["composed"] = {"quality_pass": all(v is True for v in checks.values()),
        "checks": checks, "cost": cost, "snapshot_sha256": version,
        "guard_medians": guards, "guard_failures": failed_guards,
        "relative_metric_gain": gain, "reason": reason}
    result["composition_sha256"] = seal
    if reason in ("quality_repair", "measured_metric_gain"):
        result["eligible"].append("composed")
        result["recommendation"] = "composed"
    return result


def load_library(root):
    require(not root.is_symlink(), "Library root cannot be a symlink")
    path = root / "index.json"
    if not path.exists():
        return {"schema": 1, "revision": 0, "profiles": {}, "records": {}}
    require(not path.is_symlink(), "Library index cannot be a symlink")
    return read_json(path)


def select(root, domain):
    index = load_library(root)
    profile = index["profiles"].get(domain)
    if profile:
        actual = tree_hashes(root, profile["path"])
        require(digest(canonical(actual)) == profile["sha256"], "Active snapshot has changed")
    for record in index["records"].values():
        if record["domain"] == domain:
            require(file_hash(root, record["path"]) == record["sha256"], "Experience card has changed")
    observations = [v for v in index.get("observations", {}).values() if v["domain"] == domain]
    for observation in observations:
        require(file_hash(root, observation["path"]) == observation["sha256"],
                "Review observation has changed")
    return {"revision": index["revision"], "domain": domain, "active": profile,
            "experiences": [v for v in index["records"].values() if v["domain"] == domain],
            "observations": observations,
            "other_domains": sorted({v["domain"] for v in index["records"].values()} - {domain}),
            "loading": "The host must read the active snapshot; this command does not load an Agent"}


def record(root, library, expected_revision, activate=None):
    report = compare(root)
    require(activate is None or activate in report["eligible"], "Cannot activate an unqualified candidate")
    library.mkdir(parents=True, exist_ok=True)
    require(not library.is_symlink(), "Library root cannot be a symlink")
    lock = library / ".writer.lock"
    with lock.open("x") as stream:
        stream.write(str(os.getpid()))
    try:
        index = load_library(library)
        require(index["revision"] == expected_revision, "Stale library revision; reread before writing")
        domain = report["domain"]
        current = index["profiles"].get(domain)
        if current:
            select(library, domain)
            require(current["sha256"] == report["arms"]["baseline"]["snapshot_sha256"],
                    "Experiment did not use the current domain baseline")
        exp = report["experiment_id"]
        require(exp not in index["records"], "Experiment already recorded")
        record_dir = local(library, "records")
        record_dir.mkdir(exist_ok=True)
        card_path = local(library, "records/" + exp + ".json")
        require(not card_path.exists(), "Uncommitted record exists; inspect it before recovery")
        temporary = local(library, "index.pending.json")
        require(not temporary.exists(), "Pending index exists; inspect it before recovery")
        previous = current
        if activate:
            for arm in ("baseline", activate):
                version = report["arms"][arm]["snapshot_sha256"]
                relative = "versions/" + version
                target = local(library, relative)
                target.parent.mkdir(exist_ok=True)
                if not target.exists():
                    shutil.copytree(local(root, "arms/" + arm), target)
                require(digest(canonical(tree_hashes(library, relative))) == version, "Version copy mismatch")
                if arm == "baseline" and previous is None:
                    previous = {"path": relative, "sha256": version, "experiment_id": exp,
                                "source": "initial_baseline"}
            index["profiles"][domain] = {"path": relative, "sha256": version, "experiment_id": exp}
        card = {"comparison": report, "source_experiment": str(root.resolve()),
                "adopted": activate, "previous": previous,
                "generalization": "Current domain only; other domains require new trials"}
        card["proposals"] = {a: (root / "proposals" / (a + ".md")).read_text(encoding="utf-8")
                             for a in ARMS[1:]}
        card["evidence"] = read_json(root / "evaluation.json")
        if "composition_sha256" in report:
            card["composition"] = read_json(root / "compose-plan.json")
            card["composition_evidence"] = read_json(root / "composition-evaluation.json")
        if (root / "reflection.json").exists():
            card["reflection"] = read_json(root / "reflection.json")
            card["reflection_sha256"] = file_hash(root, "reflection.json")
        write_new(card_path, card)
        index["records"][exp] = {"domain": domain, "path": card_path.relative_to(library).as_posix(),
                                 "sha256": file_hash(library, card_path.relative_to(library).as_posix()),
                                 "adopted": activate, "eligible": report["eligible"]}
        index["revision"] += 1
        write_new(temporary, index)
        os.replace(temporary, library / "index.json")
        require(read_json(library / "index.json") == index, "Index readback mismatch")
        return select(library, domain)
    finally:
        lock.unlink()


def observe(library, review_path, expected_revision):
    """Append a checked reuse observation without silently promoting another version."""
    review = read_json(review_path)
    observation_id = review.get("observation_id")
    require(isinstance(observation_id, str) and
            re.fullmatch(r"[a-zA-Z0-9][a-zA-Z0-9._-]{0,95}", observation_id), "Invalid observation_id")
    require(all(isinstance(review.get(k), str) and review[k].strip()
                for k in ("domain", "active_sha256", "lesson", "limitations", "next_probe")),
            "Review requires scope, lesson, limits and next probe")
    evidence = review.get("evidence")
    require(isinstance(evidence, dict) and evidence, "Review evidence required")
    for path, expected in evidence.items():
        source = Path(path)
        require(source.is_absolute() and not source.is_symlink() and source.is_file() and
                digest(source.read_bytes()) == expected, "Review evidence missing or changed")
    require(not library.is_symlink(), "Library root cannot be a symlink")
    lock = library / ".writer.lock"
    with lock.open("x") as stream:
        stream.write(str(os.getpid()))
    try:
        index = load_library(library)
        require(index["revision"] == expected_revision, "Stale library revision")
        active = select(library, review["domain"])["active"]
        require(active and active["sha256"] == review["active_sha256"],
                "Review did not use the current active snapshot")
        observations = index.setdefault("observations", {})
        require(observation_id not in observations, "Observation already recorded")
        temporary = local(library, "index.pending.json")
        require(not temporary.exists(), "Pending index exists; inspect it before recovery")
        folder = local(library, "observations")
        folder.mkdir(exist_ok=True)
        relative = "observations/" + observation_id + ".json"
        write_new(local(library, relative), review)
        observations[observation_id] = {"domain": review["domain"], "path": relative,
                                       "sha256": file_hash(library, relative),
                                       "active_sha256": review["active_sha256"]}
        index["revision"] += 1
        write_new(temporary, index)
        os.replace(temporary, library / "index.json")
        require(read_json(library / "index.json") == index, "Index readback mismatch")
        return select(library, review["domain"])
    finally:
        lock.unlink()


def rollback(library, experiment_id, expected_revision, reason):
    require(bool(reason.strip()), "Rollback reason required")
    require(not library.is_symlink(), "Library root cannot be a symlink")
    lock = library / ".writer.lock"
    with lock.open("x") as stream:
        stream.write(str(os.getpid()))
    try:
        index = load_library(library)
        require(index["revision"] == expected_revision, "Stale library revision")
        entry = index["records"][experiment_id]
        require(file_hash(library, entry["path"]) == entry["sha256"], "Experience card has changed")
        card = read_json(local(library, entry["path"]))
        domain = entry["domain"]
        require(card["adopted"] is not None and card["previous"], "Record has no adoption to roll back")
        current = index["profiles"][domain]
        adopted = card["comparison"]["arms"][card["adopted"]]["snapshot_sha256"]
        require(current["experiment_id"] == experiment_id and current["sha256"] == adopted,
                "A later adoption is active; do not overwrite it")
        previous = card["previous"]
        require(digest(canonical(tree_hashes(library, previous["path"]))) == previous["sha256"],
                "Rollback snapshot has changed")
        temporary = local(library, "index.pending.json")
        require(not temporary.exists(), "Pending index exists; inspect it before recovery")
        folder = local(library, "rollbacks")
        folder.mkdir(exist_ok=True)
        index["revision"] += 1
        write_new(folder / (str(index["revision"]) + ".json"),
                  {"from": current, "to": previous, "reason": reason, "revision": index["revision"]})
        index["profiles"][domain] = previous
        write_new(temporary, index)
        os.replace(temporary, library / "index.json")
        return select(library, domain)
    finally:
        lock.unlink()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="action", required=True)
    for action in ("freeze", "freeze-compose", "compare", "record"):
        p = sub.add_parser(action)
        p.add_argument("experiment", type=Path)
        if action == "record":
            p.add_argument("--library", required=True, type=Path)
            p.add_argument("--expected-revision", required=True, type=int)
            p.add_argument("--activate", choices=(*ARMS[1:], "composed"))
    p = sub.add_parser("select")
    p.add_argument("--library", required=True, type=Path)
    p.add_argument("--domain", required=True)
    p = sub.add_parser("observe")
    p.add_argument("--library", required=True, type=Path)
    p.add_argument("--review", required=True, type=Path)
    p.add_argument("--expected-revision", required=True, type=int)
    p = sub.add_parser("rollback")
    p.add_argument("--library", required=True, type=Path)
    p.add_argument("--experiment-id", required=True)
    p.add_argument("--expected-revision", required=True, type=int)
    p.add_argument("--reason", required=True)
    args = parser.parse_args()
    try:
        if args.action == "select":
            result = select(args.library, args.domain)
        elif args.action == "observe":
            result = observe(args.library, args.review, args.expected_revision)
        elif args.action == "rollback":
            result = rollback(args.library, args.experiment_id, args.expected_revision, args.reason)
        elif args.action == "record":
            result = record(args.experiment, args.library, args.expected_revision, args.activate)
        else:
            result = {"freeze": freeze, "freeze-compose": freeze_compose,
                      "compare": compare}[args.action](args.experiment)
        print(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False))
        return 0
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(json.dumps({"status": "INCOMPLETE", "error": str(error)}, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
