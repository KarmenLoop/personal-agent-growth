# Open-source research and interoperability for 0.6.0

English · [简体中文](open-source-research.zh-CN.md)

Reviewed on November 3, 2026 (Asia/Shanghai). **This is research and an integration design, not a completed integration test.** No third-party framework was installed or executed for this review. The proposed contract fields below describe adapter boundaries; they are not claims that the current CLI implements these APIs.

## Implementation decision

Keep the core independent: Markdown remains the source of truth for durable knowledge, curriculum progress, and experience; model weights remain outside the optimization surface. Adapters exchange explicit task packages, execution receipts, and artifact references. These projects offer mechanisms to study and optional interfaces to test. Reading their documentation does not grant their capabilities to this Skill.

Start with three small contracts: a **capability evidence card**, a **bounded experiment receipt**, and **reversible experience promotion**. Reliable judgments come before more background orchestration. More instructions, chats, or checker calls do not establish improvement. A capability without host execution evidence remains planned or unavailable.

## Project findings

### 1. LangGraph: separate task recovery from durable knowledge

LangGraph distinguishes thread-scoped checkpoints from a cross-thread store. Its documentation explicitly warns that an in-memory checkpointer loses state on restart. [Persistence](https://docs.langchain.com/oss/python/langgraph/persistence), [checkpointers](https://docs.langchain.com/oss/python/langgraph/checkpointers).

For PAG, context plus the latest node restores current work; memory and experience preserve durable facts. An adapter should provide the memory-root identity, revision, and content hashes. A matching chat title is insufficient.

Failure cases include replaying a committed side effect, concurrent writes against stale revisions, and mistaking RAM persistence for process recovery. Retry only actions known to be replayable; read back an uncertain external result first.

**Next test:** interrupt before and after a receipt is saved, restart a real Agent, and verify that a completed side effect is not duplicated. A fresh chat must retrieve and cite the same Markdown experience.

**Decision:** use the separation as a design reference. Do not introduce another authoritative database or a mandatory LangSmith service. **License: MIT.** [Pinned license](https://github.com/langchain-ai/langgraph/blob/3c916d750575b22c464790e9774494d810ccd322/LICENSE).

### 2. Letta Code: background consolidation with platform limits

The old letta-ai/letta repository now directs users to letta-ai/letta-code; its retired V1 server remains on an archive branch. [Migration notice](https://github.com/letta-ai/letta/blob/main/README.md).

Current Letta documentation describes Git-backed MemFS and background subagents that review conversations and consolidate memory. A second Agent can review proposed changes. The current harness also exposes memory, skills, prompt changes, and harness mods. [Memory and dreaming](https://docs.letta.com/configuration/memory), [pinned README](https://github.com/letta-ai/letta-code/blob/9df436cffa588f45aadef86f34d43fb8f3008c40/README.md).

For PAG, produce a candidate diff before changing current experience. Consolidation and capability promotion must remain separate: saving a lesson does not prove mastery.

The README says automatic reflection is disabled by default on native Windows, packaged wheels do not support Windows ARM64, and the default backend is Letta Cloud. These facts prevent treating Letta as a verified replacement for the tested Windows ARM64 Koder path or silently moving local memory to the cloud.

**Next test:** offer a valid new lesson, an outdated preference, and an unsupported inference. Accept only evidence-backed changes, preserve the reason for corrections, and leave the inference provisional. Host-closed wakeup is a separate test.

**Decision:** study revisioned memory and quiet review; do not import its personhood claims, migrate user data, or install a persistent service. **License: Apache-2.0.** [Pinned license](https://github.com/letta-ai/letta-code/blob/9df436cffa588f45aadef86f34d43fb8f3008c40/LICENSE).

### 3. DSPy: specify module contracts and constrain optimization

DSPy optimizers use a program, an evaluation metric, and input examples. Some tune instructions or demonstrations; others fine-tune weights. Its documentation explicitly separates BootstrapFinetune and mixed optimization from prompt-only methods. [Official optimizer documentation](https://github.com/stanfordnlp/dspy/blob/c8176a8fa65e9772d9d44a33f464f4271c97b806/docs/docs/learn/optimization/optimizers.md).

For PAG, define each module's inputs, outputs, constraints, and failure modes. Limit changes to instructions, example selection, tool descriptions, retrieval, and planning. Record the fixed model identifier and request configuration. With a hosted model, this does not prove that a provider never changes internal weights.

Main risks are optimizing surface formatting, overfitting a small development set, leaking held-out answers, and improving one module while degrading the full task.

**Next test:** compare baseline, general, domain, and composed candidates under the same model and task budget. Development tasks inform changes; sealed tasks are evaluated afterward.

**Decision:** borrow explicit signatures and modular optimization, not fine-tuning, distillation, or RL. Do not adopt documentation prices or timings as PAG results. **License: MIT.** [Pinned license](https://github.com/stanfordnlp/dspy/blob/c8176a8fa65e9772d9d44a33f464f4271c97b806/LICENSE).

### 4. GEPA: readable feedback and complementary candidates

GEPA uses execution feedback to propose prompt changes and retains candidates with complementary strengths. Its adapter separates execution, feedback construction, proposal generation, and state restoration. This is a close research reference for Propose–Probe–Compose. [Paper v2](https://arxiv.org/abs/2507.19457v2), [official adapter](https://github.com/gepa-ai/gepa/blob/8c7b697a71977980afc7537dac0881e784eef99f/src/gepa/core/adapter.py).

PAG should retain tool failures, artifact defects, constraint violations, and resource bottlenecks, rather than one score. Test a general candidate G and a domain candidate D independently. If their strengths are complementary, build C and run C separately. Two good patches can interact badly.

“Do not look at the answer” means candidate authors do not receive sealed reference answers. Evaluators still need a fixed rubric, independently verifiable facts, or real delivery checks. Otherwise optimization becomes self-approval.

Do not transfer GEPA's published speed or quality improvements to this project. Observable calls, outputs, artifacts, and concise decision rationales are sufficient; private hidden reasoning is not a required artifact.

**Next test:** compare full-task quality, elapsed time, work time, token usage, billing, and regressions for all four variants. Reject a composite that harms existing capability.

**Decision:** use research principles and an optional evaluator adapter; independently implement the candidate lifecycle. Do not copy the optimizer or claim its research as ours. **License: MIT.** [Pinned license](https://github.com/gepa-ai/gepa/blob/8c7b697a71977980afc7537dac0881e784eef99f/LICENSE).

### 5. OpenHands: distinguish the host, executor, and scheduler

The current main repository describes Agent Canvas. The software-agent-sdk repository owns the Agent Server, tools, events, and execution; the automation repository owns schedules, webhooks, history, and dispatch. Canvas can select backends and connect to ACP-compatible agents. [Pinned architecture and repository boundaries](https://github.com/OpenHands/OpenHands/blob/7f6c52f8ea7187249dfe1b363a4c1efbfa9a6bc6/README.md).

PAG's Skill decides whether preparation or review is useful. A host adapter must create and verify an actual schedule. A runner executes the task, and a verifier checks its result. A schedule file is not a wakeup.

Failure cases include treating a UI's scheduled label as a trigger, treating dispatch as completion, and allowing multiple chats to race in one workspace.

**Next test:** bind host automation ID, native event ID, scheduled and actual times, and run ID. Resume the same memory root from that event and read back the result. Shared knowledge must coexist with isolated workspaces and detectable write conflicts.

**Decision:** study the separation of scheduling and execution. Do not deploy Canvas or connect external channels by default. An unsandboxed local backend has host filesystem access; open-source status does not grant permission.

**License: MIT for the inspected main repository.** Subrepositories and dependencies require separate review. [Pinned license](https://github.com/OpenHands/OpenHands/blob/7f6c52f8ea7187249dfe1b363a4c1efbfa9a6bc6/LICENSE).

### 6. mini-swe-agent: test whether complexity earns its cost

The current main line is v2. It separates model, environment, and Agent; the README describes a linear history and independently executed shell actions. [Pinned README](https://github.com/SWE-agent/mini-swe-agent/blob/04d809ceab9df28f9adaed044884180159172930/README.md).

Keep a short baseline for every new learning procedure. If the elaborate workflow produces the same quality more slowly and expensively, shorten it or route it only to tasks that benefit. Not every task needs an entire teaching curriculum.

Bash-only execution is not universal across GUI, Windows, and document tasks. An available training interface does not authorize RL in our project.

**Next test:** compare a real defect repair and a teaching task against a minimal baseline, using complete task outcomes and all resource costs.

**Decision:** use it as a baseline design reference, not a substitute for the actual Koder, Cursor, or Codex Agent identity. **License: MIT, in LICENSE.md.** An initial LICENSE request returned 404; the correct file was then read. [Pinned license](https://github.com/SWE-agent/mini-swe-agent/blob/04d809ceab9df28f9adaed044884180159172930/LICENSE.md).

### 7. Inspect: resumable evaluation and complete resource accounting

Inspect separates tasks, solvers, and scorers, supports resumable evaluation sets, and records evaluation logs. Its limits distinguish working time from elapsed time; the documentation notes that concurrency can make working time undercount. [Logs](https://inspect.aisi.org.uk/eval-logs.html), [evaluation sets](https://inspect.aisi.org.uk/eval-sets.html), [limits](https://inspect.aisi.org.uk/setting-limits.html).

For PAG, execution and assessment should be distinct. Include failed attempts, preparation, review, and repair in total costs. Never hide coordinator effort as free work.

Inspect can clean up failed-run logs after successful retries. PAG should not adopt that behavior for its evidence ledger. Raw .eval or JSON logs may be attachments, but durable knowledge remains readable Markdown.

**Next test:** resume without rerunning successful samples; distinguish failed, cancelled, timed-out, and unknown outcomes. Unknown cost is null with a reason, never zero. Preserve old scores when rubric versions change.

**Decision:** use its evaluation structure or an optional external evaluator, not its entire benchmark catalog. **License: MIT.** [Pinned license](https://github.com/UKGovernmentBEIS/inspect_ai/blob/706b4c5d6a3af83150ae3fc66ddf84b6bc37f50f/LICENSE).

### 8. promptfoo: fixed criteria and paired comparisons

Promptfoo documents deterministic assertions, model grading, custom metrics, trajectory checks, and latency/cost measurements. It distinguishes weighted scores from checks that must all pass. [Assertions and metrics](https://www.promptfoo.dev/docs/configuration/expected-outputs/).

For PAG, source identity, artifact existence, permission boundaries, and user constraints are hard gates. Readability and usefulness can be graded dimensions. A high average must not cancel a hard failure.

Risks include changing the evaluator to pass a current answer, verbosity bias in model grading, counting cached output as a fresh Agent run, and assuming local evaluation means remote model requests never leave the device.

**Next test:** include controlled counterexamples: correct format with false content, a fast answer that omits a constraint, a stale receipt, and successful tool execution with a bad artifact. Keep the rubric fixed and blind candidate labels.

**Decision:** use layered criteria; do not initiate production red teaming. **License: MIT.** [Pinned license](https://github.com/promptfoo/promptfoo/blob/f2b012e3c9f9ffb7b23edf4cf88ea63febf72f5a/LICENSE).

### 9. MCP Python SDK: shared interfaces do not create permissions

The SDK exposes standard tools, resources, and prompts through clients and servers. The current README points to v2 documentation and Python 3.11+, so older examples are not a safe installation contract. [Pinned README](https://github.com/modelcontextprotocol/python-sdk/blob/d7845c073a2b9ba5ab2817ecf93d3e45ef24cd14/README.md), [protocol security guidance](https://modelcontextprotocol.io/specification/latest/basic/security_best_practices).

Possible PAG interfaces include learning.read, learning.search, learning.checkpoint, and learning.record_evidence. These are proposals. Scheduling still requires an available host capability, permission, and a real receipt.

**Next test:** bounded paths and sizes, revision-checked writes, rejection of unknown tools, and read operations that cannot mutate. External content cannot override user constraints. Two hosts must read identical Markdown bytes and record the next revision after continuation.

**Decision:** keep MCP optional. Preserve a file/CLI path without a third-party SDK prerequisite. **License: MIT.** [Pinned license](https://github.com/modelcontextprotocol/python-sdk/blob/d7845c073a2b9ba5ab2817ecf93d3e45ef24cd14/LICENSE).

### 10. AutoGen: retain reasons not to adopt a familiar framework

The current README says the project is no longer maintained and recommends Microsoft Agent Framework. The repository API returned archived=false in the same review. Record that discrepancy rather than silently selecting one status. [Pinned README](https://github.com/microsoft/autogen/blob/d07c667a3239ea4ab7af62a53b0f4ff205a1f23d/README.md).

GitHub's license summary is also insufficient: LICENSE-CODE is MIT while the root LICENSE contains CC-BY-4.0. [Code license](https://github.com/microsoft/autogen/blob/d07c667a3239ea4ab7af62a53b0f4ff205a1f23d/LICENSE-CODE), [root license](https://github.com/microsoft/autogen/blob/d07c667a3239ea4ab7af62a53b0f4ff205a1f23d/LICENSE).

Its core transport, higher-level AgentChat, and extensions remain architectural references. **Decision:** historical research only; no new runtime dependency. The successor is a future candidate, not an inspected or integrated dependency in this review.

## Proposed interoperability contracts

These are independently designed boundary proposals, not implemented API claims. Save structured fields in Markdown metadata and explanations in the body. JSON may transport or index that information; removing derived JSON must not erase the knowledge.

### CapabilityCard

```yaml
id: cap-domain-task-name
scope: project/example
stage: unknown | reproduces | explains | transfers | teaches | delivers
status: untested | verified | needs_review | unavailable
prerequisites: [cap-...]
gap_kind: knowledge | procedure | tool | environment | authorization | evidence
evidence: [{path: runs/run-id.md, sha256: "...", claim: "..."}]
valid_for: {tool: "...", platform: "...", versions: ["..."]}
review_due: "actual date or null"
```

Stages summarize several dimensions, not an automatic ladder. Someone can operate without teaching well, or explain without delivering. Mastery is limited to the tested task distribution and environment. Missing tools, environment, or permission cannot be resolved by adding more self-instructions.

### RunReceipt

```yaml
id: run-...
task_id: ...
candidate_id: baseline | general | domain | composed
actor: {host: "...", agent: "...", model: "...", session_id: "..."}
inputs: [{path: "...", sha256: "..."}]
memory: {root_identity: "...", read_revision: 7, written_revision: 8}
trigger: {kind: user | native_schedule | continuation, host_event_id: null}
started: ...
ended: ...
execution: {status: passed | failed | cancelled | unknown, exit_code: null}
artifacts: [{path: "...", sha256: "..."}]
quality: {rubric_version: "...", hard_gates: [], dimensions: {}, assessor: "..."}
usage: {wall_seconds: null, working_seconds: null, model_tokens: null, money: null, currency: null, unknown_reason: "..."}
follow_up: {decision: keep | repair | rehearse | review | reject, evidence: "..."}
```

Keep tool receipts separate from the model's account. Exit zero, a self-assigned score, and a written summary do not prove task success. Use observable actions and concise explanations; do not require private hidden reasoning.

### CandidatePatch

```yaml
candidate_id: ...
kind: general | domain | composed
parent_version: ...
change_surface: prompt | skill | tool-description | retrieval | scheduler-policy | runner
hypothesis: ...
expected_improvement: ...
scope: ...
patch_sha256: ...
protected: [user_constraints, evidence_history, rubric, permission_boundary, held_out_tasks]
probe_runs: [...]
decision: proposed | rejected | provisional | adopted | reverted
```

Changing the surrounding harness does not authorize bypassing host permissions. Scheduling changes require native readback; a plan file does not change a scheduler.

## Data flow and adoption gate

1. Restore relevant context and experience, then record the actual gap and an initial prediction.
2. For a knowledge or method gap, consult credible sources, save provenance, test understanding on a small task, and define a bounded curriculum.
3. Propose G and D under the same task constraints. Keep the baseline unchanged and make each main change attributable.
4. Run B/G/D separately. Create C only when supported by complementary evidence, and execute C independently.
5. Use development tasks for revisions. Keep sealed evaluation tasks separate and preserve existing capability regression checks.
6. Require every hard gate. Compare quality, elapsed time, and cost separately. A quality gain that costs more is a tradeoff, not a claim of improvement on every axis.
7. Version accepted changes. Experience records carry scope, counterexamples, evidence, and review conditions. A new session must actually be able to use them.
8. Test transfer in a later real task. A failure can demote or revert a provisional lesson.

## Selection rules

For each project, identify the reproducible gap it addresses, official source, per-file license, data location, network behavior, platform support, removal path, and the specific test that could reject it.

Reject unclear source or licensing, hidden memory migration, required weight training, demos without observable interfaces, deletion of failure evidence to improve metrics, and unbounded background work unrelated to a task.

Start with a small adapter and at most one indispensable runtime dependency. If existing tools provide the capability without a measurable disadvantage, do not add a framework. Popularity and maintenance activity provide context; they do not replace capability, compatibility, licensing, or cost evidence.

## Suggested real experiments

These are **proposed experiments, not execution records**.

- **Domain A:** repair a real input-boundary defect in a small tool. Deliver the patch, positive and negative cases, regression results, and an installation check. A transfer task changes the encoding or caller to test causal understanding rather than memorization.
- **Domain B:** write a Chinese operating guide from official documentation. A separate Agent receives only the guide and must produce the intended artifact. Grade explanation, source accuracy, actionability, and execution separately.
- Within each domain, keep inputs and tool budgets fixed for B/G/D/C. Promote G beyond a domain only after evidence in both; keep D scoped.
- Two tasks are an initial probe, not proof of universal mastery or statistically established acceleration. Report sample count, variation, failures, and human help. Without billing receipts, report tokens and time rather than invented monetary savings.
- Review requires the actual clock and a host event. Editing a date is not a wakeup. Teaching success requires a learner's new-task performance, not the teacher's self-rating.

## Worked adoption-and-rollback example

This is an **unexecuted design example**. The defect is that background review saved a lesson, but a new chat did not use it. Success means the new chat finishes a related task, correctly cites the source file, and has complete time and cost accounting.

1. **Discover:** inspect the failed receipt and establish that the file exists but retrieval missed it. Study Letta's consolidation and LangGraph's checkpoint/store separation. Save citations without installing a service.
2. **Propose:** G adds applicability conditions and counterexamples to experiences. D adds platform and permission tags to Windows handoff lessons. Freeze the baseline, memory revision, tasks, public rubric, and experiment budget. Reuse existing authorization for isolated local tests; request only genuinely additional permissions for a new paid or remote service.
3. **Admit:** execute B/G/D in isolated copies, recording original outputs, complete quality, time, and tokens. If the intended Letta distribution does not support Windows ARM64, mark that third-party runtime adapter unavailable. Do not invent its execution or confuse that limit with failure of our independently testable memory rule. Test the rule with an already supported host.
4. **Compose:** if G improves attribution and D improves recall without regressions, propose C. Run C in another fresh session; its score cannot be assembled from the two earlier passes.
5. **Revert:** suppose C ranks an outdated lesson above a new user instruction. Reject C and restore the previous version. Preserve the failure receipt, mark the lesson needs_review, and record a targeted correction. Do not weaken the current-instruction hard gate.
6. **Retain:** only a genuinely passing G or D can be provisionally adopted in its tested scope. Observe use in the next task. A review date remains a plan until a real host schedule and trigger are verified.

The useful property is not endless adoption. It is the ability to attribute a result, reject a change, and reverse it.

## What independent development means

The team can accurately describe independently implemented orchestration, Markdown contracts, capability evidence, promotion, rollback, and evaluation while citing public research. Referenced research does not become our original theory. A project that uses an external framework must not claim to have no third-party components.

Mechanism research requires attribution and does not justify copying source, branding, or whole manuals. If a dependency or source fragment is later incorporated, pin its version, preserve its license, copyright and applicable notices, and document modifications. The existing AGPL license does not erase upstream obligations. This review makes no blanket legal-compatibility finding about future combinations. No runtime dependency was added.

## Verification record and limits

The review read README and license files for ten main projects through the GitHub connector, then reread the same files at explicit commits. **All 20 blob identities matched.** Additional reads covered the Letta migration notice and DSPy/GEPA interface documentation. These are source/documentation checks, not runtime tests.

Preserved lookup failures: mini-swe-agent's LICENSE path returned 404 before LICENSE.md succeeded; an old mini architecture URL was unavailable, so no claim relies on it; DSPy's documentation redirect exposed no content, so the official repository source was used; an old Inspect limits URL had no readable body, and the official index led to the current limits page.

| Project | Reviewed commit | Reread file blob IDs (Git object IDs, not file SHA-256 hashes) |
|---|---|---|
| langchain-ai/langgraph | `3c916d750575b22c464790e9774494d810ccd322` | README.md: `97c31e9cb4d8fe56be8d768ce3eb5e22400e897e`<br>LICENSE: `fc0602feecdd6748623c852ab534e1ca612673c7` |
| letta-ai/letta-code | `9df436cffa588f45aadef86f34d43fb8f3008c40` | README.md: `6b09e6cf359981d7c2a6c225a6fa1b8617a8435b`<br>LICENSE: `e72f5de5dd5610ee3fee7feb791ebff246cc931e` |
| stanfordnlp/dspy | `c8176a8fa65e9772d9d44a33f464f4271c97b806` | README.md: `f92d3311e085fed87af6c724b2d43e2076b57cc6`<br>LICENSE: `be3f5c0e3fc7e6b0e7c9dddd9db313ab15bfa62b` |
| gepa-ai/gepa | `8c7b697a71977980afc7537dac0881e784eef99f` | README.md: `365edf3d878f6996259cfc95c401547825fdc65b`<br>LICENSE: `a2d71aed19ccc43d94b9c3afe6430da9b2277f32` |
| OpenHands/OpenHands | `7f6c52f8ea7187249dfe1b363a4c1efbfa9a6bc6` | README.md: `d2c59eb5c77b9afed050b5a2e28b79317f7fab18`<br>LICENSE: `f6f60f52368bcc96f82fbe59ec65049c2c3af9db` |
| SWE-agent/mini-swe-agent | `04d809ceab9df28f9adaed044884180159172930` | README.md: `7db1d82dfa92eaa00adeb10c8681677a9e6ec639`<br>LICENSE.md: `503821c9dbe06f13a48e54088eb6cd203adb407f` |
| UKGovernmentBEIS/inspect_ai | `706b4c5d6a3af83150ae3fc66ddf84b6bc37f50f` | README.md: `0a035b0ca7039767517be2e50a60e1b034a3c1d4`<br>LICENSE: `72fc87742ef8a944fab4f28fe6231696c62f2fa4` |
| promptfoo/promptfoo | `f2b012e3c9f9ffb7b23edf4cf88ea63febf72f5a` | README.md: `2a56017c2609e3a92d7d5539147c9c7e620a3420`<br>LICENSE: `af3fa111d9303b3041d225fb851534e50a4bbec2` |
| modelcontextprotocol/python-sdk | `d7845c073a2b9ba5ab2817ecf93d3e45ef24cd14` | README.md: `50ea0ed227b72de82917d67d678d1d24783ab2e9`<br>LICENSE: `3d48435454b105021b4f777c11b6b07d8d2ffea3` |
| microsoft/autogen | `d07c667a3239ea4ab7af62a53b0f4ff205a1f23d` | README.md: `042b9df197a220ec7072a116d694cd497ec332ad`<br>LICENSE-CODE: `9e841e7a26e4eb057b24511e7b92d42b257a80e5` |

Performance, actual interoperability, autonomous wakeups, and platform behavior require separate PAG execution evidence. This research does not mark any of those capabilities as passed.
