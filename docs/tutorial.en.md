# From installation to preparation, review, and handoff · 0.4.1

[中文](tutorial.zh-CN.md) · [Install](install.md) · [Decision method](reasoning.en.md)

The useful task is to **check the current release, create a reusable acceptance card, and have another host reuse it after relocation**. This is a tutorial, not a claim that its steps have already run. Use the actual package; create negative cases only in isolated test copies.

## 1. Bind three locations

Resolve absolute `<SKILL>`, `<LEARNING>`, and `<TASK>` paths for the skill, private Markdown knowledge, and inputs/raw receipts. Use a stable project ID such as `handoff-review`. Keep actual user records out of public GitHub.

Read SKILL and the [Markdown protocol](../references/markdown-learning.en.md). Instantiate policy, index, memory, context, and an initial node from the [templates](../templates/learning/README.md). Supply the goal, constraints, acceptance, and writer. Record outcomes only after observing them.

## 2. Save the judgment and prediction first

Give the agent:

> Complete acceptance of the current handoff package. Read context, the newest node, and memory, recording their actual identities. Predict whether ZIP and manifest agree and state what that would and would not establish. The recipient must continue after relocation. Identify decisive unknowns, inspect format and reference rules, then execute checks. Deliver an acceptance card, commands/outputs/exits, input hashes, current conclusion, and the next useful review. Finish solvable work; ask only for a decision I must make.

A useful preparation question concerns exit 2's reached stage or reference resolution from the containing document. An unbounded survey of every tool is unnecessary. Retain sources, applicability, and the next verification.

## 3. Execute and preserve failures

Use a real tool and replace the placeholders:

```sh
python3 -B <SKILL>/scripts/verify_handoff.py \
  --archive <TASK>/inputs/personal-agent-growth-0.4.1.zip \
  --manifest <TASK>/inputs/manifest.json
```

On Windows use `py -3 -B -X utf8`. Save the full command, stdout/stderr, exit, UTC and monotonic duration where supported, and program/input hashes. Exit 0 means consistent, 1 means an inspected inconsistency, and 2 means incomplete inspection. It does not authenticate the publisher or establish resource usability.

Make an isolated copy, remove one input from that test copy, and invoke the checker again. Expect an incomplete check rather than a conclusion about archive content. Retain that attempt, restore the input, and recheck the original package. Preserve the published originals.

## 4. Remediate and revise

Compare observation with prediction. A nonexistent path requires location/mapping repair; a reference that only works at the old location requires relocation checking. Record prior judgment, new evidence, revision, method change, and retest in a node. Put only durable facts in memory.

The acceptance card identifies object/version, environment, stage, raw evidence, and conclusion scope. ZIP consistency cannot be labeled second-host usability. Start candidate experience as untested; actual application supports local validation, retaining counterexamples and invalidation conditions.

## 5. Pause and change tools

The original host refreshes context, appends a node, identifies the next action, preserves artifact identities, transfers writer, and increments revision. The receiving host uses the same LEARNING/TASK:

> Resume handoff-review from the same learning root. Read context and the newest node first, then memory; verify revision and writer. Reuse the previous artifacts, move an isolated copy, and ensure the former location cannot supply test resources. Perform a meaningful review variation. Retain the actual read set, new outputs, changed judgment if any, and next action. Write back to the existing root rather than making another state copy.

Check the receiver's actual Agent turn, file hashes, tool returns, and new revision. Two Python processes can test file protocols but do not replace this real Agent step. If the device is unavailable, preserve the recovery point instead of inventing success.

## 6. Daily/weekly loop and future action

The daily report links both nodes, knowledge changes, and failures. Weekly close reads the whole week's reports for recurring patterns. The following Monday checks actual application and updates preview. An unused lesson stays unverified.

If future work has a concrete purpose, register a bounded review with expiry and run count through the host and read its binding back. Execute and inspect after a real event; stop on acceptance or retain a specific remediation action. Follow contact preferences. A saved plan is not registered scheduling.

## 7. Enable two-level recursive improvement

Create general/domain proposals in a new experiment and freeze model configuration, inputs, quality, and budget. Baseline and candidates each complete the whole task, not just the checker. Save native receipts, artifacts, quality, elapsed time, tokens, and unknown costs. Changed composition needs a separate run.

```sh
python3 -B <SKILL>/scripts/compare_trials.py freeze <EXPERIMENT>
python3 -B <SKILL>/scripts/compare_trials.py compare <EXPERIMENT>
python3 -B <SKILL>/scripts/compare_trials.py freeze-compose <EXPERIMENT>
python3 -B <SKILL>/scripts/compare_trials.py compare <EXPERIMENT>
```

These commands require real file contracts and execution evidence. They do not launch Agents or create success records. See [the protocol](../references/recursive-improvement.en.md) for schemas and record/select/observe/rollback. JSON experiments retain raw evidence; Markdown experience records learning conclusions and source links. Promote outer generation/routing strategies only after new-domain transfer and original-task regression.

<a id="adapter"></a>
## 8. Existing five-tool adapter: a separate optional mode

This supports legacy SQLite checkpoint workflows in a root separate from Markdown learning. Create the workspace, then run:

```sh
python3 <SKILL>/scripts/host.py --root <PRIVATE-STATE> --workspace <PROJECT> --install-host codex install
python3 <SKILL>/scripts/host.py --root <PRIVATE-STATE> --workspace <PROJECT> --install-host cursor install
```

It adds a project entry to `.codex/config.toml` or `.cursor/mcp.json` and refuses an existing same-name server. Reload, follow host approval requirements, and verify all five tools:

| Tool | Key input | Effect |
|---|---|---|
| growth_start | task_id, goal, acceptance | Create a durable task with current writer |
| growth_read | task_id | Recover state and inspect artifact hashes |
| growth_checkpoint | expected_revision, phase, next_action, artifacts, observation | Commit as the current writer |
| growth_handoff | expected_revision, target_host | Transfer responsibility with current evidence |
| growth_export | task_id | Write private handoff JSON |

Start in Codex, perform a real step, checkpoint, and hand off to cursor. Cursor reads, verifies, continues, and checkpoints. The old writer is rejected; stale revisions require rereading. Changed artifacts produce evidence_current=false and must be checked before handoff.

Direct inspection can use `host.py --root ... --workspace ... --host-id cursor call growth_read --input request.json`, with `{"task_id":"your-task-id"}` in the request. This tests storage/interfaces rather than Cursor model consumption. Schedule remains not_registered; the adapter is not a scheduler.

## 9. Expected deliverables

Retain a sourced acceptance card, real commands/outputs, prediction differences, retests, a recoverable project packet, bounded experience, and an actual read set. Add a verified host binding only when future work warranted one. Mark missing Agent/device/scheduling evidence NOT_RUN. Write the completed summary only when current evidence meets the goal.
