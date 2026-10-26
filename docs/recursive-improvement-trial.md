# Propose–Probe–Compose: local development trial

Publication note, October 27, 2026: the report below records the earlier local trial and its original artifacts. Version 0.4.1 now includes the retained work with expanded bilingual documentation and Markdown learning contracts. Historical counts, hashes, and “unpublished” statements describe that earlier run, not the current release. See [current acceptance](release-0.4.1-acceptance.en.md).

This report covers the 0.4.0 development candidate on one Mac, using actual Codex Agent execution. It is not a released-version, Windows, Cursor, background-wakeup, or universal improvement result. No changes were pushed to GitHub during this work; the previously requested Windows Agent acceptance remains blocked by device availability.

A later [cross-domain complete-task trial](cross-domain-trial.md) measures whole-task quality, native tokens and elapsed time. Its results are separate from the checker-process counts reported here.

## Task and predeclared comparison

The useful task was to inspect three offline archive/manifest pairs and produce a reusable acceptance card. One pair used the published 0.3.2 archive, one was a clearly recorded controlled archive change, and one had an internally inconsistent manifest. These were local copies, not edits to the published release. The execution Agents received neutral case IDs and no prewritten verdict labels or answer key.

Before execution, the coordinator saved two proposals, full candidate snapshots, inputs, model configuration, acceptance criteria, and the evaluator. The original freeze SHA-256 was `e1da31322c28c8ef1d1637a97b69e87f9675b1802b376ac8ede56413b4dc84e5`.

- The general proposal added an explicit outcome and retry map.
- The domain proposal added a batch wrapper around the unchanged verifier.
- The baseline retained the original single-package command.

Each Agent used a separate context and write directory. Model settings were inherited with no overrides, and no training, fine-tuning, reinforcement learning, or parameter-update operation was used. The provider's weight digest and total Agent token/cost telemetry were not available.

The prespecified metric was checker subprocess launches, with a 20% minimum reduction and a candidate ceiling of three launches. It excluded model calls, preparation, report writing, and optimization overhead. Timing was captured but not used to rank candidates. The general arm launched its three checks concurrently; the baseline ran them sequentially. That difference prevents elapsed-time claims, but does not change the observed launch counts.

## Probe and Compose results

| Execution | Checker processes | Five fixed quality checks | Decision |
|---|---:|---|---|
| Baseline | 3 | All passed | Reference |
| General proposal | 3 | All passed | No demonstrated gain; drop the extra prompt map |
| Domain proposal | 1 | All passed | Retain batching within this domain |
| Composed successor | 1 | All passed | Activate the independently executed full snapshot |

The five checks covered all cases, consistency with the frozen verifier's actual output, input identity, raw receipts, and independently reviewed acceptance cards. A package REJECT or INCOMPLETE was a correct retained finding, not a quality-check failure. All four executions observed PASS/0, REJECT/1, and INCOMPLETE/2 for the three original cases. The coordinator reran the same fixed verifier constraints and inspected the cards; no prewritten answer labels were used as feedback. This task has observable deterministic constraints, so it does not validate quality judgments on open-ended work with no verifiable feedback.

Compose retained the working batch tool, discarded the redundant general prompt expansion, and rewrote concise routing and report-recovery rules. Component decisions referenced the actual Probe records. The successor and its evaluator routing adapter were frozen before a fourth, fresh-context Agent executed them. The adapter retained the original quality criteria and inputs. The composition gate also checked that the successor did not regress relative to the best qualified Probe.

Checker launches decreased from three to one: a **66.7% reduction in this metric**. This is not a 66.7% reduction in total Agent cost or runtime. Creating and running four variants incurred additional work; cumulative payback has not been established.

The [comparison JSON](evidence/recursive-0.4.0-comparison.json) and [sanitized process receipt summary](evidence/recursive-0.4.0-processes.json) record the measured results. The latter identifies the actual PIDs, timestamps, invocations, exits, and hashes of retained raw receipts. Host completion records are explicitly coordinator observations, not fabricated native event exports.

