# Autonomous wakeup and result continuation

[中文](autonomous-continuation.md)

Use for useful future work, scheduled recovery, interval changes, and stopping. The skill provides decision rules; actual execution depends on verified host interfaces, login state, and workspace.

## Make pending work recoverable

Before registration, retain task ID and goal revision, current phase, verified artifacts, next action, acceptance, contact policy, owner, expiry, and run limit. Settings depend on purpose/cost rather than fixed trial minute intervals.

Every follow-up must explain what will become actionable then. Do current work now. Schedule for new input, spaced review, or external results. Use the actual backend, bind the task/session, preserve its return, and read configuration back. Prefer updating an existing related binding over creating duplicates.

| State | Evidence |
|---|---|
| planned | Saved purpose and next action |
| registered | Backend acceptance and verified ID, target, status, schedule |
| triggered | Actual host event and corresponding turn; local numbers are only indices |
| executed | Real calls, input identity, artifacts, exits, raw returns |
| verified | Later reuse and completion checking |
| stopped | Backend pause/delete confirmed, local final state saved |

File timestamps, manual continuation, subagent messages, or ACTIVE alone do not replace actual trigger evidence.

## On each wakeup

1. Read binding/current state and check trigger, goal version, cancellation, expiry, budget, and writer. A late event for finished/cancelled work verifies stopping and skips duplicates.
2. Inspect artifacts before choosing a recovery step. If an action finished before state persistence, reconcile using its real receipt. Inspect an unknown external effect before retrying.
3. Save a prediction, prepare/execute/review as appropriate. Attribute discrepancies to input, method, environment, permission, or reached stage. Repair locally and return to the task.
4. Preserve results and unknowns. Choose continuation, focused remediation, interval change, a user decision, or completion, with a concrete next action and stop rule.
5. Perform backend updates and read back before marking them effective. After acceptance, actually pause/delete and verify the backend before final completion.

If a backend update succeeded before local persistence failed, repair from readback/receipts rather than creating another binding. If the backend is unavailable, retain the exact failure, independent completed work, and unregistered next action. Ask only for a decision the user must make.

## Establish learning

Preparation works backward from use with prediction and conditions. Review actually reuses prior artifacts/methods through a variation. Preserve prior judgment, new evidence, change, and retest. Repeating an old answer or creating more files is insufficient.

When one host schedules and another executes, record both responsibilities and actual behavior. A receiver's proposed action is not registered scheduling. Copying a skill cannot transfer a native scheduler.

## Contact

Follow current user preference. Under decision-only contact, solve and record ordinary findings; combine material choices into one question. Final delivery and per-run notifications are different. Preserve final facts and recovery conditions at termination rather than contacting indefinitely.


<!-- Copyright (C) 2026 KARMENLOOP Official Team. SPDX-License-Identifier: AGPL-3.0-only -->
