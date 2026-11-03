# Measure a strategy before adopting it

[简体中文](measured-learning.zh-CN.md) · [Protocol](../references/measured-learning.en.md) · [Architecture source](diagrams/measured-learning.en.mmd)

![Measured-learning architecture](diagrams/measured-learning.en.svg)

This tutorial covers version **0.7.0**: strategy freezes and seeded schedules, complete task-cost records, and explicit causal mappings. It uses Python 3.11+ and the standard library. Run shell examples from the repository root on macOS or Linux; on Windows use an equivalent authorized shell and Python path. No adapter, global profile, network call, or package installation is needed for the offline steps.

**Every fixture below is synthetic.** Running these examples checks file contracts and arithmetic. It does not execute an Agent, certify an unseen task, measure provider charges, or establish a strategy benefit. The one real-CLI command is separated below and requires an authorized environment.

## 1. Define the comparison and freeze the strategies

Choose a fresh task-local root. The setup writes JSON front matter in Markdown; the helpers do not accept arbitrary YAML syntax. Paths inside metadata are relative to this root. Use stable ASCII IDs, exact path spelling and no symlinks. Existing immutable records must not be overwritten: use a new study/run/attempt identity when appropriate.

The example has two arms and three repetitions. For a real study, write the original quality rubric, the improvement threshold, complete resource budget, stopping rule, visible model/effort/transport and permissions **before** targets are released. Test general and domain proposals separately under the existing [PPC protocol](../references/recursive-improvement.en.md); a changed composition needs its own trial. A two-arm file demonstration alone does not meet those adoption gates.

<!-- demo:setup -->
```sh
PAG_REPO="$PWD"
PAG_DEMO="${PAG_DEMO:-$(mktemp -d "${TMPDIR:-/tmp}/pag-measured.XXXXXX")}"
PAG_MODEL="${PAG_MODEL:-protocol-demo-no-model}"
export PAG_REPO PAG_DEMO PAG_MODEL
python3 -B - <<'PYCODE'
from pathlib import Path
import json, os
root = Path(os.environ["PAG_DEMO"])
root.mkdir(parents=True, exist_ok=True)
with (root / ".tutorial-root").open("x", encoding="utf-8") as f:
    f.write("Synthetic protocol demonstration; no Agent outcomes.\n")
for name in ("evidence", "requests", "private", "prompts"):
    (root / name).mkdir()
def md(path, metadata, body):
    target = root / path
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("x", encoding="utf-8") as f:
        f.write("---\n" + json.dumps(metadata, indent=2) + "\n---\n\n" + body + "\n")
for arm, text in {
    "baseline": "Read input/task.md and the supplied data. Produce the requested artifact in output/. Check it before delivery.",
    "candidate": "Read input/task.md and the supplied data. State the quantity being measured, check overlapping intervals and unknown values, then produce and verify the artifact in output/."
}.items():
    folder = root / "strategy" / arm
    folder.mkdir(parents=True)
    (folder / "SKILL.md").write_text("# Synthetic " + arm + "\n\n" + text + "\n", encoding="utf-8")
md("plan.md", {
    "id": "synthetic-study", "type": "blind-plan",
    "arms": {"baseline": "strategy/baseline", "candidate": "strategy/candidate"},
    "model_config": {"model": os.environ["PAG_MODEL"], "training": False,
                     "reasoning_effort": "low", "transport": "default"},
    "repetitions": 3, "seed": 20261104, "deadline_seconds": 120,
    "metric": "native_tokens"
}, """Synthetic development protocol, not a held-out benefit study.
Unit: one task x one repetition x one arm; each attempt has a fresh context.
Quality: original external artifact criteria must all pass; no candidate rubric edits.
Example gain rule: at least 10% lower native-token total over all repetitions
for each task, with complete usage coverage and no quality loss; retain paired detail.
Time guard: no more than 10% higher complete-task time. Unknown coverage is inconclusive.
Budget: six invocations at most, each with an Agent-process limit of
120 seconds and 12 commands plus grading up to 30 seconds. The host enforces
a 1,200-second study envelope, including 300 seconds for setup/review and other
controller overhead; record actual overhead separately. Monetary budget is unknown until
real billing is available; apply the host's authorized spending cap before any call.
Stop on permission/input/strategy drift, exhausted budget, or unresolved effects.
Keep every failed/cancelled attempt. Retries need a new attempt ID and retained cost.
The helper stores these prose rules; independent review must enforce them.""")
print(root)
PYCODE
python3 -B scripts/blind_trials.py freeze --root "$PAG_DEMO" \
  --file "$PAG_DEMO/plan.md" > "$PAG_DEMO/evidence/freeze.json"
```

