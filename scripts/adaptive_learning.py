#!/usr/bin/env python3
# Copyright (C) 2026 KARMENLOOP Official Team
# SPDX-License-Identifier: AGPL-3.0-only
"""Replayable Markdown learning decisions. The host Agent supplies and executes actions.

Ranking uses declared estimates, not a model or a measurement of intelligence.
Actor strings are declarations, not authentication. Real host receipts and semantic
review remain necessary. Budget is wall time since init, including planning and
waiting inside this run; earlier setup is outside that interval. CLI uses real UTC.
"""
import argparse
from datetime import timedelta
import json
from pathlib import Path
import secrets
import sys

import capability_ledger as md

KINDS = {"research", "retrieve", "experiment", "tool", "reflect", "deliver", "ask"}
OUTCOMES = {"progress", "no_progress", "failed", "delivered", "unknown"}


def strings(items, label, empty=False):
    md.require(isinstance(items, list) and len(items) <= 100 and (items or empty), "Invalid " + label)
    for item in items:
        md.text(item, label)
    md.require(len(set(items)) == len(items), "Duplicate " + label)
    return items


def fields(value, required, optional=()):
    md.require(isinstance(value, dict) and set(required) <= set(value) <= set(required) | set(optional), "Invalid fields")


def fraction(value):
    return md.number(value) and value <= 1


def request_check(item):
    fields(item, {"id", "type", "goal", "domain", "acceptance", "budget_seconds", "max_actions", "allowed_actions"}, {"max_plans"})
    md.identifier(item["id"])
    md.require(item["type"] == "learning-request", "Expected learning-request")
    md.text(item["goal"], "goal"); md.text(item["domain"], "domain", 200)
    strings(item["acceptance"], "acceptance")
    md.require(md.number(item["budget_seconds"]) and 0 < item["budget_seconds"] <= 604800, "Invalid budget")
    md.require(type(item["max_actions"]) is int and 1 <= item["max_actions"] <= 100, "Invalid max_actions")
    md.require(type(item.get("max_plans", 4 * item["max_actions"])) is int and
               1 <= item.get("max_plans", 4 * item["max_actions"]) <= 400, "Invalid max_plans")
    strings(item["allowed_actions"], "allowed_actions")
    md.require(set(item["allowed_actions"]) <= KINDS, "Unknown action kind")


def blank(request, created):
    return {"request": request, "created_at": created, "revision": 0, "plan": None,
            "pending": None, "unknowns": {}, "resolved": set(), "started": 0,
            "planned": 0, "stalled": 0, "delivered": False, "delivered_at": None,
            "stopped_at": None, "stop_reason": None, "observations": [], "event_ids": set()}


