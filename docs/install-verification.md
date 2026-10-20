# Installation command verification

This page records the macOS run. The later [Windows verification](windows-install-verification.md) covers PowerShell 5.1 and 7 installation, shared-file recovery, and removal.

Observed October 21, 2026, Asia/Shanghai time (2026-10-20 19:29:50 UTC).

The macOS installation block in the [English guide](install.md) was executed on macOS 27.0 ARM64 with zsh. Only `GrowthRoot` and `GrowthSkillsRoot` were redirected into an isolated directory; both paths included spaces, and the knowledge path included Chinese characters. The release was downloaded from GitHub during the run. No user-level skill installation was changed.

The English and [Chinese guide](install.zh-CN.md) contain identical macOS and Windows installation command blocks.

| Action | Actual result |
|---|---|
| Execute the macOS installation block | Exit 0; ZIP and manifest SHA-256 checks passed. |
| Inspect the installed folder | Exactly eight files; every hash matched the release manifest. |
| Resolve the discovery entry | The symbolic link resolved to the intended canonical skill folder. |
| Run the installed verifier with Python 3.12.14 | Exit 0, PASS, 21 checks. |
| Run the installation block again | Exit 1 with the existing-installation message; skill files and a task-memory record were preserved. |
| Execute the guide's symbolic-link removal block | Exit 0; only the entry was removed; all canonical files and the task-memory record remained. |
| Check repository Markdown references | Exit 0 with strict relocation checking. |

## Inputs

- ZIP SHA-256: `b2e58a97357cee25cac9c890e053d381cb4240b4d63ff1815886c0dfcd9a61b0`.
- Manifest SHA-256: `38c173aded1b11f91814684a52e82d3f71275c44cf86da420a7e28d2b07ebc9a`.
- English guide at execution: `6fb0cec195d6b5c48296904d72f475474317f3837b18b07c94b95f64071f9d32`.
- Chinese guide at execution: `5279384ea3f827d39612b9a02b0473654a64ed83c7cf51c5a449b7f27646c5c1`.

## Scope

This is a maintainer-run shell installation and removal check. The private receipt retains the exact commands, paths, stdout, stderr, exit codes, and file identities.

Windows installation commands were not executed in this macOS run. They were subsequently executed in the separate Windows verification linked above. The original three-platform utility CI remains a different check.

This run did not test fresh-chat skill selection, a new Codex-to-Cursor behavior sequence, scheduling, or cross-device memory. Earlier behavior trials and their limits are recorded in [validation](validation.md). Local ARM64 command execution is separate from the Intel macOS CI result in the [release acceptance report](release-0.3.2-acceptance.md).