`blind-trials/synthetic-study/frozen.md` contains the plan hash and each strategy inventory. It is a content freeze, not a signed record or an access-control boundary. Keep native host evidence of when independent authors received and released targets. Never add answers, exposed target-specific repairs, credentials or private graders to the frozen strategy. `model_config` declares visible configuration; do not claim an authenticated server weight identity from it.

## 2. Release a target after the freeze; save the seeded order

This next block intentionally creates a **development** task. Its input, provenance and evaluator are visible to the tutorial reader. A genuine holdout must instead come from an independent author, represent a real failure or new applicable task, carry provenance, and remain unexposed to strategy authors and executors until release. Use `role: "holdout"` only when those conditions actually hold; record historical replays and reserve variants separately.

The evaluator is a Python program accepting `--output`, `--public` and `--report`. The runner invokes it separately with a 30-second timeout and saves its stdout, stderr and exit. This demo's exact arithmetic check illustrates that interface. Real acceptance must check the task's original substantive criteria and relevant traces.

<!-- demo:release -->
```sh
python3 -B - <<'PYCODE'
from pathlib import Path
import hashlib, json, os
root = Path(os.environ["PAG_DEMO"])
public = root / "public" / "window-demo"
public.mkdir(parents=True)
(public / "task.md").write_text(
    "# Synthetic interval task\n\nRead input/windows.json. Write output/occupancy.json with exactly "
    "the integer keys union_seconds and naive_sum_seconds. Intervals share one "
    "monotonic clock; endpoints are half-open. Do not claim measured billing or inference time.\n",
    encoding="utf-8")
(public / "windows.json").write_text(json.dumps([[0, 5], [4, 9]]) + "\n", encoding="utf-8")
(root / "private" / "provenance.md").write_text(
    "# Synthetic fixture\n\nAuthored for this tutorial after strategy freeze. The input and evaluator "
    "are visible in the tutorial; this is development evidence, not a real failure-derived holdout.\n",
    encoding="utf-8")
(root / "private" / "evaluate.py").write_text("""import argparse, json
from pathlib import Path
p = argparse.ArgumentParser()
p.add_argument("--output", type=Path, required=True)
p.add_argument("--public", type=Path, required=True)
p.add_argument("--report", type=Path, required=True)
a = p.parse_args()
try:
    value = json.loads((a.output / "occupancy.json").read_text(encoding="utf-8"))
    ok = (isinstance(value, dict) and set(value) == {"union_seconds", "naive_sum_seconds"}
          and all(type(v) is int for v in value.values())
          and value == {"union_seconds": 9, "naive_sum_seconds": 10})
    detail = "Exact synthetic artifact check"
except (OSError, ValueError) as error:
    ok, detail = False, str(error)
a.report.write_text(json.dumps({"verdict": "pass" if ok else "fail", "detail": detail}) + "\\n", encoding="utf-8")
raise SystemExit(0 if ok else 1)
""", encoding="utf-8")
def ref(path):
    return {"path": path, "sha256": hashlib.sha256((root / path).read_bytes()).hexdigest()}
meta = {"id": "window-demo", "type": "blind-task", "domain": "interval-audit",
        "role": "development", "public_dir": "public/window-demo",
        "evaluator": ref("private/evaluate.py"), "provenance": ref("private/provenance.md")}
(root / "target.md").write_text("---\n" + json.dumps(meta, indent=2) +
    "\n---\n\nSynthetic released target; no novelty or Agent-benefit claim.\n", encoding="utf-8")
PYCODE
python3 -B scripts/blind_trials.py release --root "$PAG_DEMO" \
  --id synthetic-study --file "$PAG_DEMO/target.md" > "$PAG_DEMO/evidence/release.json"
python3 -B scripts/blind_trials.py schedule --root "$PAG_DEMO" \
  --id synthetic-study > "$PAG_DEMO/evidence/schedule.json"
```

