#!/usr/bin/env python3
# Copyright (C) 2026 KARMENLOOP Official Team
# SPDX-License-Identifier: AGPL-3.0-only
"""Execute Windows guide commands and retain real receipts.

Memory workers are independent test processes, not Codex or Cursor agents.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import shutil
import subprocess
import sys
import tempfile
import traceback
import uuid

ROOT = Path(__file__).resolve().parents[1]
SELF = Path(__file__).resolve()


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n",
                    encoding="utf-8")


def snapshot(folder):
    return {p.relative_to(folder).as_posix(): digest(p)
            for p in folder.rglob("*") if p.is_file()}


def prepare_guides(en, zh, version, local=None):
    """Keep guide behavior intact while substituting only CI artifact transport."""
    if not re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+", version):
        raise ValueError("Invalid publication version")
    pattern = r"^[ ]*" + chr(96) * 3 + r"powershell\n(.*?)^[ ]*" + chr(96) * 3
    blocks = re.findall(pattern, en, re.M | re.S)
    if len(blocks) != 3 or blocks != re.findall(pattern, zh, re.M | re.S):
        raise ValueError("English and Chinese PowerShell guide blocks differ")
    install, _, uninstall = blocks
    if "downloads\\" + version not in install or "releases/download/v" + version not in install:
        raise ValueError("Guide does not match the publication version")
    if local is not None:
        local = local.resolve()
        archive_name = "personal-agent-growth-" + version + ".zip"
        manifest = json.loads((local / "manifest.json").read_text(encoding="utf-8"))
        if manifest.get("declared_version") != version or manifest.get("archive", {}).get("name") != archive_name:
            raise ValueError("Local artifacts do not match the publication version")
        for name, destination in [(archive_name, "$ZipPath"), ("manifest.json", "$ManifestPath")]:
            original = 'Invoke-WebRequest -UseBasicParsing -Uri "$ReleaseUrl/' + name + '" -OutFile ' + destination
            replacement = "Copy-Item -LiteralPath '" + str(local / name).replace("'", "''") + "' -Destination " + destination
            if install.count(original) != 1:
                raise ValueError("Expected one guide download for " + name)
            install = install.replace(original, replacement)
    return install, uninstall


def memory_worker(phase, task, skill, release):
    """Exercise file recovery and revision discipline without a model."""
    state_path = task / "state.json"
    if phase == "prepare":
        task.mkdir(parents=True)
        state = {
            "task_id": str(uuid.uuid4()), "state_revision": 1,
            "writer": "process-b", "phase": "review-package",
            "prediction": {"status": "PASS", "checks": 5 + 2 * len(json.loads((release / "manifest.json").read_text(encoding="utf-8"))["files"])},
            "preference": "能自行解决就先完成，只在需要我决定时联系",
            "producer_pid": os.getpid(), "nonce": str(uuid.uuid4()),
            "next_action": "Reuse the installed checker on the downloaded package",
        }
        write_json(state_path, state)
    else:
        state = json.loads(state_path.read_text(encoding="utf-8"))
        expected = 1 if phase == "review" else 2
        owner = "process-b" if phase == "review" else "process-a"
        if state["state_revision"] != expected or state["writer"] != owner:
            print("STALE_REVISION_OR_WRITER: no write performed")
            return 3
        before = state_path.read_bytes()
        if phase == "review":
            argv = [sys.executable, "-X", "utf8", str(skill / "scripts/verify_handoff.py"),
                    "--archive", str(release / json.loads((release / "manifest.json").read_text(encoding="utf-8"))["archive"]["name"]),
                    "--manifest", str(release / "manifest.json")]
            run = subprocess.run(argv, capture_output=True, timeout=60)
            (task / "review.stdout").write_bytes(run.stdout)
            (task / "review.stderr").write_bytes(run.stderr)
            verdict = json.loads(run.stdout)
            assert run.returncode == 0 and verdict["status"] == "PASS"
            assert len(verdict["checks"]) == state["prediction"]["checks"]
            state.update(writer="process-a", phase="review-completed",
                         reviewer_pid=os.getpid(), review_exit_code=run.returncode,
                         review_argv=argv, review_output_sha256=digest(task / "review.stdout"),
                         next_action="Read back the saved review and close the task")
        else:
            assert digest(task / "review.stdout") == state["review_output_sha256"]
            assert json.loads((task / "review.stdout").read_bytes())["status"] == "PASS"
            state.update(writer=None, phase="completed", next_action=None,
                         final_reader_pid=os.getpid())
        # This guard belongs to this helper, not a claimed skill runtime lock.
        assert state_path.read_bytes() == before
        state["state_revision"] += 1
        write_json(state_path, state)
    print(json.dumps({"phase": phase, "pid": os.getpid(), "path": str(task.resolve()),
                      "state": state}, ensure_ascii=False))
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--shell", choices=["powershell", "pwsh"])
    parser.add_argument("--output", type=Path)
    parser.add_argument("--memory-worker", choices=["prepare", "review", "finish"])
    parser.add_argument("--task", type=Path)
    parser.add_argument("--skill", type=Path)
    parser.add_argument("--release", type=Path)
    parser.add_argument("--local-artifacts", type=Path, help="Use locally built release files; download transport is not exercised")
    args = parser.parse_args()
    if os.name != "nt":
        parser.error("This acceptance check must run on actual Windows.")
    if args.memory_worker:
        return memory_worker(args.memory_worker, args.task, args.skill, args.release)
    if not args.shell or not args.output:
        parser.error("--shell and --output are required")
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    report = {
        "status": "RUNNING", "observed_at": datetime.now(timezone.utc).isoformat(),
        "platform": platform.platform(), "python": sys.version,
        "shell": args.shell, "github_run_id": os.environ.get("GITHUB_RUN_ID"),
        "commit": os.environ.get("GITHUB_SHA"), "records": [], "cases": [],
        "scope": "Windows guide commands and shared-file recovery by test processes; no desktop agent behavior or scheduler claim",
    }

    def save():
        write_json(output / "receipt.json", report)

    def run(label, argv, expected=0, contains=None):
        # PS7 -> Python -> Windows PowerShell otherwise inherits PS7 modules.
        env = None
        if Path(argv[0]).name.lower() in ("powershell", "powershell.exe"):
            env = {k: v for k, v in os.environ.items() if k.upper() != "PSMODULEPATH"}
        result = subprocess.run(argv, capture_output=True, timeout=240, env=env)
        (output / (label + ".stdout")).write_bytes(result.stdout)
        (output / (label + ".stderr")).write_bytes(result.stderr)
        record = {"label": label, "argv": argv, "exit_code": result.returncode,
                  "expected_exit_code": expected, "stdout": label + ".stdout",
                  "child_psmodulepath_reset": env is not None,
                  "stderr": label + ".stderr",
                  "observed_at": datetime.now(timezone.utc).isoformat()}
        report["records"].append(record)
        save()
        combined = (result.stdout + result.stderr).decode("utf-8-sig", errors="replace")
        assert result.returncode == expected, combined
        assert contains is None or contains in combined, combined
        print(json.dumps(record, ensure_ascii=False), flush=True)
        return result.stdout.decode("utf-8-sig")

    def ps(label, source, expected=0, contains=None):
        path = output / (label + ".ps1")
        # BOM lets Windows PowerShell 5.1 read Chinese paths correctly.
        prefix = "$ErrorActionPreference = 'Stop'\n$ProgressPreference = 'SilentlyContinue'\n[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false)\n"
        path.write_text(prefix + source, encoding="utf-8-sig")
        return run(label, [args.shell, "-NoProfile", "-NonInteractive",
                           "-File", str(path)], expected, contains)

    def quoted(path):
        return "'" + str(path).replace("'", "''") + "'"

    try:
        en = (ROOT / "docs/install.md").read_text(encoding="utf-8")
        zh = (ROOT / "docs/install.zh-CN.md").read_text(encoding="utf-8")
        version = json.loads((ROOT / "publication.json").read_text(encoding="utf-8"))["version"]
        install, uninstall = prepare_guides(en, zh, version, args.local_artifacts)
        report["release_version"] = version
        report["artifact_transport"] = ("local files; published download URL not exercised" if args.local_artifacts
                                        else "published GitHub release download")
        report["guide_sha256"] = {p: digest(ROOT / p) for p in
                                   ["docs/install.md", "docs/install.zh-CN.md"]}
        root_line = "$GrowthRoot = if (Test-Path -LiteralPath 'D:\\') { 'D:\\AgentKnowledge' } else { 'C:\\AgentKnowledge' }"
        discovery_line = "$GrowthSkillsRoot = Join-Path $env:USERPROFILE '.agents\\skills'"
        entry_line = "$SkillEntry = Join-Path $env:USERPROFILE '.agents\\skills\\personal-agent-growth'"
        assert root_line in install and discovery_line in install and entry_line in uninstall
        environment = json.loads(ps("environment", root_line + """
