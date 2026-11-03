# From a learning plan to a verifiable action

A 15-minute contributor workshop for Personal Agent Growth 0.6.0.

You will run both adaptive helpers, inspect a deliberately rejected stale command, and explain which work belongs to the host Agent. You need Python 3.11+, a checkout containing both helpers, a terminal, and the adjacent `practice.py`. The helper uses the Python standard library. Allow setup time before the workshop; the 15-minute agenda is a facilitation target, not a measured completion time.

## What you should be able to do

- Retrieve a candidate by matching structure or mechanism labels and check its conditions.
- Distinguish a plan, a recorded start, a real host action, and an observation.
- Recover from an expected stale-revision rejection without deleting the failure.
- Explain why a fixture pass is neither reviewed delivery nor evidence that a person learned.

## The 15-minute session

| Minute | Do this | Visible result |
| --- | --- | --- |
| 0–2 | Read the four distinctions below. Predict whether `start` writes the result file. | One sentence saved before running. |
| 2–4 | Inspect `practice.py`, especially the fixture labels and `reviewer: None`. Set the three paths. | A valid checkout and a fresh output path. |
| 4–8 | Run the practice once. Read the stale failure and successful start receipts. | Eight CLI calls, including one expected rejection. |
| 8–11 | Trace the actual host write into the observation's artifact hash. Inspect final status. | Revision 3, `active`, no pending action, latest outcome `progress`. |
| 11–14 | Attempt the independent variation below. Explain a different-domain analogy and its limit. | A prediction, new query, and inspected output. |
| 14–15 | Use the exit check. Keep failed or incomplete work with the next step. | A short evidence-based handoff. |

## Four distinctions to keep visible

`experience_transfer.py` retrieves declared labels and checks conditions. It does not infer arbitrary synonyms or prove a causal mechanism. A different domain can match; a shared domain alone cannot admit a candidate. Read the candidate's original scope, exceptions, feedback, and complete `snapshot_ref` before reusing it.

`adaptive_learning.py plan` saves proposed questions and actions. Its score uses declared importance, information gain, and duration estimates. It is a suggestion, not a measured learning-speed score.

`start` saves intent and a start token. The host still executes the action. `observe` binds the result to that token and to real artifacts. After a known terminal outcome clears the pending action, propose the next action against the current revision; do not continue an old queue silently. An `unknown` outcome keeps the same pending action and start token: reconcile its actual effect before any new plan or retry.

`progress` can be recorded without a reviewer. `delivered` requires a started delivery action, resolved blocking questions, exact acceptance checks, artifacts, and an actual independent review. Different actor strings alone do not establish independence.

## Run the controlled practice

These are POSIX-shell commands. Set `PYTHON` to a Python 3.11+ executable, `SKILL_DIR` to your checkout, and `WORKSHOP_DIR` to the folder containing this handout and `practice.py`. Use a fresh `LAB_DIR`; the script refuses an existing directory so earlier failures survive. Windows users can pass the same flags in PowerShell using their Python executable and native paths; that shell variant has not been tested for this handout.

```sh
PYTHON="python3"
SKILL_DIR="/absolute/path/to/personal-agent-growth"
WORKSHOP_DIR="/absolute/path/to/workshop"
LAB_DIR="/absolute/path/to/new-workshop-lab"
"$PYTHON" --version
"$PYTHON" -B "$WORKSHOP_DIR/practice.py" --skill "$SKILL_DIR" --work "$LAB_DIR"
```

The script uses an explicitly controlled experience fixture, not a purported real historical lesson. It invokes the actual helpers using subprocesses and keeps exact argument arrays, raw stdout/stderr, actual timestamps, exit codes, and hashes in numbered receipt folders. It does not simulate a reviewer or declare delivery.

Read these files after it runs:

```sh
cat "$LAB_DIR/05-stale-start/stderr.txt"
cat "$LAB_DIR/06-start/stdout.txt"
cat "$LAB_DIR/learning/host-action.json"
cat "$LAB_DIR/08-status/stdout.txt"
cat "$LAB_DIR/summary.json"
```

The exact failed call is equivalent to the following command after the plan has advanced the run to revision 1. Do not rerun it against a later state and call that the same attempt.

```sh
"$PYTHON" -B "$SKILL_DIR/scripts/adaptive_learning.py" start --root "$LAB_DIR/learning" --id practice --action write-evidence --expected-revision 0
```

Expect exit 2 with a stale-revision diagnostic. The script retains this rejection, then uses the known current revision 1. In real work, inspect status and pending effects before choosing the next command; an unknown effect must be reconciled, not blindly repeated.

## Independent variation: make one condition unknown

Before looking at the answer, predict what happens when `decision-can-be-revised` changes from `true` to `null` in a new query. Copy `learning/query.md` to a new file, give it a new ID, and change only that fact. Keep the original. Run:

```sh
"$PYTHON" -B "$SKILL_DIR/scripts/experience_transfer.py" retrieve --root "$LAB_DIR/learning" --query "$LAB_DIR/learning/query-unknown.md"
```

Explain whether the candidate disappears or remains with a blocked probe. What evidence would establish the condition in a real task? Then name a domain other than software and describe one corresponding relationship and one difference that could invalidate the analogy. Merely renaming the domain is not transfer.

<details>
<summary>Check after predicting and running</summary>

The matching candidate should remain, with `decision-can-be-revised` in `unresolved_conditions` and `eligible_for_probe` false. Do not change the fact back just to obtain eligibility. Establish it with actual evidence first. A label mismatch can instead yield zero candidates, because this is explicit-label retrieval.

</details>

## Exit check and failure diagnosis

Pass the exercise only if you can point to the saved prediction, the expected failed receipt, the successful start token, the host's separate file write, and the matching observation artifact. Explain why final `active`/`progress` is correct here. Have another contributor inspect the independent variation and explanation before claiming teaching success.

| Observation | Meaning and next action |
| --- | --- |
| Stale start exits 2 | Expected exercise outcome. Read current revision; keep this failed attempt. |
| A different command exits nonzero | An unplanned failure. Keep stdout/stderr and diagnose the first failed operation before starting a fresh lab. |
| No candidate matches | Inspect structure/mechanism vocabulary. Do not claim no relevant knowledge exists. |
| Candidate has unknown/conflicting conditions | Investigate conditions or reject the analogy; a score is not authority. |
| Receipt exists, but its artifact is missing or changed | Evidence is not valid for that claim. Preserve the original attempt and recheck the actual object. |
| Script runs, but explanation or variation fails | CLI execution succeeded; teaching acceptance remains open. Repair that specific misunderstanding. |

## Sources and scope

Project sources, inspected for this workshop: [adaptive tutorial](https://github.com/KarmenLoop/personal-agent-growth/blob/main/docs/adaptive-learning.en.md), [adaptive protocol](https://github.com/KarmenLoop/personal-agent-growth/blob/main/references/adaptive-learning.en.md), [capability protocol](https://github.com/KarmenLoop/personal-agent-growth/blob/main/references/capability-learning.en.md), and the actual `--help` and source for `scripts/adaptive_learning.py` and `scripts/experience_transfer.py`. The local source fingerprint in the evidence bundle identifies the tested candidate; moving `main` links may differ from that candidate.

This workshop borrows the project's prediction, practice, feedback, and bounded-claim approach. It makes no claim about measured human learning, delayed retention, fixed-weight model improvement, universal transfer, or adopted PPC policy. The lab checks a controlled CLI contract. Actual teaching effectiveness needs independent learner work.

Copyright (C) 2026 KARMENLOOP Official Team. SPDX-License-Identifier: AGPL-3.0-only