def plan_check(item, state, root, fresh=False):
    fields(item, {"id", "type", "based_on_revision", "unknowns", "actions", "experience_refs", "artifacts"})
    md.identifier(item["id"])
    md.require(item["type"] == "learning-plan", "Expected learning-plan")
    md.require(type(item["based_on_revision"]) is int and item["based_on_revision"] == state["revision"], "Stale plan revision")
    md.require(isinstance(item["unknowns"], list) and len(item["unknowns"]) <= 100, "Invalid unknowns")
    questions = {}
    for question in item["unknowns"]:
        fields(question, {"id", "question", "importance"}, {"blocking"})
        key = md.identifier(question["id"]); md.text(question["question"], "question")
        md.require(key not in questions and key not in state["resolved"], "Duplicate or already resolved question")
        md.require(fraction(question["importance"]), "Invalid importance")
        md.require(type(question.get("blocking", True)) is bool, "Invalid blocking flag")
        if key in state["unknowns"]:
            prior = state["unknowns"][key]
            md.require(prior["question"] == question["question"] and prior.get("blocking", True) == question.get("blocking", True),
                       "Question identity or blocking scope changed; resolve with evidence and introduce a new question")
        questions[key] = question
    md.require(set(state["unknowns"]) - state["resolved"] <= set(questions), "Unresolved questions cannot disappear")
    md.require(isinstance(item["actions"], list) and 1 <= len(item["actions"]) <= 30, "Invalid actions")
    action_ids = set()
    for action in item["actions"]:
        fields(action, {"id", "kind", "question_ids", "description", "expected_information_gain", "estimated_seconds", "preconditions"})
        key = md.identifier(action["id"])
        md.require(key not in action_ids, "Duplicate action id"); action_ids.add(key)
        md.require(action["kind"] in state["request"]["allowed_actions"], "Action outside request scope")
        md.text(action["description"], "description")
        strings(action["question_ids"], "question ids", empty=action["kind"] in {"deliver", "ask"})
        md.require(set(action["question_ids"]) <= set(questions), "Unknown question id")
        strings(action["preconditions"], "unmet preconditions", empty=True)
        md.require(fraction(action["expected_information_gain"]), "Invalid information gain estimate")
        md.require(md.number(action["estimated_seconds"]) and 0.001 <= action["estimated_seconds"] <= 604800, "Duration estimate must be 0.001..604800 seconds")
    md.artifacts(root, item["artifacts"], required=False)
    md.require(isinstance(item["experience_refs"], list) and len(item["experience_refs"]) <= 20, "Invalid experience refs")
    seen = set()
    for ref in item["experience_refs"]:
        fields(ref, {"path", "sha256", "revision", "head_sha256"})
        md.require(ref["path"] not in seen, "Duplicate experience reference"); seen.add(ref["path"])
        md.artifacts(root, [{"path": ref["path"], "sha256": ref["sha256"]}], required=True)
        md.require(type(ref["revision"]) is int and ref["revision"] >= 0, "Invalid experience revision")
        md.require(isinstance(ref["head_sha256"], str) and len(ref["head_sha256"]) == 64 and
                   all(c in "0123456789abcdef" for c in ref["head_sha256"]), "Invalid experience head hash")
        if fresh:
            import experience_transfer
            experience_transfer.verify_ref(root, ref)


def observation_check(item, state, root):
    fields(item, {"id", "type", "start_id", "action_id", "outcome", "finding", "hypothesis_change", "resolved_questions",
                  "artifacts", "executor", "reviewer", "cost", "acceptance_checks"})
    md.identifier(item["id"])
    md.require(item["type"] == "learning-observation" and item["outcome"] in OUTCOMES, "Invalid observation")
    pending = state["pending"]
    md.require(pending is not None and pending["start_id"] == item["start_id"] and
               pending["action"]["id"] == item["action_id"], "Observation does not match the pending start token")
    md.text(item["finding"], "finding"); md.text(item["hypothesis_change"], "hypothesis change")
    strings(item["resolved_questions"], "resolved questions", empty=True)
    md.require(set(item["resolved_questions"]) <= set(pending["action"]["question_ids"]) - state["resolved"], "Resolution not targeted by this action")
    if item["outcome"] in {"unknown", "no_progress", "failed"}:
        md.require(not item["resolved_questions"], "Unresolved outcomes cannot resolve questions")
    md.artifacts(root, item["artifacts"], required=item["outcome"] != "unknown")
    md.text(item["executor"], "executor", 200)
    md.require(item["reviewer"] is None or isinstance(item["reviewer"], str) and item["reviewer"].strip(), "Invalid reviewer")
    cost = item["cost"]
    fields(cost, {"tokens", "usd"})
    md.require(all(value is None or md.number(value) for value in cost.values()), "Invalid cost; unknown must be null")
    checks = item["acceptance_checks"]
    md.require(isinstance(checks, dict) and set(checks) <= set(state["request"]["acceptance"]) and
               all(type(value) is bool or value is None for value in checks.values()), "Invalid acceptance checks")
    if item["outcome"] == "delivered":
        md.require(pending["action"]["kind"] == "deliver", "Delivery requires a deliver action")
        md.require(set(checks) == set(state["request"]["acceptance"]) and all(value is True for value in checks.values()), "Incomplete delivery evidence")
        md.require(item["reviewer"] and item["reviewer"] != item["executor"], "Independent delivery review required")
        md.require(not any(q.get("blocking", True) for key, q in state["unknowns"].items()
                           if key not in state["resolved"] | set(item["resolved_questions"])), "Blocking question remains")


