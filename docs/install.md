# Complete installation, update, and removal · 0.4.1

[中文](install.zh-CN.md) · [Hands-on tutorial](tutorial.en.md) · [Full offline bundle](../START-HERE.md)

## 1. Choose the package and location

The release provides a core `personal-agent-growth-0.4.1.zip` containing the skill, bilingual protocols, templates, and utilities. The **complete delivery bundle** also contains all source, tests, the historical experience seed, bilingual long-form guides, and diagram sources. Core-package links to omitted long-form material point to versioned GitHub documents. Choose the complete bundle for offline documentation and experience installation.

Use a working host account, writable local folders, and Python 3.11+. Utilities need only the standard library, with no pip install. Check `python3 --version` on macOS or `py -3 --version` on Windows. Markdown can be read without Python, but utility execution cannot be claimed. Installation creates no account, daemon, scheduled task, or device sync.

The suggested skill root is `~/Desktop/AgentKnowledge` on macOS and D: when present, otherwise C:, on Windows. Choose a user-owned directory if those locations are not writable. Set a separate private Markdown root such as `AgentKnowledge/learning`, or explicitly share Koder's `~/.koder/learning`. Preserve an existing library instead of replacing it with an empty one.

```text
AgentKnowledge/
  skills/personal-agent-growth/   Canonical skill
  downloads/0.4.1/                Release assets
  learning/                      Private Markdown knowledge
  tasks/                         Inputs, experiments, raw receipts
  experience/                    Optional historical seed, separate from the current profile
```

## 2. Install the core package on macOS

Run the entire block in Terminal. It stops when a skill or discovery entry already exists; follow the update procedure instead. Comparing the downloaded manifest and ZIP checks consistency, not an independent publisher signature.

```bash
(
  set -e
  GrowthRoot="$HOME/Desktop/AgentKnowledge"
  GrowthSkillsRoot="$HOME/.agents/skills"
  SkillDir="$GrowthRoot/skills/personal-agent-growth"
  SkillEntry="$GrowthSkillsRoot/personal-agent-growth"
  ReleaseDir="$GrowthRoot/downloads/0.4.1"
  ReleaseUrl="https://github.com/KarmenLoop/personal-agent-growth/releases/download/v0.4.1"
  if [ -e "$SkillDir" ] || [ -L "$SkillDir" ] || [ -e "$SkillEntry" ] || [ -L "$SkillEntry" ]; then
    echo "An installation already exists. Follow the update section." >&2
    exit 1
  fi
  mkdir -p "$ReleaseDir" "$GrowthRoot/skills" "$GrowthRoot/tasks" "$GrowthSkillsRoot"
  curl --fail --location --retry 2 --max-time 90 "$ReleaseUrl/personal-agent-growth-0.4.1.zip" -o "$ReleaseDir/personal-agent-growth-0.4.1.zip"
  curl --fail --location --retry 2 --max-time 90 "$ReleaseUrl/manifest.json" -o "$ReleaseDir/manifest.json"
  python3 - "$ReleaseDir" <<'PY'
import hashlib, json, pathlib, sys
p = pathlib.Path(sys.argv[1])
m = json.loads((p / 'manifest.json').read_text(encoding='utf-8'))
assert m['archive']['name'] == 'personal-agent-growth-0.4.1.zip'
assert hashlib.sha256((p / m['archive']['name']).read_bytes()).hexdigest() == m['archive']['sha256'], 'ZIP checksum mismatch'
print('Archive hash matches the supplied manifest')
PY
  unzip -q "$ReleaseDir/personal-agent-growth-0.4.1.zip" -d "$GrowthRoot/skills"
  python3 -B "$SkillDir/scripts/verify_handoff.py" --archive "$ReleaseDir/personal-agent-growth-0.4.1.zip" --manifest "$ReleaseDir/manifest.json"
  ln -s "$SkillDir" "$SkillEntry"
  test -f "$SkillEntry/SKILL.md"
  printf 'Skill: %s\nDiscovery entry: %s\nTask memory: %s\n' "$SkillDir" "$SkillEntry" "$GrowthRoot/tasks"
)
```

Expect a matching hash, package PASS/exit 0, and three paths. Preserve output on failure. If extraction succeeded before link creation failed, inspect the existing copy rather than repeatedly overwriting it.

## 3. Install the core package on Windows

Use PowerShell 5.1 or 7 rather than CMD. Change the root if needed. Retain UTF-8 mode, particularly for Chinese/space-containing paths and redirected output.

