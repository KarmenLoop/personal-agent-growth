# Propose–Probe–Compose and two recursive levels

[中文](recursive-improvement.md)

Apply to each new task after the user enables this mode. Inspect the host's actual tools and execution capability. If no execution agent is available, retain NOT_RUN. Prepared files, simulated receipts, and the comparator itself are not Agent executions.

## Fixed and mutable components

Freeze visible model/sampling configuration, task inputs, budget, and evaluation criteria. Do not invoke training, fine-tuning, gradients, weight updates, or reinforcement learning. Hosted models often expose no weight digest: record visible model/provider versions without claiming independent proof of server-side weight constancy. Unknown or changed configuration limits attribution to the scaffold.

Mutable components are restricted to user-authorized project-owned prompts, candidate-generation prompts, tool code/interfaces, context preparation, retrieval/routing, stopping/recovery rules, and orchestration. Current higher-priority host instructions, permissions, credentials, budget ceilings, evaluation, and frozen inputs are outside the candidate. A modified generator also needs cross-task evaluation; it cannot relax its own test.

Enabling the mode authorizes bounded proposing, editing, testing, selecting, activating, and rollback in that scope. Record authorized roots and current version. Ask again only for a new user-owned tradeoff, authority scope, or budget ceiling.

| Component | Observed bottleneck | What to inspect |
|---|---|---|
| Prompt, selection, parsing | Misunderstanding, omissions, repeated instructions | Same-goal actions and artifacts |
| Tool implementation, batching, caching | Repeated launches, redundant I/O | Calls, input identity, invalidation, error propagation |
| Context, retrieval, summary | Irrelevant reads, lost decisions, bad recovery | Actual reads, omissions, continuity, cost |
| Assignment, sequence/parallelism, retry | Wasted waits, duplicates, overwritten work | Full trajectory, shared writes, recovery, overhead |
| Scheduling and review | Unproductive wakeups, unused learning, repeated failure | Actual trigger, application, recurrence and repair |
| Proposal and composition strategy | Similar proposals, prompt bloat, failed transfer | Real portfolio results and regression |

Project-owned files may be called system prompts or guardrails; that name does not make live host instructions editable. Allocate within existing ceilings. Register future work through verified host APIs. Record observable reads, calls, returns, failures, concise public rationale, identities, and next actions rather than hidden reasoning.

## Inner level: improve one task

One coordinator owns an experiment. Baseline/general/domain execution leaves share its ID and remaining budget; they run their frozen arm without recursively starting more three-arm experiments.

1. **Recover the baseline.** Read current accepted version, domain, and lessons. Record configuration, input hashes, full scaffold snapshot, authority, and metrics. Include accepted improvements from earlier tasks rather than resetting to the initial version.
2. **Propose twice.** General targets a transferable mechanism; domain targets the current field. Each states observation, concrete change, predicted gain, possible regression, applicability, and rejection condition. Both derive independently from the same baseline. Unproven weaknesses remain exploratory hypotheses.
3. **Freeze.** Save full snapshots, inputs, and evaluator, then run `freeze`. Any later change to frozen inputs defines a new round while retaining the old one. Predictions precede execution; retrospective explanation is labeled.
4. **Probe three complete executions.** Use fresh contexts or isolated workspaces, equal tools and budgets, and only that arm's snapshot. Preserve raw receipts/artifacts. Rotate order and record cache, login, network, and load differences. Repairs consume budget and do not erase failures.
5. **Compare trajectories and artifacts.** Candidates cannot award their own final grade. A fixed evaluator and responsible reviewer inspect identity, actions, and outputs before writing evaluation.json. The comparator checks completeness and declared gates; a self-described JSON agent identity is not independently authentic.
6. **Compose when supported.** Required quality must pass, and the candidate must repair a demonstrated baseline failure or exceed a predeclared improvement threshold. Reject a fast but poor result. A complete tested arm can be selected; combining components needs another run. On ties, missing evidence, or conflict, retain baseline.
7. **Return to the user's task.** Use accepted artifacts within scope and retain changed judgment and continuation. External sends, deployment, deletion, or payments happen only once; comparisons use isolated copies or repeatable read-only stages.

The default is at most two candidate rounds per task, bounded before starting by practical time/token/tool limits. At the ceiling, deliver the best supported result and label untested candidates. An experiment cannot recursively increase its own allowance.

## Composition contract

