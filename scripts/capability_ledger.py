#!/usr/bin/env python3
# Copyright (C) 2026 KARMENLOOP Official Team
# SPDX-License-Identifier: AGPL-3.0-only
"""Markdown-only capability evidence, with replayed state and review suggestions.

An observation is Markdown with a JSON object as its YAML 1.2 front matter:
---
{"id":"apply-one","kind":"apply","task_id":"task-one",
 "executor":"host/session-one","reviewer":"host/reviewer-one",
 "outcome":"pass","observed_at":"2026-11-03T01:00:00Z",
 "summary":"Built and independently checked the requested artifact.",
 "artifacts":[{"path":"evidence/result.md","sha256":"<64 lowercase hex>"}],
 "cost":{"wall_seconds":12.4,"tokens":null,"usd":null}}
---
Human-readable notes, evidence limits and interpretation belong here.

Kinds: explain, apply, counterexample, transfer, teach, deliver, recall, regression.
Transfer also needs source_attempt (a prior passed apply ID) and a new task_id.
Teach also needs learner, learner_task_id, and learner_artifacts (same shape as
artifacts). Recall needs source_attempt and no_answer_visible:true, at least
policy.recall_min_hours after that passed attempt. All times must be UTC.

init(root,id,goal,domain,policy=None) supports immutable initialization policy:
{"recall_min_hours":24,"review_days":[1,3,7]}. No retrospective policy edits.
record(root,id,observation_md,expected_revision); status(root,id); due(root).
Only the MD files are semantic state. Lock/temp files are transaction mechanics.
Declared actors and hashes are consistency evidence, NOT Agent authentication,
semantic quality judgment, proof of learning, or a registered host scheduler.
Past events/unknown costs remain visible. Expired evidence needs fresh review.
Cost sums are reported observation increments, not authenticated whole-Agent cost.
Record non-overlapping increments; repeated reports of one run duplicate its cost.
The forward hash chain detects earlier edits once a successor exists; this is
not a signed or tamper-proof log, and cannot authenticate the latest entry.
The optional internal now parameter is for tests; CLI always uses the real clock.
"""
import argparse
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import re
import secrets
import sys

KINDS = ("explain", "apply", "counterexample", "transfer", "teach", "deliver", "recall", "regression")
DEFAULT_POLICY = {"recall_min_hours": 24, "review_days": [1, 3, 7]}
BASE_KEYS = {"id", "kind", "task_id", "executor", "reviewer", "outcome", "observed_at", "summary", "artifacts", "cost"}
EXTRA_KEYS = {"transfer": {"source_attempt"}, "recall": {"source_attempt", "no_answer_visible"},
              "teach": {"learner", "learner_task_id", "learner_artifacts"}}


def require(ok, message):
    if not ok:
        raise ValueError(message)


def text(value, label, limit=8000):
    require(isinstance(value, str) and value.strip() and len(value) <= limit, "Invalid " + label)
    return value


def identifier(value):
    require(isinstance(value, str) and re.fullmatch(r"[a-zA-Z0-9][a-zA-Z0-9_-]{0,79}", value), "Unsafe id")
    require(value.upper() not in {"CON", "PRN", "AUX", "NUL", *(f"COM{i}" for i in range(1, 10)),
                               *(f"LPT{i}" for i in range(1, 10))}, "Reserved id")
    return value


def number(value):
    try:
        return type(value) in (int, float) and math.isfinite(value) and value >= 0
    except OverflowError:
        return False


def utc(value):
    require(isinstance(value, str) and (value.endswith("Z") or value.endswith("+00:00")), "Timestamp must be UTC")
    result = datetime.fromisoformat(value.replace("Z", "+00:00"))
    require(result.utcoffset() == timedelta(0), "Timestamp must be UTC")
    return result


def clock(now=None):
    now = now if now is not None else datetime.now(timezone.utc)
    require(isinstance(now, datetime) and now.tzinfo is not None and now.utcoffset() == timedelta(0), "Clock must be UTC")
    return now


def sha(data):
    return hashlib.sha256(data).hexdigest()


