# Personal Agent Growth

[English](README.md) · [简体中文](README.zh-CN.md) · **0.4.3**

[![Checks](https://github.com/KarmenLoop/personal-agent-growth/actions/workflows/check.yml/badge.svg)](https://github.com/KarmenLoop/personal-agent-growth/actions/workflows/check.yml)
[![Release](https://img.shields.io/github/v/release/KarmenLoop/personal-agent-growth)](https://github.com/KarmenLoop/personal-agent-growth/releases/latest)

Personal Agent Growth is an open-source skill for preparing, executing, reviewing, and improving ongoing agent work. It connects durable task memory, evidence-based decisions, cross-tool recovery, and **Propose–Probe–Compose** experiments. Improvements change authorized prompts, tools, retrieval, and workflow components; model training and weight updates are outside the method.

An agent should be able to explain which observation changed its decision, reuse the resulting lesson in another task, and show the result. A larger prompt or a growing collection of notes is not sufficient evidence of improvement.

## Start here

| Need | English | 中文 |
|---|---|---|
| Install, update, remove | [Installation](docs/install.md) | [安装说明](docs/install.zh-CN.md) |
| Complete a first task and hand it off | [Tutorial](docs/tutorial.en.md) | [实操教程](docs/tutorial.zh-CN.md) |
| Understand the whole architecture | [Architecture](docs/architecture.en.md) | [架构剖析](docs/architecture.zh-CN.md) |
| Follow the decision and learning logic | [Reasoning method](docs/reasoning.en.md) | [思考与判断方法](docs/reasoning.zh-CN.md) |
| Explore the detailed maps | [Mind maps and diagrams](docs/mindmaps.en.md) | [复杂思维导图](docs/mindmaps.zh-CN.md) |
| Use daily, weekly, and project memory | [Markdown learning](docs/markdown-learning.en.md) | [Markdown 学习体系](docs/markdown-learning.zh-CN.md) |
| Check actual support and evidence | [Compatibility and evidence](docs/compatibility.en.md) | [兼容性与验收边界](docs/compatibility.zh-CN.md) |
| Browse all documents | [Documentation index](docs/index.en.md) | [完整文档索引](docs/index.zh-CN.md) |

![Architecture and responsibilities](docs/diagrams/architecture.en.svg)

Open the [full system mind map](docs/diagrams/system.en.svg) to zoom into the capability tree. The [diagram guide](docs/mindmaps.en.md) connects it to decision logic, memory, recursive experiments, scheduling, and handoff sequences. Editable Mermaid sources accompany every diagram.

## How the work connects

1. **Recover.** Read the current project context, latest checkpoint, constraints, and relevant lessons. Check artifact identity and who may write next.
2. **Judge.** Separate observations, hypotheses, unknowns, and user choices. Define completion before choosing a method.
3. **Prepare.** Identify the next missing capability, learn only what can affect the next action, and record a prediction.
4. **Execute.** Use actual host tools and preserve input identity, outputs, failures, and reached stages.
5. **Review.** Compare the outcome with the prediction. Diagnose a wrong assumption, missing knowledge, environment failure, or method defect before changing anything.
6. **Improve.** Propose a general change and a domain change, run each against the baseline, and test any composition before adoption.
7. **Retain and resume.** Write the lesson with its scope and counterexamples. Complete the task, hand it off, or register useful future work with a real host scheduler.

The user can choose: **finish anything the agent can resolve; contact the user only when their decision is required**. The skill avoids routine questions, duplicate schedules, and unnecessary chats.

## What ships

| Component | Responsibility |
|---|---|
| [SKILL.md](SKILL.md) / [English text](SKILL.en.md) | Portable instructions and links to the relevant procedure |
| [References](references/recursive-improvement.en.md) | Decision, learning, recovery, scheduling, and recursive-improvement contracts |
| [32 learning templates](templates/learning/README.md) | Sixteen document types in each language, including daily/weekly reports, checkpoints, experience, and user evidence |
| `scripts/verify_handoff.py` | Bounded ZIP/manifest consistency checks |
| `scripts/compare_trials.py` | Frozen experiments, comparison, composition checks, experience versions, and rollback |
| `scripts/host.py` | Optional local CLI/MCP adapter with five checkpoint and handoff tools |
| `tools/local_install.py` and delivery tools | Full bundle installation, relocation checks, experience loading, and removal that retains memory |
| `examples/experience-seed` | Reviewed historical profiles and lesson excerpts with export provenance |

The skill depends on its host for the model, tools, execution permissions, and scheduling. Installation does not start a daemon or connect another device. Read [the storage boundaries](docs/architecture.en.md#storage): the optional SQLite handoff adapter and legacy JSON experiment library are separate from the new Markdown learning contract. They are not a second user profile.

## Quick start

Download the **complete delivery bundle** and `SHA256SUMS.txt` from [v0.4.3](https://github.com/KarmenLoop/personal-agent-growth/releases/tag/v0.4.3). Extract it and follow [START-HERE.md](START-HERE.md). Python 3.11+ is needed for the utilities; there are no runtime pip dependencies.

From the extracted full bundle on macOS:

```sh
python3 -B tools/check_delivery.py .
python3 -B tools/local_install.py install --root "$HOME/Desktop/AgentKnowledge"
```

On Windows, use `py -3 -B -X utf8`; the guide prefers `D:\AgentKnowledge` when D: exists, otherwise C:, or a user-selected writable location. Keep your private learning directory separate from the public distribution. `~/.koder/learning` is the default in the separate Koder candidate; other hosts can share an explicitly chosen path.

Give your agent an actual task:

> Read the installed personal-agent-growth/SKILL.md. Complete this task using the private learning root I provide. Before resuming, read the project context and latest node. Record the next prediction, run the relevant tools, review the outcome, and retain useful experience with sources. Use the Markdown learning protocol for daily, weekly, and project records. Finish solvable work yourself; ask only when my decision is required. Do not create a schedule unless a future review has a concrete purpose.

For automatic skill discovery, use one supported discovery entry pointing at the canonical folder. Explicitly reading `SKILL.md` is a valid fallback, but it does not establish automatic selection. See [installation](docs/install.md) for both hosts and both operating systems.

## Recursive improvement with frozen model configuration

When this mode is enabled, each new task starts from its current accepted baseline and two proposals: a transferable weakness and a domain-specific weakness. Baseline, general, and domain arms complete the same task with frozen inputs, quality criteria, model configuration, and budgets. A composed successor receives a separate run. Leaf workers do not spawn recursive experiments.

The outer loop improves proposal generation, retrieval, routing, and budget allocation across tasks. Promotion requires transfer and regression tasks in at least two domains. The method uses observable constraints, environment feedback, and independent reuse rather than supplied standard answers. See the [complete protocol](references/recursive-improvement.en.md).

Weights are not trained or updated by this project. A hosted model may not expose a weight hash; visible configuration is recorded, and unobservable provider changes remain a limitation.

## What the evidence supports

- A historical Codex trial received **two genuine scheduler wakeups**, executed work, changed the schedule, restored results, and paused the automation.
- A separate same-Mac Cursor trial read and advanced shared task revisions **1→2, 3→4, 5→6**, with repairs after relocation failures.
- **24 actual Codex CLI executions** compared software-release acceptance and NASA data analysis. Across the composed runs, tokens fell **5.9%**, while elapsed time rose **7.4%**. This does not establish an overall speedup or universal intelligence gain. [Full report](docs/cross-domain-trial.md)
- All **21 original skips now execute and pass**: 17 in the macOS suite, plus 4 in a real Windows ARM64 VM. Three additional real ACL checks also pass. The retained macOS full run remains **1485 pass, 0 fail, 0 cancelled, 4 platform skips**; the separate Windows run used a privileged SYSTEM context. [Per-case audit](docs/release-0.4.3-acceptance.en.md)

![Full-task token and time measurements, including the timing anomaly](docs/images/cross-domain-0.4.1.png)

Repository tests establish file, utility, and protocol behavior. They do not replace Windows desktop Agent execution, a fresh authenticated Cursor model turn, cross-device synchronization, or operation after the app closes. Current publication checks and their exact scope are in the [0.4.3 acceptance report](docs/release-0.4.3-acceptance.en.md).

## Development

```sh
python3 -B -m unittest discover -s tests -v
python3 -B scripts/check_publication.py
python3 -B tools/build_release.py --output dist
python3 -B scripts/verify_handoff.py --archive dist/personal-agent-growth-0.4.3.zip --manifest dist/manifest.json
python3 -B tools/build_delivery.py --output /path/to/fresh-output
```

[Contributing](CONTRIBUTING.md) explains the distinction between utility checks and host behavior. Keep task records, credentials, user profiles, and private traces out of public contributions.

## Team and license

Created and maintained by the **KARMENLOOP Official Team**, Shanghai, China. We build Koder and KARMEN BOT. [Team](TEAM.md) · [Website](https://karmenloop.com) · [GitHub](https://github.com/KarmenLoop) · [Email](mailto:info@karmenloop.com)

Copyright (C) 2026 KARMENLOOP Official Team. Licensed under **AGPL-3.0-only**. Keep [LICENSE](LICENSE) and [NOTICE](NOTICE) with covered copies. Commercial use is allowed; distribution and modified network-service use carry the license's applicable source obligations. AGPL does not require private changes to be posted on GitHub. The [licensing guide](docs/licensing.md) explains the scope.