The schedule has six entries: each task/repetition block includes both arms; the seed shuffles the blocks and arm order. Save that exact order. Reissuing `schedule` does not execute anything or register a scheduler. The helper rejects a changed strategy, released input or bound evaluator/provenance when scheduling. Do not repair files in place and continue under the old freeze.

A task exposed for diagnosis becomes development evidence. Preserve its failures; use an unexposed reserve for the next holdout claim. Several assertions or commands inside one task do not create independent repetitions. Budget every attempt, including retries and cancellations.

## 3. Prepare a real request, then use the authorized CLI

The following block prepares **one request**, for the next saved schedule entry. It cross-checks the freeze, release, model configuration and inventories and writes the evidence links into the Markdown body. It starts no process. The runner itself does not join a request to a frozen study or enforce the whole schedule; the host must retain this cross-check and audit every later request. After recording the preceding entry, set `PAG_RUN_INDEX=1` (then 2, and so on) before rerunning this block. For a justified retry set `PAG_ATTEMPT=2`, keeping the same schedule index and retaining attempt 1; it must fit the predeclared total budget.

<!-- demo:request -->
```sh
python3 -B - <<'PYCODE'
from pathlib import Path
import hashlib, json, os
root = Path(os.environ["PAG_DEMO"])
def read_md(path):
    lines = path.read_text(encoding="utf-8").splitlines()
    return json.loads("\n".join(lines[1:lines.index("---", 1)]))
def ref(path):
    return {"path": path, "sha256": hashlib.sha256((root / path).read_bytes()).hexdigest()}
schedule = json.loads((root / "evidence/schedule.json").read_text(encoding="utf-8"))
frozen = read_md(root / "blind-trials/synthetic-study/frozen.md")
assert schedule["model_config"] == frozen["plan"]["model_config"]
assert schedule["frozen_sha256"] == ref("blind-trials/synthetic-study/frozen.md")["sha256"]
run_index = int(os.environ.get("PAG_RUN_INDEX", "0"))
assert 0 <= run_index < len(schedule["runs"])
run = schedule["runs"][run_index]  # Advance only after preserving the preceding result.
attempt = int(os.environ.get("PAG_ATTEMPT", "1"))
assert attempt >= 1
released = read_md(root / ("blind-trials/synthetic-study/tasks/" + run["task_id"] + ".md"))
assert released["frozen_sha256"] == schedule["frozen_sha256"]
assert run["public_dir"] == released["task"]["public_dir"]
strategy = frozen["plan"]["arms"][run["arm"]]
for relative, expected in ((strategy, frozen["strategies"][run["arm"]]),
                           (run["public_dir"], released["public_inventory"])):
    actual = {p.relative_to(root / relative).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
              for p in (root / relative).rglob("*") if p.is_file()}
    assert actual == expected
prompt_path = "prompts/" + run["id"] + "-a" + str(attempt) + ".txt"
(root / prompt_path).write_text(
    "Read skill/SKILL.md, then input/task.md. Do the task using only assigned inputs. "
    "Save the requested artifact under output/. Report checks and unknowns. "
    "Do not seek private graders, other arms, past answers, or external effects.\n", encoding="utf-8")
trial_id = run["id"] + "-a" + str(attempt)
spec = {"id": trial_id, "type": "agent-trial-request", "task_id": run["task_id"],
        "arm": run["arm"], "replicate": run["replicate"], "attempt": attempt,
        "public_dir": run["public_dir"], "strategy_dir": strategy, "prompt": ref(prompt_path),
        "evaluator": released["task"]["evaluator"], "model_config": schedule["model_config"],
        "deadline_seconds": frozen["plan"]["deadline_seconds"], "max_commands": 12,
        "codex_binary": os.environ.get("PAG_CODEX", "codex")}
path = root / "requests" / (trial_id + ".md")
body = ("Prepared request only; no Agent has been started.\n"
        + "Freeze SHA-256: " + schedule["frozen_sha256"] + "\n"
        + "Released target SHA-256: " + ref("blind-trials/synthetic-study/tasks/" + run["task_id"] + ".md")["sha256"] + "\n"
        + "Schedule SHA-256: " + ref("evidence/schedule.json")["sha256"] + "\n")
with path.open("x", encoding="utf-8") as f:
    f.write("---\n" + json.dumps(spec, indent=2) + "\n---\n\n" + body)
(root / "evidence/next-request.txt").write_text(str(path) + "\n", encoding="utf-8")
print(path)
print("No Agent started; host authorization and protected evaluation are still required.")
PYCODE
```

