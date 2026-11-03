# Release 0.6.0 acceptance — 2026-11-03

[中文](release-0.6.0-acceptance.zh-CN.md) · [Tutorial](adaptive-learning.en.md) · [Runnable examples](examples/adaptive-learning/README.md)

0.6.0 adds task-derived questions, mechanism-based experience retrieval, feedback-driven replanning, and recoverable Markdown decisions. The original capability ledger, host permissions, model configuration and historical evidence remain. This release adds working infrastructure and bounded Agent demonstrations; it does not certify general intelligence or mastery.

## What actually ran

Four fresh host Agents produced usable artifacts across two task types: an instructional-design workshop, then three independently dispatched operations runbooks. These are actual model turns with tools and parent review. The drills they authored use clearly labeled controlled local file effects; those subprocesses are not counted as Agents, production incidents or new scheduler wakeups.

The workshop Agent first retrieved no experience, aligned explicit structural vocabulary, then found a candidate. It built and executed a contributor workshop. Independent review found that its first handout incorrectly suggested replanning after any observation; a new immutable revision correctly distinguishes unknown-effect reconciliation. Its derived lesson remains a hypothesis.

The general operations Agent actually read that task's context, latest node and current run state from the **same physical Markdown root**, retrieved the new instructional-design experience, explained the mapping, and adapted it to operational recovery. Its cold plan already contained core nonrepetition ideas, so retrieval is not credited with inventing them. Review found a negative probe hitting the stale-plan gate before the claimed pending-state gate. The revised script uses a valid current-revision plan and checks exact diagnostics. Original artifacts and the mistaken attribution remain. A new derived experience records rejection-cause isolation; use feedback records inconclusive causal benefit.

All four real runs were subsequently replayed from Markdown with the final helper: instruction revision 15/5 actions, baseline revision 6/2 actions, general revision 12/4 actions, domain revision 6/2 actions; each returned `delivered` with no pending action. The parent independently read the complete artifacts and reproduced each operations drill. [Agent replay receipts](evidence/adaptive-learning-20261103/agents.json).

## Predeclared exploratory comparison

The same operations task and fixed artifact criteria were used for baseline, general-experience and domain-specific planning candidates. Proposals were saved before dispatch. Each arm executed a complete task, not just a checker-count exercise.

| Arm | First reviewable draft | Recorded intake through completion | Artifact quality |
|---|---:|---:|---|
| Baseline | 203.78 s | 418.05 s | Passed first review |
| General experience | 242.64 s | 608.24 s | Attribution defect repaired; corrected usable artifact at 371.67 s |
| Domain planning | 251.70 s | 512.44 s | Passed first review |

These are real wall-clock windows including preparation, authoring, repair, review coordination and finalization. Concurrent execution and parent review waiting are confounders. Pure reviewer reading time, native tokens, charges and backend weight identity are unavailable. The workshop's 359.09 seconds is only its initialized-run interval; preparation before recorded intake is unknown. Do not compare it as a complete-task efficiency result.

**No new global strategy was promoted.** One sample per arm and unavailable costs do not qualify a speed or superiority claim. The existing PPC comparison gates remain unchanged. Baseline and both candidates are retained; no changed composition was activated, and no composition run is fabricated. [Comparison and limitations](evidence/adaptive-learning-20261103/comparison.json).

## Repairs and regression

Seven implementation defects were reproduced and repaired: stored envelopes exceeding the readable size limit; stopped-run time continuing to grow; plan-limit dead ends; nonfinite action rankings from tiny durations; full journals blocking pending-result reconciliation; cross-domain harmful feedback silently disappearing; and abandoned publication files consuming the final reconciliation capacity. The later review's suspected additional soft-stop timing bug was retracted after checking the actual source; it is not counted as another defect.

Final local public regression: **133 passed, zero failed, zero skipped**, Python 3.12.14 on macOS arm64, 19.473 seconds. Product scripts/tests/tools retained the same hashes before and after the run. [Full output](evidence/adaptive-learning-20261103/regression.stderr) · [commands and source identities](evidence/adaptive-learning-20261103/regression.json).

The first complete regression retained one failure and one setup error because the new acceptance document was not yet present. A later package probe encountered the not-yet-rendered SVG. Its tool response is retained as a summarized observation, with no separate raw output claimed. Focused RED/GREEN logs remain in the trace archive. No failed run was relabeled as success.

## Package and documentation

The core contains **74 files** and passed **153 ZIP/manifest checks**. The full distribution was actually installed into a path with spaces and Chinese characters, relocated, used to run both new helpers and recover a run in another process, then removed while the Markdown memory hash stayed identical. Eight recorded commands cover this local package smoke. [Package receipt](evidence/adaptive-learning-20261103/package.json).

English and Chinese protocols, tutorials, architecture links and examples accompany the release. Both new diagrams were actually rendered with Mermaid 11.4.1 and Chromium and visually inspected: **56 nodes and 77 connections each**. An English group-heading overlap was repaired. The previous 22 diagrams and their 44 source/image files remain byte-identical; the library now has 24 diagrams. [Render/layout receipt](evidence/adaptive-learning-20261103/diagrams.json).

The release's GitHub Actions runs and downloadable `RELEASE-VERIFICATION.md` identify remote platform checks, exact release assets, public readback and final source revision. These are separate from the local checks above. Earlier Windows Koder, Windows Cursor, native wakeup and delayed-review boundaries remain at their original evidence level; this release does not replace them with local subprocess results.

## Evidence and limits

[Trace export](evidence/adaptive-learning-20261103/trace-export.zip) contains sanitized derivatives of actual local commands, outputs, immutable events, reviews, predictions, corrections and timings. [Export manifest](evidence/adaptive-learning-20261103/export-manifest.json) records original and exported SHA-256 values. Home and root paths are replaced. The ZIP is a readable audit export, **not a canonical memory root to replay directly**. Runnable examples are separate, with their controlled scope stated.

The host still forms questions, aligns semantic vocabulary, selects and executes tools, and judges meaning. Label matching and declared rankings are transparent aids. A fresh task may reject a prior analogy. Feedback never grants new permissions. This release makes those decisions and their consequences inspectable; general learning speed and broad mastery remain unproven.
