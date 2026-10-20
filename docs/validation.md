# Validation and limitations

This page separates prior maintainer-run local trials from checks anyone can run from this repository. It is an account of observed results, not a claim that every host or task behaves the same way.

## Native Codex continuation

On October 21, 2026, Asia/Shanghai time, a local task received two actual Codex scheduler wakeups without a new human task message between them.

The first turn recorded a prediction, reviewed a verification method, created the offline ZIP checker, and ran seven controlled cases. It then changed the registered interval from one minute to three minutes and read the configuration back.

The second turn restored the saved task state, checked the earlier artifacts, reused the checker on the original package, and obtained exit 0 with 11 consistency checks. The task then paused its automation through the host interface and confirmed the paused state.

The recorded times of the host events were 00:25:18.696 and 00:36:50.763. The interval setting was not a promise of exact trigger latency.

This establishes a bounded native-scheduler trial. It does not establish operation after shutdown, with the application closed, or without the required host capabilities.

## Codex-to-Cursor recovery

A separate same-Mac task used one Cursor desktop chat and shared files. Cursor read task revisions 1, 3, and 5 and wrote back revisions 2, 4, and 6.

The task built and reviewed a Markdown resource checker. It used preparation experiments, real package checks, controlled failures, and subsequent reviews. An independent check found that an absolute symbolic link could work before relocation and fail afterward. A later check found an indirect form of the same problem through a directory link. Both findings changed the next action and led to another repair.

The final independent run covered 17 cases: ten checks before and after actual relocation, five Markdown-reference variations, and two checks of the sample and skill. Each result matched its expectation, including cases that were supposed to be rejected.

A duplicate lesson identifier was corrected while preserving both facts. A late Cursor message was also observed rereading the newer revision and skipping a duplicate write.

This cross-tool trial did not observe a new scheduler trigger. It demonstrates shared-memory recovery and execution; native scheduling is evidenced by the separate Codex trial above.

## What version 0.3.2 contains

Cursor actually used the 0.3.0 and 0.3.1 method texts. Version 0.3.2 adds the resulting rules for unique lesson identifiers and late messages. Its structure, archive, extracted references, and relocated references were checked. A new complete Cursor behavior trial of 0.3.2 has not been claimed.

The public edition adds licensing metadata and notices to those six method and utility files, plus public installation, team, and validation documentation. The decision rules and checker behavior are preserved. The public archive has a different hash from the earlier private handoff archive because it includes the license and notices.

The Markdown checker used in the cross-tool trial is not bundled here. The included utility is `scripts/verify_handoff.py`, which checks ZIP/manifest consistency.

## Reproducible repository checks

Run:

```sh
python3 -m unittest discover -s tests -v
python3 tools/build_release.py --output dist
python3 scripts/verify_handoff.py \
  --archive dist/personal-agent-growth-0.3.2.zip \
  --manifest dist/manifest.json
```

The tests exercise the real command-line checker with controlled inputs, including a valid package, altered bytes with a refreshed archive hash, missing and extra members, duplicate and unsafe members, malformed or inconsistent manifests, missing inputs, and invalid ZIP data. The release check builds the installable archive from an explicit file list and checks it with the same verifier.

The GitHub workflow runs these utility and packaging checks on Linux, macOS, and Windows. Its actual run results are the evidence for each platform; they are not host-agent behavior tests.

## Evidence boundaries

The local trial's raw task memory, chats, screenshots, and host configuration remain private. This public summary is therefore a maintainer report of those trials, not a publicly reproducible host transcript. The repository's tests can be rerun independently.

One early trial error stream was overwritten during a retry. That missing original record remains a known evidence gap; a later summary was not treated as its replacement.

Not established: fresh-chat automatic skill selection, cross-device synchronization, Windows agent execution, a Cursor-native scheduler, publisher authenticity from the ZIP checker, or a general improvement in intelligence.