[ordered]@{
  powershell = $PSVersionTable.PSVersion.ToString()
  module_path = $env:PSModulePath
  hash_command_module = (Get-Command Get-FileHash).ModuleName
  os = (Get-CimInstance Win32_OperatingSystem).Caption
  selected_root = $GrowthRoot
  d_drive_present = (Test-Path -LiteralPath 'D:\\')
  volumes = @(Get-Volume | Select-Object DriveLetter, FileSystem, DriveType)
} | ConvertTo-Json -Depth 4 -Compress
"""))
        report["windows_environment"] = environment
        base = Path(tempfile.mkdtemp(prefix="growth-install-"))
        roots = [("default", Path(environment["selected_root"])),
                 ("custom", base / "Knowledge space 中文 & review")]
        for label, growth in roots:
            assert not growth.exists(), "Refuse to overwrite any existing knowledge root"
            discovery = base / label / "Discovery 中文 & entry" / ".agents/skills"
            skill = growth / "skills/personal-agent-growth"
            entry = discovery / "personal-agent-growth"
            release = growth / "downloads" / version
            source = install.replace(discovery_line, "$GrowthSkillsRoot = " + quoted(discovery))
            substitutions = ["GrowthSkillsRoot"]
            if label == "custom":
                source = source.replace(root_line, "$GrowthRoot = " + quoted(growth))
                substitutions.append("GrowthRoot")
            ps(label + "-install", source)
            manifest = json.loads((release / "manifest.json").read_text())
            expected_files = {p: v["sha256"] for p, v in manifest["files"].items()}
            assert expected_files and snapshot(skill) == expected_files
            assert os.path.samefile(entry / "SKILL.md", skill / "SKILL.md")
            ps(label + "-entry", "Get-Item -LiteralPath " + quoted(entry) +
               " | Select-Object LinkType, Target, FullName | ConvertTo-Json -Compress")
            task = growth / "tasks/shared-review"
            alias = base / label / "Second reader 中文"
            ps(label + "-memory-entry", "New-Item -ItemType Junction -Path " +
               quoted(alias) + " -Target " + quoted(growth / "tasks") + " | Out-Null")
            alternate = alias / "shared-review"

            def worker(phase, path, expected=0):
                try:
                    return run(label + "-memory-" + phase + ("-stale" if expected else ""),
                               [sys.executable, "-X", "utf8", str(SELF), "--memory-worker", phase,
                                "--task", str(path), "--skill", str(entry),
                                "--release", str(release)], expected)
                finally:
                    for stream in ("stdout", "stderr"):
                        raw = task / ("review." + stream)
                        if raw.exists():
                            shutil.copyfile(raw, output / (label + "-verifier." + stream))

            first = json.loads(worker("prepare", task))
            assert os.path.samefile(task / "state.json", alternate / "state.json")
            copied = base / label / "copied-state.json"
            shutil.copyfile(task / "state.json", copied)
            assert not os.path.samefile(task / "state.json", copied)
            if label == "custom":
                run("legacy-non-utf8-verifier",
                    [sys.executable, str(entry / "scripts/verify_handoff.py"),
                     "--archive", str(release / json.loads((release / "manifest.json").read_text(encoding="utf-8"))["archive"]["name"]),
                     "--manifest", str(release / "manifest.json")],
                    expected=1, contains="UnicodeEncodeError")
            reviewed = json.loads(worker("review", alternate))
            assert first["state"]["nonce"] == reviewed["state"]["nonce"]
            assert json.loads((task / "state.json").read_text(encoding="utf-8")) == reviewed["state"]
            before_stale = (task / "state.json").read_bytes()
            worker("review", alternate, expected=3)
            assert (task / "state.json").read_bytes() == before_stale
            finished = json.loads(worker("finish", task))
            assert finished["state"]["state_revision"] == 3
            assert finished["state"]["phase"] == "completed"
            assert len({first["pid"], reviewed["pid"], finished["pid"]}) == 3
            assert json.loads((alternate / "state.json").read_text(encoding="utf-8")) == finished["state"]
            write_json(output / (label + "-memory-final.json"), finished)
            shutil.copyfile(task / "review.stdout", output / (label + "-verifier.json"))
            saved = snapshot(growth)
            ps(label + "-repeat-install", source, expected=1, contains="already exists")
            assert snapshot(growth) == saved
            remove = uninstall.replace(entry_line, "$SkillEntry = " + quoted(entry))
            ps(label + "-uninstall", remove)
            assert not entry.exists() and not entry.is_symlink()
            assert snapshot(growth) == saved
            entry.mkdir()
            sentinel = entry / "keep.txt"
            sentinel.write_text("Preserve an ordinary directory", encoding="utf-8")
            ps(label + "-uninstall-ordinary-directory", remove, expected=1,
               contains="not the expected junction")
            assert sentinel.exists() and snapshot(growth) == saved
            report["cases"].append({
                "case": label, "status": "PASS", "root": str(growth),
                "command_substitutions": substitutions, "installed_files": len(expected_files),
                "package_checks": len(json.loads((task / "review.stdout").read_bytes())["checks"]), "skill_file_identity_shared": True,
                "memory_file_identity_shared": True, "copied_state_rejected_as_shared": True,
                "memory_revisions": [1, 2, 3], "worker_pids": [first["pid"], reviewed["pid"], finished["pid"]],
                "stale_revision_rejected_without_write": True,
                "repeat_install_preserved_files": True,
                "uninstall_preserved_skill_and_memory": True,
                "ordinary_directory_removal_rejected": True,
            })
            save()
        report["status"] = "PASS"
    except Exception as exc:
        report["status"] = "FAIL"
        report["error"] = str(exc)
        report["traceback"] = traceback.format_exc()
        raise
    finally:
        save()
        print(json.dumps(report, ensure_ascii=False, indent=2), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
