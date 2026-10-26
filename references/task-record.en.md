# Task records

[中文](task-record.md)

Reuse existing task records. A small task can use one Markdown file or operational JSON record; useful relationships matter more than file count. In Markdown learning mode, learning facts and conclusions remain in MD; JSON may hold raw operational receipts.

| Object | Required relationships |
|---|---|
| Goal | ID, revision, desired outcome, acceptance, scope |
| Evidence | ID, source, actual observation, time, covered scope |
| Interpretation | ID, revision, explanation, support/opposition, conditions |
| Decision | Goal/interpretation revisions, options, choice, prediction, revision condition |
| Action | Decision, actual call, result, evidence location |
| Learning | Trigger, cause hypothesis, changed object, validation, applicability |
| Contact | User decision needed, related questions, reply state, independent work |
| Continuation | Condition, owner, state, actual backend ID or not_registered |

Fix important predictions before acting. Append observations and revisions afterward. Label retrospective notes and reference original returns; they are not prior predictions. For a tool failure, identify which stage was not reached. A checker that never started leaves its target unjudged.

Bind each result to target ID/path, version/hash, environment, exact tool input, reached stage, exit, raw output, and conclusion scope. Reassess reuse when the object/version changes. Historical failures do not automatically belong to a new candidate.

Share an index of current goals, decisions, and results. The portable skill carries the method; private task state and contact preferences are supplied separately through authorized materials. Skill copies do not transfer those states automatically.

Use task-relative references, with host absolute locations in configuration. Exclude private user records, credentials, and machine environment from skill distribution. A learned method needs actual sources/results; multiple summaries of one source are not independent evidence.


<!-- Copyright (C) 2026 KARMENLOOP Official Team. SPDX-License-Identifier: AGPL-3.0-only -->
