# Personal Agent Growth v0.4.0 tutorial

[English](tutorial.en.md) · [中文](tutorial.zh-CN.md)

Download and extract the versioned release. Use Python 3.11+. Keep task data outside the skill and repository. Both tools must use the same private data root and the same workspace files on this computer.

```sh
python /path/to/scripts/host.py --root /private/task-state --workspace /path/to/project --install-host codex install
python /path/to/scripts/host.py --root /private/task-state --workspace /path/to/project --install-host cursor install
```

Reload each host, approve the specific server, and verify its five `growth_*` tools. A configured entry alone is not acceptance.

In Codex, call `growth_start` with `task_id`, `goal`, and `acceptance`. Complete a real step in the project. Then call `growth_checkpoint` with the current `expected_revision`, phase, observation, next action, and workspace-relative artifact paths. The adapter hashes existing files; it does not create evidence for you.

Call `growth_handoff` with the current revision and `target_host: cursor`. In Cursor, call `growth_read` with the same task ID. Verify the writer, next action, and `evidence_current`. The old writer can still read but cannot update. Continue the work, then commit a new checkpoint with the receiving host's current revision. `growth_export` writes a private handoff JSON.

For direct inspection without a model:

```sh
python /path/to/scripts/host.py --root /private/task-state --workspace /path/to/project --host-id cursor call growth_read --input request.json
```

`request.json` contains `{"task_id":"your-task-id"}`. Restarting the process preserves its checkpoint. A stale revision requires a fresh read; missing or changed artifacts must be rechecked before handoff. Do not overwrite the database to clear a conflict. To back up the store, stop writers and copy its private directory.

The scheduler field deliberately remains `not_registered`: no wake-up was created. Cross-host state on one computer does not imply cross-device synchronization. A live Codex read and separate MCP-client handoff passed on macOS; Cursor discovered the tools, while an authenticated model turn and native Windows/Linux operation remain unverified.
