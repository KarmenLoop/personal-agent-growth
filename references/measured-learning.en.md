# Held-out tasks, complete cost records, and causal transfer

[简体中文](measured-learning.md)

Read this protocol when evaluating a strategy change, testing whether experience helps unfamiliar work, or claiming time or cost savings. Ordinary tasks can reuse an applicable strategy. New benefit claims require comparison. Markdown remains the learning-semantic source; native events and JSON outputs are evidence or derived views.

## Freeze strategies before releasing targets

Define the comparison unit, candidates, original quality criteria, visible model configuration, repetitions, complete budget and stopping rule. Preserve general and domain proposals separately; test any changed composition. Freeze candidate strategies before an independent author organizes held-out tasks from real failures. Executors receive neither reference answers, expected diagnoses nor the private evaluator.

`scripts/blind_trials.py` writes Markdown strategy freezes, binds subsequently released inputs and evaluator hashes, and generates seeded task/repetition blocks containing every arm. Use fresh context for each trial. Changed inputs or strategies invalidate the freeze. This does not certify novelty relative to model pretraining or provide OS-level isolation; the host controls workspaces, read-only evaluation and access review. Candidates cannot redefine their acceptance criteria.

Once a target is used for repair, retain it as development evidence and use an unexposed reserve for a new holdout claim. Label historical replay and new variants separately. Many assertions, commands or agreeing responses inside one task are not independent repetitions.

## Account for complete execution and missing values

Record input preparation, actual Agent execution through delivery, tool activity, failed retries, independent acceptance, review and publication boundaries. Include useful preparation, experience retrieval and repair in the task window. Research/review phase labels are declarations, not facts independently measured from process duration. Keep overall study setup, source preparation, tool development and release overhead visible rather than hiding or arbitrarily allocating it to one arm.

`scripts/task_costs.py` derives immutable Markdown records from hash-bound native Codex events, per-event host monotonic clocks and the full trial window. It records:

- Native input, cached input, output and available reasoning-token detail. Cached input is included in input; reasoning detail is included in output.
- Complete trial/process time, the union of observed tool intervals, overlapping phases and unattributed time.
- Failed native turns, reconnects, missing usage, command state and unknown fees.

Unattributed time can include model, network and host overhead; it is not measured inference time. Do not add a parent interval to its children. Missing usage is unknown, not zero. Preserve known counts and mark incomplete coverage after errors or reconnects. Without billing receipts, tokens measure resource consumption rather than money charged. Account-wide quota changes are not per-task charges. Hashes establish content identity, not provider authenticity.

For an authorized local CLI trial, `scripts/run_agent_trial.py` actually starts Codex, saves native events and clocks, bounds time and commands, runs an external evaluator separately, and invokes cost recording. Keep model, permissions, inputs, strategy and transport configuration consistent across arms. Reuse existing CLI sign-in without copying credentials or changing global configuration. Controlled runs can explicitly read the assigned Skill and omit unrelated automatic context. Stopping the local invocation does not prove remote billing stopped or external effects were undone; reconcile unknown effects before retrying.

## Transfer a mechanism and test its conditions

Existing `scripts/experience_transfer.py` supports legacy label retrieval and an optional `causal_model`: variable roles, directed relations and falsifiable predictions. Queries may supply `causal_context` and experience-specific `causal_mappings`. Deriving a model from a legacy lesson creates a sourced candidate; it does not overwrite the old record.

For each analogy, identify:

1. The source problem and actual supporting evidence.
2. Source-to-target variables and preservation of roles and directed relations.
3. Verified prerequisites, unknown conditions and the strongest counterexample.
4. An observable prediction and a result that would falsify the target application.
5. Actual artifacts and feedback after adopting, adapting or rejecting the lesson.

Explicit mappings can retrieve experiences without common labels. Reversed relations, merged distinct variables, role mismatches and a missing source model cannot validate an analogy. Condition conflicts and negative feedback still gate probing. Structural agreement proposes a hypothesis; it does not establish real causality, usefulness or new permission. Written predictions require actual execution to become evidence.

Optional fields extend the existing experience/query metadata. Variable IDs can change; the host explicitly aligns roles and relations. These examples define syntax, not an observed result.

```json
{"causal_model":{"variables":{"state":"context","claim":"decision"},"relations":[{"from":"state","to":"claim","relation":"conditions"}],"predictions":[{"intervention":"Change a prerequisite","expected":"Recheck the dependent claim","falsifier":"The claim has independent support"}]}}
```

The query's `causal_context` has the same graph shape. `causal_mappings` is indexed by source experience ID:

```json
{"causal_context":{"variables":{"target-state":"context","target-claim":"decision"},"relations":[{"from":"target-state","to":"target-claim","relation":"conditions"}],"predictions":[{"intervention":"Describe a target check","expected":"Describe the observable prediction","falsifier":"Describe contrary evidence"}]},"causal_mappings":{"source-experience-id":{"variables":{"state":"target-state","claim":"target-claim"},"rationale":"Why this relationship could transfer","prediction":"What to check in this task","falsifier":"What would reject the analogy"}}}
```

Use `experience_transfer.py add --root <root> --experience <candidate.md>`, followed by `retrieve --root <root> --query <query.md>` to inspect the mapping and blockers. JSON objects can serve as YAML frontmatter. Source artifacts still need actual paths and SHA-256 values; placeholders are not verified inputs.

## Adopt only within the supported scope

Independently check artifacts and relevant traces, then compare each task's complete repetitions, time and known resources. Retain successes, failures, cancellations and non-comparable attempts. Do not select the fastest trial or count passed assertions as task quality. Use existing PPC and regression gates; report quality, native tokens, time and billing coverage separately.

Two correct arms do not prove an improvement. Fewer tokens do not establish lower charges. A small portfolio does not establish general mastery. If a candidate misses the predeclared gain or quality/resource guardrails, retain the baseline and proposals without global activation. Later tasks must actually read, apply or reject the experience and preserve results to add transfer evidence.

<!-- Copyright (C) 2026 KARMENLOOP Official Team. SPDX-License-Identifier: AGPL-3.0-only -->
