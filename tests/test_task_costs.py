# Copyright (C) 2026 KARMENLOOP Official Team
# SPDX-License-Identifier: AGPL-3.0-only
import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import capability_ledger as store
import task_costs as costs


def events():
    return [{"type": "thread.started", "thread_id": "controlled-host-thread"},
            {"type": "turn.started"},
            {"type": "item.started", "item": {"id": "cmd-1", "type": "command_execution"}},
            {"type": "item.completed", "item": {"id": "cmd-1", "type": "command_execution", "exit_code": 1}},
            {"type": "turn.completed", "usage": {"input_tokens": 100, "cached_input_tokens": 70,
                                                  "output_tokens": 30, "reasoning_output_tokens": 20}}]


def measurement():
    return {"elapsed_seconds": 10, "agent_start_offset": 1, "agent_elapsed_seconds": 7,
            "exit_code": 0, "phase_spans": [{"phase": "preparation", "start": 0, "end": 1},
                                            {"phase": "agent", "start": 1, "end": 8},
                                            {"phase": "grading", "start": 8, "end": 10}]}


def timeline():
    return [{"event_index": i, "offset_seconds": offset} for i, offset in enumerate([0, .5, 2, 4, 7])]


def request_fixture(root):
    refs = {}
    for name, value in (("events", events()), ("timeline", timeline())):
        raw = "".join(json.dumps(row) + "\n" for row in value).encode()
        (root/(name+".jsonl")).write_bytes(raw)
        refs[name] = {"path": name+".jsonl", "sha256": store.sha(raw)}
    raw = json.dumps(measurement()).encode(); (root/"measurement.json").write_bytes(raw)
    refs["measurement"] = {"path": "measurement.json", "sha256": store.sha(raw)}
    request = {"id": "trial-01", "type": "task-cost-request", "task_id": "task-a", "arm": "baseline",
               "replicate": 1, "attempt": 1, "model_config": {"model": "controlled-fixture", "training": False, "temperature": 0.7}, **refs}
    file = root/"request.md"; file.write_bytes(store.encode(request, "Controlled parser fixture, not an Agent run."))
    return file


