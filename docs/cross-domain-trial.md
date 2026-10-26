# Cross-domain complete-task trial

Publication note, October 27, 2026: the report below records the earlier local trial and its original artifacts. Version 0.4.1 now includes the retained work with expanded bilingual documentation and Markdown learning contracts. Historical counts, hashes, and “unpublished” statements describe that earlier run, not the current release. See [current acceptance](release-0.4.1-acceptance.en.md).

The composed strategy retained the required output quality in all six runs and reduced the sum of per-task median total tokens by **15.8%** against the existing baseline. It passed each task's resource limits and was activated for this tested portfolio. This is an exploratory result on one Mac and two tasks, not a universal efficiency or intelligence claim. The candidate remains local and unpublished.

## Actual tasks and quality

**Software delivery:** every execution produced a usable acceptance report for four actual archive/manifest pairs, full raw results, exact commands and exits, predictions, and a review. Two pairs passed consistency checks; one completed inspection and exposed three archive/NOTICE mismatches; one stopped at manifest validation before reading its archive. Preserving the incomplete result and its current cause was necessary for a correct report. This regresses the previously adopted package-verification capability rather than comparing against a weakened baseline.

**Scientific data analysis:** every execution exported all 37 annual rows from 1990 through 2026, retained the missing 2026 annual value as blank, calculated complete-decade means and an OLS trend, and wrote a sourced interpretation. The actual means were 0.588°C and 0.804°C anomalies, their difference was 0.216°C, and the descriptive 1990–2025 trend was approximately 0.234929215°C per decade. A fixed evaluator independently recomputed these from the frozen raw CSV using Decimal arithmetic. These calculations do not estimate uncertainty, establish causality, or forecast future temperature.

The coordinator inspected all 24 reports and reviews in addition to the frozen checks. Every complete primary-round session passed its required quality constraints. Quality was maintained, not scored as improved. Each actual Agent read shared experience, saved predictions, executed the appropriate tool or calculation, checked artifacts, and reviewed what transferred and what did not. Native session identities, usage, UTC times, hashes and per-task measurements are in the [sanitized evidence](evidence/cross-domain-0.4.1-results.json). Full native events remain in the local experiment; this summary does not pretend to contain them.

## Full-task measurements

Values below are medians of three fresh-context executions of each task. Tokens cover native input plus output; seconds cover CLI launch through exit, including model work, tools, reporting and verification.

| Strategy | Release tokens | Science tokens | Sum of task medians | Release seconds | Science seconds | Decision |
|---|---:|---:|---:|---:|---:|---|
| Baseline | 390,588 | 325,435 | 716,023 | 214 | 234 | Reference |
| General | 312,858 | 328,798 | 641,656 | Unknown | 289 | Not adopted |
| Domain | 330,710 | 406,945 | 737,655 | 218 | 259 | Not adopted |
| Composed | 305,075 | 297,483 | 602,558 | 195 | 238 | Adopted for this portfolio |

Across all six observed tasks, composed used 2,031,758 tokens versus baseline 2,158,546: **5.9% fewer**. Its cumulative elapsed time was 1452.8 seconds versus 1352.9: **7.4% longer**. The costly repair remains included. Passing the predeclared median gates does not establish an overall speedup.

![Each strategy has three observed token and elapsed-time samples for both tasks. The general release arm includes conflicting UTC and monotonic times and has no accepted timing median.](images/cross-domain-0.4.1.png)

Points show actual repetitions; black lines show medians only when all three measurements are usable. The anomalous sample shows both raw clocks. No confidence interval, significance test or stable universal speedup is claimed. The [SVG](images/cross-domain-0.4.1.svg), [figure provenance](images/cross-domain-0.4.1.provenance.json), and [underlying measurements](evidence/cross-domain-0.4.1-results.json) are available.

The frozen task-level selection statistic is the sum of task medians. The utility also calculates a median of paired portfolio totals: Baseline 724,503, General 641,656, Domain 726,932, Composed 650,656. They are different statistics; activation requires the predeclared 10% gain under both interpretations, in addition to all quality and per-task resource gates.

## What changed after observation

The general proposal reduced the sum of task token medians by 10.4%, but its scientific task took 23.6% longer than baseline, exceeding the frozen 20% limit. Its release timing also included an unresolved clock discrepancy. The domain proposal's scientific token median increased by about 25%, above the 15% limit. Neither full proposal was adopted merely because its checker or arithmetic worked.

The trajectories exposed a shared retrieval mistake: Agents sometimes looked for SKILL.md at the experience-library root, or tools in the workspace root. They recovered, but the extra reads and repeated context were part of full-task cost. Compose retained the successful archive verifier, retained the correct annual-data adapter as a component, and rewrote retrieval around an indexed context loader with actual record hashes, the assigned entry skill, relevant observations, adopted-tool binding and explicit tool interfaces. Reports still required independent checks. The new component was frozen and then used by six real Agent sessions; a coordinator-only helper check was not counted as Agent acceptance.

