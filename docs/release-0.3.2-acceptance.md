# Version 0.3.2 acceptance

**PASS for the bundled Python utilities and installable package on Linux, macOS Intel, and Windows.**

Verified on October 21, 2026, at 03:09 Asia/Shanghai. The [completed workflow](https://github.com/KarmenLoop/personal-agent-growth/actions/runs/39480710426) tested commit `43e6f6a8323a1aa8ee99cfcb3c96f7ae271014ca`. The [machine-readable receipt](release-0.3.2-acceptance.json) records job identities, counts, hashes, and the earlier failure.

## Actual results

| Environment | Python | Utility tests | Package checks | Job |
|---|---|---|---|---|
| Ubuntu 24.04, x64 | 3.11.17 | 13 passed | 21 passed | [Linux log](https://github.com/KarmenLoop/personal-agent-growth/actions/runs/39480710426/job/118828210523) |
| macOS 26.6.1, Intel x64 | 3.11.9 | 13 passed | 21 passed | [macOS log](https://github.com/KarmenLoop/personal-agent-growth/actions/runs/39480710426/job/118828210858) |
| Windows Server 2025, x64 | 3.11.9 | 13 passed | 21 passed | [Windows log](https://github.com/KarmenLoop/personal-agent-growth/actions/runs/39480710426/job/118828211169) |

Each job ran the same three commands successfully:

```sh
python -m unittest discover -s tests -v
python tools/build_release.py --output dist
python scripts/verify_handoff.py \
  --archive dist/personal-agent-growth-0.3.2.zip \
  --manifest dist/manifest.json
```

The logs contain the test count, successful completion, 21 passing archive checks, and the same package-content digest on all three platforms. Controlled invalid inputs were rejected as expected; the tests do not weaken the checker to make a failure pass.

## What failed and what changed

The [initial main-branch run](https://github.com/KarmenLoop/personal-agent-growth/actions/runs/39468002952) and [release-tag run](https://github.com/KarmenLoop/personal-agent-growth/actions/runs/39468117247) could not acquire a `macos-latest` ARM64 runner. GitHub reported capacity constraints and cancelled those jobs before any test step ran. Linux and Windows passed in those runs. The original failed runs remain available.

The workflow now names its environments explicitly: `ubuntu-24.04`, `macos-26-intel`, and `windows-2025`. It also uses pinned Node 24 versions of the checkout and Python setup actions, replacing actions that produced deprecated-runtime warnings. The test commands, assertions, checker, and package contents were not changed.

The successful macOS result is for Intel x64. It does not turn the cancelled ARM64 cloud jobs into passes.

## Published package identity

The `v0.3.2` tag remains at its original commit, `bfe713595ee22808d5a9148508369966ca71035e`. The validation commit changes only the workflow. All eight files in the released installable package match the validated source.

The published ZIP and manifest were downloaded again and checked with the actual verifier: exit 0, `PASS`, 21 checks passed.

| Item | SHA-256 |
|---|---|
| `personal-agent-growth-0.3.2.zip` | `b2e58a97357cee25cac9c890e053d381cb4240b4d63ff1815886c0dfcd9a61b0` |
| `manifest.json` | `38c173aded1b11f91814684a52e82d3f71275c44cf86da420a7e28d2b07ebc9a` |
| Package content, using the manifest's declared rule | `3b551b97ecc0551266b54492eb93f0b6f2578c7255faf595ce0aaeeb3d0c3698` |

The [release download](https://github.com/KarmenLoop/personal-agent-growth/releases/tag/v0.3.2) is unchanged. The full AGPL-3.0-only license and copyright notice remain in both the repository and the package.

## Scope

These checks establish utility behavior and package consistency on the listed environments. They do not establish agent behavior on all three operating systems, a native Cursor scheduler, automatic selection in a fresh chat, or a new complete Cursor behavior trial of version 0.3.2.

The earlier Codex wakeups and same-Mac Codex-to-Cursor recovery remain separate evidence, described in [validation and limitations](validation.md).
