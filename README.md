# Personal Agent Growth

[English](README.md) · [中文](README.zh-CN.md) · **v0.4.0**

Keep the next useful step when a task moves between tools. The bundled Python adapter saves checkpoints in a private SQLite store, verifies referenced files, and transfers write responsibility between configured hosts.

![Checkpoint and handoff workflow](docs/images/workflow-v0.4.0.svg)

A handoff carries the goal, current revision, observation, artifact hashes, and next action. The receiving host reads the same record. A stale writer or changed artifact is rejected instead of silently overwriting the handoff.

Get the [v0.4.0 package](https://github.com/KarmenLoop/personal-agent-growth/releases/tag/v0.4.0), install Python 3.11+, and follow the [tutorial](docs/tutorial.en.md). The package also retains its offline archive verifier.

This is durable local task state, not an autonomous agent runtime. It does not register timers, contact people, execute the next action, or synchronize databases across devices. Those operations require a separately authorized host. A real Codex turn read the saved handoff; Cursor discovered the tools, but its model turn remains unverified due to local sign-in and usage limits.

[AGPL-3.0](LICENSE). [KarmenLoop](https://karmenloop.com).
