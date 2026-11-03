# Copyright (C) 2026 KARMENLOOP Official Team
# SPDX-License-Identifier: AGPL-3.0-only
"""Cross-module controlled fixtures, not Agent learning or field observations."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import adaptive_learning as loop
import capability_ledger as md
import experience_transfer as transfer


class AdaptiveTransferIntegrationTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.source = self.artifact("software-source.txt", "Controlled software lesson about measured stage latency")
        self.result = self.artifact("event-analysis.txt", "Controlled event fixture: unclear instructions cause repeat visits")
        self.experience = {"id": "stage-lesson", "type": "mechanism-experience", "source_task_id": "software-source",
                           "domain": "software", "problem_structure": ["sequential-stages"], "mechanisms": ["bottleneck"],
                           "required_conditions": {"stages-observable": True},
                           "exceptions": ["Throughput alone does not represent human experience."],
                           "intervention": "Measure waiting before changing capacity.",
                           "explanation": "One shared stage may account for waiting; cross-domain use remains a hypothesis.",
                           "validation": "hypothesis", "executor": "fixture-author", "reviewer": None,
                           "artifacts": [self.source]}
        transfer.add(self.root, self.write("source-card", self.experience))
        self.query = {"id": "event-query", "type": "transfer-query", "task_id": "unseen-event",
                      "domain": "unseen-event-planning", "problem_structure": ["sequential-stages"],
                      "mechanisms": ["bottleneck"], "facts": {"stages-observable": True, "unclear-guidance": True},
                      "keywords": ["waiting"]}
        self.request = {"id": "event-request", "type": "learning-request", "goal": "Analyze a controlled unfamiliar workflow",
                        "domain": "unseen-event-planning", "acceptance": ["fixture result verified"],
                        "budget_seconds": 300, "max_actions": 10, "allowed_actions": ["research", "experiment", "deliver"]}
        loop.init(self.root, "event-run", self.write("request", self.request))

    def write(self, name, metadata):
        path = self.root / (name + ".md")
        path.write_bytes(md.encode(metadata, "Controlled integration fixture, not an Agent transcript or field evidence."))
        return path

    def artifact(self, name, text):
        path = self.root / "evidence" / name
        path.parent.mkdir(exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return {"path": path.relative_to(self.root).as_posix(), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}

    def candidates(self, **changes):
        return transfer.retrieve(self.root, self.write("query", {**self.query, **changes}))["candidates"]

    def action(self, name="inspect-capacity", preconditions=None):
        return {"id": name, "kind": "experiment", "question_ids": ["cause"],
                "description": "Controlled diagnostic: " + name, "expected_information_gain": 0.8,
                "estimated_seconds": 1, "preconditions": preconditions or []}

    def proposal(self, name, revision, refs, actions=None):
        return {"id": name, "type": "learning-plan", "based_on_revision": revision,
                "unknowns": [{"id": "cause", "question": "Which stage or feedback explains the delay?", "importance": 1}],
                "actions": actions or [self.action()], "experience_refs": refs, "artifacts": []}

    def journal(self):
        return {path.name: path.read_bytes() for path in (self.root / "learning-runs/event-run/events").glob("*.md")}

    def record_harm(self):
        feedback = {"id": "negative-use", "type": "transfer-observation", "task_id": "unseen-event",
                    "domain": "unseen-event-planning", "conditions": {"stages-observable": True, "unclear-guidance": True},
                    "outcome": "harmful", "adaptation": "Tested the capacity explanation against controlled event data.",
                    "finding": "Repeat visits explain the delay; increased capacity does not address the observed cause.",
                    "executor": "fixture-executor", "reviewer": None, "artifacts": [self.result]}
        return transfer.observe(self.root, "stage-lesson", self.write("negative-use", feedback), 0)

    def test_novel_domain_feedback_invalidates_plan_and_alternative_resumes(self):
        candidate = self.candidates()[0]
        self.assertFalse(candidate["matches"]["domain_match"])
        self.assertTrue(candidate["eligible_for_probe"])
        initial_plan = self.proposal("initial-plan", 0, [candidate["snapshot_ref"]])
        planned = loop.plan(self.root, "event-run", self.write("initial-plan", initial_plan), 0)
        self.assertEqual(planned["recommended_action"], "inspect-capacity")
        before = self.journal()
        self.record_harm()
        with self.assertRaisesRegex(ValueError, "snapshot is stale"):
            loop.start(self.root, "event-run", "inspect-capacity", 1)
        self.assertEqual(self.journal(), before)
        refreshed = self.candidates()[0]
        self.assertFalse(refreshed["eligible_for_probe"])
        self.assertEqual(refreshed["relevant_feedback"][0]["outcome"], "harmful")
        self.assertEqual(refreshed["snapshot_ref"]["revision"], 1)
        updated = self.proposal("revised-plan", 1, [refreshed["snapshot_ref"]],
                                [self.action(preconditions=["Old hypothesis contradicted by matching feedback"]),
                                 self.action("inspect-guidance")])
        planned = loop.plan(self.root, "event-run", self.write("revised-plan", updated), 1)
        self.assertEqual(planned["recommended_action"], "inspect-guidance")
        started = loop.start(self.root, "event-run", "inspect-guidance", 2)

        # Run an actual subprocess over labeled fixture inputs. The executable is
        # deliberately a calculator, not a model Agent or a real event field test.
        data = self.root / "evidence/controlled-flow.json"
        data.write_text(json.dumps({"visits": [1, 3, 1, 2]}), encoding="utf-8")
        script = self.root / "evidence/calculate.py"
        script.write_text("import json, pathlib, sys\ndata=json.loads(pathlib.Path(sys.argv[1]).read_text())\n"
                          "print(json.dumps({'extra_visits':sum(v-1 for v in data['visits'])}))\n", encoding="utf-8")
        command = [sys.executable, "-B", str(script), str(data)]
        started_at = time.perf_counter()
        execution = subprocess.run(command, capture_output=True, text=True, timeout=15)
        elapsed_seconds = time.perf_counter() - started_at
        self.assertEqual(execution.returncode, 0, execution.stderr)
        self.assertEqual(json.loads(execution.stdout), {"extra_visits": 3})
        receipt = self.artifact("calculator-receipt.json", json.dumps({"argv": command, "exit_code": execution.returncode,
                                "stdout": execution.stdout, "stderr": execution.stderr,
                                "elapsed_seconds": elapsed_seconds, "scope": "controlled fixture calculator"}))
        execution_inputs = [{"path": path.relative_to(self.root).as_posix(),
                             "sha256": hashlib.sha256(path.read_bytes()).hexdigest()} for path in (data, script)]
        observation = {"id": "guidance-result", "type": "learning-observation",
                       "start_id": started["pending"]["start_id"], "action_id": "inspect-guidance", "outcome": "progress",
                       "finding": "Controlled input contains three repeat visits.",
                       "hypothesis_change": "Inspect guidance rather than increasing capacity in this fixture.",
                       "resolved_questions": ["cause"], "artifacts": [receipt, *execution_inputs], "executor": "fixture-executor",
                       "reviewer": None, "cost": {"tokens": None, "usd": None}, "acceptance_checks": {}}
        result = loop.observe(self.root, "event-run", self.write("guidance-result", observation), 3)
        self.assertEqual(result["revision"], 4)
        self.assertEqual(result["unresolved_questions"], [])
        self.assertEqual(result["ranked_actions"], [])
        self.assertIsNone(result["pending"])
        resumed = subprocess.run([sys.executable, "-B", str(Path(loop.__file__).resolve()), "status",
                                  "--root", str(self.root), "--id", "event-run"], capture_output=True, text=True, timeout=15)
        self.assertEqual(resumed.returncode, 0, resumed.stderr)
        state = json.loads(resumed.stdout)
        self.assertEqual(state["revision"], 4)
        self.assertEqual(state["last_observation"]["finding"], observation["finding"])
        self.assertEqual(state["actions_started"], 1)
        self.assertFalse(state["scheduler_registered"])

    def test_unrelated_same_domain_card_is_not_selected_or_bound(self):
        other = {**self.experience, "id": "unrelated", "domain": self.query["domain"],
                 "problem_structure": ["narrative-arc"], "mechanisms": ["plot-resolution"]}
        transfer.add(self.root, self.write("unrelated", other))
        candidates = self.candidates()
        self.assertEqual([item["id"] for item in candidates], ["stage-lesson"])
        plan = self.proposal("cross-only", 0, [candidates[0]["snapshot_ref"]])
        loop.plan(self.root, "event-run", self.write("cross-only", plan), 0)
        stored, _, _ = md.read_md(self.root / "learning-runs/event-run/events/000001.md")
        self.assertEqual(len(stored["data"]["experience_refs"]), 1)
        self.assertIn("stage-lesson", stored["data"]["experience_refs"][0]["path"])

    def test_invalid_external_or_forged_snapshot_rejected_without_journal_write(self):
        original = self.candidates()[0]["snapshot_ref"]
        malformed = [
            {**original, "path": "../outside.md"},
            {**original, "path": "https://example.invalid/experience.md"},
            {**original, "head_sha256": "0" * 64},
            {**original, "revision": 99},
        ]
        for index, ref in enumerate(malformed):
            with self.subTest(ref=ref):
                plan = self.proposal("invalid-" + str(index), 0, [ref])
                with self.assertRaises(ValueError):
                    loop.plan(self.root, "event-run", self.write("invalid", plan), 0)
                self.assertEqual(self.journal(), {})

    def test_unknown_condition_requires_host_plan_to_resolve_it(self):
        candidate = self.candidates(facts={})[0]
        self.assertFalse(candidate["eligible_for_probe"])
        self.assertEqual(candidate["unresolved_conditions"], ["stages-observable"])
        plan = self.proposal("conditions-first", 0, [candidate["snapshot_ref"]],
                             [self.action(preconditions=["Verify whether stages are observable"]),
                              {**self.action("observe-stages"), "kind": "research"}])
        result = loop.plan(self.root, "event-run", self.write("conditions-first", plan), 0)
        self.assertEqual(result["recommended_action"], "observe-stages")
        before = self.journal()
        with self.assertRaisesRegex(ValueError, "preconditions"):
            loop.start(self.root, "event-run", "inspect-capacity", 1)
        self.assertEqual(self.journal(), before)

    def test_source_evidence_drift_blocks_bound_action_before_execution(self):
        ref = self.candidates()[0]["snapshot_ref"]
        loop.plan(self.root, "event-run", self.write("plan", self.proposal("plan", 0, [ref])), 0)
        before = self.journal()
        (self.root / self.source["path"]).write_text("Changed controlled evidence", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "Artifact changed"):
            loop.start(self.root, "event-run", "inspect-capacity", 1)
        self.assertEqual(self.journal(), before)


if __name__ == "__main__":
    unittest.main()
