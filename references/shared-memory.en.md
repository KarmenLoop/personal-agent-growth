# Shared memory and cross-tool recovery

[中文](shared-memory.md)

Use when another host/session resumes work or reads a shared library. Methods can be shared; user state, credentials, execution permissions, and scheduling are verified separately.

## Identify the same task

Read the supplied root and entry index instead of scanning all user history. Check task ID, goal revision, state revision, completed stage, pending work, artifact hashes, and writer. An old completed state does not complete a new goal; old unverified items do not erase later evidence.

Operational task state needs to express:

```json
{
  "task_id": "task-specific-id",
  "goal_revision": 1,
  "state_revision": 1,
  "status": "ready",
  "phase": "next-useful-phase",
  "writer": "host-or-agent-id",
  "completed": [],
  "input_index": "inputs/index.json",
  "contact_policy": "memory/preferences.json",
  "next_action": "a concrete action and its completion condition",
  "schedule": {"owner_host": null, "backend_id": null, "status": "not_registered"}
}
```

This is the existing operational format. New Markdown learning mode represents its learning/project facts in context/node/memory metadata and does not add this JSON as a second mutable authority. Reuse existing fields. Facts, preferences, explanations, and candidate experience retain sources, scope, and invalidation rules. Frequent relevant facts can be indexed; load the rest on demand. Unknown habits and private attributes stay unknown.

## One content source and a clear writer

On one computer, hosts read one actual task directory and may discover one linked skill. Record resolved paths and hashes; equal strings do not prove equal files. Cross-device use needs authorized transfer/synchronization and path mapping. Absolute paths, credentials, session handles, and permissions do not move automatically.

The responsible writer serializes mutable state. Read the revision before work and again before commit. If it changed, reconcile real facts or wait for responsibility rather than overwriting. Persist artifacts, receipts, and next action before transferring writer and incrementing revision. Read back after writing.

Before appending experience, inspect existing IDs; use a writer prefix or unique ID instead of guessing the next number from conversation memory. On collision, preserve both sources, the prior snapshot, and an ID mapping. Late queued messages reread writer/revision and skip already-completed corrections.

The receiving tool must actually read, use the memory, complete work, and write back. A handoff message alone is insufficient. Acceptance checks input/output identity and may reuse artifacts independently.

For a stronger continuity check, after a real responsibility return add a useful new decision or counterexample and increment revision. The next receiver identifies which revision and lesson changed action, then saves a real review. Repeating old chat is not evidence of reading new memory. If host scheduling is stored separately, preserve its binding/owner rather than treating one host's lack of registration as no schedule anywhere.

## Match host capabilities

Inspect available interfaces. CLI and desktop login state differ. Switch through an already-authorized usable entry when available, recording the choice, rather than copying credentials. A button, activity indicator, or generated panel establishes only that observation, not saved files or executed checks.

Keep explicit reading, discovery, selection, execution, and useful results separate. A directory's existence does not establish automatic selection. Explicit-path loading is a valid labeled fallback.

If the receiving host lacks a verified scheduler, return that responsibility to a capable owner and record not_registered locally. Complete immediately actionable work without manufacturing additional waiting or chats.

## Offline packages

`verify_handoff.py` returns actual input identity, environment, and stage. Exit 0 means consistent, 1 an inspected inconsistency, 2 incomplete inspection. After integrity checks, verify resources, environment, or behavior required by the current purpose. Claim readable, usable, or cross-host execution only with corresponding actual evidence.


<!-- Copyright (C) 2026 KARMENLOOP Official Team. SPDX-License-Identifier: AGPL-3.0-only -->
