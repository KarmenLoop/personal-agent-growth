#!/usr/bin/env python3
# Copyright (C) 2026 KARMENLOOP Official Team
# SPDX-License-Identifier: AGPL-3.0-only
"""Derive inspectable Markdown cost records from native Codex events and clocks.

This parser does not launch Agents, authenticate receipts, infer billing from
tokens, or equate process time with model inference time.
"""
import argparse
import json
from pathlib import Path
import sys

import capability_ledger as store

MAX_BYTES = 16 * 1024 * 1024
MAX_EVENTS = 100000
PHASES = {"preparation", "agent", "research", "retry", "grading", "review", "delivery"}


def count(value, name):
    store.require(type(value) is int and 0 <= value <= 2**63 - 1, "Invalid native " + name)
    return value


def seconds(value):
    store.require(store.number(value), "Invalid nonnegative finite duration")
    return value


def union_seconds(spans):
    """Elapsed union, so nested/concurrent spans do not inflate wall time."""
    intervals = []
    for start, end in spans:
        seconds(start); seconds(end)
        store.require(end >= start, "Reversed span")
        intervals.append((start, end))
    total, right = 0, 0
    for start, end in sorted(intervals):
        total += max(0, end - max(start, right))
        right = max(right, end)
    return total


def parse_jsonl(data):
    store.require(isinstance(data, bytes) and len(data) <= MAX_BYTES, "Oversized event stream")
    lines = data.decode("utf-8").splitlines()
    store.require(len(lines) <= MAX_EVENTS and all(line.strip() for line in lines), "Invalid event lines")
    records = []
    for line in lines:
        item = strict_json(line)
        store.require(isinstance(item, dict), "Event must be an object")
        records.append(item)
    return records


def strict_json(value):
    def unique(pairs):
        result = {}
        for key, item in pairs:
            store.require(key not in result, "Duplicate native JSON key")
            result[key] = item
        return result
    def finite(value):
        raise ValueError("Nonfinite native JSON value: " + value)
    return json.loads(value, object_pairs_hook=unique, parse_constant=finite)


def native_usage(events):
    totals = {"input_tokens": 0, "cached_input_tokens": 0, "output_tokens": 0}
    reasoning, sessions, completed, failed, errors = [], [], 0, 0, 0
    active = False
    commands, completed_commands = set(), set()
    for event in events:
        kind = event.get("type")
        if kind == "thread.started":
            value = store.text(event.get("thread_id"), "native thread id", 200)
            store.require(value not in sessions, "Duplicate native thread start")
            sessions.append(value)
        elif kind == "turn.started":
            store.require(not active, "Overlapping native turn starts")
            active = True
        elif kind in ("turn.completed", "turn.failed"):
            store.require(active, "Turn result without a unique start")
            active = False
            if kind == "turn.failed":
                failed += 1
                continue
            usage = event.get("usage")
            store.require(isinstance(usage, dict), "Missing native usage")
            values = {key: count(usage.get(key), key) for key in totals}
            store.require(values["cached_input_tokens"] <= values["input_tokens"], "Cached tokens exceed input tokens")
            detail = usage.get("reasoning_output_tokens")
            if detail is not None:
                count(detail, "reasoning_output_tokens")
                store.require(detail <= values["output_tokens"], "Reasoning detail exceeds output tokens")
            reasoning.append(detail)
            for key, value in values.items():
                totals[key] += value
                count(totals[key], key)
            completed += 1
        elif kind == "error":
            errors += 1
        if kind in ("item.started", "item.completed"):
            item = event.get("item", {})
            store.require(isinstance(item, dict), "Invalid native item")
            if item.get("type") == "command_execution":
                key = store.text(item.get("id"), "command item id", 200)
                commands.add(key)
                if kind == "item.completed":
                    store.require(key not in completed_commands, "Duplicate command completion")
                    completed_commands.add(key)
    store.require(len(sessions) <= 1 and (bool(sessions) or not completed),
                  "Completed attempts need exactly one native thread")
    complete = bool(completed) and not (active or failed or errors)
    if not completed:
        totals = {key: None for key in totals}
    return {**totals, "total_tokens": totals["input_tokens"] + totals["output_tokens"] if completed else None,
            "reasoning_output_tokens": sum(reasoning) if reasoning and all(v is not None for v in reasoning) else None,
            "native_turns_completed": completed, "native_turns_failed": failed,
            "native_error_events": errors, "coverage": "complete_reported_turns" if complete else "partial_or_unavailable",
            "session_ids": sessions, "command_items": len(commands),
            "unfinished_command_items": sorted(commands - completed_commands),
            "billed_usd": None, "billing_status": "Not supplied by these native events; not zero",
            "scope": "Host-returned token counts only; cached input is included in input and reasoning detail is included in output. Failed/unreturned provider attempts may be unmetered."}


