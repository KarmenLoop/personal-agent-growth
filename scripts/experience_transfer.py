#!/usr/bin/env python3
# Copyright (C) 2026 KARMENLOOP Official Team
# SPDX-License-Identifier: AGPL-3.0-only
"""Retrieve cross-domain hypotheses from immutable Markdown mechanism experiences.

Labels are open, normalized exact matches supplied by the host, not semantic
embeddings. A domain match alone never admits a candidate. The helper checks
declarations and evidence consistency; it neither authenticates reviewers nor
establishes causation, transfer, permission, or mastery. Supported means the
declared original scope only. JSON stdout is derived; Markdown is the truth.
"""
import argparse
import json
from pathlib import Path
import re
import sys
import unicodedata

import capability_ledger as store
import causal_models as causal

EXPERIENCE_KEYS = {"id", "type", "source_task_id", "domain", "problem_structure", "mechanisms",
                   "required_conditions", "exceptions", "intervention", "explanation", "validation",
                   "executor", "reviewer", "artifacts"}
QUERY_KEYS = {"id", "type", "task_id", "domain", "problem_structure", "mechanisms", "facts", "keywords"}
OBSERVATION_KEYS = {"id", "type", "task_id", "domain", "conditions", "outcome", "adaptation", "finding",
                    "executor", "reviewer", "artifacts"}
EXPERIENCE_INTERNAL = {"schema", "created_at"}
OBSERVATION_INTERNAL = {"sequence", "experience_sha256", "previous_sha256", "recorded_at"}
REF_KEYS = {"path", "sha256", "revision", "head_sha256"}
MAX_RECORDS = 1000
BASE = "experience/mechanism"


def normal(value):
    store.text(value, "label", 200)
    return " ".join(unicodedata.normalize("NFKC", value).casefold().split())


def fields(item, keys, optional=()):
    store.require(isinstance(item, dict) and keys <= set(item) <= keys | set(optional),
                  "Invalid metadata fields")


def labels(values, label):
    store.require(isinstance(values, list) and len(values) <= 50, "Invalid " + label)
    out = [normal(value) for value in values]
    store.require(len(set(out)) == len(out), "Duplicate normalized " + label)
    return set(out)


def facts(values, allow_unknown=False):
    store.require(isinstance(values, dict) and len(values) <= 50, "Invalid conditions")
    result = {}
    for key, value in values.items():
        key = normal(key)
        store.require(key not in result, "Duplicate normalized condition")
        store.require(type(value) is bool or (allow_unknown and value is None), "Condition must be boolean")
        result[key] = value
    return result


def actors(item, independent):
    executor = store.text(item["executor"], "executor", 200)
    reviewer = item["reviewer"]
    if reviewer is not None:
        store.text(reviewer, "reviewer", 200)
    if independent:
        store.require(reviewer is not None and normal(reviewer) != normal(executor),
                      "Distinct declared reviewer required")


def experience_check(root, item, stored=False):
    fields(item, EXPERIENCE_KEYS | (EXPERIENCE_INTERNAL if stored else set()), {"causal_model"})
    store.require(item["type"] == "mechanism-experience", "Invalid experience type")
    store.identifier(item["id"]); store.identifier(item["source_task_id"])
    normal(item["domain"])
    structure = labels(item["problem_structure"], "problem structure")
    mechanisms = labels(item["mechanisms"], "mechanisms")
    store.require(structure or mechanisms, "Structural or mechanism labels required")
    facts(item["required_conditions"])
    store.require(isinstance(item["exceptions"], list) and 1 <= len(item["exceptions"]) <= 50,
                  "At least one exception or limitation required")
    for limitation in item["exceptions"]:
        store.text(limitation, "exception")
    store.text(item["intervention"], "intervention"); store.text(item["explanation"], "explanation")
    store.require(item["validation"] in ("hypothesis", "supported"), "Invalid validation status")
    actors(item, item["validation"] == "supported")
    store.artifacts(root, item["artifacts"], True)
    if "causal_model" in item:
        causal.graph_check(item["causal_model"])
    if stored:
        store.require(type(item["schema"]) is int and item["schema"] == 1, "Unsupported experience schema")
        store.require(store.utc(item["created_at"]) <= store.clock(), "Future experience timestamp")