Before any real invocation, start a separate study with the actually authorized model and fresh targets; the default `protocol-demo-no-model` is deliberately a non-model label. Keep the visible model, effort, permissions, assigned inputs, strategy-loading policy, binary version and transport consistent across arms. Check the installed CLI's `exec --help` for the flags constructed by `run_agent_trial.py`, including `--ignore-user-config`; preserve its help/version and actual command. Use the CLI's existing sign-in. Do not copy authentication files, change global settings or use a fake local response as Agent evidence.

**The evaluator must be independently protected before execution.** A `private/` directory name and `workspace-write` do not make files unreadable. `blind_trials.py` only checks that the evaluator is outside the public directory and not byte-identical to a public input. The host must provide and verify a real read boundary, such as a separately controlled evaluator identity/service and an approved read-isolated trial environment, while allowing the controller to invoke grading. Give each run only its assigned strategy and public inputs; prevent access to other arms, answers, grader/report files and previous attempts. Review actual tool/access traces. If that boundary cannot be provided with this local runner, stop at request preparation and use an approved isolated host; do not describe the run as blind.

For an already authorized, protected study, this command **starts a real Codex invocation and may incur charges**:

```sh
PAG_REQUEST="$(cat "$PAG_DEMO/evidence/next-request.txt")"
python3 -B scripts/run_agent_trial.py --root "$PAG_DEMO" \
  --request "$PAG_REQUEST" > "$PAG_DEMO/evidence/actual-run.json" \
  2> "$PAG_DEMO/evidence/actual-run.stderr"
PAG_EXIT=$?
printf '%s\n' "$PAG_EXIT" > "$PAG_DEMO/evidence/actual-run.exit"
```

The runner copies the assigned input to `agent-work/<id>/input`, the strategy to `skill`, and an optional strategy `memory/` to `learning/`. The prompt explicitly asks for `skill/SKILL.md`. It uses a fresh ephemeral CLI context with unrelated automatic Skills, apps, plugins, memories and multi-agent context disabled by invocation flags; it does not modify global configuration. Its process deadline is at most 3,600 seconds and the command cap at most 100. The cap detects excess command starts; it is not an approval gate that guarantees an over-limit command never began.

Inspect `agent-runs/<id>/runner.json`, `events.jsonl`, `timeline.jsonl`, `stderr.txt`, `final.txt` when present, `measurement.json`, `grade.json` when produced, and grader outputs. Process exit, `grader_exit_code`, report content, input/strategy integrity and cost-record success are separate checks. A runner JSON result or exit zero is not a quality pass. Missing output remains missing. A stopped invocation can leave remote work, billing or external effects unknown: reconcile them before a retry. Do not grant new network, contact or deployment permissions through a trial prompt.

## 4. Ingest native usage and clock records without double counting

Real runs already create a hash-bound `cost-request.md` and immutable `trial-costs/<id>.md`. For an independently captured invocation, use the same exact Markdown fields: `id`, `type: "task-cost-request"`, `task_id`, `arm`, `replicate`, `attempt`, `model_config`, and `{path, sha256}` references for `events`, `timeline`, `measurement`. Preserve the native event bytes. Do not reconstruct missing usage or timestamps from a later summary.

`timeline.jsonl` has one row per event: zero-based `event_index` and monotonic `offset_seconds` relative to **Agent process start**. The measurement has `elapsed_seconds`, `agent_start_offset`, `agent_elapsed_seconds`, integer `exit_code`, and optional `phase_spans`. Phase spans are relative to the **complete trial start** and use `preparation`, `agent`, `research`, `retry`, `grading`, `review` or `delivery`. Preserve clock origin and capture method. Reconnects, failed turns, command clocks left open and usage errors must remain visible; an invalid stream is rejected rather than guessed into shape.