def timing_summary(events, timeline, measurement):
    store.require(isinstance(measurement, dict), "Measurement must be an object")
    elapsed = seconds(measurement.get("elapsed_seconds"))
    agent_start = seconds(measurement.get("agent_start_offset"))
    agent_elapsed = seconds(measurement.get("agent_elapsed_seconds"))
    store.require(agent_start + agent_elapsed <= elapsed + 1e-6, "Agent interval exceeds complete task")
    store.require(type(measurement.get("exit_code")) is int, "Process exit code required")
    store.require(len(timeline) == len(events), "Event clock coverage differs")
    offsets, last = [], 0
    for index, item in enumerate(timeline):
        store.require(set(item) == {"event_index", "offset_seconds"} and
                      type(item["event_index"]) is int and item["event_index"] == index,
                      "Event clock index differs")
        offset = seconds(item["offset_seconds"])
        store.require(last <= offset <= agent_elapsed + 1e-6, "Event clock outside process or unordered")
        offsets.append(offset); last = offset
    starts, ended, spans = {}, set(), []
    for index, event in enumerate(events):
        item = event.get("item", {})
        store.require(isinstance(item, dict), "Invalid native item")
        if item.get("type") != "command_execution":
            continue
        key = item.get("id")
        if event.get("type") == "item.started":
            store.require(key not in starts, "Duplicate command clock start")
            starts[key] = offsets[index]
        elif event.get("type") == "item.completed" and key in starts:
            store.require(key not in ended, "Duplicate command clock result")
            spans.append((starts[key], offsets[index])); ended.add(key)
    phases = {key: [] for key in PHASES}
    declared = measurement.get("phase_spans", [])
    store.require(isinstance(declared, list) and len(declared) <= 1000, "Invalid phase spans")
    for item in declared:
        store.require(set(item) == {"phase", "start", "end"} and item["phase"] in PHASES,
                      "Invalid measured phase")
        start, end = seconds(item["start"]), seconds(item["end"])
        store.require(start <= end <= elapsed + 1e-6, "Phase outside complete task")
        phases[item["phase"]].append((start, end))
    tool_seconds = union_seconds(spans)
    return {"complete_task_seconds": elapsed, "agent_process_seconds": agent_elapsed,
            "observed_command_union_seconds": tool_seconds,
            "unattributed_agent_seconds": max(0, agent_elapsed - tool_seconds),
            "model_inference_seconds": None,
            "phase_union_seconds": {key: union_seconds(value) if value else None for key, value in phases.items()},
            "all_declared_phases_union_seconds": union_seconds([(p["start"], p["end"]) for p in declared]),
            "open_command_clocks": sorted(set(starts) - ended),
            "phase_semantics": "Phase labels are recorder declarations; overlapping phases are not additive. Unattributed time includes model/network/host overhead, not measured inference time."}


def record(root, request_md):
    root = store.root_path(root)
    request, body, _ = store.read_md(Path(request_md))
    keys = {"id", "type", "task_id", "arm", "replicate", "attempt", "model_config", "events", "timeline", "measurement"}
    store.require(set(request) == keys and request["type"] == "task-cost-request", "Invalid cost request fields")
    for key in ("id", "task_id", "arm"):
        store.identifier(request[key])
    for key in ("replicate", "attempt"):
        store.require(type(request[key]) is int and request[key] >= 1, "Invalid cost attempt identity")
    store.require(isinstance(request["model_config"], dict) and request["model_config"].get("model") and
                  request["model_config"].get("training") is False, "Visible frozen model declaration required")
    refs = [request[key] for key in ("events", "timeline", "measurement")]
    contents = {}
    for key in ("events", "timeline", "measurement"):
        ref = request[key]
        store.require(isinstance(ref, dict) and set(ref) == {"path", "sha256"}, "Invalid cost source reference")
        source = store.local(root, ref["path"])
        store.require(source.is_file() and source.stat().st_size <= MAX_BYTES, "Missing or oversized cost source")
        data = source.read_bytes()
        store.require(len(data) <= MAX_BYTES, "Oversized cost source")
        store.require(store.sha(data) == ref["sha256"], "Cost source changed")
        contents[key] = data
    events, timeline = parse_jsonl(contents["events"]), parse_jsonl(contents["timeline"])
    measurement = strict_json(contents["measurement"])
    result = {"id": request["id"], "type": "task-cost", "task_id": request["task_id"],
              "arm": request["arm"], "replicate": request["replicate"], "attempt": request["attempt"],
              "model_config": request["model_config"], "created_at": store.clock().isoformat(),
              "sources": refs, "usage": native_usage(events), "timing": timing_summary(events, timeline, measurement),
              "process_exit_code": measurement["exit_code"], "source_authentication": "Hashes establish content identity, not provider authenticity"}
    # Recheck after parsing so a changed source cannot produce a current-looking record.
    for ref in refs:
        store.require(store.sha(store.local(root, ref["path"]).read_bytes()) == ref["sha256"], "Cost source changed during parsing")
    target = store.local(root, "trial-costs/" + request["id"] + ".md")
    target.parent.mkdir(parents=True, exist_ok=True)
    raw = store.encode(result, body)
    store.require(len(raw) <= 1024 * 1024, "Cost record exceeds readable size")
    store.publish(target, raw)
    return {"path": str(target), "sha256": store.sha(target.read_bytes()), "record": result}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--request", type=Path, required=True)
    args = parser.parse_args()
    try:
        result = record(args.root, args.request)
    except (OSError, ValueError, KeyError, UnicodeError) as error:
        print(json.dumps({"status": "error", "error": str(error)})); return 2
    print(json.dumps(result, ensure_ascii=False)); return 0


if __name__ == "__main__":
    sys.exit(main())
