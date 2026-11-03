#!/usr/bin/env python3
# Copyright (C) 2026 KARMENLOOP Official Team
# SPDX-License-Identifier: AGPL-3.0-only
"""Run an explicitly requested real Codex trial with native events and clocks.

Uses the host's existing CLI authentication. Does not copy credentials, train a
model, modify global config, authenticate graders, or simulate Agent responses.
"""
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import queue
import shutil
import signal
import subprocess
import sys
import threading
import time

import blind_trials as blind
import capability_ledger as store
import task_costs


def cli_arguments(binary, config, workspace, final_path):
    store.require(config.get("training") is False and isinstance(config.get("model"), str), "Frozen model required")
    effort = config.get("reasoning_effort", "low")
    store.require(effort in ("minimal", "low", "medium", "high", "xhigh"), "Invalid reasoning effort")
    transport = config.get("transport", "default")
    store.require(transport in ("default", "openai-http"), "Invalid trial transport")
    args = [binary, "exec", "--json", "--ephemeral", "--ignore-user-config", "--sandbox", "workspace-write",
            "--skip-git-repo-check", "-m", config["model"], "-c", 'model_reasoning_effort="' + effort + '"',
            "-c", "skills.include_instructions=false", "-c", "skills.bundled.enabled=false",
            "--disable", "apps", "--disable", "plugins", "--disable", "memories", "--disable", "multi_agent"]
    if transport == "openai-http":
        args += ["-c", 'model_provider="trial-http"', "-c",
                 'model_providers.trial-http={name="OpenAI HTTP trial",wire_api="responses",requires_openai_auth=true,supports_websockets=false}']
    return args + ["-C", str(workspace), "-o", str(final_path), "-"]


def stop_owned(process):
    """Stop this invocation; this is not a proof that remote work was rolled back."""
    if process.poll() is not None:
        return
    try:
        if os.name == "posix": os.killpg(process.pid, signal.SIGTERM)
        else: process.terminate()
        process.wait(timeout=5)
    except (ProcessLookupError, subprocess.TimeoutExpired):
        if process.poll() is None:
            if os.name == "posix": os.killpg(process.pid, signal.SIGKILL)
            else: process.kill()
            process.wait(timeout=5)


