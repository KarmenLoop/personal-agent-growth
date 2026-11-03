# Measured-learning feedback library

[简体中文](README.zh-CN.md) · [Study acceptance](../../release-0.7.0-acceptance.en.md)

This is a portable Markdown library derived from the actual 0.7.0 study. It contains both frozen proposals and their four task-specific feedback records. Neither proposal became a global default. `harmful` describes the observed whole-package resource regression in the named task, not a conclusion that the source lesson itself is false.

`evidence/analysis.json` is a published path-redacted derivative; each Markdown record binds the actual bytes of that derivative. The original/public identities are retained in the study export. It is not an unredacted execution log or another blind trial.

Copy this entire directory to a task-local memory root and inspect it with:

```sh
python3 -B /path/to/personal-agent-growth/scripts/experience_transfer.py retrieve --root /path/to/copied-library --query /path/to/copied-library/requests/query.md
```

The actual CLI operations that created and retrieved these records are in `operations.json`. Tool persistence and retrieval do not establish that a future Agent has used them. Existing source lessons and failures remain unchanged.