def halted(state, now):
    if state["delivered"]:
        return "delivered"
    if state["stop_reason"]:
        return state["stop_reason"]
    if state["pending"]:
        return "needs_reconciliation" if state["pending"].get("unknown") else "awaiting_observation"
    if state["revision"] >= 998:
        return "journal_limit"
    if (now - md.utc(state["created_at"])).total_seconds() >= state["request"]["budget_seconds"]:
        return "budget_exhausted"
    if state["started"] >= state["request"]["max_actions"]:
        return "action_limit"
    if state["stalled"] >= 3:
        return "paused_no_progress"
    if state["plan"] is None and state["planned"] >= state["request"].get("max_plans", 4 * state["request"]["max_actions"]):
        return "plan_limit"
    return "active"


def apply(state, event, root):
    kind, item = event["kind"], event["data"]
    md.require(event["id"] not in state["event_ids"], "Duplicate event id")
    now = md.utc(event["at"])
    if kind == "plan":
        md.require(halted(state, now) == "active", "Run cannot accept a new plan")
        md.require(state["planned"] < state["request"].get("max_plans", 4 * state["request"]["max_actions"]), "Plan limit")
        plan_check(item, state, root)
        state["unknowns"].update({q["id"]: q for q in item["unknowns"]})
        state["plan"] = item
        state["planned"] += 1
    elif kind == "start":
        fields(item, {"action_id", "plan_id", "reason", "start_id"})
        md.text(item["reason"], "selection reason")
        md.identifier(item["start_id"])
        md.require(halted(state, now) == "active" and state["plan"] is not None, "No active plan")
        md.require(item["plan_id"] == state["plan"]["id"], "Stale selected plan")
        action = next((a for a in state["plan"]["actions"] if a["id"] == item["action_id"]), None)
        md.require(action is not None and not action["preconditions"], "Unknown action or unmet preconditions")
        remaining = state["request"]["budget_seconds"] - (now - md.utc(state["created_at"])).total_seconds()
        md.require(action["estimated_seconds"] <= remaining, "Action estimate exceeds remaining budget")
        if action["kind"] == "deliver":
            md.require(not any(q.get("blocking", True) for key, q in state["unknowns"].items() if key not in state["resolved"]), "Resolve blocking questions before delivery")
        state["pending"] = {"start_id": item["start_id"], "action": action, "started_at": event["at"], "plan_id": item["plan_id"]}
        state["started"] += 1
    elif kind == "observe":
        observation_check(item, state, root)
        state["observations"].append(item)
        if item["outcome"] == "unknown":
            state["pending"]["unknown"] = True
        else:
            state["resolved"].update(item["resolved_questions"])
            state["stalled"] = state["stalled"] + 1 if item["outcome"] in {"failed", "no_progress"} else 0
            state["delivered"] = item["outcome"] == "delivered"
            if state["delivered"]:
                state["delivered_at"] = event["at"]
            state["pending"] = None
            state["plan"] = None  # Every outcome requires an updated plan; no queued stale action.
    else:
        raise ValueError("Unknown learning event")
    state["event_ids"].add(event["id"])
    state["revision"] += 1
    if not state["pending"] and not state["stopped_at"]:
        reason = halted(state, now)
        if reason not in {"active", "delivered"}:
            state["stopped_at"], state["stop_reason"] = event["at"], reason


