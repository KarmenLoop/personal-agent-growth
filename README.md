# Personal Agent Growth

English | [简体中文](README.zh-CN.md)

Give the next work session something better than a chat recap. Keep task state, evidence, corrections, and one useful next action in a shared private folder that the next host can actually read.

[Download v0.3.3](https://github.com/KarmenLoop/personal-agent-growth/releases/tag/v0.3.3) · [Guide](docs/tutorial.en.md) · [Issues](https://github.com/KarmenLoop/personal-agent-growth/issues)

## What it does

A portable instruction skill and offline package checker for task review and handoff. The skill and its four working references are currently Chinese; the public setup guides are available in both languages.

![Personal Agent Growth workflow illustration](docs/images/workflow-v0.3.3.svg)

*Workflow illustration for v0.3.3; not an application screenshot or runtime acceptance.*

## Start here

Download the skill ZIP and manifest.json. Extract into a fresh canonical folder, then add that folder once through your host’s supported skill discovery path. Keep the skill folder separate from private task records.

Choose one private task directory that both hosts resolve to the same physical location. Record the active writer and state_revision before a handoff. Python 3.11+ is needed only for the optional offline checker, not for reading Markdown.

## A first useful task

Explicitly load SKILL.md, review a synthetic task artifact, save the actual check result, correct one mistaken assumption, and leave a concrete next review action. Confirm those files exist before changing hosts.

Have the receiving host read the current revision and use the earlier artifact in a new check. Scheduling needs an actual supported backend and separate task authorization; installation creates no timer or cross-device sync.

## Questions

**Does this retrain a model?** No. It organizes reusable task records and review methods. Model weights and provider accounts are unchanged.

## Documentation and license

[Download, setup, practice, and updates](docs/tutorial.en.md) · [LICENSE](LICENSE)

AGPL-3.0-only. The original license terms govern use and redistribution; retain the included legal files. [KarmenLoop](https://karmenloop.com).