```powershell
& {
  $ErrorActionPreference = 'Stop'
  $GrowthRoot = if (Test-Path -LiteralPath 'D:\') { 'D:\AgentKnowledge' } else { 'C:\AgentKnowledge' }
  $GrowthSkillsRoot = Join-Path $env:USERPROFILE '.agents\skills'
  $SkillDir = Join-Path $GrowthRoot 'skills\personal-agent-growth'
  $SkillEntry = Join-Path $GrowthSkillsRoot 'personal-agent-growth'
  $ReleaseDir = Join-Path $GrowthRoot 'downloads\0.4.1'
  $ReleaseUrl = 'https://github.com/KarmenLoop/personal-agent-growth/releases/download/v0.4.1'
  if ((Test-Path -LiteralPath $SkillDir) -or (Get-Item -LiteralPath $SkillEntry -Force -ErrorAction SilentlyContinue)) {
    throw 'An installation already exists. Follow the update section.'
  }
  New-Item -ItemType Directory -Force -Path $ReleaseDir, (Join-Path $GrowthRoot 'skills'), (Join-Path $GrowthRoot 'tasks'), $GrowthSkillsRoot | Out-Null
  $ZipPath = Join-Path $ReleaseDir 'personal-agent-growth-0.4.1.zip'
  $ManifestPath = Join-Path $ReleaseDir 'manifest.json'
  Invoke-WebRequest -UseBasicParsing -Uri "$ReleaseUrl/personal-agent-growth-0.4.1.zip" -OutFile $ZipPath
  Invoke-WebRequest -UseBasicParsing -Uri "$ReleaseUrl/manifest.json" -OutFile $ManifestPath
  $Manifest = Get-Content -LiteralPath $ManifestPath -Raw -Encoding UTF8 | ConvertFrom-Json
  if ($Manifest.archive.name -ne 'personal-agent-growth-0.4.1.zip') { throw 'Unexpected archive name.' }
  if ((Get-FileHash -LiteralPath $ZipPath -Algorithm SHA256).Hash -ne $Manifest.archive.sha256) {
    throw 'ZIP checksum mismatch. Nothing has been extracted.'
  }
  Expand-Archive -LiteralPath $ZipPath -DestinationPath (Join-Path $GrowthRoot 'skills')
  py -3 -B -X utf8 (Join-Path $SkillDir 'scripts\verify_handoff.py') --archive $ZipPath --manifest $ManifestPath
  if ($LASTEXITCODE -ne 0) { throw 'Package verification failed; inspect the output.' }
  New-Item -ItemType Junction -Path $SkillEntry -Target $SkillDir | Out-Null
  if (-not (Test-Path -LiteralPath (Join-Path $SkillEntry 'SKILL.md'))) { throw 'Discovery entry is unreadable.' }
  Write-Output "Skill: $SkillDir"
  Write-Output "Discovery entry: $SkillEntry"
  Write-Output "Task memory: $(Join-Path $GrowthRoot 'tasks')"
}
```

To check it again:

```powershell
$GrowthRoot = if (Test-Path -LiteralPath 'D:\') { 'D:\AgentKnowledge' } else { 'C:\AgentKnowledge' }
py -3 -B -X utf8 (Join-Path $GrowthRoot 'skills\personal-agent-growth\scripts\verify_handoff.py') --archive (Join-Path $GrowthRoot 'downloads\0.4.1\personal-agent-growth-0.4.1.zip') --manifest (Join-Path $GrowthRoot 'downloads\0.4.1\manifest.json')
if ($LASTEXITCODE -ne 0) { throw 'Verification did not pass.' }
```

Junctions require a supporting filesystem. If link creation is unavailable, put the entire extracted folder directly in a supported discovery directory. Finder aliases and Windows `.lnk` shortcuts are not filesystem links. Windows command checks and desktop Agent behavior are reported separately in [compatibility](compatibility.en.md).

## 4. Manual, project-level, and other environments

