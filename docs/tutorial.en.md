# Personal Agent Growth: user guide

English | [简体中文](tutorial.zh-CN.md) · [Project](../README.md)

This guide matches **v0.3.3**.

## 1. Download and verify

From the release, download [`personal-agent-growth-0.3.3.zip`](https://github.com/KarmenLoop/personal-agent-growth/releases/tag/v0.3.3) and its checksum file or manifest. Compare the complete SHA-256 before extracting: use shasum -a 256 on macOS, sha256sum on Linux, or Get-FileHash -Algorithm SHA256 in PowerShell. Byte consistency relies on obtaining the expected hash from a trusted source.

## 2. Install and load

Download the skill ZIP and manifest.json. Extract into a fresh canonical folder, then add that folder once through your host’s supported skill discovery path. Keep the skill folder separate from private task records.

Refresh host discovery or open a new session, explicitly read the installed SKILL.md, and check the version above. The skill needs no separate model account; the host supplies its own model, tools, and permissions.

## 3. Configure and try one task

Choose one private task directory that both hosts resolve to the same physical location. Record the active writer and state_revision before a handoff. Python 3.11+ is needed only for the optional offline checker, not for reading Markdown.

Explicitly load SKILL.md, review a synthetic task artifact, save the actual check result, correct one mistaken assumption, and leave a concrete next review action. Confirm those files exist before changing hosts.

## 4. Develop a repeatable workflow

Have the receiving host read the current revision and use the earlier artifact in a new check. Scheduling needs an actual supported backend and separate task authorization; installation creates no timer or cross-device sync.

Keep the version, actual command, exit code, resulting files, and unverified limits together. Use synthetic data for the first check.

## 5. Troubleshoot, update, and remove

If the host cannot find the skill, check its configured discovery root and SKILL.md readability. A checksum mismatch needs a fresh verified download; do not skip it.

Finish active writes and back up the skill and private task data separately. Extract updates into a new directory and verify before switching. For rollback, restore the older skill while retaining newer user records and evidence. Uninstall only its exact skill directory or discovery entry; separately registered schedules must be cancelled and confirmed in their host.

## 6. License

[AGPL-3.0-only](../LICENSE). This is concise user guidance; consult the original license for use and redistribution terms.
