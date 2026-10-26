---
name: personal-agent-growth
description: Complete ongoing tasks that need preparation, evidence-based revision, review, shared memory, or bounded recursive improvement of prompts, tools and workflow components. Use for recovery, cross-host continuation, repeated rework, and project learning; handle simple independent requests directly.
license: AGPL-3.0-only
metadata:
  version: "0.4.1"
---

# Personal Agent Growth

[中文 canonical entry](SKILL.md). This is the English translation, not a second installed skill. Keep one discovery entry pointing to this folder.

Complete the user's current objective and retain evidence, changed decisions, and reusable learning. The host supplies tools and wakeups; this skill does not start a background process.

## Optional existing handoff adapter

For the legacy SQLite checkpoint mode, follow the [host tutorial](docs/tutorial.en.md#adapter) to configure the Python 3.11+ CLI/MCP adapter. Verify actual calls and saved state. Keep it separate from Markdown learning; it does not supply host scheduling, identity accounts, or remote execution.

## Markdown learning

For daily, weekly, project, and behavior-based learning, read the [Markdown protocol](references/markdown-learning.en.md). Markdown is the sole learning-semantic truth. Resume with context and the latest node; use published scoring, source correction, and relevant injection. Legacy adapter state and experiment JSON have separate responsibilities, not another writable profile.

## Start and recover

Find current goal, state, preferences, decisions, and results. Use the user's chosen location; otherwise keep a task-local record rather than initializing a global profile/library. Complete simple tasks directly.

For complex work, identify goal, acceptance, scope, actual capabilities, and decisive unknowns. Preserve predictions, checks, and failure/unknown continuations before key actions. On recovery inspect real artifacts rather than repeating work because an old status says running. See [task records](references/task-record.en.md). For cross-host work, read [shared memory](references/shared-memory.en.md), check identity, workspace mappings, and writer, and resume the current phase.

## Decide what to do next

Separate observations, explanations, and unknowns. Important claims carry sources, scope, and counterexamples. Compare time, applicability, and authority when sources conflict. Revisit dependent decisions when new evidence changes judgment; independent useful work continues.

Choose among research, asking, a small experiment, execution, and waiting. Before collecting more information, identify which choices it distinguishes and how outcomes change action. Verify public facts independently. Ask with alternatives only for user-owned choices. Give exploration a stopping condition.

Check whether local success advances the whole objective. Attribute tool failure to its actual layer. A checker not run, an unknown result, and a failed business criterion remain distinct.

Bind every result to the inspected object/version, environment, reached stage, and raw output. If the object or directory changed, reassess attribution before reusing a conclusion. An exit code or PASS label alone is insufficient. Retain each attempt's command, output, and status before repair; label missing original output rather than replacing it with a retrospective summary.

## Learn and improve

When recursive improvement is enabled, read [Propose–Probe–Compose](references/recursive-improvement.en.md). Propose a general and domain change for each new task, run both against baseline, and compose from observed contrasts. A changed composition requires its own test. Within authorized scope, revise prompts, tools, context, rules, and orchestration, adopt qualified versions, and retain rollback without repeatedly asking for routine choices. Keep model configuration fixed, with no training/fine-tuning/RL; record unknown provider weight identity. Account for inner/outer loops separately and retain useful, ineffective, and failed proposals for actual later loading.

Prepare bounded knowledge needed by the next step and check whether it was used. After an error, form a cause hypothesis, learn specifically, and return to the original task. Review with variations or new work rather than recitation.

Decide whether the needed change concerns knowledge, interpretation, capability matching, environment, or the skill. For a method defect, preserve the old version, edit a candidate, and compare the original and meaningful other scenarios. See [learning and contact](references/learning-and-contact.en.md).

## Contact and future work

Read current contact preferences. Under decision-only contact, retain solvable findings in records and ask only about a choice that changes action and belongs to the user. Present completed work, options, and effects; combine related questions and continue independent work while waiting.

Prefer the relevant existing chat. New chats, cross-chat messages, and automations depend on user authorization and actual host capabilities. Do not create them merely to demonstrate initiative.

Schedule only concrete future work. For registration, recovery, interval changes, or stopping, use [autonomous continuation](references/autonomous-continuation.en.md) and verified host APIs. Learn immediately when the work can be done now.

## Deliver and continue

Deliver artifacts, changed judgments and evidence, remaining unknowns, and the next condition. Distinguish file checks, actual Agent adoption, new-scenario/independent reuse, and second-host/cross-turn/no-new-message behavior. Claim only the level actually evidenced. Retain useful experience with applicability; local validation does not replace every existing capability.

## Offline package checking

For ZIP and this manifest format, run `scripts/verify_handoff.py --archive <zip> --manifest <manifest>`. It checks input consistency and binds results to program, input, environment, and stage. Validate actual usability separately for the task's purpose.

Resolve Markdown references relative to their containing file, distinguishing local resources, external links, fragments, and code examples. Archive consistency, readability, and portability are separate acceptance layers. Current readability or a target inside the package does not establish relocation stability; symbolic links may depend on old absolute paths. Actually move an isolated copy before claiming portability, or limit the conclusion. Zero checks or unsupported syntax do not establish complete usability.


<!-- Copyright (C) 2026 KARMENLOOP Official Team. SPDX-License-Identifier: AGPL-3.0-only -->
