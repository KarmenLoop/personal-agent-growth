# Adaptive learning tutorial · 0.6.0

[中文](adaptive-learning.zh-CN.md) · [Runtime protocol](../references/adaptive-learning.en.md) · [Mechanism and feedback map](diagrams/adaptive-learning.en.svg)

This extension adds cross-domain candidate retrieval and a replayable learning-action loop. Python 3.11+ and the standard library are sufficient. The host Agent supplies interpretations, proposals, real tool actions, and semantic review. The helpers do not supply a model, an autonomous background worker, or a fixed domain curriculum.

## One root, two related records

Choose the actual shared Markdown root. Existing projects, daily reviews, capability records, and legacy experience remain in place.

```text
learning/
  projects/<project-id>/context.md
  projects/<project-id>/nodes/...
  experience/mechanism/<experience-id>/
    experience.md
    observations/000001.md
  learning-runs/<run-id>/
    request.md
    events/000001.md
  evidence/<task-id>/...
```

The mechanism experience is immutable source knowledge plus separately appended use feedback. The learning run records decisions for one current task. They are not duplicate editable summaries. JSON printed by a command is derived output. Keep actual artifacts outside the immutable journals and use stable copies when a file will change later.

All input documents below use a JSON object as YAML 1.2 front matter. Arbitrary YAML is not supported by these standard-library readers. Every artifact path is relative to the learning root, regardless of where an input document is stored. Replace actor identities, findings, paths, and hashes with actual evidence. The sample hash placeholders deliberately cannot pass unchanged. These examples are templates, not completed Agent trials.

Run the commands from the installed Skill directory. Replace `/absolute/learning` and input-document paths. On Windows use `py -3 -B -X utf8` instead of `python3 -B` and your actual D: or C: path; commands below are single lines.

## 1. Add a mechanism experience

Save an input such as `experience-input.md`:
```markdown
---
{
  "id": "batch-setup",
  "type": "mechanism-experience",
  "source_task_id": "software-batch-01",
  "domain": "software",
  "problem_structure": [
    "repeated-setup",
    "independent-items"
  ],
  "mechanisms": [
    "setup-amortization"
  ],
  "required_conditions": {
    "setup-repeatable": true
  },
  "exceptions": [
    "Check quality, deadlines and resource contention before applying outside the source task."
  ],
  "intervention": "Group independent items when shared setup dominates the source task.",
  "explanation": "Grouping reduced repeated setup in the source task; usefulness elsewhere is a hypothesis.",
  "validation": "hypothesis",
  "executor": "replace-with-actual-host-session",
  "reviewer": null,
  "artifacts": [
    {
      "path": "evidence/source-result.md",
      "sha256": "replace-with-actual-64-character-sha256"
    }
  ]
}
---
## Source scope
Describe the original task, actual result, alternative explanations, and what still needs testing.
```

```sh
python3 -B scripts/experience_transfer.py add --root /absolute/learning --experience /absolute/experience-input.md
python3 -B scripts/experience_transfer.py status --root /absolute/learning --id batch-setup
```

`validation` may be `hypothesis` or `supported`. Supported requires a distinct declared reviewer and verified artifacts; it describes the original scope, not universal applicability. The helper checks declarations and bytes, not truth or actor authenticity. To revise a lesson, create a new ID with links to the old lesson and contrary evidence in the body; retain the original.

## 2. Retrieve for an unfamiliar domain

Save `query.md`:
```markdown
---
{
  "id": "query-new-work",
  "type": "transfer-query",
  "task_id": "new-task-01",
  "domain": "unfamiliar-service",
  "problem_structure": [
    "repeated-setup"
  ],
  "mechanisms": [
    "setup-amortization"
  ],
  "facts": {
    "setup-repeatable": null
  },
  "keywords": [
    "setup"
  ]
}
---
## Mapping to check
Explain why these relationship labels may connect the old and new tasks, and where the analogy could fail.
```

```sh
python3 -B scripts/experience_transfer.py retrieve --root /absolute/learning --query /absolute/query.md --limit 5
```

At least one problem-structure or mechanism label must match. A shared domain or keyword alone does not admit a candidate. Labels are normalized for Unicode, case, and whitespace; the host must explicitly align synonyms and languages. This is transparent structural-label retrieval, not an embedding model or automatic causal discovery.

Inspect the matched labels, unresolved and conflicting conditions, original text, and relevant feedback. In this example `setup-repeatable` is unknown, so the candidate cannot be used as an eligible probe until that condition is actually established. Eligibility permits considering a probe; it does not grant authority or prove the old intervention will work. Same-domain harmful feedback blocks reuse when its conditions match, or when facts needed to assess them remain unknown. Harm from another domain remains visible as an unverified counterexample when its conditions do not contradict the query; it does not automatically reduce the score or block probing.

A candidate includes `snapshot_ref` with `path`, `sha256`, `revision`, and `head_sha256`. Use that entire object in a learning plan's `experience_refs`; it binds both the immutable lesson and the observed feedback revision. `evidence_refs` are artifact-style path/hash pairs. Never invent a revision or copy only the lesson hash when feedback has changed.