This runnable fixture uses **invented native-shaped events and clocks**, including a failed turn. It tests parsing only; never combine its counts with real resource totals.

<!-- demo:cost -->
```sh
python3 -B - <<'PYCODE'
from pathlib import Path
import hashlib, json, os
root = Path(os.environ["PAG_DEMO"])
folder = root / "evidence" / "synthetic-cost"
folder.mkdir()
events = [
    {"type": "thread.started", "thread_id": "synthetic-not-a-provider-receipt"},
    {"type": "turn.started"},
    {"type": "item.started", "item": {"id": "one", "type": "command_execution"}},
    {"type": "item.started", "item": {"id": "two", "type": "command_execution"}},
    {"type": "item.completed", "item": {"id": "one", "type": "command_execution"}},
    {"type": "item.completed", "item": {"id": "two", "type": "command_execution"}},
    {"type": "turn.completed", "usage": {"input_tokens": 100, "cached_input_tokens": 40,
                                        "output_tokens": 20, "reasoning_output_tokens": 8}},
    {"type": "turn.started"}, {"type": "error", "message": "Synthetic reconnect failure"},
    {"type": "turn.failed"}
]
offsets = [0, 0.1, 1, 2, 4, 5, 6, 6.5, 7, 8]
(folder / "events.jsonl").write_text("".join(json.dumps(e) + "\n" for e in events), encoding="utf-8")
(folder / "timeline.jsonl").write_text("".join(json.dumps({"event_index": i, "offset_seconds": t}) + "\n"
                                               for i, t in enumerate(offsets)), encoding="utf-8")
measurement = {"elapsed_seconds": 12, "agent_start_offset": 1,
               "agent_elapsed_seconds": 9, "exit_code": 1,
               "phase_spans": [{"phase": "preparation", "start": 0, "end": 1},
                               {"phase": "agent", "start": 1, "end": 10},
                               {"phase": "research", "start": 2, "end": 6},
                               {"phase": "grading", "start": 10, "end": 12}]}
(folder / "measurement.json").write_text(json.dumps(measurement) + "\n", encoding="utf-8")
def ref(name):
    path = "evidence/synthetic-cost/" + name
    return {"path": path, "sha256": hashlib.sha256((root / path).read_bytes()).hexdigest()}
spec = {"id": "synthetic-cost-a1", "type": "task-cost-request", "task_id": "synthetic-cost-task",
        "arm": "baseline", "replicate": 1, "attempt": 1,
        "model_config": {"model": "protocol-demo-no-model", "training": False},
        "events": ref("events.jsonl"), "timeline": ref("timeline.jsonl"),
        "measurement": ref("measurement.json")}
(root / "cost-request.md").write_text("---\n" + json.dumps(spec, indent=2) +
    "\n---\n\nSYNTHETIC parser fixture, not native execution or billing evidence.\n", encoding="utf-8")
PYCODE
python3 -B scripts/task_costs.py --root "$PAG_DEMO" \
  --request "$PAG_DEMO/cost-request.md" > "$PAG_DEMO/evidence/synthetic-cost-record.json"
```

Inspect `evidence/synthetic-cost-record.json` or its Markdown record. These are the values implied by this fixture, not an Agent result:

| Quantity | Correct interpretation |
|---|---|
| Input 100, cached input 40; output 20, reasoning detail 8 | Known total is **120**, not 168. Cached input is already in input; reasoning detail is already in output. |
| One completed turn followed by an error and failed turn | Keep 120 as the known subtotal; `coverage` is `partial_or_unavailable`. The failed attempt's unreturned usage is unknown. |
| Commands `[1,4]` and `[2,5]` | Observed command union is **4 seconds**, not 6. |
| Agent 9 seconds, complete trial 12 seconds | These intervals are nested. Do not add 9 + 12, or add tools/research to the parent interval. |
| Unattributed Agent time 5 seconds | It can include model, network and host work. `model_inference_seconds` stays `null`. |
| No billing receipt | `billed_usd` stays `null`, meaning unknown, not free. Tokens and account quota changes are not charges. |

