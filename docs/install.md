# Installation guide

[中文安装说明](install.zh-CN.md) · Version **0.3.2** · Host documentation checked October 21, 2026.

This guide installs Personal Agent Growth in Codex and Cursor on the same computer, then checks shared task memory and an optional scheduled review. Start with your operating system's instructions. No Git checkout is required.

## 1. Requirements and locations

You need a local Codex or Cursor installation that supports skills and can read the chosen folders. Use the host's normal model account, file permissions, and tool approvals. This skill has no separate account or API key.

Installation needs internet access to download the release. On macOS, the commands use Terminal with `curl`, `shasum`, and `unzip`. On Windows, use PowerShell 5.1 or later. Python **3.11 or later** is needed only for the optional package checker and tasks that use Python; the skill itself is Markdown. There is no pip package, Node dependency, or Docker service to install.

| Purpose | macOS default | Windows default |
|---|---|---|
| Knowledge root | `~/Desktop/AgentKnowledge` | `D:\AgentKnowledge` if D: exists, otherwise `C:\AgentKnowledge` |
| Canonical skill | `<root>/skills/personal-agent-growth` | `<root>\skills\personal-agent-growth` |
| Downloaded release | `<root>/downloads/0.3.2` | `<root>\downloads\0.3.2` |
| Private task records | `<root>/tasks/<task-id>` | `<root>\tasks\<task-id>` |
| User discovery entry | `~/.agents/skills/personal-agent-growth` | `%USERPROFILE%\.agents\skills\personal-agent-growth` |

Current Codex and Cursor documentation both list `.agents/skills` as a discovery location. The commands below create **one entry pointing to one canonical folder**, using a symbolic link on macOS and a directory junction on Windows. Do not add a second same-name copy under `.cursor/skills` or `.codex/skills` unless your host requires it; duplicate entries can select different versions.

Choose a different root by editing `GrowthRoot` before running the block. If D: or the root of C: is not writable, choose a writable folder such as `C:\Users\<you>\AgentKnowledge`. Avoid changing permissions across an entire drive.

## 2. Install on macOS

Open Terminal, paste the whole block, and press Return. It downloads the pinned release, checks both published SHA-256 values, extracts the skill, and creates its discovery entry. It stops if an installation already exists.

```bash
(
  set -eu
  GrowthRoot="$HOME/Desktop/AgentKnowledge"
  GrowthSkillsRoot="$HOME/.agents/skills"
  SkillDir="$GrowthRoot/skills/personal-agent-growth"
  SkillEntry="$GrowthSkillsRoot/personal-agent-growth"
  ReleaseDir="$GrowthRoot/downloads/0.3.2"
  ReleaseUrl="https://github.com/KarmenLoop/personal-agent-growth/releases/download/v0.3.2"

  if [ -e "$SkillDir" ] || [ -L "$SkillDir" ] || [ -e "$SkillEntry" ] || [ -L "$SkillEntry" ]; then
    echo "An installation already exists. Follow the update section instead."
    exit 1
  fi

  mkdir -p "$ReleaseDir" "$GrowthRoot/skills" "$GrowthRoot/tasks" "$GrowthSkillsRoot"
  curl --fail --location --retry 2 --max-time 90 "$ReleaseUrl/personal-agent-growth-0.3.2.zip" -o "$ReleaseDir/personal-agent-growth-0.3.2.zip"
  curl --fail --location --retry 2 --max-time 90 "$ReleaseUrl/manifest.json" -o "$ReleaseDir/manifest.json"

  printf '%s  %s\n' 'b2e58a97357cee25cac9c890e053d381cb4240b4d63ff1815886c0dfcd9a61b0' "$ReleaseDir/personal-agent-growth-0.3.2.zip" | shasum -a 256 -c -
  printf '%s  %s\n' '38c173aded1b11f91814684a52e82d3f71275c44cf86da420a7e28d2b07ebc9a' "$ReleaseDir/manifest.json" | shasum -a 256 -c -

  unzip -q "$ReleaseDir/personal-agent-growth-0.3.2.zip" -d "$GrowthRoot/skills"
  ln -s "$SkillDir" "$SkillEntry"
  test -f "$SkillEntry/SKILL.md"
  printf 'Skill: %s\nDiscovery entry: %s\nTask memory: %s\n' "$SkillDir" "$SkillEntry" "$GrowthRoot/tasks"
)
```