Download the exact asset and its manifest from [v0.4.1](https://github.com/KarmenLoop/personal-agent-growth/releases/tag/v0.4.1). GitHub's automatic Source code ZIP serves a different purpose from the installer asset. Extract the whole folder into `.agents/skills/personal-agent-growth` so `SKILL.md` is directly inside it.

Choose one user-level or project-level entry; a project entry uses `<project>/.agents/skills`. Linux can use the macOS procedure with `$HOME/AgentKnowledge`. WSL, SSH, and cloud environments have separate filesystems, accounts, and permissions. Identical path strings do not synchronize data. Configure authorized transfer/mounting and path mappings before cross-device use.

## 5. Verify actual loading

Codex/Cursor versions supporting Agent Skills can discover `.agents/skills`. Reload the host/project and select the skill using its current interface. If discovery is unavailable, explicitly read an absolute path:

> Read <absolute-skill-path>/SKILL.md. Report version 0.4.1, its resolved path, and the references/scripts needed for this task. The private learning root is <absolute-path>. Resume the project using the Markdown protocol and identify the context, newest node, and source revisions actually read. Do not create a schedule for this installation check.

Directory presence, discovery, automatic selection, and execution are different evidence. Explicit reading is usable but should be labeled honestly. Continue with the [full tutorial](tutorial.en.md) to produce preparation and review artifacts.

## 6. Shared memory and optional MCP

Both hosts read the same actual directory, project ID, and revision. The current writer finishes writing, retains artifacts, and transfers responsibility; the receiver checks before updating. Reading a separate copy does not establish shared memory. Follow the [Markdown contract](markdown-learning.en.md).

The existing `scripts/host.py` is a separate optional SQLite checkpoint adapter with five `growth_*` tools. Configuration, approval, and real model use require distinct checks. It does not implement the daily/weekly Markdown system. See the [adapter tutorial](tutorial.en.md#adapter). Do not let two writable stores control the same project state.

## 7. Future review and notifications

Authorize real scheduling only for useful spaced review or expected new input. Save the task, action, expiry, run limit, owner, and binding ID. Read the backend back, verify a later event, execute and inspect work, then stop. Contact the user only for a decision; avoid unchanged routine notifications.

Without a scheduler interface, retain not_registered. A Markdown plan does not register a task. In-process idle callbacks, manual continuation, and app-closed OS wakeups are separate behaviors. The [continuation protocol](../references/autonomous-continuation.en.md) defines the complete chain.

## 8. Complete offline bundle and experience

Inside the full bundle, run `python3 -B tools/check_delivery.py .`, then follow [START-HERE](../START-HERE.md) to install into a fresh root. The installer retains a distribution copy, copies the seed, and creates empty task storage; it creates no discovery entry or background work. Historical methods need current applicability and are not a current user profile or a new trial.

Native `learning` commands from the separate Koder candidate are outside this installation. The public skill provides protocols, templates, and tools; native product injection remains subject to its own acceptance limits.

## 9. Update, roll back, remove

Finish active writes and pause bindings that read the old version. Back up skill and memory separately. Download and verify into a new version directory, compare personal edits, and switch the discovery entry. Preserve learning/tasks, and do not overwrite a live library index with a new seed. In a fresh chat, verify paths/version and recover a task.

Rollback restores a known usable skill version while retaining newer facts, failures, and revisions. Check compatibility before continuing; do not overwrite current truth with an old memory backup.

Before removal, stop related host schedules. If MCP was configured, back up the configuration, remove only `personal_agent_growth`, and reload. Deleting files does not unregister schedules or MCP entries.

On macOS, inspect `readlink "$HOME/.agents/skills/personal-agent-growth"`, confirm the target, then remove only that link with `unlink "$HOME/.agents/skills/personal-agent-growth"`. On Windows, confirm the printed target is the intended skill before running:

```powershell
$SkillEntry = Join-Path $env:USERPROFILE '.agents\skills\personal-agent-growth'
$Entry = Get-Item -LiteralPath $SkillEntry -Force
if ($Entry.LinkType -ne 'Junction') { throw 'This is not the expected junction. Inspect it first.' }
Write-Output $Entry.Target
cmd /c rmdir "$SkillEntry"
if ($LASTEXITCODE -ne 0) { throw 'The junction was not removed.' }
```

These steps remove discovery only, preserving the canonical copy and memory. The full-bundle installer can additionally verify and remove an unchanged skill: `python3 -B <root>/distribution/tools/local_install.py uninstall --root <root>`. It refuses changed/added files and retains experience, tasks, distribution, and the installation receipt. For a manual install, move the skill out of discovery first. The user controls separate deletion of private memory.

## 10. Troubleshooting

| Symptom | Check and remedy |
|---|---|
| Missing skill | Folder nesting, current runtime/user, permissions, reload, explicit-path fallback |
| Existing installation | Inspect the old version and update without forced replacement |
| Unicode output failure | `py -3 -X utf8` and explicit UTF-8 decoding |
| HTML download/hash mismatch | Exact asset name/version; do not skip mismatch checks |
| Different progress in two hosts | Resolved root, ID, revision, writer, artifact hashes |
| Plan without a wakeup | Backend registration, binding, actual event, host availability |
| PS5 module error under PS7 | Clear PSModulePath only in the PS5 child environment so it rebuilds; do not change global settings |
| Weak tag drives planning | Inspect evidence and formula version, downgrade, revisit dependent plans |

Directory conventions are checked against the [Agent Skills specification](https://agentskills.io/specification), [Cursor Skills documentation](https://cursor.com/docs/skills), and actual host capabilities. Preserve [LICENSE](../LICENSE) and [NOTICE](../NOTICE). See [compatibility](compatibility.en.md) for current and historical evidence.
