# Capability learning tutorial · 0.6.1

[中文](capability-learning.zh-CN.md) · [Runtime protocol](../references/capability-learning.en.md) · [Learning research](learning-science.en.md)

This portable Python 3.11+ helper adds an executable evidence ledger to the existing Skill. It has no pip dependencies. It does not install the private Koder learning APIs, invoke a model, or create background jobs. Actual reasoning and execution use the host Agent.

## Connect the same memory

Choose the existing shared learning root explicitly. Every host uses the same physical directory; two copies with similar names are not shared memory. The capability extension coexists with daily, weekly, project, and user files:

```text
learning/
  projects/<project-id>/context.md
  projects/<project-id>/nodes/...
  experience/...
  capabilities/<capability-id>/
    capability.md
    attempts/000001.md
    attempts/000002.md
  evidence/<task-id>/...
```

Only Markdown stores capability semantics. `status` replays the current files every time; its JSON stdout is a report, not a second state store. Temporary files and an exclusive writer lock coordinate publication. Artifact files can be code, data, or command output: the Markdown records their paths and SHA-256 identities.

Use immutable copies of important receipts. If an artifact changes, status fails closed instead of claiming its earlier assessment still applies. Never point evidence at a mutable project summary that the next action will overwrite.

## Start a real learning task

From the Skill directory, on macOS/Linux:

```sh
python3 -B scripts/capability_ledger.py init \
  --root /absolute/path/to/learning \
  --id release-verification \
  --goal 'Verify a release and teach another executor to repeat the checks' \
  --domain software-release
python3 -B scripts/capability_ledger.py status \
  --root /absolute/path/to/learning --id release-verification
```

On Windows, replace `python3 -B` with `py -3 -B -X utf8`, use your actual D: or C: root, and put the command on one line or use PowerShell continuation. Verify that the chosen Python is at least 3.11. No elevation is requested by the helper.

Initialization does not award any capability. Record a prediction, read only needed sources, and perform a small real task. Have another responsible executor inspect the artifacts before recording a pass. A single operator writing two different actor strings does not prove independent review.

## Record an observation

Save a Markdown file with this **JSON-form YAML 1.2** front matter. This narrow format is intentional: the standard-library reader does not support arbitrary YAML. Replace every value with actual observations. Times are UTC, after initialization and no later than the current clock.

```markdown
---
{
  "id": "apply-release-01",
  "kind": "apply",
  "task_id": "release-task-01",
  "executor": "actual-host/actual-session",
  "reviewer": null,
  "outcome": "unknown",
  "observed_at": "2026-11-03T08:00:00Z",
  "summary": "Execution output is saved; independent content review is pending.",
  "artifacts": [{"path": "evidence/release-task-01/result.txt", "sha256": "replace-with-actual-64-character-sha256"}],
  "cost": {"wall_seconds": null, "tokens": null, "usd": null}
}
---
## What happened
Actual commands, observed result, limitations, and next check.
```

Compute the actual hash with `shasum -a 256` on macOS, `sha256sum` on Linux, or `Get-FileHash -Algorithm SHA256` on Windows. The example intentionally cannot pass unchanged. Unknown values stay `null`; do not estimate missing provider charges as zero. A measured cost on each event must cover only that event's non-overlapping work; repeated use of one artifact must not repeat its whole-session cost.

```sh
python3 -B scripts/capability_ledger.py record \
  --root /absolute/path/to/learning --id release-verification \
  --observation /absolute/path/to/observation.md --expected-revision 0
```

Read `status` before another write and use its revision. A rejected write does not consume a revision. Do not retry a stale write blindly: reread, resolve the observation against current facts, then submit the intended next record. Existing event IDs cannot be duplicated. Entries append; failures are not erased.

## What each dimension requires

| Kind | Evidence to review before recording | Additional fields |
|---|---|---|
| `explain` | A source-grounded explanation with assumptions | None |
| `apply` | Actual tool execution and a usable artifact | None |
| `counterexample` | A changed condition, prediction, and observed result | None |
| `transfer` | Successful use on a different task | `source_attempt`: earlier passed `apply`; new `task_id` |
| `teach` | A lesson and another executor's independently produced result | `learner`, different `learner_task_id`, `learner_artifacts` |
| `deliver` | Complete user outcome, not a local subtest | None |
| `recall` | Answer-hidden retrieval after a real delay, followed by review | `source_attempt`, `no_answer_visible: true`; at least 24 hours |
| `regression` | Original capability still works under prior conditions | None |

The helper checks consistency, not conceptual correctness. A reviewer must reject unsupported content even when the script accepts its shape. `pass` requires a different reviewer and nonempty verified artifacts. For teaching, learner identity differs from teacher and reviewer; its task and artifact hashes must differ. Hashes do not prove the learner actually read the lesson: retain host/tool evidence separately.

The displayed dimensions have no universal intelligence meaning. Missing teaching evidence does not prevent a useful task from being delivered. A full in-scope assessment requires all declared dimensions; a delayed test still pending cannot be changed to pass because a unit test advanced its clock.

## Review, repair, and real wakeups

```sh
python3 -B scripts/capability_ledger.py due --root /absolute/path/to/learning
```

Failure proposes remediation; unknown proposes verification. Passing observations propose reviews under an initial 1/3/7-day policy. These intervals are transparent project heuristics, not a proven optimum for LLMs. The initializer's internal API can set a stricter initial policy; the CLI does not rewrite policy after results. Changed policy needs a new capability identity.

The output always states `scheduler_registered: false`. The host uses [autonomous continuation](../references/autonomous-continuation.en.md) to register authorized future work, saves the scheduler ID, and reads the actual schedule back in the project node. On wakeup it checks the ledger and executes only useful due work. Inactive or completed projects do not justify endless polling. User availability and tool permissions are not inferred from a due date.

If evidence is inconsistent, `due` reports the affected capability as an error and can still list other valid work. It returns a nonzero exit for errors. Repair or preserve the broken record; do not silently drop it and count the remaining files as complete.

## Teach and resume across Agents

Teacher A records the method, prediction, source links, commands, failure conditions, and task artifact. Learner B starts with the same root, current project context/latest node, the lesson, and a **new input**. B performs the task independently and writes its own artifact. Reviewer C inspects both, records corrections, then appends `teach` or a failure. This validates that specific lesson and task; it is not evidence of general teaching mastery.

Host identity, tool reads, command exits, and real output remain separate acceptance gates. Do not paste the teacher's finished output into B's prompt and call that shared-memory transfer. Close the session and reopen against the same physical root to test recovery. At completion, save scope and next action in the existing project node, daily review, and candidate experience, using their original contracts.

## What stays unchanged

The optional SQLite adapter still manages historical handoff state. PPC JSON still binds experiments. Neither becomes a second writable user profile. Markdown experience remains the semantic knowledge base. This helper adds no network client, model training, automatic dependency installation, credentials, privilege changes, or permission bypass.