The runner's measured window starts at input/strategy assembly and ends after external grading. It excludes earlier study/tool/source development and later normalization, review or publication. Keep a separate overhead ledger with actual start/end boundaries, commands and receipts, and include useful task preparation/retrieval/repair in the comparison envelope. Do not call the runner window the complete user task if substantial task work happened outside it. `controller_total_seconds` includes controller normalization time; it contains the measured window and must not be added to it.

Use interval unions for overlaps, and disjoint increments for work outside the parent window. Report shared study setup/source/tool/release cost separately rather than charging it repeatedly to each arm. Retain every attempt and its metering coverage. Hash binding proves source identity, not provider authenticity; reconcile actual billed amounts against provider receipts when available. The helper has no billing-import or model-inference-time estimator.

## 5. Specify a source mechanism, target graph and explicit mapping

A causal mapping proposes a test. It does not establish real causation, usefulness or permission. An experience keeps its original labels and evidence; optional `causal_model` adds `variables`, directed `relations`, and `predictions`. A query adds the same graph as `causal_context` plus `causal_mappings` keyed by the **source experience ID**. Each mapping has exactly `variables`, `rationale`, `prediction` and `falsifier`.

All source variables must be covered exactly once; distinct source variables cannot merge. Target variables must exist, their declared roles must match, and every source relation must preserve its direction and relation label. IDs may differ. Role/relation labels are normalized exact matches, not inferred semantic equivalence. Predictions explain an observable intervention and falsifier but still need real checking. Required conditions may be unknown (`null`) only in query facts; source requirements and observed conditions are boolean. Unknown or conflicting prerequisites block probing.

The next block actually computes a tiny source arithmetic artifact and hashes it, then saves a **hypothesis**. No independent reviewer or Agent use is invented. The target has different domain, structure and mechanism labels; only the explicit mapping connects it. The reversed query retains one legacy label so the rejected row remains visible in retrieval. A third query contradicts a prerequisite while preserving the graph.