def encode(metadata, body):
    return ("---\n" + json.dumps(metadata, ensure_ascii=False, indent=2, allow_nan=False) +
            "\n---\n\n" + body.rstrip() + "\n").encode("utf-8")


def decode(raw):
    def pairs(items):
        out = {}
        for key, value in items:
            require(key not in out, "Duplicate metadata key: " + key)
            out[key] = value
        return out
    def constant(value):
        raise ValueError("Nonfinite metadata number: " + value)
    require(len(raw) <= 1024 * 1024, "Markdown exceeds 1 MiB")
    lines = raw.decode("utf-8").splitlines()
    require(lines and lines[0] == "---", "Missing JSON/YAML front matter")
    end = next((i for i in range(1, len(lines)) if lines[i] == "---"), None)
    require(end is not None, "Unterminated front matter")
    meta = json.loads("\n".join(lines[1:end]), object_pairs_hook=pairs, parse_constant=constant)
    require(isinstance(meta, dict), "Metadata must be an object")
    return meta, "\n".join(lines[end + 1:]).strip()


def root_path(root, create=False):
    root = Path(root).expanduser().absolute()
    require(not root.is_symlink(), "Root cannot be a symlink")
    if create:
        root.mkdir(parents=True, exist_ok=True)
    require(root.is_dir(), "Explicit root does not exist")
    return root.resolve()


def local(root, relative):
    require(isinstance(relative, str) and relative and "\\" not in relative and ":" not in relative, "Unsafe path")
    parts = relative.split("/")
    require(all(p not in ("", ".", "..") and not p.endswith((" ", ".")) for p in parts), "Unsafe path")
    path = root
    for part in parts:
        path /= part
        require(not path.is_symlink(), "Symlink is not allowed: " + relative)
    require(path.resolve().is_relative_to(root), "Path escapes root")
    return path


def read_md(path):
    require(not path.is_symlink() and path.is_file(), "Missing regular Markdown: " + str(path))
    require(path.stat().st_size <= 1024 * 1024, "Markdown exceeds 1 MiB")
    raw = path.read_bytes()
    meta, body = decode(raw)
    return meta, body, sha(raw)


@contextmanager
def writer(folder):
    lock = folder / ".writer.lock"
    with lock.open("x", encoding="utf-8") as stream:
        stream.write(str(os.getpid()))
    try:
        yield
    finally:
        lock.unlink()


def publish(path, raw):
    """Atomic, exclusive publication; never overwrite an existing journal entry."""
    temporary = path.parent / (".pending-" + secrets.token_hex(12))
    try:
        with temporary.open("xb") as stream:
            os.chmod(temporary, 0o600)
            stream.write(raw)
            stream.flush()
            os.fsync(stream.fileno())
        os.link(temporary, path)  # One atomic name creation; FileExistsError preserves prior content.
        require(path.read_bytes() == raw, "Publication readback mismatch")
    finally:
        if temporary.exists():
            temporary.unlink()


def policy_check(policy):
    require(isinstance(policy, dict) and set(policy) == set(DEFAULT_POLICY), "Invalid policy fields")
    require(number(policy["recall_min_hours"]) and policy["recall_min_hours"] >= 24, "Recall interval must be at least 24 hours")
    days = policy["review_days"]
    require(isinstance(days, list) and 1 <= len(days) <= 12 and
            all(type(day) is int and 1 <= day <= 365 for day in days) and days == sorted(set(days)), "Invalid review intervals")


def init(root, capability_id, goal, domain, policy=None, now=None):
    capability_id = identifier(capability_id)
    text(goal, "goal"); text(domain, "domain", 200)
    policy = dict(DEFAULT_POLICY if policy is None else policy)
    policy_check(policy)
    now = clock(now)
    root = root_path(root, create=True)
    folder = local(root, "capabilities/" + capability_id)
    folder.mkdir(parents=True, exist_ok=True)
    with writer(folder):
        config = local(root, "capabilities/" + capability_id + "/capability.md")
        require(not config.exists(), "Capability already exists")
        attempts = local(root, "capabilities/" + capability_id + "/attempts")
        require(not attempts.exists() or not any(attempts.iterdir()), "Unexpected existing attempts")
        attempts.mkdir(exist_ok=True)
        meta = {"schema": 1, "type": "capability", "id": capability_id, "goal": goal,
                "domain": domain, "created_at": now.isoformat(), "policy": policy}
        publish(config, encode(meta, "# " + capability_id + "\n\n" + goal +
                "\n\nConfiguration is immutable through this API. Start a new capability for a changed policy."))
    return status(root, capability_id, now=now)


