# Resume an adaptive run with an uncertain outcome

Use the same explicit Markdown root, task ID, and current helper version. Read the task context and latest node, then inspect the actual run. A saved `start` records an intention; the host executes the effect. An observation records the host's evidence and judgment. None of these authenticates an actor or registers a wakeup.

```sh
python3 -B "$SKILL/scripts/adaptive_learning.py" status --root "$ROOT" --id "$RUN_ID"
```

Set `SKILL` to the skill checkout, `ROOT` to the existing shared learning root, and `RUN_ID` to the original run ID. Capture stdout, stderr, exit code, command, UTC times and helper hash. Keep immutable journal events and earlier failed attempts. Never repair recovery by editing an old observation or deleting a pending event.

| Current status | Operator decision | Evidence required before proceeding |
| --- | --- | --- |
| `active`, `pending: null` | There is no pending action. Inspect latest observation and current revision. Propose a fresh plan when no current plan exists; start an eligible action only after checking its preconditions and remaining limits. | Current root/run identity; preserved prior outcome; current artifact hashes and any experience snapshot; evidence that a repeated external effect is safe. |
| `awaiting_observation` | A start exists. Determine whether the host ran its effect; do not start it again just because stdout or the observation receipt is missing. | Original `pending.start_id`, `pending.action.id`, tool receipt and actual effect. If the result remains uncertain, record `unknown` against that exact start. |
| `needs_reconciliation` | Preserve the same pending action and start token. Inspect the external system or file read-only. Do not make a new plan or repeat the effect. | Correlate actual effect identity/content with the intended operation and original start. Resolve only what the evidence demonstrates. |
| `delivered` | Read the recorded delivery artifacts and review. No further action belongs to this delivered run. A distinct authorized new task requires its own run. | Recorded acceptance checks and independent review, plus the actual usable artifacts. A declaration alone is not semantic acceptance. |
| `budget_exhausted`, `action_limit`, `plan_limit`, `journal_limit` | Stop launching work under this run. Preserve status and handoff. Do not raise limits or create a fresh run merely to bypass the limit. | A newly authorized scope/budget if further work is needed. The helper does not provide an in-place limit extension command. |
| `paused_no_progress` | Three terminal failed/no-progress observations stopped useful continuation. Diagnose the obstacle and hand off the evidence. | A changed condition and authorized next scope; renaming an action is not progress. |

A pending action takes precedence over ordinary limits: `awaiting_observation` or `needs_reconciliation` can still appear when elapsed budget has run out. Reconciliation records the result of already-started work; it does not grant a new effect. Once settled, the run may immediately report an exhausted limit. The helper reserves journal room for settlement, but corrupted or externally modified history may still prevent replay.

## Reconcile without repeating

1. Read status. If the missing observation was actually committed, the current status/journal already shows it. Inspect it; do not submit the old observation again. JSON stdout is a derived view; Markdown is the durable record.
2. Preserve the original unknown event, pending start token, action ID, command and any partial output. Check the effect using a read-only source: exact file content, a provider's operation ID, or another authoritative receipt. A missing local receipt alone does not prove the effect never happened.
3. If the effect is complete and attributable, submit a new observation using the **same pending `start_id` and action ID**, the fresh `revision`, and hash-bound evidence. For ordinary completed work use `progress`. If a known terminal failure occurred, `failed` may be appropriate; explicitly retain any partial effects. Unknown, failed and no-progress outcomes cannot resolve questions.
4. If the effect remains ambiguous, preserve `unknown`. Do not convert uncertainty to `failed` to clear the slot. Escalate when the operator lacks read access, attribution is ambiguous, repeated execution could have consequences, or recovery requires an unapproved external change. Present the known effect, missing evidence, and concrete choices to the user.
5. After an accepted **known terminal** observation, the helper clears both pending and old plan. Read status again. A fresh plan at the new revision is required before another action, and only if the run is active. A terminal failure is not proof that repeating its external effect is safe.

Write observations as Markdown with JSON front matter. Copy the live start/action IDs rather than generating replacements. Supply `id`, `type: learning-observation`, `start_id`, `action_id`, `outcome`, `finding`, `hypothesis_change`, `resolved_questions`, `artifacts`, `executor`, `reviewer`, `cost`, and `acceptance_checks`. Non-unknown outcomes require existing root-relative artifacts with SHA-256. Unknown native token/USD costs are `null`. The drill's generated `inputs/settle-original-start.md` is a concrete example; its token and hashes belong only to that drill.

```sh
python3 -B "$SKILL/scripts/adaptive_learning.py" observe \
  --root "$ROOT" --id "$RUN_ID" \
  --observation "$OBSERVATION_MD" --expected-revision "$CURRENT_REVISION"
```

A stale revision or different start must be rejected. Keep the rejection and reread status; do not blindly replace the expected revision and resend. Confirm that the intended pending action is still the same. If hashes or journal binding fail, preserve the files and investigate provenance; never silently rewrite history to make the helper accept it.

`delivered` additionally requires a deliver-kind pending action, all declared acceptance checks true, no unresolved blocking questions, and a distinct declared reviewer. Obtain actual independent review first. The helper checks declarations and file identities, not the truth of the review. Do not use a fictional reviewer to finish a drill.

## Run the controlled drill

Requires Python 3.11+ and the current skill checkout. The script is standalone and writes only under a new work directory outside the checkout. Paths may contain spaces. Do not use Python's `-O`: this drill uses assertions for checks.

```sh
python3 -B ./recovery_drill.reviewed.py --skill /path/to/personal-agent-growth --work /path/to/new-recovery-drill
```

The drill performs one exclusive real file write and deliberately withholds its outcome observation. This is controlled uncertainty, not a real crash or lost infrastructure. It records unknown, rejects replanning while pending, obtains a genuine start from a separate no-effect fixture, rejects that foreign token, inspects the original file, and settles the original action without writing its effect again. The main run then reports `action_limit` because its single permitted action is used. The foreign fixture is truthfully closed as failed because its intended effect was deliberately not attempted. No delivery reviewer is invented.

Inspect `summary.json`, `effect-inspection.json`, `controlled-uncertainty.json`, `memory/effect.jsonl`, each numbered receipt directory, and the original journal. `manifest.json` hashes all pre-manifest files. Two exit-2 receipts are expected: pending replanning and foreign token rejection. The script returns nonzero on unexpected behavior and retains `failure.json` plus earlier receipts. An existing work directory is refused rather than overwritten.

A successful drill establishes local controlled behavior for the recorded helper hashes. It does not demonstrate production recovery, arbitrary external-service exactly-once execution, automatic scheduling, native crash recovery, human training benefit, or superiority of this experience-guided approach. Delivered status and corrupted-journal recovery are explained from inspected source; this drill does not exercise them.

Source: `scripts/adaptive_learning.py` (`halted`, `apply`, `observation_check`, `append`, `report`) and `references/adaptive-learning.md` in the supplied skill checkout. Execution receipts bind the exact helper SHA-256. The source is read-only for this exercise.

Review correction: the original draft replan probe used an obsolete plan revision and hit the stale-plan gate first. The reviewed drill uses a valid revision-3 proposal and checks the exact pending-state error. It also checks the exact foreign-token diagnostic. Original scripts and receipts are retained.
