# Release acceptance · 0.4.1

[中文](release-0.4.1-acceptance.zh-CN.md) · [Compatibility](compatibility.en.md) · [Machine-readable local receipts](evidence/release-0.4.1-local.json)

## Scope and result

On October 27, 2026, local publication and distribution checks passed after correcting two rehearsal inputs. This report covers the public Skill, its documentation, diagrams, and real filesystem operations. The corrected implementation commit `52caa11` passed all three hosted operating systems. The following documentation commit adds these receipts; its checks are linked from the pull request.

| Check | Observed result |
|---|---|
| Python regression suite | 48 tests passed on macOS arm64 / Python 3.12.14 |
| Installable core | 59 files; all 123 ZIP/manifest checks passed |
| Skill format | `quick_validate.py`: Skill is valid; PyYAML used only by this development validator |
| Documentation | 21 English/Chinese document pairs; local paths and section anchors checked |
| Learning templates | 16 types per language, 32 Markdown templates with required metadata |
| New diagrams | 16 SVGs rendered with Mermaid 11.4.1 and real Chromium; source/output hashes retained |
| Embedded diagrams | All 7 existing Mermaid blocks parsed successfully |
| Visual inspection | Chinese capability map and architecture, English recursive-improvement map inspected |
| Full bundle | Installed into a Unicode/space-containing root, moved, read both actual indexed experience profiles from another working directory |
| Refusal cases | Existing root, changed skill, unknown experience domain, and repeated guide installation refused |
| Removal | Experience, task fixtures, and Markdown learning fixtures retained; only unchanged skill/discovery entries removed |
| macOS guide | Actual Bash commands executed using isolated paths and local `file://` release transport |

The 137-node system map and three 92-node topic maps in each language are architecture documentation, not proof of Agent intelligence. The local receipt has 21 entries: 20 launched commands and one launch-path error. Expected refusal exits are distinguished from failures; the two corrected inputs remain visible.

## Corrections retained

- The first relocation check requested `scientific-data-analysis`, which is not a profile in the supplied seed. The tool refused. The next call read the actual `offline-package-check` profile. No invented fallback or product patch was used.
- The rehearsal attempted `/usr/bin/unlink`; this Mac resolves `unlink` to `/bin/unlink`. The corrected executable completed removal. The installation guide already uses the PATH-resolved command.
- The Windows checker had stale 0.3.3 filenames and fixed file/check counts. It now uses the current manifest and matches the 0.4.1 guide. PowerShell 5.1 and 7 subsequently passed both tested roots; see the jobs below.
- Diagram rendering exposed literal quote entities, a sequence-parser delimiter, and two clipped headings. Sources were corrected, all 16 SVGs regenerated, hashes refreshed, and selected outputs visually inspected.
- The published 0.4.0 host adapter was retained while integrating the previously unpublished 0.4.1 experiment and delivery work.

## Hosted cross-platform results

| Runner or shell | Result | Actual run |
|---|---|---|
| Ubuntu 24.04, macOS 26 Intel, Windows Server 2025 | Each passed 48 tests, core build/123 checks, and publication checks | [Corrected implementation run](https://github.com/KarmenLoop/personal-agent-growth/actions/runs/40387260224) |
| Windows PowerShell 5.1.26100.33648 and PowerShell 7.6.7 | Both passed default D: and custom C: Unicode/space paths | [Guide and shared-file run](https://github.com/KarmenLoop/personal-agent-growth/actions/runs/40387005475) |

Windows receipts show three distinct worker processes advancing revision 1→2→3, actual shared file identities, stale-write refusal, repeated-install refusal, and removal preserving memory. They are **test processes, not Agents**. The guide downloaded no release URL in CI: transport was replaced with the current local build. See [CI summary](evidence/release-0.4.1-ci.json) and [Windows summary with raw-artifact hashes](evidence/release-0.4.1-windows.json).

The [first CI run](https://github.com/KarmenLoop/personal-agent-growth/actions/runs/40387006023) had one Windows failure: a test compared a short `RUNNER~1` path with its resolved long spelling. It now verifies the actual indexed directory with `samefile`. Snapshot/tamper checks remain intact. The failed run is retained. This is a test portability repair, not evidence that the experience loader was returning the wrong directory.

Final public assets and post-upload download receipts are available on [v0.4.1](https://github.com/KarmenLoop/personal-agent-growth/releases/tag/v0.4.1). `RELEASE-VERIFICATION.json` records the published commit, downloaded hashes, package checks, and the actual network-install result; its absence means those post-upload checks are not yet recorded. It is kept outside the ZIP to avoid a self-referential archive hash.

## What these runs do not establish

No new native Codex, Cursor, or Koder model turn was performed for this publication. No native Windows desktop Agent acceptance, cross-device synchronization, app-closed OS wakeup, universal efficiency improvement, or release of the private Koder learning implementation is implied. The separate Koder candidate still has 31 full-suite failures. Prior actual Agent experiments remain explicitly dated in [compatibility](compatibility.en.md) and [cross-domain results](cross-domain-trial.md).

The local install used locally built assets; it is not evidence of GitHub network download success. The release verification receipt identifies the separately checked final assets. Archive/manifest agreement verifies consistency, not an independent publisher signature. Public receipts replace private path prefixes with placeholders and preserve both original-output and published-output hashes.