def artifacts(root, records, required):
    require(isinstance(records, list) and len(records) <= 100 and (bool(records) or not required), "Artifact evidence required")
    seen = set()
    for record in records:
        require(isinstance(record, dict) and set(record) == {"path", "sha256"}, "Invalid artifact record")
        path = local(root, record["path"])
        require(record["path"] not in seen, "Duplicate artifact path")
        seen.add(record["path"])
        require(isinstance(record["sha256"], str) and re.fullmatch(r"[0-9a-f]{64}", record["sha256"]), "Invalid artifact hash")
        require(path.is_file() and 0 < path.stat().st_size <= 32 * 1024 * 1024, "Missing, empty or oversized artifact")
        require(sha(path.read_bytes()) == record["sha256"], "Artifact changed: " + record["path"])


def invalidated(source, events):
    index = next(i for i, event in enumerate(events) if event["id"] == source["id"])
    if any(event["kind"] == source["kind"] and event["outcome"] != "pass" for event in events[index + 1:]):
        return True
    parent = source.get("source_attempt")
    if parent:
        return invalidated(next(event for event in events[:index] if event["id"] == parent), events)
    return False


def observation_check(root, item, previous, policy, created, now):
    require(isinstance(item, dict), "Observation must be an object")
    kind = item.get("kind")
    require(kind in KINDS, "Unknown observation kind")
    require(set(item) == BASE_KEYS | EXTRA_KEYS.get(kind, set()), "Unexpected or missing observation fields")
    identifier(item["id"])
    require(item["id"] not in {e["id"] for e in previous}, "Duplicate event id")
    for key in ("task_id", "executor", "summary"):
        text(item[key], key)
    outcome = item["outcome"]
    require(outcome in ("pass", "fail", "unknown"), "Invalid outcome")
    require(item["reviewer"] is None or isinstance(item["reviewer"], str) and item["reviewer"].strip(), "Invalid reviewer")
    if outcome == "pass":
        require(item["reviewer"] and item["reviewer"] != item["executor"], "Independent reviewer required")
    at = utc(item["observed_at"])
    require(created <= at <= now, "Observation is before initialization or in the future")
    if previous:
        require(at >= utc(previous[-1]["observed_at"]), "Observations must be chronological")
    cost = item["cost"]
    require(isinstance(cost, dict) and set(cost) == {"wall_seconds", "tokens", "usd"} and
            all(v is None or number(v) for v in cost.values()), "Invalid cost; use null for unknown")
    artifacts(root, item["artifacts"], outcome == "pass")
    if kind in ("transfer", "recall"):
        source = next((event for event in previous if event["id"] == item["source_attempt"]), None)
        require(source is not None and source["outcome"] == "pass", "A prior passed source_attempt is required")
        if outcome == "pass":
            require(not invalidated(source, previous), "Source attempt has been invalidated by later evidence")
        if kind == "transfer":
            require(source["kind"] == "apply" and source["task_id"] != item["task_id"], "Transfer requires prior apply and a new task")
        else:
            require(item["no_answer_visible"] is True, "Recall must be closed book")
            require(at - utc(source["observed_at"]) >= timedelta(hours=policy["recall_min_hours"]), "Recall interval has not elapsed")
    if kind == "teach":
        text(item["learner"], "learner"); text(item["learner_task_id"], "learner_task_id")
        require(item["learner"] not in (item["executor"], item["reviewer"]) and
                item["learner_task_id"] != item["task_id"], "Teaching needs an independent learner on a new task")
        artifacts(root, item["learner_artifacts"], outcome == "pass")
        require(not ({a["sha256"] for a in item["artifacts"]} &
                     {a["sha256"] for a in item["learner_artifacts"]}), "Learner cannot reuse teacher artifact hashes")