Align observation → baseline action → candidate action → result → cost. Each `compose-plan.json` decision contains `component`, `source` (baseline/general/domain/new), `action` (keep/drop/rewrite), `reason`, and actual Probe `evidence`. Discarding both proposals is valid; composition is not mandatory concatenation.

Place a complete successor in `arms/composed/`. Before execution, `freeze-compose` binds original evidence, decisions, evaluation routing adapter, and snapshot. The adapter keeps task, quality criteria, configuration, and metric; only execution paths may change. Save an actual fresh `runs/composed/run.json` and `composition-evaluation.json`, both bound to `composition_sha256`.

Compare again. Composition must pass original quality, improve over baseline, and not worsen the selected metric relative to the best qualified arm. A frozen but unexecuted composition cannot activate. Preserve the original three-arm records.

## Evaluation without standard answers

Do not provide prewritten answers, hidden labels, or post-hoc success conditions to the solver, improver, or evaluator. Freeze observable criteria before work:

| Signal | Use | Limit |
|---|---|---|
| Identity and structure | Hashes, schemas, references, conserved counts, required fields, exits | Correct format does not establish correct content |
| Environment feedback | Real tools, compiler/runtime, supplied acceptance | Bound to the task/environment |
| Metamorphic relations | Relocation, equivalent-input permutation, deduplication, round-trip recovery | Tests relations without answer labels |
| Independent reuse | Another executor uses the artifact in new work | Stronger than restatement, still inspect output |
| Open questions | Blind candidate labels, fixed source/omission rubric, swapped order | Preserve disagreements; prose preference is not objective gain |

Repeated agreement by the same model is not independent truth. With no verifiable feedback, retain a hypothesis rather than claiming improved quality. A useful change is not guaranteed on every task.

## Full-task efficiency and cost

Choose units before collection: success, artifacts, tools/processes, tokens, dollars, and time are distinct. Timing comparisons need at least three paired repetitions of the same task. One fast run does not establish stable acceleration. Unknown model usage stays unknown.

Count launch through final delivery and exit, including memory, model turns, tools, retries, reporting, and checks. A final successful tool's time is not whole-Agent time. Preserve each domain's quality and resource limits; a faster domain cannot conceal another domain's failure or excessive regression. Three repetitions support exploratory comparison, not universal speed claims.

Reserve budget for checks and host completion receipts. If artifacts exist but a turn is truncated, preserve them and the interruption instead of inventing a normal completion. Missing native usage remains null. Changed deadlines/output contracts require a separately frozen round applied to every arm; never extend only a losing arm or mix rounds.

Preserve native usage events before aggregating input, cached input, output, and total tokens. Cached input is generally already included in input; do not add it twice. Retain cache measurements and rotate order. Fewer tokens do not automatically mean lower billing; unknown actual charges remain null.

`performance_guards` in plan.json freezes secondary limits, e.g. `{"release_tokens":0.15,"analysis_wall_seconds":0.20}` allows at most 15% and 20% median increases for those task metrics. Each arm supplies same-name `guard_samples` arrays with the declared sample count. Timing needs three samples. Unknown, missing, or over-limit evidence prevents adoption, including composition. Never relax thresholds after seeing outcomes.

Save UTC start/end and monotonic durations. Unexplained disagreement retains both raw clocks and marks the affected sample null. Do not subtract a guessed pause or delete the sample. An unresolved candidate can remain undecided without blocking another complete candidate; unknown baseline evidence blocks its comparisons.

Track three ledgers: selected-version task cost, optimization overhead, and later actual reuse cost. Three checker launches becoming one is not a two-thirds reduction in Agent cost. Predicted payback is labeled until later tasks establish actual cumulative benefit. If whole-cost fields are missing, report only the selected metric.

## Outer level: improve later tasks

At task end retain accepted, ineffective, failed, and unresolved proposals with triggers, causal hypotheses, changed components, baseline, trajectories, evaluation, actual cost, counterexamples, scope, invalidation, and rollback.

`reflection.json` records `trigger`, `bottleneck`, `intervention`, `evidence`, `observed_result`, `scope`, `invalid_when`, and `next_probe`. Distinguish observed lessons from hypotheses and preserve regression risks. `record` binds reflection, proposals, comparisons, and composition into a lesson card. `select` returns applicable cards; the next proposal must actually read and explain use/rejection, not just list paths.

`record <experiment> --library <private-library> --expected-revision N` preserves experience. `--activate general|domain|composed` promotes only a passing full snapshot for that domain. Read current revision with `select` first. These commands manage the selected library, not host global prompts or installed directories, and start no background service. Read back revision/hash; host consumption is separate evidence.

