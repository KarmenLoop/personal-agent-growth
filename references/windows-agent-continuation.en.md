---
id: exp-windows-agent-continuation-en
type: experience
project: windows-user-continuation
tags: [domain/windows, workflow/recovery, workflow/agent-validation]
status: active
created: 2026-10-27
updated: 2026-10-28
sources: [https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/icacls]
---
# Resume a Windows Agent from shared memory

[中文](windows-agent-continuation.md)

## Scenario

A real Windows CLI Agent resumes a shared Markdown project to verify installation or file operations without elevation. A launcher supplies the task and captures receipts. The model must choose tools, read sources, execute work, and write the result itself.

## Method

Recover context, the latest node, and durable constraints before choosing an action. Use existing verified token, input hashes, and receipts to identify the smallest unresolved question. Do not repeat a complete environment survey on every resume. After reading sources that affect the next action, save the prediction, acceptance conditions, and failure branch before execution. End preparation when additional information would not change that action.

Use commands appropriate to the actual Windows shell. Put complex expressions in a reviewable workspace script; preserve errors and exit codes instead of suppressing them. On `SHELL_RECONCILIATION_REQUIRED`, retain the original call ID, reason, cleanup state, and output. Inspect effects with the permitted read-only tools. Do not replay the blocked command through another tool. Continue remaining work in a later turn only after reconciliation, the current turn has ended, and existing authorization permits it. Respect a host requirement for a human action.

Separate provider output, the visible reply, and reusable memory. Automatic summaries store the visible reply and verifiable facts. Split protocol thinking before clipping; preserve literal markers inside code examples. Keep raw protocol receipts in the controlled evidence directory, outside durable semantic memory and public reports.

Check the actual memory tool contract before writing. In Koder, `learning_read open` takes the document's front-matter ID, not its path. `learning_write experience` takes `evidence` as an array of source objects returned by a read, including `document_id` and `excerpt_sha256`. Copy the complete returned object without adding fields. `anchor` is an exact behavior event ID supplied by the tool, never a Markdown heading; preserve any read-scope fields. Prefer `learning_read open` on a stable node and use its returned `source`. Narrative evidence belongs in `why`, `steps`, or `pitfalls`. Prefer an immutable node as a source. A decision or checkpoint changes memory/context hashes. After that write, read the new node before saving an experience or completion; do not batch these writes with old mutable references. Completion must not cite its own project memory/context, which it changes itself. On `LEARNING_SOURCE_CHANGED`, read again and reconsider the claim; never invent a hash or repeatedly submit the stale reference. A failed write is not an experience entry. Confirm the returned path and read the saved Markdown before handing off. Agent-written experiences remain `untested` candidates until a separate verification promotes them.


Read only the relevant context, latest node, memory, and named receipts. Do not recursively list the learning tree to locate a known file. Check the file tool’s workspace scope first: binding shared memory does not authorize access to another workspace. If direct receipt access is unavailable, a coordinator may hand over specifically authorized original files with their source paths, byte lengths, and hashes. The receiving Agent verifies those copies independently and identifies them as copies. Never duplicate the memory store to simulate a shared-root resume. On an output limit or unknown process state, retain the receipt, reconcile processes and effects, end the turn, and continue only unfinished work. Do not broaden limits or permissions to hide the failure.

If a finishing turn repeatedly drifts into environment scans, narrow its tool surface while keeping the real model and the same step limit. The matching Koder candidate supports explicit `--harness learning-review`: named-file reading/writing, Skill, and memory tools; no shell, directory search, browser, or external actions. This profile is for review, not execution. Choose an appropriate profile separately when an authorized task actually requires a new check. First establish that the prior turn ended and reconcile its effects; never use a profile to replay an unknown operation. Obtain environment settings from named launch receipts rather than scanning an installation tree.

## Why it helps

An explicit project-pack read must observe current disk state. After a checkpoint, check that its revision and latest node changed instead of reusing the startup cache. Page through long files using `read_file` offset/maxBytes and the returned nextOffset, preserving UTF-8 character boundaries. Never use a no-op replacement as a substitute for reading. A manifest source path is a transport claim; it does not independently prove that the original directory exists or a command ran. Execution claims require actual command, output, and completion receipts. Correct a flawed experience with a new entry and `supersedes`, retaining the deprecated predecessor, then complete the bounded project again.

Excessive preflight consumes the task budget and creates unrelated failure paths. Classify a failure from its receipt instead of guessing from words such as permission or safety. A saved prediction can be compared with the actual result; a model conclusion alone cannot demonstrate learning.

## Counterexamples and limits

- SYSTEM success does not establish non-elevated success. Record the effective token, integrity level, and elevation. Distinguish a filtered administrator token from an independently created standard account.
- A new process must use the same physical Markdown root and project ID. Pasting the old chat or copying the knowledge store into its prompt is not a shared-memory resume.
- Exit zero, tool counts, and a generated summary are not task-quality acceptance. Review the artifact, raw output, sources, and remaining gaps.
- Preserve the failed turn. A successful follow-up covers only the conditions actually retested. Usage comes from the provider; unavailable cost remains unknown rather than zero.

## Reusable steps

1. Record session, workspace, project, memory root, Skill hash, model, effective privileges, and input identity.
2. Read the minimum recovery pack and relevant sources. Save a prediction, then execute.
3. Check raw receipts. Repair the identified defect without weakening assertions or changing the required privilege scope.
4. Store facts, a candidate experience, and a paused checkpoint with exact artifact paths. End the first session.
5. Start a fresh conversation in another workspace with the same memory root and project. Prove recovery with read records, revisions, and before/after file hashes. Inspect the first phase's artifacts and apply the lesson to a new deliverable.
6. Update the next action and scope. Complete the task or retain a specific blocker. Do not schedule work without a concrete future purpose.

## Related links

[Markdown learning](markdown-learning.en.md) · [Regression repair](regression-repair.en.md) · [Shared memory](shared-memory.en.md)