def replay(root, run_id, now):
    root = md.root_path(root)
    run_id = md.identifier(run_id)
    folder = md.local(root, "learning-runs/" + run_id)
    config, _, config_hash = md.read_md(md.local(root, "learning-runs/" + run_id + "/request.md"))
    fields(config, {"schema", "type", "id", "created_at", "request"})
    md.require(config["schema"] == 1 and config["type"] == "adaptive-run" and config["id"] == run_id, "Invalid run configuration")
    request_check(config["request"])
    previous_time = md.utc(config["created_at"])
    md.require(previous_time <= now, "Run starts in the future")
    state = blank(config["request"], config["created_at"])
    journal = md.local(root, "learning-runs/" + run_id + "/events")
    paths = []
    for path in journal.iterdir():
        if path.name.startswith(".pending-"):
            continue  # Unpublished crash remnants are not accepted journal events.
        md.require(len(path.name) == 9 and path.name[:6].isdigit() and path.suffix == ".md", "Invalid journal inventory")
        paths.append(path)
        md.require(len(paths) <= 1000, "Invalid journal inventory")
    paths.sort()
    previous_hash = config_hash
    for index, path in enumerate((p for p in paths if p.suffix == ".md"), 1):
        md.require(path.name == f"{index:06d}.md", "Journal sequence gap")
        event, _, event_hash = md.read_md(path)
        fields(event, {"schema", "type", "id", "kind", "at", "request_sha256", "previous_sha256", "data"})
        md.require(event["schema"] == 1 and event["type"] == "learning-event" and
                   event["request_sha256"] == config_hash and event["previous_sha256"] == previous_hash, "Journal binding changed")
        stamp = md.utc(event["at"])
        md.require(previous_time <= stamp <= now, "Invalid event chronology")
        apply(state, event, root)
        previous_time, previous_hash = stamp, event_hash
    return root, folder, state, config_hash, previous_hash, previous_time


def report(state, now):
    endpoint = md.utc(state["delivered_at"] or state["stopped_at"]) if state["delivered_at"] or state["stopped_at"] else now
    if not state["pending"] and not state["delivered_at"] and not state["stopped_at"]:
        endpoint = min(endpoint, md.utc(state["created_at"]) + timedelta(seconds=state["request"]["budget_seconds"]))
    elapsed = (endpoint - md.utc(state["created_at"])).total_seconds()
    remaining = max(0, state["request"]["budget_seconds"] - elapsed)
    ranked = []
    if state["plan"] and halted(state, now) == "active":
        for action in state["plan"]["actions"]:
            importance = max((state["unknowns"][key]["importance"] for key in action["question_ids"]), default=1)
            blockers = list(action["preconditions"])
            if action["estimated_seconds"] > remaining:
                blockers.append("estimate_exceeds_remaining_budget")
            if action["kind"] == "deliver" and any(q.get("blocking", True) for key, q in state["unknowns"].items() if key not in state["resolved"]):
                blockers.append("blocking_questions_remain")
            ranked.append({"id": action["id"], "kind": action["kind"], "description": action["description"],
                           "score": importance * action["expected_information_gain"] / action["estimated_seconds"],
                           "eligible": not blockers, "blockers": blockers,
                           "basis": "declared max question importance * estimated information gain / estimated seconds"})
        ranked.sort(key=lambda item: (not item["eligible"], -item["score"], item["id"]))
    costs = {}
    for key in ("tokens", "usd"):
        values = [o["cost"][key] for o in state["observations"] if o["cost"][key] is not None]
        total = sum(values)
        costs[key] = {"known_sum": total if md.number(total) else None,
                      "unknown_count": len(state["observations"]) - len(values), "scope": "declared nonoverlapping observation increments"}
    return {"revision": state["revision"], "state": halted(state, now), "goal": state["request"]["goal"],
            "elapsed_seconds_since_init": elapsed, "remaining_seconds": remaining,
            "budget_overrun": elapsed > state["request"]["budget_seconds"],
            "actions_started": state["started"], "plans_recorded": state["planned"],
            "pending": state["pending"], "unresolved_questions": [q for key, q in state["unknowns"].items() if key not in state["resolved"]],
            "ranked_actions": ranked, "recommended_action": next((r["id"] for r in ranked if r["eligible"]), None),
            "last_observation": state["observations"][-1] if state["observations"] else None,
            "cost": costs, "scheduler_registered": False,
            "scope": "Host-proposed decisions and declared outcomes; no model execution, authenticated identity, semantic truth or mastery certification"}