<!-- demo:causal -->
```sh
python3 -B - <<'PYCODE'
from pathlib import Path
import hashlib, json, os
root = Path(os.environ["PAG_DEMO"])
def md(path, metadata, body):
    with (root / path).open("x", encoding="utf-8") as f:
        f.write("---\n" + json.dumps(metadata, indent=2) + "\n---\n\n" + body + "\n")
# Controlled integer-second arithmetic, independent of the helper's interval code.
source_intervals = [[0, 4], [2, 6]]
source = {"scope": "synthetic stdlib arithmetic, no Agent", "intervals": source_intervals,
          "sum_seconds": sum(b-a for a, b in source_intervals),
          "union_seconds": len(set().union(*(set(range(a, b)) for a, b in source_intervals)))}
path = "evidence/source-arithmetic.json"
(root / path).write_text(json.dumps(source) + "\n", encoding="utf-8")
source_ref = {"path": path, "sha256": hashlib.sha256((root / path).read_bytes()).hexdigest()}
model = {"variables": {"stages": "input intervals", "wall": "elapsed measurement"},
         "relations": [{"from": "stages", "to": "wall", "relation": "determines union"}],
         "predictions": [{"intervention": "Overlap two same-clock intervals",
                          "expected": "Union is smaller than their duration sum",
                          "falsifier": "The metric is aggregate worker time, not elapsed occupancy"}]}
md("experience-candidate.md", {
    "id": "synthetic-union", "type": "mechanism-experience", "source_task_id": "synthetic-build-source",
    "domain": "build-timing", "problem_structure": ["overlapping-stages"],
    "mechanisms": ["interval-union"],
    "required_conditions": {"same clock": True, "elapsed metric": True},
    "exceptions": ["Aggregate worker time may legitimately add overlapping durations."],
    "intervention": "Use the interval union for elapsed time, not the duration sum.",
    "explanation": "Overlapping portions occupy the same elapsed seconds.",
    "validation": "hypothesis", "executor": "tutorial/stdlib", "reviewer": None,
    "artifacts": [source_ref], "causal_model": model
}, "Synthetic sourced candidate. Arithmetic is checked; Agent usefulness is untested.")
target = {"variables": {"bookings": "input intervals", "occupied": "elapsed measurement"},
          "relations": [{"from": "bookings", "to": "occupied", "relation": "determines union"}],
          "predictions": [{"intervention": "Overlap two bookings on the same clock",
                           "expected": "Occupied seconds are less than summed booking seconds",
                           "falsifier": "The actual requirement counts person-seconds"}]}
mapping = {"variables": {"stages": "bookings", "wall": "occupied"},
           "rationale": "Both are half-open same-clock intervals with elapsed union as the quantity.",
           "prediction": "For [0,5) and [4,9), union is 9 while sum is 10.",
           "falsifier": "A person-seconds or separate-clock requirement rejects this use."}
query = {"id": "synthetic-occupancy-query", "type": "transfer-query", "task_id": "synthetic-occupancy-target",
         "domain": "room-occupancy", "problem_structure": ["room-bookings"],
         "mechanisms": ["occupied-seconds"], "facts": {"same clock": True, "elapsed metric": True},
         "keywords": [], "causal_context": target, "causal_mappings": {"synthetic-union": mapping}}
md("target-query.md", query, "No shared labels; explicit mapping proposes a hypothesis.")
reverse = json.loads(json.dumps(query))
reverse["id"] = "synthetic-reversed-query"
reverse["problem_structure"] = ["overlapping-stages"]  # Keep the rejected row visible via a legacy label.
reverse["causal_context"]["relations"][0].update({"from": "occupied", "to": "bookings"})
md("reversed-query.md", reverse, "Counterexample: relation direction is reversed; reject the analogy.")
conflict = json.loads(json.dumps(query))
conflict["id"] = "synthetic-condition-conflict"
conflict["facts"]["same clock"] = False
md("condition-conflict.md", conflict, "A matching graph cannot override a contradicted prerequisite.")
PYCODE
python3 -B scripts/experience_transfer.py add --root "$PAG_DEMO" \
  --experience "$PAG_DEMO/experience-candidate.md" > "$PAG_DEMO/evidence/experience-added.json"
python3 -B scripts/experience_transfer.py retrieve --root "$PAG_DEMO" \
  --query "$PAG_DEMO/target-query.md" > "$PAG_DEMO/evidence/mapped-query.json"
python3 -B scripts/experience_transfer.py retrieve --root "$PAG_DEMO" \
  --query "$PAG_DEMO/reversed-query.md" > "$PAG_DEMO/evidence/reversed-query.json"
python3 -B scripts/experience_transfer.py retrieve --root "$PAG_DEMO" \
  --query "$PAG_DEMO/condition-conflict.md" > "$PAG_DEMO/evidence/condition-conflict.json"
```

Inspect the candidate rows:

| Query | Expected protocol decision |
|---|---|
| `target-query.md` | `causal_match.status: structurally_compatible`, no label overlap, `eligible_for_probe: true`. This means conditions permit a bounded test, not adoption. |
| `reversed-query.md` | `compatible: false`, issue `directed_relations_not_preserved`, `eligible_for_probe: false`. Reject the analogy. |
| `condition-conflict.md` | Graph may match, but `same clock` is conflicting and `eligible_for_probe: false`. A graph cannot override facts. |

A missing source model, role mismatch, merged source variables or uncovered relation also prevents a causal match. Without a model, existing label retrieval retains its legacy scope; a domain match alone does not admit a candidate. Inspect `errors`, all relevant negative feedback and cross-domain counterexamples, not only ranking scores. Same-domain harmful feedback can block a probe; foreign harmful feedback requires applicability review. JSON output is a derived view; the immutable Markdown experience and observation journal remain semantic records. If extending a legacy lesson, add a new sourced candidate with the old record's actual path/hash rather than overwrite it.

## 6. Run a follow-up check before recording an observation

This block performs the target arithmetic using standard-library sets, writes the actual result, and only then prepares an observation. It records `inconclusive` for **Agent transfer benefit**, even though the synthetic arithmetic returns 9 rather than the naive 10. The new target task ID differs from the source. This is an executable example of recording actual follow-up evidence, not an example of a successful Agent transfer.

