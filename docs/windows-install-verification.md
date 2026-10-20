# Windows installation and shared-memory verification

**PASS** on real GitHub-hosted Windows Server 2025 x64 runners. The [completed run](https://github.com/KarmenLoop/personal-agent-growth/actions/runs/39485618391) tested commit `89c3bddefc95b788e320bb117c0e8f4324a9a566`.

| Shell | Actual version | Default D: layout | Custom C: layout |
|---|---|---|---|
| Windows PowerShell | 5.1.26100.33438 | PASS | PASS |
| PowerShell | 7.6.6 | PASS | PASS |

Both jobs used Python 3.11.9. The C: paths included Chinese characters, spaces, and an ampersand. The default case executed the guide's real D:/C: selector, which selected D: on both runners. Discovery entries were redirected to isolated test locations; the commands did not alter the runners' user-level skill directories.

## What actually ran

The [test runner](../tools/check_windows_install.py) extracts the three PowerShell blocks from the English and Chinese guides and requires them to match. It executes the install and uninstall blocks with the recorded path substitutions. The shared-memory review invokes the installed checker with the guide's UTF-8 option.

Each of the four shell/layout combinations completed:

1. Download the published ZIP and manifest, check both SHA-256 values, extract, and create the discovery junction.
2. Compare all eight installed files with the manifest and check that the discovery entry resolves to the same Windows file as the canonical skill.
3. Create a real task record in a separate memory directory. A fresh process accesses it through a second junction, restores revision 1, preserves the task ID and unique marker, runs the installed checker, and writes revision 2.
4. A third process reads the same result, verifies the saved review output, and writes completed revision 3. Each package review returned exit 0 and passed all 21 checks.
5. Reject a byte-for-byte copy as shared memory using file identity. Reject a stale revision in the test helper without changing the current file.
6. Attempt installation again: exit 1 with the existing-installation message, preserving the complete skill and task-memory snapshot.
7. Execute the guide's uninstall command: exit 0; the discovery junction is gone, while every canonical skill and memory file retains its previous hash.
8. Place an ordinary directory at the former entry path and run uninstall: exit 1, with its sentinel file retained.

There are 22 recorded child commands per shell. These include expected rejections and the controlled encoding failure; they are not 22 unrelated unit tests. The full receipt records each actual command, expected and actual exit code, stdout, stderr, environment, file identities, and state progression.

## Failures found and corrections

The [first run](https://github.com/KarmenLoop/personal-agent-growth/actions/runs/39485238116) remains available and is included in the evidence archive.

**Windows PowerShell module lookup.** Launching PowerShell 5.1 through Python under PowerShell 7 inherited the wrong module search paths. `Get-FileHash` was unavailable before extraction. The test runner now removes `PSModulePath` only from the 5.1 child process environment; Windows PowerShell reconstructs its native paths. The follow-up receipt confirms `Microsoft.PowerShell.Utility` supplies the command. The guides explain direct launch and this embedded-launch case. This is a launcher-context correction, not a missing skill dependency. Microsoft's [PSModulePath documentation](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_psmodulepath?view=powershell-7.5) describes this inheritance behavior.

**Captured Unicode output.** The C: Chinese-path review initially received unusable output. That first wrapper record retained the JSON parsing failure but did not export the nested verifier's raw error. The follow-up retained a direct reproduction: Python 3.11's cp1252 redirected output raised `UnicodeEncodeError`. Invoking the same released checker with `python -X utf8` produced valid UTF-8 JSON and passed all 21 checks. The Windows guide and README now use `py -3 -X utf8`; the test runner preserves nested stdout and stderr even on failure. Python documents [UTF-8 mode](https://docs.python.org/3.11/using/windows.html#utf-8-mode).

The skill remains version 0.3.2. Its ZIP, manifest, and eight installed files are unchanged. The correction is the Windows invocation and launch environment.

## Receipts and reproduction

- [Machine-readable results](windows-install-results.json), including exact shell versions, cases, guide hashes, job URLs, and receipt hashes.
- [Full evidence ZIP](https://github.com/KarmenLoop/personal-agent-growth/releases/download/v0.3.2/windows-install-evidence-39485618391.zip), containing the first failure and successful follow-up commands and outputs.
- Evidence ZIP SHA-256: `0b3b63cdb274a72f7b81444094a7002240f81421068adba4ecb08cdd97e6dd62`.
- [Windows workflow](../.github/workflows/windows-install.yml), which can be dispatched again and retains its receipts even when a check fails.

On a clean Windows test machine with no existing default knowledge root, the same checks can be run from this repository:

```powershell
python -X utf8 tools/check_windows_install.py --shell powershell --output windows-evidence-51
python -X utf8 tools/check_windows_install.py --shell pwsh --output windows-evidence-7
```

Use separate clean environments for these two commands: each check leaves the canonical skill and memory intact to demonstrate preservation. The runner refuses to overwrite an existing knowledge root or evidence directory.

## Scope

These are actual Windows filesystem, PowerShell, Python, and independent-process recovery checks. The workers are test programs, not authenticated Codex or Cursor desktop agents. They establish a usable shared directory and recovery protocol; they do not establish fresh-chat discovery, model judgment, automatic skill selection, a built-in locking service, or native scheduling.

Both D: and a custom C: installation were exercised. The physical absence of D: was not reproduced, so the automatic no-D: fallback branch is not claimed as a hardware-environment test. The runners also do not establish behavior for every Windows edition or non-administrator permission configuration.

The [earlier macOS command check](install-verification.md) and [same-Mac agent trials](validation.md) retain their separate evidence scopes. No user credentials or private task memory were transferred to Windows.