class CostTests(unittest.TestCase):
    def test_cached_and_reasoning_details_are_not_added_twice(self):
        result = costs.native_usage(events())
        self.assertEqual(result["total_tokens"], 130)
        self.assertEqual(result["cached_input_tokens"], 70)
        self.assertEqual(result["reasoning_output_tokens"], 20)
        self.assertIsNone(result["billed_usd"])

    def test_multiple_native_turns_sum_including_failed_tool_execution(self):
        values = events() + [events()[1], events()[-1]]
        self.assertEqual(costs.native_usage(values)["total_tokens"], 260)
        self.assertEqual(costs.native_usage(values)["command_items"], 1)

    def test_reconnects_make_coverage_partial_without_hiding_known_usage(self):
        values = events(); values.insert(2, {"type": "error", "message": "reconnecting"})
        result = costs.native_usage(values)
        self.assertEqual(result["total_tokens"], 130)
        self.assertEqual(result["coverage"], "partial_or_unavailable")

    def test_failed_or_missing_model_output_keeps_cost_unknown(self):
        for values in ([], events()[:2] + [{"type": "turn.failed"}], events()[:2]):
            result = costs.native_usage(values)
            self.assertIsNone(result["total_tokens"])
            self.assertIsNone(result["input_tokens"])
            self.assertIsNone(result["billed_usd"])

    def test_duplicate_result_does_not_double_count(self):
        with self.assertRaises(ValueError): costs.native_usage(events() + [events()[-1]])
        with self.assertRaises(ValueError): costs.native_usage(events()[:4] + [events()[3], events()[-1]])

    def test_missing_session_and_overlapping_turns_rejected(self):
        with self.assertRaises(ValueError): costs.native_usage(events()[1:])
        with self.assertRaises(ValueError): costs.native_usage(events()[:2] + [events()[1]])

    def test_impossible_native_counts_rejected(self):
        for change in ({"cached_input_tokens": 101}, {"input_tokens": True},
                       {"output_tokens": -1}, {"reasoning_output_tokens": 31},
                       {"input_tokens": 2**64}):
            values = events(); values[-1]["usage"].update(change)
            with self.assertRaises(ValueError): costs.native_usage(values)

    def test_overlap_is_union_and_not_inference_time(self):
        self.assertEqual(costs.union_seconds([(1, 5), (2, 3), (4, 7)]), 6)
        result = costs.timing_summary(events(), timeline(), measurement())
        self.assertEqual(result["complete_task_seconds"], 10)
        self.assertEqual(result["observed_command_union_seconds"], 2)
        self.assertEqual(result["unattributed_agent_seconds"], 5)
        self.assertIsNone(result["model_inference_seconds"])
        self.assertIsNone(result["phase_union_seconds"]["research"])

    def test_concurrent_tool_intervals_are_not_double_counted(self):
        values = [{"type": kind, "item": {"id": key, "type": "command_execution"}}
                  for kind, key in [("item.started", "a"), ("item.started", "b"),
                                    ("item.completed", "a"), ("item.completed", "b")]]
        clocks = [{"event_index": i, "offset_seconds": n} for i, n in enumerate([1, 2, 4, 5])]
        self.assertEqual(costs.timing_summary(values, clocks, measurement())["observed_command_union_seconds"], 4)

    def test_bad_clock_and_outside_phases_rejected(self):
        for mutate in (lambda c: c[2].update({"event_index": 8}),
                       lambda c: c[3].update({"offset_seconds": .1}),
                       lambda c: c[-1].update({"offset_seconds": 8})):
            clocks = timeline(); mutate(clocks)
            with self.assertRaises(ValueError): costs.timing_summary(events(), clocks, measurement())
        value = measurement(); value["phase_spans"][0]["end"] = 11
        with self.assertRaises(ValueError): costs.timing_summary(events(), timeline(), value)

    def test_malformed_or_duplicate_native_json_rejected(self):
        for raw in (b'{"type":"x","type":"turn.completed"}', b'{"x":NaN}', b'[]', b'\n'):
            with self.assertRaises(ValueError): costs.parse_jsonl(raw)

    def test_immutable_markdown_record_and_changed_source(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            file = request_fixture(root)
            result = costs.record(root, file)
            saved, _, _ = store.read_md(Path(result["path"]))
            self.assertEqual(saved["usage"]["total_tokens"], 130)
            before = Path(result["path"]).read_bytes()
            with self.assertRaises(FileExistsError): costs.record(root, file)
            self.assertEqual(Path(result["path"]).read_bytes(), before)
            (root/"events.jsonl").write_text("changed")
            with self.assertRaises(ValueError): costs.record(root, file)

    def test_late_encode_failure_leaves_no_poisoned_final_name(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary); file = request_fixture(root); valid = file.read_bytes()
            file.write_bytes(valid.replace(b'"temperature": 0.7', b'"temperature": 1e999'))
            with self.assertRaises(ValueError): costs.record(root, file)
            self.assertFalse((root/"trial-costs/trial-01.md").exists())
            file.write_bytes(valid)
            self.assertEqual(costs.record(root, file)["record"]["usage"]["total_tokens"], 130)

    def test_partial_write_is_not_published_and_retry_can_succeed(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary); file = request_fixture(root); original = Path.open
            class FailingWriter:
                def __init__(self, stream): self.stream = stream
                def __enter__(self): self.stream.__enter__(); return self
                def __exit__(self, *args): return self.stream.__exit__(*args)
                def write(self, raw):
                    self.stream.write(raw[:31]); self.stream.flush()
                    raise OSError("Controlled partial disk write")
            def fail(path, *args, **kwargs):
                stream = original(path, *args, **kwargs)
                return FailingWriter(stream) if path.parent.name == "trial-costs" and args and args[0] == "xb" else stream
            with patch.object(Path, "open", fail):
                with self.assertRaises(OSError): costs.record(root, file)
            self.assertFalse((root/"trial-costs/trial-01.md").exists())
            self.assertEqual(list((root/"trial-costs").glob(".pending-*")), [])
            self.assertEqual(costs.record(root, file)["record"]["usage"]["total_tokens"], 130)


if __name__ == "__main__": unittest.main()