def replay(root, capability_id, now):
    capability_id = identifier(capability_id)
    folder = local(root, "capabilities/" + capability_id)
    config, _, config_hash = read_md(local(root, "capabilities/" + capability_id + "/capability.md"))
    require(set(config) == {"schema", "type", "id", "goal", "domain", "created_at", "policy"} and
            type(config["schema"]) is int and config["schema"] == 1 and config["type"] == "capability" and
            config["id"] == capability_id, "Invalid capability configuration")
    text(config["goal"], "goal"); text(config["domain"], "domain", 200)
    policy_check(config["policy"])
    created = utc(config["created_at"])
    require(created <= now, "Configuration is in the future")
    attempts = local(root, "capabilities/" + capability_id + "/attempts")
    require(attempts.is_dir(), "Missing attempts directory")
    paths = sorted(attempts.iterdir())
    require(all(p.name.startswith(".pending-") or re.fullmatch(r"\d{6}\.md", p.name) for p in paths), "Unexpected journal entry")
    paths = [p for p in paths if not p.name.startswith(".pending-")]
    events, previous_hash = [], None
    for revision, path in enumerate(paths, 1):
        require(path.name == f"{revision:06d}.md", "Journal revision gap")
        saved, _, event_hash = read_md(path)
        require(set(saved) == {"schema", "type", "revision", "config_sha256", "previous_attempt_sha256", "observation"} and
                type(saved["schema"]) is int and saved["schema"] == 1 and saved["type"] == "attempt" and
                type(saved["revision"]) is int and saved["revision"] == revision and
                saved["config_sha256"] == config_hash and saved["previous_attempt_sha256"] == previous_hash,
                "Journal or configuration binding changed")
        observation_check(root, saved["observation"], events, config["policy"], created, now)
        events.append(saved["observation"])
        previous_hash = event_hash
    return config, config_hash, events, folder


def status(root, capability_id, now=None):
    now = clock(now)
    root = root_path(root)
    config, _, events, _ = replay(root, capability_id, now)
    dimensions, due_items = {}, []
    for kind in KINDS:
        matching = [e for e in events if e["kind"] == kind]
        if not matching:
            dimensions[kind] = {"state": "unobserved", "attempt_id": None}
            continue
        latest = matching[-1]
        state, action = latest["outcome"], None
        at = utc(latest["observed_at"])
        if state == "pass" and latest.get("source_attempt"):
            source = next(event for event in events if event["id"] == latest["source_attempt"])
            if invalidated(source, events):
                state, action = "source_invalidated", "verify_source"
        if state == "pass":
            streak, task_ids, evidence_sets, basis = 0, set(), set(), None
            for event in matching:
                if event["outcome"] != "pass" or invalidated(event, events):
                    streak, task_ids, evidence_sets, basis = 0, set(), set(), None
                    continue
                # A later duplicate is a retained observation, not a new practice.
                # Teaching practice is established by learner work, not a rewritten lesson.
                task_id = event["learner_task_id"] if kind == "teach" else event["task_id"]
                records = event["learner_artifacts"] if kind == "teach" else event["artifacts"]
                evidence = tuple(sorted(a["sha256"] for a in records))
                if task_id not in task_ids and evidence not in evidence_sets:
                    streak += 1
                    task_ids.add(task_id)
                    evidence_sets.add(evidence)
                    basis = event
            days = config["policy"]["review_days"][min(streak - 1, len(config["policy"]["review_days"]) - 1)]
            deadline = utc(basis["observed_at"]) + timedelta(days=days)
            if now >= deadline:
                state, action = "review_due", "closed_book_review"
        else:
            deadline, action = at, action or ("remediate" if state == "fail" else "verify")
        dimensions[kind] = {"state": state, "attempt_id": latest["id"], "task_id": latest["task_id"],
                            "observed_at": latest["observed_at"], "review_at": deadline.isoformat()}
        due_items.append({"kind": kind, "attempt_id": latest["id"], "action": action or "closed_book_review",
                          "due_at": deadline.isoformat(), "due": now >= deadline})
    missing = [kind for kind, dimension in dimensions.items() if dimension["state"] != "pass"]
    cost = {}
    for key in ("wall_seconds", "tokens", "usd"):
        known = [event["cost"][key] for event in events if event["cost"][key] is not None]
        total = sum(known)
        overflow = not number(total)
        cost[key] = {"known_sum": None if overflow else total, "unknown_count": len(events) - len(known),
                     "total": total if not overflow and len(known) == len(events) else None,
                     "aggregation_overflow": overflow}
    return {"id": capability_id, "goal": config["goal"], "domain": config["domain"], "revision": len(events),
            "dimensions": dimensions, "missing_gates": missing,
            "assessment": "demonstrated_in_scope" if not missing else "incomplete_or_review_due",
            "cost": cost, "cost_scope": "reported_observation_increments_not_whole_agent_total",
            "next_actions": sorted(due_items, key=lambda x: x["due_at"]),
            "scheduler_registered": False, "history": events,
            "limits": "Declared identities and artifact consistency only; no universal mastery or authenticated Agent claim."}


