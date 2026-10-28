# Resume work with Koder CLI on Windows · 0.4.4

[中文](windows-agent-continuation.zh-CN.md) · [Installation and removal](install.md) · [Markdown learning](markdown-learning.en.md)

## Check the runtime

These native commands require the separate Koder CLI candidate with Markdown learning. Installing this Skill does not add `learning` commands to another build. Check `koder version`, `koder learning status --json`, and `koder skills list --query personal-agent-growth --json`. If a command is absent, follow the [file protocol](../references/markdown-learning.en.md) and identify the missing native integration; do not claim native acceptance.

Run the Agent in an ordinary PowerShell window. Record its effective token. A filtered administrator token and an independently created standard account are different test conditions. Configure the model through Koder's own settings; credentials do not belong in the Skill, task files, or experience store.

Follow the general installation guide for downloads, hashes, and removal. This Koder candidate uses `%USERPROFILE%\.koder-cli` as its default configuration directory, overridden by `KODER_CLI_HOME`. Place the verified Skill at `skills\personal-agent-growth` inside that directory. The learning root defaults to `%USERPROFILE%\.koder\learning`, separate from conversation runtime storage.

## Share memory across two conversations

Set the same `KODER_LEARNING_ROOT` in both sessions. Do not copy it into two stores. Change the example workspace paths as needed, while keeping the project ID stable.

```powershell
$env:KODER_LEARNING_ROOT = Join-Path $env:USERPROFILE '.koder\learning'
$WorkA = Join-Path $env:USERPROFILE 'Projects\review-a'
$WorkB = Join-Path $env:USERPROFILE 'Projects\review-b'
New-Item -ItemType Directory -Force -Path $WorkA, $WorkB | Out-Null
koder learning init --timezone Asia/Shanghai --json
koder learning project review-demo -w $WorkA --goal 'Complete the task and retain verifiable recovery evidence' --json
koder learning project review-demo -w $WorkB --json
```

Write the real task into `task-a.txt` in the first workspace. Include acceptance criteria, permitted effects, and the purpose of the later review. Ask the Agent to recover memory, read the relevant Skill and sources, save a prediction, and execute. Before pausing, it should use `learning_write` to store decisions, a candidate lesson, and a checkpoint with actual artifact paths.

```powershell
[Console]::InputEncoding = [Console]::OutputEncoding = $OutputEncoding = New-Object System.Text.UTF8Encoding($false)
Get-Content -LiteralPath (Join-Path $WorkA 'task-a.txt') -Raw -Encoding UTF8 |
  koder run --stdin --new --session review-a --lang en --skill personal-agent-growth --learning-project review-demo -w $WorkA
```

End the first conversation. In the second workspace, create a short `task-b.txt`: recover the same project, inspect the first phase's raw artifacts, apply the lesson to a new deliverable, and adjust the next action. Do not paste the old chat, expected answer, or entire knowledge store. Normal tool authorization still applies.

```powershell
[Console]::InputEncoding = [Console]::OutputEncoding = $OutputEncoding = New-Object System.Text.UTF8Encoding($false)
Get-Content -LiteralPath (Join-Path $WorkB 'task-b.txt') -Raw -Encoding UTF8 |
  koder run --stdin --new --session review-b --lang en --skill personal-agent-growth --learning-project review-demo -w $WorkB
koder learning resume review-demo --json
```

`--new` starts a separate conversation. The shared learning root and stable project ID provide file continuity. Inspect `projects/review-demo/context.md`, the latest `nodes/*.md`, `memory.md`, and the experience entries. Use tool read records and before/after hashes to verify sharing. Matching prose or a claim of recovery is not evidence by itself.

## Recover from an interruption

- Unknown command result: retain the original call and receipt, then inspect effects read-only. Do not replay an unreconciled operation through another tool or conversation.
- Turn budget exhausted: inspect completed artifacts and narrow the remaining task. Do not repeat verified work or mistake an automatic node for a completed lesson.
- Required learning unavailable: an explicit `--learning-project` must not silently continue without learning tools. The repaired candidate stops before sending a model request. Check `koder memory diagnose --json` and `koder learning status --json`, restore the verified store, then resume the same project. Do not replace shared memory with a new empty store or bypass its ACL check.
- A test input requires extra privileges: separate provisioning from evaluation. In this trial a separate step created the file symlink; the Agent still evaluated its rejection without elevation. This does not establish non-elevated symlink creation.
- Protocol thinking appears in a summary: use the candidate with the summary repair. Preserve raw receipts and add a sourced correction to the current recovery record; retain historical failures.

- Invalid experience input: use the document ID with `learning_read open`; copy its returned source into an `evidence` array. Put explanatory text in `why`, `steps`, or `pitfalls`. Confirm the saved file by reading it back; a failed tool call does not create a lesson.

The native memory API and general file tools have different scopes. A project binding does not grant general access to a sibling workspace. Use the host’s supported authorization flow when needed, or have an authorized coordinator hand over a short, explicit list of original artifacts with source paths and hashes. The Agent must verify the received copies. Keep one physical learning root and report that artifact transport separately; it is not cross-device synchronization. Avoid recursive listings of the learning tree.

- A stale source hash: a decision/checkpoint changes memory and context. Read the resulting immutable node before citing it in an experience or completion. Execute dependent writes sequentially. Completion rejects its own mutable memory/context sources before changing any file.

- Long decision history: a successful pack may return `deferredReads` and `LEARNING_MEMORY_READ_REQUIRED`. Use `learning_read open` on that exact memory ID; follow its `next` cursor until null, then write. Keep goals and constraints in the pack and history on disk. A failed pack cannot be substituted with an arbitrary node read.

## Review and choose the next action

The matching Koder candidate provides an explicit `--harness learning-review` profile for the finishing phase. It exposes named-file and memory tools, while withholding shell, directory search, browser and external operations. Use it after execution and reconciliation, when the remaining work is to review receipts, correct a deliverable and save experience. It keeps the 16-step limit and normal authorization; it cannot run a new test. Read named launch receipts to document environment settings, instead of scanning an installation tree. A general Koder build may not contain this profile.

A review should inspect raw results and artifacts, then apply the lesson to a useful new deliverable. Revise the next action when evidence changes and record the scope. Do not schedule a task without concrete future work. These manually started conversations do not establish autonomous execution after the app closes.


After a checkpoint, explicitly read the project pack and confirm the new revision and latest node. For long workspace files, request bounded byte pages and follow nextOffset until null; do not use an unchanged edit to inspect hidden text. A manifest establishes the declared transport source, not execution. Use actual output and completion receipts. Correct a flawed lesson with a new candidate linked through supersedes; preserve the deprecated entry and its sources.

![Real Agent continuation and evidence boundaries](diagrams/windows-agent.en.svg)

[Editable source](diagrams/windows-agent.en.mmd) · [Reusable procedure](../references/windows-agent-continuation.en.md)
