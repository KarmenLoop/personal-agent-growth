# Copyright (C) 2026 KARMENLOOP Official Team
# SPDX-License-Identifier: AGPL-3.0-only
"""Synthetic gate tests. These fixtures do not constitute Agent execution evidence."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

SPEC = importlib.util.spec_from_file_location(
    "gate", Path(__file__).resolve().parents[1] / "scripts/compare_trials.py")
gate = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(gate)


class TrialTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "experiment"
        self.root.mkdir()
        self.library = Path(self.temp.name) / "library"
        self.plan = {"experiment_id": "test-one", "task_id": "task-one", "domain": "archive",
                     "model_config": {"model": "synthetic-test", "training": False},
                     "quality_checks": ["identity", "usable"], "metric": "processes",
                     "min_relative_gain": 0.2, "samples": 1, "max_candidate_cost": 3,
                     "inputs": ["inputs/item.txt"], "evaluator": "evaluator.py"}
        self.save("plan.json", self.plan)
        self.put("inputs/item.txt", "controlled input")
        self.put("evaluator.py", "# synthetic fixed evaluator")
        for arm in gate.ARMS:
            self.put("arms/" + arm + "/prompt.md", arm)
        for arm in gate.ARMS[1:]:
            self.put("proposals/" + arm + ".md", "predeclared " + arm)
        self.seal = gate.freeze(self.root)["frozen_sha256"]
        self.evaluation = {"frozen_sha256": self.seal, "reviewer": "independent-test-reviewer",
                           "optimization_cost": None, "arms": {}}
        for arm in gate.ARMS:
            prefix = "runs/" + arm + "/"
            for name in ("trace.jsonl", "host.txt", "artifact.txt", "review.txt"):
                self.put(prefix + name, "synthetic fixture " + name)
            run = {"model_config": self.plan["model_config"], "frozen_sha256": self.seal,
                   "executor": {"kind": "agent", "host": "SYNTHETIC TEST ONLY", "session_id": arm},
                   "trace": prefix + "trace.jsonl", "host_receipt": prefix + "host.txt",
                   "artifacts": [prefix + "artifact.txt"]}
            self.save(prefix + "run.json", run)
            paths = [run["trace"], run["host_receipt"], *run["artifacts"]]
            self.evaluation["arms"][arm] = {
                "run_sha256": gate.file_hash(self.root, prefix + "run.json"),
                "evidence_sha256": {p: gate.file_hash(self.root, p) for p in paths},
                "checks": {"identity": True, "usable": True},
                "metric_samples": [1 if arm == "domain" else 3],
                "evidence": prefix + "review.txt"}
        self.save("evaluation.json", self.evaluation)

    def put(self, path, value):
        target = self.root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(value, encoding="utf-8")

    def save(self, path, value):
        self.put(path, json.dumps(value))

    def test_narrow_gain_and_no_overall_claim(self):
        report = gate.compare(self.root)
        self.assertEqual(report["eligible"], ["domain"])
        self.assertEqual(report["recommendation"], "domain")
        self.assertEqual(report["arms"]["general"]["reason"], "no_demonstrated_gain")
        self.assertIsNone(report["optimization_cost"])

    def test_missing_second_trial_blocks_comparison(self):
        (self.root / "runs/domain/run.json").unlink()
        with self.assertRaises(OSError): gate.compare(self.root)

    def test_frozen_drift_blocks(self):
        for path in ("inputs/item.txt", "arms/domain/prompt.md", "evaluator.py", "proposals/general.md"):
            with self.subTest(path=path):
                original = (self.root / path).read_bytes()
                self.put(path, "changed")
                with self.assertRaisesRegex(ValueError, "drift"): gate.compare(self.root)
                (self.root / path).write_bytes(original)

    def test_changed_raw_receipt_blocks(self):
        self.put("runs/domain/host.txt", "replacement")
        with self.assertRaisesRegex(ValueError, "evidence changed"): gate.compare(self.root)

    def test_model_drift_blocks(self):
        path = "runs/domain/run.json"
        run = gate.read_json(self.root / path)
        run["model_config"] = {"model": "different", "training": False}
        self.save(path, run)
        with self.assertRaisesRegex(ValueError, "Model configuration drift"): gate.compare(self.root)

    def test_cheap_but_bad_candidate_is_rejected(self):
        self.evaluation["arms"]["domain"]["checks"]["usable"] = False
        self.save("evaluation.json", self.evaluation)
        self.assertEqual(gate.compare(self.root)["eligible"], [])
        with self.assertRaisesRegex(ValueError, "unqualified"):
            gate.record(self.root, self.library, 0, "domain")

    def test_unknown_quality_and_nonfinite_metrics(self):
        self.evaluation["arms"]["domain"]["checks"]["usable"] = None
        self.save("evaluation.json", self.evaluation)
        self.assertEqual(gate.compare(self.root)["eligible"], [])
        for value in (True, float("nan"), -1):
            self.evaluation["arms"]["domain"]["metric_samples"] = [value]
            self.save("evaluation.json", self.evaluation)
            with self.assertRaises(ValueError): gate.compare(self.root)

    def test_domain_adoption_and_next_load(self):
        selected = gate.record(self.root, self.library, 0, "domain")
        self.assertEqual(selected["revision"], 1)
        active = self.library / selected["active"]["path"]
        self.assertEqual((active / "prompt.md").read_text(), "domain")
        self.assertIsNone(gate.select(self.library, "other-domain")["active"])
        with self.assertRaisesRegex(ValueError, "Stale library revision"):
            gate.record(self.root, self.library, 0, "domain")
        self.assertEqual(gate.load_library(self.library)["revision"], 1)
        (active / "prompt.md").write_text("modified outside adoption")
        with self.assertRaisesRegex(ValueError, "snapshot has changed"):
            gate.select(self.library, "archive")

    def test_modified_experience_is_not_loaded_or_used_for_rollback(self):
        selected = gate.record(self.root, self.library, 0, "domain")
        card = self.library / selected["experiences"][0]["path"]
        card.write_text("replaced lesson")
        with self.assertRaisesRegex(ValueError, "Experience card has changed"):
            gate.select(self.library, "archive")
        with self.assertRaisesRegex(ValueError, "Experience card has changed"):
            gate.rollback(self.library, "test-one", 1, "Controlled corruption check")

    def test_reuse_observation_is_indexed_without_replacing_active_version(self):
        selected = gate.record(self.root, self.library, 0, "domain")
        review = {"observation_id": "reuse-one", "domain": "archive",
                  "active_sha256": selected["active"]["sha256"], "lesson": "Synthetic fixture lesson",
                  "limitations": "Not an Agent run", "next_probe": "Try a new actual input",
                  "evidence": {str(self.root / "runs/domain/artifact.txt"):
                               gate.file_hash(self.root, "runs/domain/artifact.txt")}}
        self.save("reuse.json", review)
        observed = gate.observe(self.library, self.root / "reuse.json", 1)
        self.assertEqual(observed["revision"], 2)
        self.assertEqual(observed["active"], selected["active"])
        self.assertEqual(len(gate.select(self.library, "archive")["observations"]), 1)
        with self.assertRaisesRegex(ValueError, "Stale library revision"):
            gate.observe(self.library, self.root / "reuse.json", 1)
        with self.assertRaisesRegex(ValueError, "already recorded"):
            gate.observe(self.library, self.root / "reuse.json", 2)
        (self.root / "runs/domain/artifact.txt").write_text("changed")
        with self.assertRaisesRegex(ValueError, "evidence missing or changed"):
            gate.observe(self.library, self.root / "reuse.json", 2)

    def test_review_for_another_snapshot_is_not_accepted(self):
        gate.record(self.root, self.library, 0, "domain")
        self.save("reuse.json", {"observation_id": "wrong-profile", "domain": "archive",
            "active_sha256": "wrong", "lesson": "Synthetic", "limitations": "Fixture",
            "next_probe": "Recheck", "evidence": {str(self.root / "runs/domain/artifact.txt"):
                                                   gate.file_hash(self.root, "runs/domain/artifact.txt")}})
        with self.assertRaisesRegex(ValueError, "current active snapshot"):
            gate.observe(self.library, self.root / "reuse.json", 1)

    def test_no_gain_is_still_retained_as_experience(self):
        self.evaluation["arms"]["domain"]["metric_samples"] = [3]
        self.save("evaluation.json", self.evaluation)
        selected = gate.record(self.root, self.library, 0)
        self.assertIsNone(selected["active"])
        self.assertEqual(len(selected["experiences"]), 1)
        with self.assertRaisesRegex(ValueError, "already recorded"):
            gate.record(self.root, self.library, 1)

    def test_traversal_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "Unsafe relative path"):
            gate.local(self.root, "../outside")

    def test_unknown_baseline_does_not_become_a_proven_failure(self):
        self.evaluation["arms"]["baseline"]["checks"]["usable"] = None
        self.save("evaluation.json", self.evaluation)
        result = gate.compare(self.root)
        self.assertEqual(result["eligible"], [])
        self.assertEqual(result["arms"]["domain"]["reason"], "baseline_quality_unknown")

    def test_first_adoption_preserves_a_real_rollback_snapshot(self):
        gate.record(self.root, self.library, 0, "domain")
        restored = gate.rollback(self.library, "test-one", 1, "Controlled rollback check")
        self.assertEqual(restored["revision"], 2)
        self.assertEqual((self.library / restored["active"]["path"] / "prompt.md").read_text(), "baseline")
        self.assertTrue((self.library / "rollbacks/2.json").is_file())
        with self.assertRaisesRegex(ValueError, "later adoption"):
            gate.rollback(self.library, "test-one", 2, "Repeated stale rollback")

    def test_freeze_after_execution_and_refreeze_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "Already frozen"): gate.freeze(self.root)
        (self.root / "frozen.json").unlink()
        with self.assertRaisesRegex(ValueError, "after run records"): gate.freeze(self.root)

    def prepare_composition(self):
        self.put("arms/composed/prompt.md", "composed tested successor")
        self.put("compose-evaluator.py", "# Same fixed criteria; composed routing only")
        self.save("compose-plan.json", {"evaluator": "compose-evaluator.py", "decisions": [
            {"component": "prompt.md", "source": "domain", "action": "rewrite",
             "reason": "Synthetic test decision", "evidence": ["runs/domain/review.txt"]}]})
        seal = gate.freeze_compose(self.root)["composition_sha256"]
        prefix = "runs/composed/"
        for name in ("trace.jsonl", "host.txt", "artifact.txt", "review.txt"):
            self.put(prefix + name, "synthetic composition fixture")
        run = {"model_config": self.plan["model_config"], "frozen_sha256": self.seal,
               "composition_sha256": seal,
               "executor": {"kind": "agent", "host": "SYNTHETIC ONLY", "session_id": "composed"},
               "trace": prefix + "trace.jsonl", "host_receipt": prefix + "host.txt",
               "artifacts": [prefix + "artifact.txt"]}
        self.save(prefix + "run.json", run)
        row = {"run_sha256": gate.file_hash(self.root, prefix + "run.json"),
               "evidence_sha256": {p: gate.file_hash(self.root, p) for p in
                                   [run["trace"], run["host_receipt"], *run["artifacts"]]},
               "checks": {"identity": True, "usable": True}, "metric_samples": [1],
               "evidence": prefix + "review.txt"}
        self.compose_evaluation = {"frozen_sha256": self.seal, "composition_sha256": seal,
                                   "reviewer": "independent-test-reviewer", "arms": {"composed": row}}
        self.save("composition-evaluation.json", self.compose_evaluation)

    def test_composition_requires_its_own_run_and_can_be_adopted(self):
        self.prepare_composition()
        report = gate.compare(self.root)
        self.assertEqual(report["recommendation"], "composed")
        selected = gate.record(self.root, self.library, 0, "composed")
        self.assertEqual((self.library / selected["active"]["path"] / "prompt.md").read_text(),
                         "composed tested successor")
        (self.root / "runs/composed/run.json").unlink()
        with self.assertRaises(OSError): gate.compare(self.root)

    def test_composition_must_not_regress_against_best_probe(self):
        self.prepare_composition()
        self.compose_evaluation["arms"]["composed"]["metric_samples"] = [2]
        self.save("composition-evaluation.json", self.compose_evaluation)
        result = gate.compare(self.root)
        self.assertEqual(result["recommendation"], "domain")
        self.assertEqual(result["arms"]["composed"]["reason"], "composition_regressed")

    def test_composition_drift_and_unbound_execution_are_rejected(self):
        self.prepare_composition()
        self.put("arms/composed/prompt.md", "unprobed modification")
        with self.assertRaisesRegex(ValueError, "drift"): gate.compare(self.root)
        self.put("arms/composed/prompt.md", "composed tested successor")
        self.compose_evaluation["composition_sha256"] = "wrong"
        self.save("composition-evaluation.json", self.compose_evaluation)
        with self.assertRaisesRegex(ValueError, "not bound"): gate.compare(self.root)

    def test_portfolio_requires_transfer_regression_and_domain_coverage(self):
        self.plan.update(layer="harnessing", promotion="cross-domain")
        self.save("plan.json", self.plan)
        with self.assertRaisesRegex(ValueError, "task portfolio"): gate.inventory(self.root)
        self.plan["portfolio"] = [{"task_id": "one", "domain": "archive", "role": "transfer"},
                                  {"task_id": "two", "domain": "archive", "role": "regression"}]
        self.save("plan.json", self.plan)
        with self.assertRaisesRegex(ValueError, "two domains"): gate.inventory(self.root)
        self.plan["portfolio"][1]["domain"] = "documents"
        self.save("plan.json", self.plan)
        self.assertIn("snapshots", gate.inventory(self.root))

    def enable_resource_guards(self):
        # Rebuild a synthetic seal; this helper never edits a real experiment.
        self.plan["performance_guards"] = {"archive_tokens": 0.10, "analysis_tokens": 0.10}
        self.save("plan.json", self.plan)
        self.save("frozen.json", {"schema": 1, "inventory": gate.inventory(self.root)})
        self.seal = gate.file_hash(self.root, "frozen.json")
        self.evaluation["frozen_sha256"] = self.seal
        for arm in gate.ARMS:
            path = "runs/" + arm + "/run.json"
            run = gate.read_json(self.root / path)
            run["frozen_sha256"] = self.seal
            self.save(path, run)
            row = self.evaluation["arms"][arm]
            row["run_sha256"] = gate.file_hash(self.root, path)
            row["guard_samples"] = {"archive_tokens": [100], "analysis_tokens": [100]}
        self.save("evaluation.json", self.evaluation)

    def test_total_gain_cannot_hide_one_task_regression(self):
        self.enable_resource_guards()
        self.evaluation["arms"]["domain"]["guard_samples"]["archive_tokens"] = [111]
        self.save("evaluation.json", self.evaluation)
        result = gate.compare(self.root)
        self.assertEqual(result["eligible"], [])
        self.assertEqual(result["arms"]["domain"]["reason"], "whole_task_resource_regression")
        self.assertEqual(result["arms"]["domain"]["guard_failures"], ["archive_tokens"])

    def test_unknown_guard_is_not_zero_cost(self):
        self.enable_resource_guards()
        self.evaluation["arms"]["domain"]["guard_samples"]["archive_tokens"] = [None]
        self.save("evaluation.json", self.evaluation)
        report = gate.compare(self.root)
        self.assertEqual(report["eligible"], [])
        self.assertEqual(report["arms"]["domain"]["reason"], "resource_evidence_unknown")
        self.assertIsNone(report["arms"]["domain"]["guard_medians"]["archive_tokens"])
        for value in (True, float("nan"), -1):
            self.evaluation["arms"]["domain"]["guard_samples"]["archive_tokens"] = [value]
            self.save("evaluation.json", self.evaluation)
            with self.assertRaisesRegex(ValueError, "Invalid measured guard"):
                gate.compare(self.root)

    def test_composition_also_checks_each_task(self):
        self.enable_resource_guards()
        self.prepare_composition()
        row = self.compose_evaluation["arms"]["composed"]
        row["guard_samples"] = {"archive_tokens": [100], "analysis_tokens": [120]}
        self.save("composition-evaluation.json", self.compose_evaluation)
        result = gate.compare(self.root)
        self.assertEqual(result["recommendation"], "domain")
        self.assertEqual(result["arms"]["composed"]["reason"], "whole_task_resource_regression")

    def test_unknown_candidate_does_not_block_an_independently_measured_candidate(self):
        self.enable_resource_guards()
        self.evaluation["arms"]["general"]["guard_samples"]["archive_tokens"] = [None]
        self.save("evaluation.json", self.evaluation)
        result = gate.compare(self.root)
        self.assertEqual(result["eligible"], ["domain"])
        self.assertEqual(result["arms"]["general"]["reason"], "resource_evidence_unknown")
        self.evaluation["arms"]["baseline"]["guard_samples"]["archive_tokens"] = [None]
        self.save("evaluation.json", self.evaluation)
        self.assertEqual(gate.compare(self.root)["eligible"], [])

    def test_timing_guard_requires_repetition_even_with_token_primary(self):
        self.plan["metric"] = "total_tokens"
        self.plan["performance_guards"] = {"analysis_wall_seconds": 0.20}
        self.save("plan.json", self.plan)
        with self.assertRaisesRegex(ValueError, "three samples"):
            gate.inventory(self.root)


if __name__ == "__main__":
    unittest.main()
