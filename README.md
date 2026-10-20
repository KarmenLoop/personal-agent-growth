# Personal Agent Growth

A skill for keeping an agent's work connected across tasks, reviews, and tools. It helps the agent prepare for its next step, learn from a failed attempt, revise a decision when evidence changes, and resume from shared task records.

Version **0.3.2** includes lessons from real Codex scheduled runs and a Codex-to-Cursor handoff on one Mac. The skill instructions are in Chinese. Complete installation guides are available in English and Chinese; licensing and contributor documentation are in English.

## What it does

- Records a goal, a prediction, the evidence needed to check it, and the next useful action.
- Uses targeted preparation and review instead of collecting information without a purpose.
- Keeps task state and lessons in a shared location with a clear writer and revision.
- Revises a skill when a method has failed, then checks the change against the task and meaningful variations.
- Uses a host's scheduling interface when future work is useful, verifies the actual trigger, and stops the schedule after completion.
- Respects the user's contact preference, including completing solvable work before asking for a decision.

The skill is a set of instructions and a small offline package checker. It does not install a background service, supply a model, synchronize devices, or grant access to another tool. Scheduled work needs an authorized scheduler in the host application.

## Install

Start with the complete [English installation guide](docs/install.md) or [Chinese installation guide](docs/install.zh-CN.md). Both cover macOS and Windows commands, Codex and Cursor discovery, shared task memory, verification, scheduled reviews, updates, and removal.

Download `personal-agent-growth-0.3.2.zip` and `manifest.json` from the [release](https://github.com/KarmenLoop/personal-agent-growth/releases/tag/v0.3.2). Extract the `personal-agent-growth` folder into a skill directory supported by your agent. Keep its `references`, `scripts`, `LICENSE`, and `NOTICE` files together.

Alternatively, clone the source:

```sh
git clone https://github.com/KarmenLoop/personal-agent-growth.git
```

Open the extracted or cloned folder in your tool and explicitly ask it to read `SKILL.md`. This is also a fallback when the tool has not discovered the skill automatically.

For shared use, point both tools at the same skill folder and the same **separate task-memory folder**. Confirm the resolved paths and current state before handing off work. A shared skill does not share login credentials, permissions, or a scheduler.

The recommended installation uses one shared skill folder and one discovery entry under `.agents/skills`, supported by current Codex and Cursor versions. Follow the guide to check actual loading in your host.

The macOS guide's install and removal commands were executed in an isolated directory. See the [installation command results](docs/install-verification.md) for checks, file identities, and the untested Windows-command scope.

## Start a task

Give the agent a real outcome and a location for its task records:

> Read this skill's SKILL.md and use it to finish the current task. Keep the goal, state, decisions, evidence, and next action in the task-memory folder I provide. Prepare for the next useful step, test uncertain assumptions, and review the result. Complete anything you can resolve yourself; ask me only when my decision is required.

When handing the task to another tool, give it the same memory location and ask it to resume from the current revision. The [shared-memory reference](references/shared-memory.md) defines the write and handoff rules.

## Check an offline package

Python 3.11 or later is the supported baseline for the bundled utilities. They use only the standard library.

Run this from the repository or extracted skill folder, replacing the two paths:

```sh
python3 scripts/verify_handoff.py \
  --archive /path/to/personal-agent-growth-0.3.2.zip \
  --manifest /path/to/manifest.json
```

On Windows, use `py -3` in place of `python3` and supply Windows paths.

| Exit | Result | Meaning |
|---|---|---|
| 0 | PASS | The archive and supplied manifest are consistent. |
| 1 | REJECT | Inspection found an archive inconsistency. |
| 2 | INCOMPLETE | An input, invocation, or resource limit prevented full inspection. |

This check does not authenticate the publisher or prove that a host will use the skill correctly. The [manifest format](docs/manifest.md) explains the checks and limits.

## Validation

Version 0.3.2 passed 13 utility tests and 21 package checks on each of Linux, macOS Intel, and Windows. The [release acceptance report](docs/release-0.3.2-acceptance.md) includes the completed CI jobs, package hashes, and the resolved macOS scheduling issue.

The preceding local trials included two genuine Codex scheduler wakeups and three Cursor recoveries from shared task memory. An independent review found two relocation mistakes, which were corrected and checked again.

The final 0.3.2 text adds the lessons from those trials. It has not had a separate complete Cursor behavior trial. See [validation and limitations](docs/validation.md) for the exact scope.

The repository includes reproducible checks:

```sh
python3 -m unittest discover -s tests -v
python3 tools/build_release.py --output dist
python3 scripts/verify_handoff.py \
  --archive dist/personal-agent-growth-0.3.2.zip \
  --manifest dist/manifest.json
```

## Team

Created and maintained by the **KARMENLOOP Official Team**, based in **Shanghai, China**. We build Koder and KARMEN BOT, with tools for coding and everyday work.

- Website: [karmenloop.com](https://karmenloop.com)
- GitHub: [KarmenLoop](https://github.com/KarmenLoop)
- Email: [info@karmenloop.com](mailto:info@karmenloop.com)
- [Team and project information](TEAM.md)

## License

Copyright (C) 2026 KARMENLOOP Official Team.

The original skill instructions, reference documents, scripts, tests, and repository documentation are licensed under **GNU Affero General Public License version 3 only (`AGPL-3.0-only`)**. See [LICENSE](LICENSE) and [NOTICE](NOTICE).

Commercial use is allowed. Distribution of covered modified versions carries source and license obligations. A modified version that supports remote network interaction must offer its corresponding source to those users as required by section 13. Purely private changes do not have to be published, and AGPL does not require using GitHub. Read the [licensing guide](docs/licensing.md) for practical examples.