def query_check(item):
    fields(item, QUERY_KEYS, {"causal_context", "causal_mappings"})
    store.require(item["type"] == "transfer-query", "Invalid query type")
    store.identifier(item["id"]); store.identifier(item["task_id"])
    normal(item["domain"])
    labels(item["problem_structure"], "problem structure"); labels(item["mechanisms"], "mechanisms")
    labels(item["keywords"], "keywords"); facts(item["facts"], True)
    if "causal_context" in item:
        causal.graph_check(item["causal_context"])
    if "causal_mappings" in item:
        causal.mappings_check(item["causal_mappings"], item.get("causal_context"))


def observation_check(root, item, source, stored=False):
    fields(item, OBSERVATION_KEYS | (OBSERVATION_INTERNAL if stored else set()))
    store.require(item["type"] == "transfer-observation", "Invalid observation type")
    store.identifier(item["id"]); store.identifier(item["task_id"])
    store.require(normal(item["task_id"]) != normal(source["source_task_id"]), "A different task is required")
    normal(item["domain"])
    store.require(bool(facts(item["conditions"])), "Observed context conditions required")
    store.require(item["outcome"] in ("helpful", "harmful", "inconclusive"), "Invalid outcome")
    store.text(item["adaptation"], "adaptation"); store.text(item["finding"], "finding")
    actors(item, item["outcome"] == "helpful")
    store.artifacts(root, item["artifacts"], True)


def folder_for(root, experience_id):
    return store.local(root, BASE + "/" + store.identifier(experience_id))


def bounded_entries(folder, limit):
    entries = []
    for path in folder.iterdir():
        if path.name.startswith(".pending-") or path.name == ".writer.lock":
            continue
        entries.append(path)
        store.require(len(entries) <= limit, "Record limit exceeded")
    return sorted(entries, key=lambda p: p.name)


def _read(root, experience_id):
    folder_for(root, experience_id)
    path = store.local(root, BASE + "/" + experience_id + "/experience.md")
    experience, body, source_hash = store.read_md(path)
    experience_check(root, experience, True)
    store.require(experience["id"] == experience_id, "Experience identity differs from path")
    observations_path = store.local(root, BASE + "/" + experience_id + "/observations")
    store.require(observations_path.is_dir(), "Missing observations directory")
    observations = []
    refs = [{"path": path.relative_to(root).as_posix(), "sha256": source_hash}]
    seen = set()
    previous = source_hash
    last_time = store.utc(experience["created_at"])
    for sequence, event_path in enumerate(bounded_entries(observations_path, MAX_RECORDS), 1):
        store.require(event_path.name == f"{sequence:06}.md", "Noncontiguous observation journal")
        event_path = store.local(root, event_path.relative_to(root).as_posix())
        event, event_body, event_hash = store.read_md(event_path)
        observation_check(root, event, experience, True)
        store.require(type(event["sequence"]) is int and event["sequence"] == sequence,
                      "Invalid observation sequence")
        store.require(event["experience_sha256"] == source_hash and event["previous_sha256"] == previous,
                      "Observation binding changed")
        stamp = store.utc(event["recorded_at"])
        store.require(last_time <= stamp <= store.clock(), "Invalid observation time")
        store.require(normal(event["id"]) not in seen, "Duplicate observation id")
        seen.add(normal(event["id"]))
        previous, last_time = event_hash, stamp
        refs.append({"path": event_path.relative_to(root).as_posix(), "sha256": event_hash})
        observations.append({"metadata": event, "body": event_body, "ref": refs[-1]})
    snapshot = {**refs[0], "revision": len(observations), "head_sha256": previous}
    return {"id": experience_id, "revision": len(observations), "experience": experience, "body": body,
            "observations": observations, "snapshot_ref": snapshot, "evidence_refs": refs,
            "scope": "Declared experience and verified file identities; no authenticated actors or semantic proof"}


def status(root, experience_id):
    return _read(store.root_path(root), experience_id)


def verify_ref(root, ref):
    fields(ref, REF_KEYS)
    store.require(type(ref["revision"]) is int and 0 <= ref["revision"] <= MAX_RECORDS, "Invalid snapshot revision")
    for key in ("sha256", "head_sha256"):
        store.require(isinstance(ref[key], str) and re.fullmatch(r"[0-9a-f]{64}", ref[key]), "Invalid snapshot hash")
    store.require(isinstance(ref["path"], str), "Invalid snapshot path")
    parts = ref["path"].split("/")
    store.require(len(parts) == 4 and parts[:2] == ["experience", "mechanism"] and parts[-1] == "experience.md",
                  "Invalid experience snapshot path")
    result = status(root, parts[2])
    store.require(result["snapshot_ref"] == ref, "Experience snapshot is stale")
    return result