One composed scientific run exposed two new mistakes: an overly strict numeric guard rejected NASA's valid `-.17` notation, and a later exact-equality assertion rejected a normal floating-point representation. The Agent repaired its local checks, retained the failed attempts, and passed the unchanged independent evaluator. That run cost 479,041 tokens and 408 seconds; it remains in all sample summaries and the figure. The fixed candidate snapshots and evaluator were not rewritten to hide it.

The trials support this combination on these two tasks. They do not isolate the causal contribution of each clause or prove that every retained recovery rule was exercised. In particular, the composed runs did not induce a report-writing failure to test that recovery branch.

## Experience, skill and measured cost

The shared library remained at revision 2 during every trial. Recording the experiment advanced it to revision 3; a separate, explicitly retrospective cost review advanced it to revision 4. Successful, failed and unresolved lessons, both proposals, actual comparisons, component decisions and the old domain profile remain preserved. The new profile's immutable snapshot is `af3c2b187b4c749b1c42bab15a5d938a7324f39ae5e0bd1b6c3ce9f875f40a4a`. A fresh selection and tool readback verified two experience records and two review observations. The cost review and tool readback are not an additional post-adoption Agent task or an automatic-discovery test.

The 0.4.1 coordinator skill adds per-task resource gates, explicit handling of unknown timing evidence, full-turn accounting, and timeout recovery in a separately frozen round. The comparison utility checks these gates for Probe and Compose. The selected execution profile is stored separately from the portable coordinator package; the host must actually load the returned profile for reuse.

The 24 primary-round tasks consumed **8,255,689 measured native tokens**. Adding the earlier completed release task and readiness check gives a measured lower bound of **8,855,994 tokens**. The timed-out and cancelled sessions and coordinator/proposal work are not fully measured. Actual charges are unknown; cached input is already part of input and is not counted twice. Cumulative net savings or payback has not been established.

## Design, repairs and limits

Three Probe arms each completed both tasks three times, with counterbalanced strategy order and serial execution. Compose ran afterward in six fresh sessions. Every arm received the same frozen inputs, task contract and 600-second limit. The solver and improver received no prewritten answer key or sibling results. An independent fixed evaluator and coordinator checked observable constraints. Shared cache stayed enabled; later cache warmth and host variability limit timing interpretation.

The initial 300-second experiment timed out before one climate session returned native completion and usage. The next session was cancelled, the failed round was preserved, and one repaired round was separately frozen for all strategies. Earlier successes were not mixed into the final comparison. One general release session measured about 787 seconds in UTC and 284 seconds monotonically. Its cause remains unknown; no pause was subtracted and no sample was discarded. Its timing guard is unknown, while independent candidates can still be assessed.

Visible settings were gpt-6.1-sol, xhigh, through Codex CLI 0.163.0-alpha.10.2. No training, fine-tuning, reinforcement learning or parameter-update operation ran. A provider weight digest is unavailable. Frozen Probe SHA-256: `12cf2bfc7cfa55ae221fffed186e15e8dedd12ec8587be825671b197bbd6616c`. Compose SHA-256: `9618bee9e2e36de1fe45cdd7e3c7aa03643a08114e6679f29abe1ded2297f592`.

The scientific input came from the official [NASA GISTEMP CSV](https://data.giss.nasa.gov/gistemp/tabledata_v4/GLB.Ts+dSST.csv), retrieved October 23, 2026, with [v4 source documentation](https://data.giss.nasa.gov/gistemp/data_v4.html). Its frozen SHA-256 is `4c64eda288bce32b8d76926278f346ecea1e53506df8ee72a3d5accb0657c416`. Execution sessions used the supplied snapshot offline.

This trial adds no Windows, Cursor desktop, scheduler-wakeup, multi-device or unseen third-domain acceptance. The Windows Agent continuation remains blocked by device availability. A later task must actually load the selected snapshot before claiming post-adoption reuse.

## Local checks and reproduction

The coordinator utilities passed 38 tests; skill structure validation passed; the actual 0.4.1 ZIP passed 25 content and identity checks. Seven Mermaid diagrams parsed. These checks are separate from the 24 real Agent task executions. Candidate ZIP SHA-256: `bc7945fd3d1da9d874b5a59d9a57646391ed381083a742632aea7ba2d9406862`. The published installation guide still pins release 0.3.2; it does not install this unpublished candidate.

To reproduce the figure from the retained public measurements:

```sh
python3 -m pip install 'matplotlib==3.10.8' 'Pillow==12.3.0'
python3 tools/plot_cross_domain.py docs/evidence/cross-domain-0.4.1-results.json docs/images/cross-domain-0.4.1
```

<!-- Copyright (C) 2026 KARMENLOOP Official Team
SPDX-License-Identifier: AGPL-3.0-only -->