## 3. Start a bounded learning run

Save `request.md`:
```markdown
---
{
  "id": "request-new-work",
  "type": "learning-request",
  "goal": "Determine whether batching helps this new task without reducing quality.",
  "domain": "unfamiliar-service",
  "acceptance": [
    "Recommendation is supported by the supplied evidence.",
    "Quality and timing tradeoffs are stated."
  ],
  "budget_seconds": 1800,
  "max_actions": 6,
  "allowed_actions": [
    "retrieve",
    "research",
    "experiment",
    "reflect",
    "deliver"
  ]
}
---
## Context and authority
State the user goal, current constraints, permitted inputs and actions, and why the task matters.
```

```sh
python3 -B scripts/adaptive_learning.py init --root /absolute/learning --id new-task --request /absolute/request.md
python3 -B scripts/adaptive_learning.py status --root /absolute/learning --id new-task
```

The run starts at revision 0. Its budget is elapsed wall time since initialization, including planning and waiting inside this run; prior setup is not included. The helper cannot terminate a host tool or meter its native charges. It prevents starting more work after its limits, records overrun, and still permits reconciliation of an action that already started.

Optional `max_plans` caps planning events at 1–400; its default is four times `max_actions`. Each `estimated_seconds` must be between 0.001 and 604800. A stored Markdown record cannot exceed 1 MiB. A run has at most 1000 events: the controller stops new plans and starts at revision 998, refuses further `unknown` reports at 999, and reserves the final slot for reconciling a pending action. Completion, action/plan limits, and repeated no-progress freeze recorded elapsed time; an unresolved pending action continues to accrue time. These bounds prevent an expanding loop from silently consuming unlimited work. `allowed_actions` accepts `research`, `retrieve`, `experiment`, `tool`, `reflect`, `deliver`, and `ask`. These are operation types, not subject restrictions. Include `ask` only when the task may require an actual user choice or operation; do not use it for routine uncertainty the Agent can investigate.

## 4. Propose and choose the next useful action

Save `plan.md`:
```markdown
---
{
  "id": "plan-inspect",
  "type": "learning-plan",
  "based_on_revision": 0,
  "unknowns": [
    {
      "id": "conditions",
      "question": "Can setup be shared without breaking the new task quality requirement?",
      "importance": 1.0,
      "blocking": true
    }
  ],
  "actions": [
    {
      "id": "inspect-evidence",
      "kind": "research",
      "question_ids": [
        "conditions"
      ],
      "description": "Inspect source evidence and identify the local setup and quality constraints.",
      "expected_information_gain": 0.8,
      "estimated_seconds": 120,
      "preconditions": []
    }
  ],
  "experience_refs": [],
  "artifacts": []
}
---
## Prediction
State what each plausible observation would change. This sample has no bound experience; insert a real snapshot_ref when relying on a retrieved lesson.
```

```sh
python3 -B scripts/adaptive_learning.py plan --root /absolute/learning --id new-task --proposal /absolute/plan.md --expected-revision 0
python3 -B scripts/adaptive_learning.py start --root /absolute/learning --id new-task --action inspect-evidence --reason "Resolve the condition that determines whether the analogy is usable." --expected-revision 1
```

A successful plan advances to revision 1; start advances to 2 and returns `pending.start_id`. Preserve the actual token for the observation. Starting registers intent; now the host must perform the real permitted action and retain its receipts.

The score is the maximum addressed question importance multiplied by estimated information gain and divided by estimated seconds. These declared estimates are not measured intelligence or speed. The host may choose another eligible candidate and provide a reason. Nonempty `preconditions` are unresolved blockers; obtain evidence and issue a new plan rather than merely deleting inconvenient constraints.

Every unresolved question must remain in later plans. Questions default to `blocking: true`; explicitly nonblocking exploration does not prevent delivery. To replace an incorrect question, first resolve or reject it with evidence, then introduce a new identity. Do not rename it to hide an unresolved issue.

## 5. Record actual feedback and replan

After the host action, save `observation.md`:
```markdown
---
{
  "id": "observation-inspect",
  "type": "learning-observation",
  "start_id": "replace-with-returned-pending-start-id",
  "action_id": "inspect-evidence",
  "outcome": "progress",
  "finding": "Replace with the actual observation and its limits.",
  "hypothesis_change": "Replace with the reason for keeping, narrowing or rejecting the proposed mechanism.",
  "resolved_questions": [],
  "artifacts": [
    {
      "path": "evidence/new-task-result.md",
      "sha256": "replace-with-actual-64-character-sha256"
    }
  ],
  "executor": "replace-with-actual-host-session",
  "reviewer": null,
  "cost": {
    "tokens": null,
    "usd": null
  },
  "acceptance_checks": {}
}
---
## Actual execution
Preserve commands, inputs, stdout/stderr, exits, artifact identities, received assistance, and the exact basis for the judgment.
```

```sh
python3 -B scripts/adaptive_learning.py observe --root /absolute/learning --id new-task --observation /absolute/observation.md --expected-revision 2
python3 -B scripts/adaptive_learning.py status --root /absolute/learning --id new-task
```