def add(root, experience_md):
    root = store.root_path(root, create=True)
    item, body, _ = store.read_md(Path(experience_md))
    experience_check(root, item)
    parent = store.local(root, BASE)
    parent.mkdir(parents=True, exist_ok=True)
    with store.writer(parent):
        names = bounded_entries(parent, MAX_RECORDS)
        store.require(len(names) < MAX_RECORDS, "Record limit exceeded")
        store.require(not any(normal(p.name) == normal(item["id"]) for p in names), "Experience already exists")
        raw = store.encode({**item, "schema": 1, "created_at": store.clock().isoformat()}, body)
        store.require(len(raw) <= 1024 * 1024, "Markdown exceeds 1 MiB")
        folder = folder_for(root, item["id"])
        folder.mkdir()
        (folder / "observations").mkdir()
        store.publish(folder / "experience.md", raw)
    return status(root, item["id"])


def observe(root, experience_id, observation_md, expected_revision):
    root = store.root_path(root)
    store.require(type(expected_revision) is int and expected_revision >= 0, "Invalid expected revision")
    folder = folder_for(root, experience_id)
    with store.writer(folder):
        current = _read(root, experience_id)
        store.require(current["revision"] == expected_revision, "Stale revision; no observation written")
        store.require(expected_revision < MAX_RECORDS, "Record limit exceeded")
        item, body, _ = store.read_md(Path(observation_md))
        observation_check(root, item, current["experience"])
        seen = {normal(record["metadata"]["id"]) for record in current["observations"]}
        store.require(normal(item["id"]) not in seen, "Duplicate observation id")
        stamp = store.clock()
        last = (current["observations"][-1]["metadata"]["recorded_at"] if current["observations"]
                else current["experience"]["created_at"])
        store.require(stamp >= store.utc(last), "Clock precedes previous observation")
        item = {**item, "sequence": expected_revision + 1,
                "experience_sha256": current["snapshot_ref"]["sha256"],
                "previous_sha256": current["snapshot_ref"]["head_sha256"], "recorded_at": stamp.isoformat()}
        raw = store.encode(item, body)
        store.require(len(raw) <= 1024 * 1024, "Markdown exceeds 1 MiB")
        store.publish(folder / "observations" / f"{expected_revision + 1:06}.md", raw)
    return status(root, experience_id)


def similarity(a, b):
    return len(a & b) / len(a | b) if a | b else 0


def feedback_for(current, query):
    query_facts = facts(query["facts"], True)
    feedback = []
    for record in current["observations"]:
        event = record["metadata"]
        same_domain = normal(event["domain"]) == normal(query["domain"])
        # A foreign counterexample is useful to inspect, but its applicability
        # is not established in the target domain by label overlap alone.
        if not same_domain and event["outcome"] != "harmful":
            continue
        conditions = facts(event["conditions"])
        if any(query_facts.get(key) is not None and query_facts[key] != value for key, value in conditions.items()):
            continue
        missing = sorted(key for key in conditions if query_facts.get(key) is None)
        feedback.append({"id": event["id"], "task_id": event["task_id"], "outcome": event["outcome"],
                         "finding": event["finding"], "adaptation": event["adaptation"],
                         "conditions": event["conditions"], "source_domain": event["domain"],
                         "target_domain": query["domain"],
                         "target_scope": "same-domain" if same_domain else "cross-domain-unverified",
                         "context_match": "unknown" if missing else "matched", "unresolved_conditions": missing,
                         "ref": record["ref"]})
    return feedback


