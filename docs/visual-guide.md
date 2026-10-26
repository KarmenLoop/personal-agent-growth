# Visual guide

[中文入口](visual-guide.zh-CN.md) · [Expanded diagrams for 0.4.1](mindmaps.en.md)

Use these diagrams with the [installation guide](install.md). They describe the intended workflow and the evidence needed to accept a result. Actual platform results are linked below; an arrow in a diagram is not an execution record.

## Install once, keep task memory separate

```mermaid
flowchart TD
    R["Download the release ZIP and manifest"] --> H{"Both pinned hashes match?"}
    H -->|No| X["Preserve the downloads and resolve the mismatch"]
    H -->|Yes| S["Extract one canonical skill folder"]
    S --> L["Create one discovery entry pointing to that folder"]
    L --> A["Codex or Cursor reads the actual SKILL.md"]
    A --> T["Run a useful task in a separate private memory folder"]
    T --> C["Inspect the saved state and real command receipts"]
```

For the recommended installation, the discovery entry is `.agents/skills/personal-agent-growth`. It points to `<root>/skills/personal-agent-growth` through a macOS symbolic link or a Windows directory junction. The Windows root defaults to D: when available and otherwise C:; use a writable custom root when necessary. On macOS, the default root is `~/Desktop/AgentKnowledge`.

```mermaid
flowchart LR
    A["Host A"] -->|Read instructions| S["One canonical skill folder"]
    B["Host B"] -->|Read instructions| S
    A -->|Current writer only| M["One private task directory"]
    B -->|After responsibility transfers| M
    M --> ST["state.json: task ID, revision, writer, next action"]
    M --> EV["Evidence: exact commands, outputs and input identities"]
    M --> LE["Lessons and user contact preference"]
    A -.-> HA["Host A permissions and scheduler"]
    B -.-> HB["Host B permissions and scheduler"]
```

Both hosts must resolve the same task files. A copied directory with matching content does not establish shared mutable memory. Authentication, execution permissions, and scheduling remain with each host. Cross-device use needs an authorized transfer or synchronization method and explicit path mapping.

Removing the discovery link leaves the canonical skill and private task memory in place. The removal commands check the entry type before removing it; they refuse an ordinary directory. See the guide for updates and removal.

## Resume a task without losing newer facts

The revision numbers below are illustrative. The actual task chooses its writer, IDs, and revisions from its saved state.

```mermaid
sequenceDiagram
    participant A as First agent
    participant M as Shared task directory
    participant C as Coordinator
    participant B as Receiving agent
    A->>M: Read revision and writer
    A->>A: Predict, prepare and test
    A->>M: Recheck, save receipts and revision 2
    C->>M: Inspect artifacts and identities
    C->>M: Add new condition and revision 3
    B->>M: Read revision 3 and prior lessons
    B->>B: Run the new check
    B->>M: Save review and revision 4
    A->>M: Restore revision 4 before writing
    A->>A: Accept or repair
```

A handoff is accepted when the receiving agent actually reads the saved revision, applies the relevant lesson, executes the next check, and writes back a verified result. Sending a prompt or seeing an activity indicator establishes only that stage. A late message must reread the current state and skip work already completed.

When a long terminal prompt is unreliable, put the complete task in a file, verify the transferred bytes, and send a short instruction to read its absolute path. Then inspect the agent's actual response and saved outputs. Successful file transfer proves delivery of the input file; it does not establish that the agent read or executed it.

## Decide whether to act now or arrange a wakeup

```mermaid
flowchart TD
    S["Read current state, responsibility and stop conditions"] --> N{"Useful work available now?"}
    N -->|Yes| E["Prepare or review, execute, and save evidence"]
    E --> J{"What remains?"}
    J -->|Actionable repair| E
    J -->|Needs time or new external input| F["Define the next useful action and its deadline"]
    N -->|No, future work is justified| F
    F --> H{"Authorized host scheduler available?"}
    H -->|Yes| R["Register or update the schedule; read it back"]
    R --> T["Receive an actual host trigger"]
    T --> S
    H -->|No| B["Record the missing capability and return responsibility"]
    J -->|User choice required| U["Ask a focused question with the evidence"]
    J -->|Acceptance met| D["Stop the registered schedule and verify its state"]
    D --> Z["Save the final result"]
```