<!-- demo:followup -->
```sh
python3 -B - <<'PYCODE'
from pathlib import Path
import hashlib, json, os
root = Path(os.environ["PAG_DEMO"])
intervals = json.loads((root / "public/window-demo/windows.json").read_text(encoding="utf-8"))
result = {"scope": "actual execution of a synthetic stdlib arithmetic check; no Agent",
          "intervals": intervals, "sum_seconds": sum(b-a for a, b in intervals),
          "union_seconds": len(set().union(*(set(range(a, b)) for a, b in intervals)))}
path = "evidence/target-arithmetic.json"
with (root / path).open("x", encoding="utf-8") as f:
    f.write(json.dumps(result) + "\n")
assert result["union_seconds"] == 9 and result["sum_seconds"] == 10
observation = {"id": "synthetic-followup-01", "type": "transfer-observation",
    "task_id": "synthetic-occupancy-target", "domain": "room-occupancy",
    "conditions": {"same clock": True, "elapsed metric": True}, "outcome": "inconclusive",
    "adaptation": "Applied the union calculation only in this controlled arithmetic check.",
    "finding": "Actual synthetic calculation returned union 9 and sum 10; no Agent used this lesson, so Agent transfer benefit is unknown.",
    "executor": "tutorial/stdlib", "reviewer": None,
    "artifacts": [{"path": path, "sha256": hashlib.sha256((root / path).read_bytes()).hexdigest()}]}
with (root / "followup.md").open("x", encoding="utf-8") as f:
    f.write("---\n" + json.dumps(observation, indent=2) + "\n---\n\n"
            "The arithmetic ran before this record was authored. Reversed mapping and the condition conflict remain rejected.\n")
print(json.dumps(result))
PYCODE
python3 -B scripts/experience_transfer.py status --root "$PAG_DEMO" \
  --id synthetic-union > "$PAG_DEMO/evidence/before-followup.json"
python3 -B scripts/experience_transfer.py observe --root "$PAG_DEMO" \
  --id synthetic-union --observation "$PAG_DEMO/followup.md" \
  --expected-revision 0 > "$PAG_DEMO/evidence/after-followup.json"
```

The example is single-writer, so the pre-observation revision is 0. In shared use, read `status`, review its `revision` and pass that value. If stale, reread and resolve the intended observation; do not blindly resubmit. Keep the rejected mapping and failed conditions alongside any later positive evidence. Never relabel this arithmetic record as `helpful` to imply Agent learning.

For a real target, the authorized Agent must actually read the lesson, adopt/adapt/reject it, execute the task where needed and retain artifacts and relevant host traces. Record the prediction, strongest counterexample, changed conditions and observed result. `helpful` needs a distinct declared reviewer and verified artifacts; a declared identity alone does not authenticate independence. A rejection can itself be useful evidence, but a written rejection or prediction is not an execution result.

## 7. Decide from all trials and keep rollback

Review independently accepted quality first, then every scheduled task/repetition and every attempt. Keep failures, cancellations, missing usage, exposed targets and non-comparable configurations in the report. Do not select the fastest run, count assertions as tasks, or discard failed costs. Compare paired repetitions at the task level under the frozen metric, gain threshold and resource/quality guards; the current helpers do not supply an automatic statistical comparison or join between freeze, runner, grader and billing.

Report quality, native tokens and coverage, complete task time, setup/repair/review overhead, and actual billing coverage separately. Unknown or non-comparable values can make the claimed gain inconclusive. Two correct arms do not demonstrate improvement; token savings alone do not demonstrate lower charges. If the candidate misses the predeclared gain or a guard, keep the baseline and preserve the candidate with its failure evidence.

Apply the existing PPC composition and regression gates before scoped adoption. Save the enabled version and rollback path. A changed composition or repaired exposed task needs a new freeze and unexposed reserve before a new holdout claim. Later tasks must actually load and use, adapt or reject the experience and retain the result; writing a future plan does not add transfer evidence. Record the next useful action in the existing Markdown context/project node; host scheduling remains separate.

<!-- Copyright (C) 2026 KARMENLOOP Official Team. SPDX-License-Identifier: AGPL-3.0-only -->