def retrieve(root, query_md, limit=5):
    root = store.root_path(root)
    store.require(type(limit) is int and 1 <= limit <= 50, "Limit must be 1..50")
    query, _, query_hash = store.read_md(Path(query_md))
    query_check(query)
    structure, mechanisms = labels(query["problem_structure"], "structure"), labels(query["mechanisms"], "mechanisms")
    query_facts = facts(query["facts"], True)
    keywords = labels(query["keywords"], "keywords")
    candidates, errors = [], []
    parent = store.local(root, BASE)
    entries = bounded_entries(parent, MAX_RECORDS) if parent.exists() else []
    for folder in entries:
        try:
            current = _read(root, folder.name)
            item = current["experience"]
            old_structure, old_mechanisms = labels(item["problem_structure"], "structure"), labels(item["mechanisms"], "mechanisms")
            smatch, mmatch = structure & old_structure, mechanisms & old_mechanisms
            analogy = causal.match(item.get("causal_model"), query.get("causal_context"),
                                   query.get("causal_mappings", {}).get(item["id"]))
            if not (smatch or mmatch or analogy["compatible"] is True):
                continue
            requirements = facts(item["required_conditions"])
            unresolved = sorted(key for key in requirements if query_facts.get(key) is None)
            conflicting = sorted(key for key, value in requirements.items()
                                 if query_facts.get(key) is not None and query_facts[key] != value)
            domain_match = normal(query["domain"]) == normal(item["domain"])
            corpus = unicodedata.normalize("NFKC", item["intervention"] + " " + item["explanation"] + " " + current["body"]).casefold()
            kmatch = sorted(key for key in keywords if key in corpus)
            feedback = feedback_for(current, query)
            scoped_harm = [row for row in feedback if row["outcome"] == "harmful" and row["target_scope"] == "same-domain"]
            known_harm = any(row["context_match"] == "matched" for row in scoped_harm)
            possible_harm = bool(scoped_harm)
            relevance = (0.35 * similarity(structure, old_structure) + 0.55 * similarity(mechanisms, old_mechanisms)
                         + 0.05 * domain_match + 0.05 * len(kmatch) / max(1, len(keywords)))
            score = max(0.0, relevance - (0.4 if known_harm else 0))
            candidates.append({"id": item["id"], "score": round(score, 6), "relevance_before_feedback": round(relevance, 6),
                               "matches": {"problem_structure": sorted(smatch), "mechanisms": sorted(mmatch),
                                           "keywords": kmatch, "domain_match": domain_match},
                               "unresolved_conditions": unresolved, "conflicting_conditions": conflicting,
                               "relevant_feedback": feedback,
                               "counterexample_review_required": any(row["target_scope"] == "cross-domain-unverified" for row in feedback),
                               "causal_match": analogy,
                               "eligible_for_probe": not (unresolved or conflicting or possible_harm or
                                                          analogy["compatible"] is False),
                               "adaptation_required": True, "experience": item, "body": current["body"],
                               "snapshot_ref": current["snapshot_ref"], "evidence_refs": current["evidence_refs"]})
        except (ValueError, OSError, UnicodeError) as error:
            errors.append({"entry": folder.name, "error": str(error)})
    candidates.sort(key=lambda item: (item["causal_match"]["compatible"] is not True,
                                     -item["score"], item["id"]))
    return {"query_id": query["id"], "query_sha256": query_hash, "task_id": query["task_id"],
            "candidates": candidates[:limit], "matched_count": len(candidates), "errors": errors,
            "ranking": "Explicit structurally compatible causal mappings first; remaining heuristic is 0.35 structure Jaccard + 0.55 mechanism Jaccard + 0.05 domain + 0.05 keyword fraction; matching same-domain harmful feedback subtracts 0.4; foreign counterexamples require review without automatic penalty. Neither ranking is a causal probability.",
            "scope": "Heuristic hypothesis retrieval, not semantic matching, authorization, automatic activation or proof of transfer"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    for command in ("add", "retrieve", "observe", "status"):
        child = sub.add_parser(command)
        child.add_argument("--root", type=Path, required=True)
        if command == "add": child.add_argument("--experience", type=Path, required=True)
        if command == "retrieve":
            child.add_argument("--query", type=Path, required=True); child.add_argument("--limit", type=int, default=5)
        if command in ("observe", "status"): child.add_argument("--id", required=True)
        if command == "observe":
            child.add_argument("--observation", type=Path, required=True); child.add_argument("--expected-revision", type=int, required=True)
    args = parser.parse_args()
    try:
        if args.command == "add": result = add(args.root, args.experience)
        elif args.command == "retrieve": result = retrieve(args.root, args.query, args.limit)
        elif args.command == "observe": result = observe(args.root, args.id, args.observation, args.expected_revision)
        else: result = status(args.root, args.id)
        print(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False))
        return 2 if result.get("errors") else 0
    except (ValueError, OSError, UnicodeError) as error:
        print(json.dumps({"error": str(error), "status": "REJECTED"}, ensure_ascii=False))
        return 2


if __name__ == "__main__":
    sys.exit(main())