Scheduling is useful only when a later turn has work to do. The skill does not start a service by itself. Preserve the actual registration, trigger, execution, verification, and stop records separately. A manually continued chat, file timestamp, or `ACTIVE` setting cannot stand in for a real scheduled trigger.

## Compare, compose, and reuse

```mermaid
flowchart TD
    M["Load applicable version and experience"] --> P["Propose: general and domain changes"]
    P --> F["Freeze inputs, model configuration and acceptance criteria"]
    F --> B["Run baseline Agent"]
    F --> G["Probe general candidate"]
    F --> D["Probe domain candidate"]
    B --> C["Contrast actual actions, artifacts and measured cost"]
    G --> C
    D --> C
    C --> S["Compose: keep, drop or rewrite components with evidence"]
    S --> T["Freeze and run the composed successor"]
    T --> A{"Quality retained and useful gain demonstrated?"}
    A -->|Yes| V["Activate the tested snapshot with rollback"]
    A -->|No| O["Keep the best tested version"]
    V --> E["Record effective, ineffective and failed changes"]
    O --> E
    E --> R["Next task actually reads version and relevant lessons"]
    R --> M
    E --> X["Outer loop proposes changes to the improvement strategy"]
    X --> Y["Probe a portfolio of transfer and regression tasks"]
    Y --> Z["Adopt only the supported strategy scope"]
    Z --> P
```

The inner loop changes the execution setup for one task. The outer loop uses evidence to improve how future changes are proposed, tested, composed, and retrieved. Both keep model weights unchanged. The agent may change project-owned workflow rules within the user's authorization; it cannot rewrite higher-priority host instructions or retroactively change the current experiment's acceptance criteria.

A composition may discard an entire proposal. It is not required to combine every edit. A new composition must pass its own real execution before activation. See the [measured local trial](recursive-improvement-trial.md); reduced checker process count does not establish lower total Agent cost.

## Read the results at the right level

| Question | Evidence to inspect | Recorded results |
|---|---|---|
| Do the package and manifest agree? | Checker command, exact inputs, raw output and exit code | [Release acceptance](release-0.3.2-acceptance.md) |
| Do installation, links and removal work? | Actual shell commands, file identities and preserved memory | [macOS](install-verification.md), [Windows](windows-install-verification.md) |
| Did an agent use shared memory and review its work? | Actual host behavior plus saved revisions, receipts and follow-up changes | [Agent behavior and limits](validation.md) |
| Did scheduled work really wake and stop? | Host trigger events, executed work and backend readback | [Codex continuation trial](validation.md#native-codex-continuation) |

The published Windows installation results use independent test processes. They do not prove Windows Koder or Cursor Agent behavior. That remains a separate acceptance requirement until the corresponding real-agent records have been inspected. The diagrams above are not a claim that this requirement has passed.

<!-- Copyright (C) 2026 KARMENLOOP Official Team
SPDX-License-Identifier: AGPL-3.0-only -->

## Compare complete tasks across domains

The task, not an individual checker process, is the unit of comparison. Each strategy completes both domains in fresh Agent sessions, with repeated runs and a fixed quality contract.

```mermaid
flowchart TD
    A[Current skill and indexed experience] --> B[Freeze two tasks and two proposals]
    B --> C[Release acceptance: regression task]
    B --> D[Public data analysis: transfer task]
    C --> E[Baseline, general and domain strategies]
    D --> E
    E --> F[Three complete runs per task and strategy]
    F --> G[Inspect artifacts and native execution traces]
    G --> H[Compare quality, elapsed time and token usage per task]
    H --> I{All required evidence available?}
    I -->|No| J[Retain uncertainty and keep the current version]
    I -->|Yes| K[Apply gain and regression limits]
    K --> L[Keep, drop or rewrite supported components]
    L --> M[Test the complete composed strategy]
    M --> N[Versioned experience and a recoverable adoption decision]
```

Cached input tokens remain part of input tokens; they are not added a second time. Actual billing can remain unknown. Interrupted sessions and conflicting clock readings are retained, rather than converted to successful or zero-cost runs.
