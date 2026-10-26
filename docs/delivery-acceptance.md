# Offline delivery acceptance

Publication note, October 27, 2026: the report below records the earlier local trial and its original artifacts. Version 0.4.1 now includes the retained work with expanded bilingual documentation and Markdown learning contracts. Historical counts, hashes, and “unpublished” statements describe that earlier run, not the current release. See [current acceptance](release-0.4.1-acceptance.en.md).

The **0.4.1-bundle.1** delivery passed actual local extraction, installation, relocation, experience loading, tool reuse, and removal checks on **macOS 27.0 ARM64 with Python 3.12.14** on October 23, 2026. This is filesystem and utility acceptance. It adds no Windows desktop, Cursor, scheduler, new Agent run or performance result.

The [machine-readable report](evidence/delivery-0.4.1-results.json) contains 16 actual commands, their exits, timings, output hashes and program identities, with private paths replaced by placeholders. Original command receipts and output remain in the local acceptance directory. Expected rejection cases exit 1 and are recorded as such. The rehearsal archive is identified in that report; adding this report changes the outer archive. Final archive identity and final readback are delivered alongside the final ZIP, avoiding a self-referential archive hash.

## Observed results

| Check | Actual result |
|---|---|
| Utilities and packaging protections | 44 tests passed, including existing-root refusal, tamper refusal, deterministic ZIP generation, moved-library loading, modified-skill removal refusal and memory retention |
| Coordinator archive | Original 0.4.1 ZIP unchanged; 25 checks passed |
| Extract and move distribution | Content inventory passed before and after a directory move; old extraction path no longer existed |
| Install and move knowledge root | Installed into a new directory, then moved it; old install path no longer existed |
| Discovery entry | Created and read an isolated macOS symbolic link, then removed and recreated it for the new location; no global entry was changed |
| Experience | Both indexed profiles loaded from the moved root; the context loader read two cards and two observations at seed revision 1 from an unrelated working directory |
| Tool identity | The selected profile's batch checker and verifier matched the retained archive profile |
| Archive reuse | Real package plus an explicitly controlled missing-file case returned per-item exits 0, 2, 0; the final valid item still completed |
| Scientific adapter reuse | The retained NASA CSV produced 37 annual rows, kept the missing annual value blank, and matched independent Decimal means and OLS within 1e-12 |
| Uninstall | Refused added user content; after removing that controlled file and the isolated discovery link, removed only the canonical skill and preserved the experience and task trees byte for byte |
| Original private experience library | Every file remained unchanged |
| Documentation | Eight Mermaid diagrams parsed; 114 local Markdown links resolved in the rehearsal bundle |
| Distribution review | No matches for the source user's home or private runtime paths in the reviewed text files; private raw traces, account files and task records were not included |

The frozen NASA input SHA-256 was `4c64eda288bce32b8d76926278f346ecea1e53506df8ee72a3d5accb0657c416`. This utility reuse did not retrieve new data or measure model cost. The controlled missing archive was a package-check variation, not an Agent failure or a Windows test.

## Repairs included

The original ten-file ZIP omitted the separately stored learned execution profile and experience library. The full delivery now carries a reviewed seed, complete source, bilingual instructions, plots, team details and license files around that unchanged ZIP. The installer keeps task memory separate and refuses to overwrite an existing installation root.

The cross-domain profile had an absolute local library path and locale-dependent text reads. The export changes only `memory-location.json` and `scripts/context_loader.py`, resolving the library relative to the profile and reading UTF-8 explicitly. The source snapshot remains untouched. The derived snapshot has a new hash, and its imported cards do not pretend that a new Agent trial adopted it. Its source performance results remain in the separate [cross-domain report](cross-domain-trial.md).

An ownership-check edge case was corrected before the acceptance run: a file named `DELIVERY-MANIFEST.json` added inside the installed skill must count as unexpected user content, even though the outer delivery verifier excludes its own manifest from the file inventory. The regression test confirms that removal stops and preserves the file.

## Scope and next use

The [English](../START-HERE.md) and [Chinese](../开始使用.md) instructions are ready for the local candidate. The old published guide remains pinned to 0.3.2. The complete bundle is reproducible from its included source and seed; it does not depend on the original private library.

The source archive profile remains `55ce7da5eab6024369167edaacecc7a5af41418c205443c495ce0475a2085e78`. The original cross-domain profile is `af3c2b187b4c749b1c42bab15a5d938a7324f39ae5e0bd1b6c3ce9f875f40a4a`; its portable derivative is `a288e4ce31afbb290ade7c2425f645d2b3ad7dbd1e883576fa7817050afe15e9`. See [export provenance](../examples/experience-seed/export-provenance.json).

Imported lessons can inform the next authorized task. They do not justify a claim that the derived profile has repeated the original 24-session Agent trial, generalized to a third domain, resumed private work automatically, or passed on the unavailable Windows device. A new host must actually read the selected profile and produce task evidence before such claims are made. No new GitHub release was published in this packaging pass.
