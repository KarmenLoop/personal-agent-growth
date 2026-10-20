# Installation and shared use

## First use

Extract the release ZIP into a location you control. A cloned repository also works. The folder containing `SKILL.md` is the skill root; preserve the reference and script paths beneath it.

In your agent, open that location and ask it to read `SKILL.md` before starting a relevant task. Check its actual response and work instead of assuming that opening the folder enabled automatic selection.

## Host discovery

The maintainer's same-Mac trial used project-local `.agents/skills/personal-agent-growth` and `.cursor/skills/personal-agent-growth` entries that resolved to one canonical skill folder. Cursor was also given an explicit skill attachment. That trial does not establish automatic discovery in every host version.

For a project using these directories, each entry can point at your extracted skill folder. On macOS or Linux, the following example creates two links; replace the source path and run it from the project root. Do not replace an existing installation without checking it.

```sh
mkdir -p .agents/skills .cursor/skills
ln -s /absolute/path/to/personal-agent-growth .agents/skills/personal-agent-growth
ln -s /absolute/path/to/personal-agent-growth .cursor/skills/personal-agent-growth
```

When links are unsuitable, install copies in the host's supported locations and track the version of each copy. Method copies can differ; the task's mutable state must still have one agreed location and writer.

On Windows, extract to a chosen local location and explicitly provide the `SKILL.md` path. A possible location is `D:\AgentKnowledge\skills\personal-agent-growth` when D: exists and is writable, otherwise `C:\Users\<you>\AgentKnowledge\skills\personal-agent-growth`. The skill does not create or scan those locations automatically.

On macOS, a folder you select, including a Desktop folder, is suitable. Task-specific records belong in a separate location, not inside the public source checkout.

## Resume across tools

1. Choose a task-memory folder both tools can access. Give each tool its path.
2. Have the current tool record the goal, current revision, evidence, remaining work, and next writer.
3. Have the receiving tool read the actual files and verify the revision before acting.
4. Check that it used the records to complete useful work and wrote results back to the same location.
5. Before another write, reread the revision and writer so that a late message cannot overwrite newer work.

The minimal state example and conflict rules are in [shared memory](../references/shared-memory.md). A chat message saying that a task was handed off is not evidence that the next tool recovered it.

## Scheduled continuation

Ask the agent to use a scheduler only when there is useful future work and the host exposes an authorized interface. It should save the binding, read back the schedule, verify a real host trigger, perform the work, and stop or revise the schedule based on the result.

Copying the skill cannot add a scheduler to a host. The previous trial established native Codex wakeups; it did not establish a native Cursor scheduler or execution after the host application closes.