def run(root, request_md):
    root = store.root_path(root)
    spec, _, spec_hash = store.read_md(Path(request_md))
    keys = {"id", "type", "task_id", "arm", "replicate", "attempt", "public_dir", "strategy_dir", "prompt",
            "evaluator", "model_config", "deadline_seconds", "max_commands", "codex_binary"}
    store.require(set(spec) == keys and spec["type"] == "agent-trial-request", "Invalid Agent trial request")
    for key in ("id", "task_id", "arm"): store.identifier(spec[key])
    for key in ("replicate", "attempt", "max_commands"):
        store.require(type(spec[key]) is int and spec[key] >= 1, "Invalid trial count")
    store.require(spec["max_commands"] <= 100, "Command cap exceeds trial limit")
    store.require(store.number(spec["deadline_seconds"]) and 0 < spec["deadline_seconds"] <= 3600,
                  "Invalid Agent deadline")
    store.artifacts(root, [spec["prompt"], spec["evaluator"]], True)
    source_inputs, source_strategy = blind.inventory(root, spec["public_dir"]), blind.inventory(root, spec["strategy_dir"])
    workspace = store.local(root, "agent-work/" + spec["id"])
    evidence = store.local(root, "agent-runs/" + spec["id"])
    store.require(not workspace.exists() and not evidence.exists(), "Trial attempt already exists")
    overall_start = time.monotonic(); started_at = datetime.now(timezone.utc).isoformat()
    workspace.mkdir(parents=True); evidence.mkdir(parents=True)
    shutil.copytree(store.local(root, spec["public_dir"]), workspace/"input")
    shutil.copytree(store.local(root, spec["strategy_dir"]), workspace/"skill")
    if (workspace/"skill/memory").is_dir():
        shutil.copytree(workspace/"skill/memory", workspace/"learning")
    output = workspace/"output"; output.mkdir()
    prompt = store.local(root, spec["prompt"]["path"]).read_text(encoding="utf-8")
    (evidence/"prompt.txt").write_text(prompt, encoding="utf-8")
    args = cli_arguments(spec["codex_binary"], spec["model_config"], workspace, evidence/"final.txt")
    agent_start = time.monotonic(); agent_offset = agent_start - overall_start
    messages = queue.Queue(); stop_reason = None; command_items = set()
    process = None; returncode = 127
    with (evidence/"stderr.txt").open("wb") as errors, (evidence/"events.jsonl").open("wb") as raw, (evidence/"timeline.jsonl").open("w", encoding="utf-8") as clocks:
        try:
            environment = dict(os.environ); environment["PYTHONDONTWRITEBYTECODE"] = "1"
            process = subprocess.Popen(args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=errors,
                                       start_new_session=os.name == "posix", env=environment)
            def reader():
                try:
                    for line in process.stdout:
                        messages.put((time.monotonic()-agent_start, line))
                finally: messages.put(None)
            threading.Thread(target=reader, daemon=True).start()
            process.stdin.write(prompt.encode("utf-8")); process.stdin.close()
            index = 0; done = False
            while not done:
                if time.monotonic()-agent_start > spec["deadline_seconds"]:
                    stop_reason = "deadline"; stop_owned(process)
                try: message = messages.get(timeout=.1)
                except queue.Empty:
                    if stop_reason: break
                    continue
                if message is None: break
                offset, line = message; raw.write(line); raw.flush()
                clocks.write(json.dumps({"event_index":index, "offset_seconds":offset})+"\n"); clocks.flush(); index += 1
                try: event = json.loads(line)
                except (ValueError, UnicodeError): continue
                item = event.get("item", {})
                if event.get("type") == "item.started" and isinstance(item, dict) and item.get("type") == "command_execution":
                    command_items.add(item.get("id"))
                    if len(command_items) > spec["max_commands"]:
                        stop_reason = "command_limit"; stop_owned(process)
            returncode = process.wait(timeout=10)
        except (OSError, subprocess.TimeoutExpired, BrokenPipeError) as error:
            if process is not None: stop_owned(process); returncode = process.returncode
            errors.write(("\nTrial controller: "+str(error)).encode("utf-8"))
    agent_end = time.monotonic()
    grade_start = time.monotonic()
    grade_args = [sys.executable, "-I", "-B", str(store.local(root, spec["evaluator"]["path"])),
                  "--output", str(output), "--public", str(store.local(root, spec["public_dir"])),
                  "--report", str(evidence/"grade.json")]
    try:
        graded = subprocess.run(grade_args, capture_output=True, timeout=30)
        (evidence/"grader.stdout").write_bytes(graded.stdout); (evidence/"grader.stderr").write_bytes(graded.stderr)
        grader_exit = graded.returncode
    except subprocess.TimeoutExpired as error:
        (evidence/"grader.stdout").write_bytes(error.stdout or b"")
        (evidence/"grader.stderr").write_bytes(error.stderr or b"")
        grader_exit = 124
    end = time.monotonic()
    phases = [{"phase":"preparation", "start":0, "end":agent_offset},
              {"phase":"agent", "start":agent_offset, "end":agent_end-overall_start},
              {"phase":"grading", "start":grade_start-overall_start, "end":end-overall_start}]
    measurement = {"elapsed_seconds":end-overall_start, "agent_start_offset":agent_offset,
                   "agent_elapsed_seconds":agent_end-agent_start, "exit_code":returncode,
                   "phase_spans":phases, "started_at":started_at,
                   "finished_at":datetime.now(timezone.utc).isoformat(), "stop_reason":stop_reason,
                   "scope":"Input/strategy assembly through actual Agent execution and independent artifact grading; normalization/publication overhead is reported separately"}
    (evidence/"measurement.json").write_text(json.dumps(measurement,indent=2)+"\n",encoding="utf-8")
    refs = {key:{"path":(evidence/name).relative_to(root).as_posix(), "sha256":store.sha((evidence/name).read_bytes())}
            for key,name in (("events","events.jsonl"),("timeline","timeline.jsonl"),("measurement","measurement.json"))}
    cost_spec = {"id":spec["id"], "type":"task-cost-request", "task_id":spec["task_id"], "arm":spec["arm"],
                 "replicate":spec["replicate"], "attempt":spec["attempt"], "model_config":spec["model_config"], **refs}
    cost_request = evidence/"cost-request.md"; cost_request.write_bytes(store.encode(cost_spec,"Actual host invocation. Billing and model-inference time may be unavailable."))
    try: cost_result = task_costs.record(root, cost_request); cost_error = None
    except (OSError, ValueError, KeyError, UnicodeError) as error: cost_result = None; cost_error = str(error)
    intact = (blind.inventory(root, spec["public_dir"]) == source_inputs and
              blind.inventory(root, spec["strategy_dir"]) == source_strategy and
              blind.inventory(workspace, "input") == source_inputs and blind.inventory(workspace,"skill") == source_strategy)
    result = {"id":spec["id"], "request_sha256":spec_hash, "command":args, "process_exit_code":returncode,
              "grader_command":grade_args, "grader_exit_code":grader_exit, "stop_reason":stop_reason,
              "inputs_and_strategy_unchanged":intact, "source_inputs":source_inputs, "source_strategy":source_strategy,
              "cost_record":None if cost_result is None else {"path":cost_result["path"],"sha256":cost_result["sha256"]},
              "cost_error":cost_error, "controller_total_seconds":time.monotonic()-overall_start,
              "scope":"One real CLI invocation; actual grading is separate from process exit and token collection"}
    store.publish(evidence/"runner.json", json.dumps(result,indent=2,ensure_ascii=False).encode())
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True); parser.add_argument("--request", type=Path, required=True)
    args = parser.parse_args()
    try: result = run(args.root,args.request)
    except (OSError,ValueError,KeyError,TypeError) as error:
        print(json.dumps({"status":"error","error":str(error)})); return 2
    print(json.dumps(result,ensure_ascii=False)); return 0


if __name__ == "__main__": sys.exit(main())