Success prints two checksum lines ending in `OK` and three paths labeled `Skill`, `Discovery entry`, and `Task memory`. The variables exist only inside this block; later examples define their own paths.

The canonical folder should contain exactly these eight files:

```text
personal-agent-growth/
├── SKILL.md
├── references/
│   ├── task-record.md
│   ├── learning-and-contact.md
│   ├── autonomous-continuation.md
│   └── shared-memory.md
├── scripts/
│   └── verify_handoff.py
├── LICENSE
└── NOTICE
```

## 3. Install on Windows

Open **PowerShell**, not Command Prompt. Paste the whole block. It chooses D: when present and C: otherwise. Edit `$GrowthRoot` first if you want another location.

```powershell
& {
  $ErrorActionPreference = 'Stop'
  $GrowthRoot = if (Test-Path -LiteralPath 'D:\') { 'D:\AgentKnowledge' } else { 'C:\AgentKnowledge' }
  $GrowthSkillsRoot = Join-Path $env:USERPROFILE '.agents\skills'
  $SkillDir = Join-Path $GrowthRoot 'skills\personal-agent-growth'
  $SkillEntry = Join-Path $GrowthSkillsRoot 'personal-agent-growth'
  $ReleaseDir = Join-Path $GrowthRoot 'downloads\0.3.2'
  $ReleaseUrl = 'https://github.com/KarmenLoop/personal-agent-growth/releases/download/v0.3.2'

  if ((Test-Path -LiteralPath $SkillDir) -or (Test-Path -LiteralPath $SkillEntry)) {
    throw 'An installation already exists. Follow the update section instead.'
  }

  New-Item -ItemType Directory -Force -Path $ReleaseDir, (Join-Path $GrowthRoot 'skills'), (Join-Path $GrowthRoot 'tasks'), $GrowthSkillsRoot | Out-Null
  $ZipPath = Join-Path $ReleaseDir 'personal-agent-growth-0.3.2.zip'
  $ManifestPath = Join-Path $ReleaseDir 'manifest.json'
  Invoke-WebRequest -UseBasicParsing -Uri "$ReleaseUrl/personal-agent-growth-0.3.2.zip" -OutFile $ZipPath
  Invoke-WebRequest -UseBasicParsing -Uri "$ReleaseUrl/manifest.json" -OutFile $ManifestPath

  if ((Get-FileHash -LiteralPath $ZipPath -Algorithm SHA256).Hash -ne 'b2e58a97357cee25cac9c890e053d381cb4240b4d63ff1815886c0dfcd9a61b0') {
    throw 'ZIP checksum mismatch. Nothing has been extracted.'
  }
  if ((Get-FileHash -LiteralPath $ManifestPath -Algorithm SHA256).Hash -ne '38c173aded1b11f91814684a52e82d3f71275c44cf86da420a7e28d2b07ebc9a') {
    throw 'Manifest checksum mismatch. Nothing has been extracted.'
  }

  Expand-Archive -LiteralPath $ZipPath -DestinationPath (Join-Path $GrowthRoot 'skills')
  New-Item -ItemType Junction -Path $SkillEntry -Target $SkillDir | Out-Null
  if (-not (Test-Path -LiteralPath (Join-Path $SkillEntry 'SKILL.md'))) {
    throw 'The discovery entry cannot read SKILL.md.'
  }
  Write-Output "Skill: $SkillDir"
  Write-Output "Discovery entry: $SkillEntry"
  Write-Output "Task memory: $(Join-Path $GrowthRoot 'tasks')"
}
```

Success prints the three installation paths. Keep the eight files shown above together. A directory junction needs a supported local filesystem and permission to create the entry. If junction creation fails after extraction, the canonical skill is still present: fix the destination or use the manual option below. Do not repeatedly extract over it.

## 4. Other installation options

### Manual download