Repeated mechanisms can motivate changes to the proposal generator, retrieval, routing, or budget policy. Compare on at least two tasks, including new transfer and prior-success regression. General promotion additionally needs two domains. Mark development cases already seen separately. Keep fixed model and acceptance; do not introduce an unbounded third recursion level.

For outer experiments set `layer: harnessing` and a `portfolio` of distinct task IDs with `domain` and `role` (development/transfer/regression), including transfer and regression. `promotion: cross-domain` requires two domains. Freeze checks declarations; the host/evaluator verifies actual execution. Separate meta-strategy keys such as `meta:archive-workflows` from inner execution-domain keys.

The utility stores complete snapshots by domain/strategy key. Cross-domain lessons inform proposals; they do not automatically replace every domain. The name general expresses intent, not proven universality. Adoption needs real portfolio evidence.

Use one writer, explicit revision checks, and immutable snapshots. Restore current state before selecting. On failure, create a new revision restoring the recorded prior full snapshot; retain failed versions. Missing frozen inputs or receipts stops promotion, while useful user work can continue with a verified baseline.

Post-adoption review must return to retrieval. A review JSON includes `observation_id`, `domain`, actual `active_sha256`, `lesson`, `limitations`, `next_probe`, and `evidence` mapping local absolute paths to hashes. `observe --library ... --review ... --expected-revision N` appends an immutable checked observation and increments revision. It checks evidence/version binding, not semantic truth, and adopts no new version. Later selection returns experiences and observations. Markdown learning mode records the resulting learning conclusion in a sourced MD entry rather than treating JSON as a second profile.

## File contracts

```text
experiment/
  plan.json
  proposals/general.md, domain.md
  arms/baseline/, general/, domain/
  inputs/
  evaluator.py
  frozen.json
  runs/<arm>/run.json
  evaluation.json
  compose-plan.json
  arms/composed/
  compose-frozen.json
  composition-evaluation.json
  reflection.json
```

Plan requires `experiment_id, task_id, domain, model_config, quality_checks, metric, min_relative_gain, samples, max_candidate_cost, inputs, evaluator`. Model configuration includes `training:false`. Inputs and evaluator are experiment-relative paths. Both proposals must be nonempty. Name the timing metric `wall_seconds`.

Each run records matching `model_config`, `frozen_sha256`, `executor` (kind agent plus actual host/session ID), `trace`, `host_receipt`, and `artifacts`. Referenced files live within the experiment; raw receipts are nonempty. If native events cannot be exported, distinguish coordinator observation from executor statement rather than fabricating exports.

Evaluation has `frozen_sha256`, `reviewer`, `optimization_cost`, and `arms`. Baseline/general/domain each have `run_sha256`, `evidence_sha256`, `checks`, `metric_samples`, and `evidence`. The evidence hash map covers the run's trace, host receipt, and every artifact. Check names exactly match plan quality criteria, with true/false/null values. Metrics are nonnegative finite samples. Unknown optimization cost is null, not zero. Composition uses the same evaluation shape with only composed and its composition hash.

```sh
python3 scripts/compare_trials.py freeze /path/to/experiment
# Run the three real Agents and retain independent evaluation before compare.
python3 scripts/compare_trials.py compare /path/to/experiment
python3 scripts/compare_trials.py freeze-compose /path/to/experiment
# Run the composed Agent and retain its independent evaluation before compare.
python3 scripts/compare_trials.py compare /path/to/experiment
python3 scripts/compare_trials.py record /path/to/experiment --library /path/to/private-experience --expected-revision 0 --activate composed
python3 scripts/compare_trials.py select --library /path/to/private-experience --domain offline-package-check
python3 scripts/compare_trials.py rollback --library /path/to/private-experience --experiment-id experiment-id --expected-revision 1 --reason "Observed regression"
```

Windows uses `py -3 -X utf8`. Exit 0 means valid records and may have no winner; exit 2 means missing/drifted records or invocation failure. Success exit alone does not establish improvement. Record without activate only archives lessons.

Mechanism reference: [official Harness² repository](https://github.com/google-research/harness2) and [paper](https://arxiv.org/abs/2610.14224). This project independently implements the idea with fixed quality gates, composition retesting, revision checks, and rollback. It does not integrate the upstream runner or claim upstream benchmark gains as its evidence.


<!-- Copyright (C) 2026 KARMENLOOP Official Team. SPDX-License-Identifier: AGPL-3.0-only -->