def record(root, capability_id, observation_md, expected_revision, now=None):
    now = clock(now)
    root = root_path(root)
    capability_id = identifier(capability_id)
    require(type(expected_revision) is int and expected_revision >= 0, "Invalid expected revision")
    item, body, _ = read_md(Path(observation_md))
    folder = local(root, "capabilities/" + capability_id)
    with writer(folder):
        config, config_hash, previous, _ = replay(root, capability_id, now)
        require(len(previous) == expected_revision, "Stale revision; read status again")
        require(expected_revision < 999999, "Journal capacity reached")
        observation_check(root, item, previous, config["policy"], utc(config["created_at"]), now)
        revision = expected_revision + 1
        previous_hash = sha((folder / "attempts" / f"{expected_revision:06d}.md").read_bytes()) if previous else None
        meta = {"schema": 1, "type": "attempt", "revision": revision, "previous_attempt_sha256": previous_hash,
                "config_sha256": config_hash, "observation": item}
        path = local(root, f"capabilities/{capability_id}/attempts/{revision:06d}.md")
        publish(path, encode(meta, f"# {item['kind']}: {item['outcome']}\n\n{item['summary']}\n\n" + body))
        return status(root, capability_id, now=now)


def due(root, now=None):
    now = clock(now)
    root = root_path(root)
    folder = local(root, "capabilities")
    require(folder.is_dir(), "Missing capabilities directory")
    tasks, errors = [], []
    for path in sorted(folder.iterdir()):
        try:
            identifier(path.name)
            require(path.is_dir() and not path.is_symlink(), "Invalid capability directory")
            result = status(root, path.name, now=now)
            tasks.extend({"capability_id": path.name, **item} for item in result["next_actions"] if item["due"])
        except (OSError, ValueError, KeyError, TypeError) as error:
            errors.append({"capability_id": path.name, "error": str(error)})
    return {"as_of": now.isoformat(), "tasks": tasks, "errors": errors, "scheduler_registered": False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="action", required=True)
    for action in ("init", "record", "status", "due"):
        p = sub.add_parser(action)
        p.add_argument("--root", type=Path, required=True)
        if action != "due":
            p.add_argument("--id", required=True)
        if action == "init":
            p.add_argument("--goal", required=True); p.add_argument("--domain", required=True)
        if action == "record":
            p.add_argument("--observation", type=Path, required=True)
            p.add_argument("--expected-revision", type=int, required=True)
    args = parser.parse_args()
    try:
        if args.action == "init":
            result = init(args.root, args.id, args.goal, args.domain)
        elif args.action == "record":
            result = record(args.root, args.id, args.observation, args.expected_revision)
        elif args.action == "status":
            result = status(args.root, args.id)
        else:
            result = due(args.root)
        print(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False))
        return 2 if result.get("errors") else 0
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(json.dumps({"status": "INCOMPLETE", "error": str(error)}, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