## Experience and limits

The composed snapshot was activated in a private experience library at revision 1. The library preserves the initial baseline, the adopted full snapshot, both proposals, independent evidence, composition decisions, and structured lessons. The learned selection rule is specific: use batching for matching independent offline checks, preserve each item's status and reached stage, and avoid adding a redundant prompt rule without new evidence.

A general-arm report-generation SyntaxError was retained and repaired without rerunning its checker. The resulting recovery lesson is a candidate rule; no controlled composed-arm report failure was induced. A new rule appearing in an accepted snapshot is not, by itself, proof that every rule improved behavior.

The CLI supports freezing and comparing task portfolios for outer-loop strategy changes. It requires transfer and regression task declarations, plus two domains for cross-domain promotion. Real portfolio execution is still performed and assessed by the host. This trial does not establish a generally better proposal generator, universal self-improvement, or a cross-domain performance gain.

## Actual reuse and review writeback

The Agent that originally ran the baseline later read library revision 1, opened the returned experience card and composed snapshot, and ran the tool directly from that version directory. The task variation relocated the input directory, changed case IDs and ordering, and introduced a missing archive. The actual results were:

| New case | Result | Reached stage |
|---|---|---|
| review-x | REJECT / 1 | completed_inspection |
| review-y | INCOMPLETE / 2 | read_archive |
| review-z | PASS / 0 | completed_inspection |

The missing-archive case reached a different failure stage from the earlier invalid-manifest case. The Agent recorded the current FileNotFoundError rather than reusing the old explanation, and the following valid case still completed. It used one real batch subprocess, PID 23514. The coordinator independently reproduced the same per-item results and checked that the executed tool's path and hash belonged to the selected library snapshot.

This review initially exposed a persistence gap: its output was saved, but the next library lookup would not retrieve it. The new `observe` command appends checked review evidence and lessons without replacing the active version or rewriting the original experience card. The actual append advanced the library to revision 2, and a fresh `select` returned both the original experience and the new observation. Tests cover stale revisions, changed evidence, and an observation referring to the wrong active version.

The coordinator entry skill is the 0.4.0 candidate; the task execution snapshot is derived from the original 0.3.2 skill and identified by its content hash `55ce7da5eab6024369167edaacecc7a5af41418c205443c495ce0475a2085e78`. Loading that execution snapshot does not replace the coordinator's improvement protocol. This is same-task variation and memory reuse, not a separate cross-domain strategy trial or automatic skill discovery test.

## Local checks and distribution

- 33 utility tests passed. Their synthetic gate fixtures test consistency and failure handling; they are separate from the real Agent executions above.
- The package builder initially exposed a stale eight-file test assumption. The test now checks the exact ten intended files, including the recursive protocol and comparison utility.
- Skill structure validation passed after installing PyYAML into an isolated validation directory. The initial missing-dependency failure remains recorded.
- The actual candidate ZIP passed 25 identity and content checks.
- All six Mermaid diagrams parsed. This establishes syntax validity, not a new browser rendering review.

Candidate archive SHA-256: `5341390f7a870aa991141b28c2121c5a6a3bde0418ccf887e0f3439f4db54df2`.

The candidate can be used by extracting the ZIP with its sibling manifest, checking both against the saved receipt, and asking the host to read the extracted `SKILL.md`. Use a separate private experiment and experience directory. The published [installation guide](install.md) continues to pin released version 0.3.2; it must not be described as installing this unpublished candidate.

Mechanism reference: the [official Harness² repository](https://github.com/google-research/harness2) describes Propose–Probe–Compose and persistent improvement experience with frozen model weights. This skill implements its own host-driven protocol and evidence utilities; it does not bundle the upstream runner or claim its benchmark gains.

<!-- Copyright (C) 2026 KARMENLOOP Official Team
SPDX-License-Identifier: AGPL-3.0-only -->