1. Open the [v0.3.2 release](https://github.com/KarmenLoop/personal-agent-growth/releases/tag/v0.3.2). Download the asset named `personal-agent-growth-0.3.2.zip` and `manifest.json`. GitHub's automatically generated “Source code” archives are different archives with different hashes.
2. Verify the two downloads with the checksum commands above or your SHA-256 tool. The expected values are:

   | File | SHA-256 |
   |---|---|
   | `personal-agent-growth-0.3.2.zip` | `b2e58a97357cee25cac9c890e053d381cb4240b4d63ff1815886c0dfcd9a61b0` |
   | `manifest.json` | `38c173aded1b11f91814684a52e82d3f71275c44cf86da420a7e28d2b07ebc9a` |

3. Extract the archive. Place the **whole** `personal-agent-growth` folder directly under your user's `.agents/skills` directory. The result must be `.agents/skills/personal-agent-growth/SKILL.md`, without an extra nested folder.
4. Create a separate `AgentKnowledge/tasks` location for private records. In this manual option, the canonical skill lives in `.agents/skills`, rather than under `AgentKnowledge/skills`. Use that actual location in subsequent commands.
5. In Finder, use **Go → Go to Folder** with `~/.agents/skills`; in Windows Explorer, enter `%USERPROFILE%\.agents\skills`. Create missing directories first. A Finder alias or a Windows `.lnk` shortcut is not the filesystem link used by the recommended commands.

This is a standalone skill. It does not include a Cursor plugin marketplace manifest, so do not assume Cursor's plugin repository import will install this repository.

### Limit installation to one project

Before running the command block, change `GrowthSkillsRoot` to your project's absolute `.agents/skills` path. Then open that project in the host. Use either a user entry or a project entry for this skill, not both. Keep private task memory outside a public repository, or explicitly exclude it from version control.

### Linux, WSL, SSH, and cloud agents

For Linux, adapt the macOS block to a writable root such as `$HOME/AgentKnowledge` and ensure `curl`, `unzip`, and `shasum` are available. With `sha256sum`, replace `shasum -a 256 -c -` with `sha256sum -c -`. The same user's `~/.agents/skills` discovery location applies.

WSL and SSH sessions have their own home directories and execution permissions. A Windows installation is not automatically a WSL installation. Use the paths visible to the executing host; sharing through `/mnt/d` requires that mount to be available. A cloud agent cannot read a local Desktop or D: folder just because a chat contains its path. Cross-device use requires a separately configured, authorized transfer or sync method and a path mapping.

## 5. Confirm that the host can use it

Open a new chat in each host. In Codex, select the skill where the Skills interface is available; in CLI/IDE interfaces, use `/skills` or a `$` skill mention. In Cursor, search for the skill with `/` or attach it with `@` where supported. Exact controls depend on the host version.

If it does not appear, reopen the project or restart the host and check the discovery path. Explicitly reading the absolute `SKILL.md` path is a useful fallback; record that as explicit loading, rather than automatic discovery.

Paste this, replacing both placeholders with actual absolute paths:

> Read <SKILL_DIR>/SKILL.md and the references needed for this task. Report the resolved skill directory, declared version, and whether all four references and scripts/verify_handoff.py are readable. Use <TASK_DIR> for this task's private records. Do not start a scheduler during this installation check.

Expected result: version `0.3.2`, the intended resolved path, and readable resources. A directory existing is only the installation check; the first useful task below checks actual use.

### Optional: inspect the release with the bundled checker

Check `python3 --version` on macOS or `py -3 --version` on Windows. Use an installed Python 3.11+ interpreter. If missing, install a current supported Python from [python.org](https://www.python.org/downloads/) and reopen the terminal. No `pip install` is needed.

macOS, with the default root:

```bash
python3 "$HOME/Desktop/AgentKnowledge/skills/personal-agent-growth/scripts/verify_handoff.py" \
  --archive "$HOME/Desktop/AgentKnowledge/downloads/0.3.2/personal-agent-growth-0.3.2.zip" \
  --manifest "$HOME/Desktop/AgentKnowledge/downloads/0.3.2/manifest.json"
echo "Exit code: $?"
```

Windows, with the default D:/C: selection:

```powershell
$GrowthRoot = if (Test-Path -LiteralPath 'D:\') { 'D:\AgentKnowledge' } else { 'C:\AgentKnowledge' }
py -3 (Join-Path $GrowthRoot 'skills\personal-agent-growth\scripts\verify_handoff.py') --archive (Join-Path $GrowthRoot 'downloads\0.3.2\personal-agent-growth-0.3.2.zip') --manifest (Join-Path $GrowthRoot 'downloads\0.3.2\manifest.json')
Write-Output "Exit code: $LASTEXITCODE"
```

Change paths for a custom or manual installation. Expected: `PASS`, exit `0`, **21 checks**. Exit `1` means rejection after inspection; exit `2` means incomplete inspection. If Python did not start, no package verdict exists. The checker compares the supplied archive and manifest; it does not authenticate a publisher or test agent behavior. See the [manifest contract](manifest.md).

## 6. Initialize private memory and complete a first task

Choose one task folder, for example `~/Desktop/AgentKnowledge/tasks/install-review` or `D:\AgentKnowledge\tasks\install-review`. Give both hosts its full absolute path. Expand `~` to your actual user path when sharing it.

A useful layout is:

```text
tasks/install-review/
├── task.md                 # Goal, scope, completion criteria, current index
├── state.json              # Task ID, revision, phase, writer, next action
├── memory/
│   ├── preferences.json    # Explicit user preferences and their source
│   └── lessons.md          # Evidence, revised decisions, limits
└── evidence/               # Commands, outputs, input identities, results
```

The agent creates these records when needed; installation does not populate a profile or import your chat history. Existing task records should be reused. Small tasks may use fewer files.

Copy this prompt after replacing the two paths:

> Use Personal Agent Growth at <SKILL_DIR>. Task memory is <TASK_DIR>. Complete a useful installation review: before checking, record which resources you expect to be available and why. Read the installed skill and its references, inspect the downloaded release with the verifier if Python is available, and save the actual commands, exit codes, output, and file identities. If a resource or environment assumption fails, identify the cause, learn only what is needed to fix it, and check again. Record what changed your judgment. Create or reuse task.md, state.json, and the evidence index. Record my preference: finish anything you can resolve yourself; contact me only for a decision I must make. Do not invent personal attributes. Leave a concrete review action for the next host. Do not create an automation for this installation review.

This first task should leave a usable result, not just a folder tree. Check the saved output and the next action. It is valid to record an unavailable Python checker separately while completing file and resource checks.

## 7. Resume and review in Cursor or Codex

Finish the current write before switching tools. Ask the current host to save the result, transfer `writer` to the receiving host, and increment `state_revision`. Both tools must resolve the task directory to the same physical location. This is a cooperative writing rule, not an automatic database lock or sync service.

In the receiving host, paste:

> Read <SKILL_DIR>/SKILL.md. Resume from the actual records in <TASK_DIR>. First report task_id, state_revision, writer, the resolved task path, and the next action. Use the previous prediction, failure records, and lessons to complete the pending review. Reuse the existing checker or artifact, save new output, explain whether the evidence changes the earlier conclusion, and update the same state. Reread its revision immediately before writing. If another writer has advanced it, preserve the newer facts and resolve the handoff before writing. Do not create a separate memory copy or unnecessary chat.

Confirm that the second host **read the current revision, used an earlier artifact, and wrote a new result to the same directory**. To check that it is reading files rather than repeating chat context, hand ownership back, record a useful new decision or counterexample, and have the receiving host review that newer revision. Do this only when it adds useful work.

See [shared-memory rules](../references/shared-memory.md) for conflict handling and evidence identity.

## 8. Optional: authorize a scheduled review

Installation does not create a timer. Use scheduling when a future review, external result, or new input gives the next run a purpose. Complete work that is ready now.

Example authorization, after replacing the task path:

> For <TASK_DIR>, arrange a review tomorrow at 09:00 in my current time zone, using this host's supported scheduling interface. First check for an existing binding. Permit at most two automatic runs, expiring 48 hours after registration. Save the goal, review action, completion criteria, deadline, and scheduler owner. Read back the actual registered schedule and record its backend ID. On a real host trigger, recover the current state, perform the review, save evidence, and adjust or stop the schedule according to the result. Verify the stopped state when finished. Resolve routine problems yourself; ask only for a decision I must make. Do not send routine progress notifications.

Use the host's actual notification settings where supported. Do not assume text in a prompt alone controls notifications. If the scheduling interface is unavailable, record that fact and the unregistered next action; do not claim a background job exists.

The complete chain is: registration readback → real host event → state recovery → actual work → checked result → revised or stopped backend schedule. A plan file or `ACTIVE` label alone does not establish that chain. Prior trials verified native Codex wakeups; they did not verify a native Cursor scheduler or execution while the app is closed. Current capabilities must be checked in each host. See [scheduled continuation](../references/autonomous-continuation.md).

## 9. Update, roll back, or uninstall

### Update

1. Finish or pause current writes and any bound schedule that would use the files being replaced. Record the current writer and state revision.
2. Back up the canonical skill folder and task records separately. Preserve personal skill edits and their evidence before updating.
3. Download the desired published release and its matching manifest into a new versioned download directory. Verify that release's hashes; the hashes above apply only to **0.3.2**.
4. Extract into a staging directory and inspect its version, resources, and package result. Compare any local method changes before choosing what to keep.
5. Rename the old canonical folder to a versioned backup, then move the new `personal-agent-growth` folder into the original canonical path. The discovery entry can keep pointing to that path. Leave the separate `tasks` directory in place.
6. Open a new host chat, verify the resolved path/version, and review an existing task before reactivating a paused schedule through its actual host interface.

If you installed a direct folder under `.agents/skills`, that folder is the canonical target. If you deliberately keep separate host copies, update and verify each. A Git clone is an alternative for maintainers: inspect local changes and the target revision before updating; do not use a destructive reset to replace personal edits.

### Roll back

Pause affected writes/schedules, preserve the failed candidate and its evidence, then restore the backed-up skill to the same canonical path. Recheck the loaded version. Retain newer task facts; review record compatibility instead of overwriting current memory with an older backup.

### Uninstall

1. Pause or delete this task's bound automation through its host and confirm the result. Removing files does not unregister a scheduler.
2. Remove only the discovery entry. For the recommended macOS layout, the command below refuses to remove an ordinary directory:

   ```bash
   if [ -L "$HOME/.agents/skills/personal-agent-growth" ]; then
     unlink "$HOME/.agents/skills/personal-agent-growth"
   else
     echo "No symbolic link removed. Inspect the installed directory first."
   fi
   ```

   On Windows, confirm the entry is a junction before using the nonrecursive removal command:

   ```powershell
   $SkillEntry = Join-Path $env:USERPROFILE '.agents\skills\personal-agent-growth'
   $Entry = Get-Item -LiteralPath $SkillEntry -Force
   if ($Entry.LinkType -ne 'Junction') { throw 'This is not the expected junction. Inspect it first.' }
   cmd /c rmdir "$SkillEntry"
   if ($LASTEXITCODE -ne 0) { throw 'The junction was not removed.' }
   ```

3. Reopen the host. Keep or archive the canonical skill and task records as you prefer. With a manual direct-folder installation, move that folder out of the discovery directory instead. Delete private memory only when you intend to discard it.

## 10. Troubleshooting

| Symptom | Check or fix |
|---|---|
| Skill is absent | Check the exact `.agents/skills/personal-agent-growth/SKILL.md` path, host execution environment, and folder access; reopen the host and try explicit loading. |
| Two copies appear | Resolve each discovery entry. Keep the intended version and move the stale entry out of discovery after checking it. |
| Installer says it already exists | Inspect the existing version. Use the update procedure; do not force-overwrite it. |
| Junction or link fails | Check local filesystem support, writable paths, and stale entries. Use a direct-folder installation if necessary. |
| Download is HTML or its hash differs | Use the named release assets, not “Source code”; redownload and compare. Do not skip the mismatch. |
| Python is missing or too old | Install Python 3.11+ or select that interpreter explicitly. Loading Markdown does not require Python. |
| Both tools claim shared memory, but revisions differ | Compare resolved paths, task_id, file content, and current writer. Same-looking paths on different devices are not the same files. |
| Agent writes plans but performs no review | Explicitly select the skill, give a concrete artifact and completion check, and inspect saved commands/results. |
| Nothing wakes automatically | Check a real backend registration, binding, host availability, deadline, and run limit. Installing the skill alone does not schedule work. |
| A remote host cannot read memory | Configure an authorized transfer/mount and path mapping; copying a local path into a chat does not transfer files. |

## Verification scope and sources

The release's utility tests and package checks passed on Linux, macOS Intel, and Windows. Separate maintainer trials covered native Codex wakeups and same-Mac Cursor shared-memory recovery. These are different checks; they do not establish automatic selection in every fresh chat or behavior on every platform. See [release acceptance](release-0.3.2-acceptance.md) and [validation limits](validation.md).

Current installation locations and host behavior were checked against [OpenAI's skills documentation](https://learn.chatgpt.com/docs/build-skills), [Cursor's skills documentation](https://cursor.com/docs/skills), and [Cursor's customization help](https://cursor.com/help/customization/skills). Windows commands use documented [New-Item junction support](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.management/new-item?view=powershell-7.5) and [Expand-Archive](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.archive/expand-archive?view=powershell-7.5).

The package retains its [AGPL-3.0-only license](../LICENSE) and [notice](../NOTICE). Keep them with copies and modified distributions; see the [licensing guide](licensing.md) for the obligations.