A terminal observation advances to revision 3 and clears the plan. The next proposal must use the new revision and current evidence; old queued actions cannot continue silently. Resolve only questions targeted by the action and supported by its result. `failed` and `no_progress` cannot mark questions resolved. A refuted hypothesis can still be `progress` when actual evidence resolved the question; explain the distinction.

Use `unknown` when the action's effect is not known. It keeps the same pending action and start token, enters reconciliation state, and prevents a blind retry or new plan. It may have no artifacts, but requires an explicit finding. Later observations can reconcile that same start, including after the budget expires. Do not invent a successful outcome to unlock the next action.

Tokens and charges are declared nonoverlapping increments; leave them null when unavailable. An unknown report followed by its reconciliation must not charge the same native usage twice. Consecutive failed/no-progress outcomes pause new work after three such outcomes. Completion, limits, and pending reconciliation are separate states.

## 6. Return transfer feedback to the next task

When the old lesson was actually applied or probed in a different task, save a use observation. This harmful-outcome template is appropriate only when actual evidence supports that result:
```markdown
---
{
  "id": "use-new-work",
  "type": "transfer-observation",
  "task_id": "new-task-01",
  "domain": "unfamiliar-service",
  "conditions": {
    "setup-repeatable": true,
    "quality-sensitive-to-delay": true
  },
  "outcome": "harmful",
  "adaptation": "Replace with the actual adaptation and permitted test.",
  "finding": "Replace with evidence that applying the old intervention harmed the current acceptance criterion.",
  "executor": "replace-with-actual-host-session",
  "reviewer": null,
  "artifacts": [
    {
      "path": "evidence/new-task-result.md",
      "sha256": "replace-with-actual-64-character-sha256"
    }
  ]
}
---
## Boundary learned
Explain the changed condition and the next test. A failed analogy may teach a useful boundary; it does not justify deleting the original experience.
```

```sh
python3 -B scripts/experience_transfer.py observe --root /absolute/learning --id batch-setup --observation /absolute/use.md --expected-revision 0
```

Relevant feedback includes `source_domain`, `target_domain`, `target_scope` (`same-domain` or `cross-domain-unverified`), and the original `adaptation`. A candidate with such a cross-domain harmful counterexample sets `counterexample_review_required: true`. The host reviews whether the mechanism and conditions apply; the flag alone does not change `eligible_for_probe`. Helpful or inconclusive observations from another domain do not become target-domain support.

Read the actual experience revision before writing. Helpful feedback requires a distinct declared reviewer; harmful or inconclusive feedback can retain a null reviewer. Conditions are observed boolean facts, not guesses. Automatic score and eligibility penalties from negative feedback apply to the recorded normalized domain and matching or unresolved contextual conditions; they do not automatically apply to unrelated contexts. Rerun retrieval with the new task's actual facts and read the returned feedback before choosing.

Learning-run observations do not automatically write transfer observations. These are distinct records: what happened in the current task and what it means for reusing a particular source lesson. The host saves and verifies both where applicable. New feedback invalidates an older plan snapshot; retrieve again and make a fresh plan before starting an action that depends on the changed lesson.

## 7. Deliver and preserve the next useful question

After resolving all blocking questions, propose a `deliver` action. A `delivered` observation must have that action's actual start token, real artifacts, a reviewer different from the executor, and `acceptance_checks` containing exactly every request acceptance string with value `true`. This consistency check cannot decide whether the artifact is useful; the reviewer must inspect it. Leave other outcomes' checks empty or record only supported checks.

Read back status, update project context and a node, and link candidate experience and actual use feedback. A new host reads these same files before continuing. A pending action requires reconciliation, not an automatic repeat. CLI exits 2 on invalid/stale/drifted input; retrieval can return valid candidates plus entry errors and still exit 2. Inspect the errors rather than discarding them and claiming complete coverage.

## Worked example: old software experience changes in a new setting

The following is a design example, not a field trial or a measured improvement. An Agent knows that grouping independent software jobs can reduce repeated setup. It is asked to improve an unfamiliar service workflow while keeping quality and waiting acceptable. It retrieves the setup-amortization mechanism, learns the actual stages and resource constraints, and tests whether the grouping assumption holds.

If observations show that grouping shortens preparation but creates unacceptable delay for some items, the Agent must reject that intervention under those conditions. It retains the original software evidence, records the harmful transfer context, and derives a narrower candidate: shared setup can be useful when delay-sensitive quality and deadlines remain satisfied. The next action investigates those constraints rather than adding more parallel workers by default.

A later software task with strict per-item deadlines can retrieve both the old benefit and this new boundary. The new field has therefore changed what the Agent checks in its original field. Whether that improves the later task still requires actual execution and review.

## Preserve the two-layer improvement contract

The loop can introduce new questions and actions; it does not autonomously rewrite its own acceptance or budget. Changes to prompts, tools, retrieval, or the learning policy still enter [PPC](../references/recursive-improvement.en.md), including actual baseline/general/domain comparisons and composition validation. [Capability evidence](capability-learning.en.md) remains separately scoped. Register any meaningful future review through the actual host scheduler; neither helper performs background execution.