def init(root, run_id, request_md, now=None):
    now = md.clock(now); run_id = md.identifier(run_id)
    request, body, _ = md.read_md(Path(request_md))
    request_check(request)
    root = md.root_path(root, create=True)
    folder = md.local(root, "learning-runs/" + run_id); folder.mkdir(parents=True, exist_ok=True)
    with md.writer(folder):
        config = md.local(root, "learning-runs/" + run_id + "/request.md")
        md.require(not config.exists(), "Run already exists")
        journal = md.local(root, "learning-runs/" + run_id + "/events")
        md.require(not journal.exists() or not any(journal.iterdir()), "Existing run events")
        journal.mkdir(exist_ok=True)
        raw = md.encode({"schema": 1, "type": "adaptive-run", "id": run_id,
                         "created_at": now.isoformat(), "request": request}, body)
        md.decode(raw)  # Check the stored envelope size before exclusive publication.
        md.publish(config, raw)
    return status(root, run_id, now=now)


def append(root, run_id, kind, item, body, expected_revision, now=None):
    now = md.clock(now)
    root = md.root_path(root); folder = md.local(root, "learning-runs/" + md.identifier(run_id))
    with md.writer(folder):
        root, folder, state, config_hash, previous_hash, previous_time = replay(root, run_id, now)
        md.require(type(expected_revision) is int and expected_revision == state["revision"], "Stale writer revision")
        # Keep room for a lost receipt and its final reconciliation. Do not let
        # a full journal strand an already-started external action forever.
        limit = 998 if kind in {"plan", "start"} else 999 if item.get("outcome") == "unknown" else 1000
        md.require(state["revision"] < limit, "Event limit reached; capacity reserved for reconciliation")
        if kind == "plan":
            plan_check(item, state, root, fresh=True)
        if kind == "start":
            md.require(state["plan"] is not None, "No current plan")
            for ref in state["plan"]["experience_refs"]:
                import experience_transfer
                experience_transfer.verify_ref(root, ref)
            item = {**item, "plan_id": state["plan"]["id"], "start_id": "start-" + secrets.token_hex(12)}
        event = {"schema": 1, "type": "learning-event", "id": item.get("id", item.get("start_id")),
                 "kind": kind, "at": now.isoformat(), "request_sha256": config_hash,
                 "previous_sha256": previous_hash, "data": item}
        apply(state, event, root)
        raw = md.encode(event, body)
        md.decode(raw)
        json.dumps(report(state, now), allow_nan=False)  # A rejected report must not poison the journal.
        md.publish(folder / "events" / f"{state['revision']:06d}.md", raw)
    return status(root, run_id, now=now)


def plan(root, run_id, proposal_md, expected_revision, now=None):
    item, body, _ = md.read_md(Path(proposal_md))
    return append(root, run_id, "plan", item, body, expected_revision, now)


def start(root, run_id, action_id, expected_revision, reason="Host selected this action from the current plan.", now=None):
    return append(root, run_id, "start", {"action_id": md.identifier(action_id), "reason": reason}, reason, expected_revision, now)


def observe(root, run_id, observation_md, expected_revision, now=None):
    item, body, _ = md.read_md(Path(observation_md))
    return append(root, run_id, "observe", item, body, expected_revision, now)


def status(root, run_id, now=None):
    now = md.clock(now)
    return report(replay(root, run_id, now)[2], now)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    for command in ("init", "plan", "start", "observe", "status"):
        child = sub.add_parser(command)
        child.add_argument("--root", type=Path, required=True); child.add_argument("--id", required=True)
        if command == "init": child.add_argument("--request", type=Path, required=True)
        if command == "plan": child.add_argument("--proposal", type=Path, required=True)
        if command == "start":
            child.add_argument("--action", required=True)
            child.add_argument("--reason", default="Host selected this action from the current plan.")
        if command == "observe": child.add_argument("--observation", type=Path, required=True)
        if command in {"plan", "start", "observe"}: child.add_argument("--expected-revision", type=int, required=True)
    args = parser.parse_args()
    try:
        if args.command == "init": result = init(args.root, args.id, args.request)
        elif args.command == "plan": result = plan(args.root, args.id, args.proposal, args.expected_revision)
        elif args.command == "start": result = start(args.root, args.id, args.action, args.expected_revision, args.reason)
        elif args.command == "observe": result = observe(args.root, args.id, args.observation, args.expected_revision)
        else: result = status(args.root, args.id)
        print(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False))
        return 0
    except (ValueError, OSError, KeyError, TypeError, OverflowError) as error:
        print(json.dumps({"status": "REJECT", "error": str(error)}, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
