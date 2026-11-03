# Copyright (C) 2026 KARMENLOOP Official Team
# SPDX-License-Identifier: AGPL-3.0-only
"""Controlled fixtures for open-domain retrieval and append-only use evidence."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import capability_ledger as store
import experience_transfer as transfer
from test_causal_models import graph as causal_graph, mapping as causal_mapping


class ExperienceTransferTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.source = self.artifact("source.txt", "Controlled software trace: shared stage and waiting")
        self.result = self.artifact("event.txt", "Controlled event analysis: signage caused repeat visits")

    def artifact(self, name, text):
        path = self.root / "evidence" / name
        path.parent.mkdir(exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return {"path": path.relative_to(self.root).as_posix(), "sha256": store.sha(path.read_bytes())}

    def md(self, name, data, body="Controlled fixture, not actual Agent or real-world evidence."):
        path = self.root / name
        path.write_bytes(store.encode(data, body))
        return path

    def experience(self, name="stages", **changes):
        return {"id": name, "type": "mechanism-experience", "source_task_id": "software-01",
                "domain": "software", "problem_structure": ["sequential-stages", "shared-resource"],
                "mechanisms": ["bottleneck"], "required_conditions": {"stage-observable": True},
                "exceptions": ["Human experience is not reducible to throughput."],
                "intervention": "Measure stage waits before increasing capacity.",
                "explanation": "A shared stage may accumulate waiting; cross-domain application is a hypothesis.",
                "validation": "hypothesis", "executor": "fixture/author", "reviewer": None,
                "artifacts": [self.source], **changes}

    def query(self, **changes):
        return {"id": "query-event", "type": "transfer-query", "task_id": "event-01", "domain": "events",
                "problem_structure": ["sequential-stages"], "mechanisms": ["bottleneck"],
                "facts": {"stage-observable": True}, "keywords": ["waiting"], **changes}

    def observation(self, name="event-use", **changes):
        return {"id": name, "type": "transfer-observation", "task_id": "event-01", "domain": "events",
                "conditions": {"stage-observable": True, "signage-unclear": True}, "outcome": "harmful",
                "adaptation": "Tested the stage model on event inputs.",
                "finding": "Repeat visits, not service capacity, explained the observed delay.",
                "executor": "fixture/learner", "reviewer": None, "artifacts": [self.result], **changes}

    def add(self, name="stages", **changes):
        return transfer.add(self.root, self.md(name + ".md", self.experience(name, **changes)))

    def retrieve(self, **changes):
        return transfer.retrieve(self.root, self.md("query.md", self.query(**changes)))

    def observe(self, name="event-use", revision=0, **changes):
        return transfer.observe(self.root, "stages", self.md(name + ".md", self.observation(name, **changes)), revision)

    def test_new_domain_retrieves_mechanism_and_actual_text(self):
        added = self.add()
        result = self.retrieve()
        self.assertEqual(result["errors"], [])
        candidate = result["candidates"][0]
        self.assertFalse(candidate["matches"]["domain_match"])
        self.assertEqual(candidate["matches"]["mechanisms"], ["bottleneck"])
        self.assertTrue(candidate["eligible_for_probe"])
        self.assertTrue(candidate["adaptation_required"])
        self.assertIn("Human experience", candidate["experience"]["exceptions"][0])
        self.assertEqual(candidate["snapshot_ref"], added["snapshot_ref"])
        self.assertEqual(candidate["snapshot_ref"]["revision"], 0)
        self.assertEqual(candidate["snapshot_ref"]["head_sha256"], candidate["snapshot_ref"]["sha256"])

    def test_renamed_causal_structure_can_retrieve_without_overlapping_tags(self):
        self.add(causal_model=causal_graph())
        result = self.retrieve(problem_structure=["fresh-context"], mechanisms=["different-words"],
                               causal_context=causal_graph("conditions", "recommendation"),
                               causal_mappings={"stages": causal_mapping()})
        candidate = result["candidates"][0]
        self.assertTrue(candidate["causal_match"]["compatible"])
        self.assertTrue(candidate["eligible_for_probe"])
        self.assertEqual(candidate["matches"]["problem_structure"], [])
        self.assertEqual(candidate["matches"]["mechanisms"], [])

    def test_causal_analogy_still_requires_conditions_and_valid_direction(self):
        self.add(causal_model=causal_graph())
        query = {"causal_context": causal_graph("conditions", "recommendation"),
                 "causal_mappings": {"stages": causal_mapping()}}
        self.assertFalse(self.retrieve(facts={"stage-observable": False}, **query)["candidates"][0]["eligible_for_probe"])
        query["causal_context"]["relations"][0].update({"from":"recommendation", "to":"conditions"})
        candidate = self.retrieve(**query)["candidates"][0]
        self.assertFalse(candidate["eligible_for_probe"])
        self.assertIn("directed_relations_not_preserved", candidate["causal_match"]["issues"])

    def test_source_model_requires_mapping_and_legacy_explicit_mapping_cannot_bypass(self):
        self.add(causal_model=causal_graph())
        self.assertFalse(self.retrieve()["candidates"][0]["eligible_for_probe"])
        self.add("legacy")
        result = self.retrieve(causal_context=causal_graph("conditions", "recommendation"),
                               causal_mappings={"legacy": causal_mapping()})
        candidate = next(row for row in result["candidates"] if row["id"] == "legacy")
        self.assertFalse(candidate["eligible_for_probe"])
        self.assertIn("source_causal_model_missing", candidate["causal_match"]["issues"])

    def test_domain_or_keywords_alone_do_not_admit(self):
        self.add()
        result = self.retrieve(domain="software", problem_structure=["narrative-arc"], mechanisms=["attention"])
        self.assertEqual(result["candidates"], [])
        self.assertEqual(result["matched_count"], 0)

    def test_unknown_and_contradictory_conditions_block_probe(self):
        self.add()
        candidate = self.retrieve(facts={})["candidates"][0]
        self.assertEqual(candidate["unresolved_conditions"], ["stage-observable"])
        self.assertFalse(candidate["eligible_for_probe"])
        candidate = self.retrieve(facts={"stage-observable": False})["candidates"][0]
        self.assertEqual(candidate["conflicting_conditions"], ["stage-observable"])
        self.assertFalse(candidate["eligible_for_probe"])

    def test_false_required_condition_is_not_treated_as_missing(self):
        self.add(required_conditions={"irreversible": False})
        candidate = self.retrieve(facts={"irreversible": False})["candidates"][0]
        self.assertTrue(candidate["eligible_for_probe"])
        candidate = self.retrieve(facts={"irreversible": True})["candidates"][0]
        self.assertEqual(candidate["conflicting_conditions"], ["irreversible"])

    def test_harmful_observation_changes_same_context_and_snapshot(self):
        original = self.add()
        query_facts = {"stage-observable": True, "signage-unclear": True}
        before = self.retrieve(facts=query_facts)["candidates"][0]
        observed = self.observe()
        after = self.retrieve(facts=query_facts)["candidates"][0]
        self.assertLess(after["score"], before["score"])
        self.assertFalse(after["eligible_for_probe"])
        self.assertEqual(after["relevant_feedback"][0]["context_match"], "matched")
        self.assertEqual(after["relevant_feedback"][0]["target_scope"], "same-domain")
        self.assertEqual(after["relevant_feedback"][0]["source_domain"], "events")
        self.assertFalse(after["counterexample_review_required"])
        self.assertEqual(observed["revision"], 1)
        with self.assertRaisesRegex(ValueError, "snapshot is stale"):
            transfer.verify_ref(self.root, original["snapshot_ref"])
        transfer.verify_ref(self.root, observed["snapshot_ref"])

    def test_missing_feedback_condition_does_not_hide_possible_harm(self):
        self.add()
        before = self.retrieve()["candidates"][0]
        self.observe()
        after = self.retrieve()["candidates"][0]
        self.assertEqual(after["score"], before["score"])
        self.assertFalse(after["eligible_for_probe"])
        self.assertEqual(after["relevant_feedback"][0]["unresolved_conditions"], ["signage-unclear"])
        self.assertEqual(after["relevant_feedback"][0]["target_scope"], "same-domain")

    def test_cross_domain_counterexample_visible_without_proven_harm_penalty(self):
        self.add()
        query_facts = {"stage-observable": True, "signage-unclear": True}
        before = self.retrieve(domain="manufacturing", facts=query_facts)["candidates"][0]
        observed = self.observe()
        after = self.retrieve(domain="manufacturing", facts=query_facts)["candidates"][0]
        self.assertEqual(len(after["relevant_feedback"]), 1)
        caution = after["relevant_feedback"][0]
        self.assertEqual(caution["source_domain"], "events")
        self.assertEqual(caution["target_domain"], "manufacturing")
        self.assertEqual(caution["target_scope"], "cross-domain-unverified")
        self.assertEqual(caution["context_match"], "matched")
        self.assertEqual(caution["outcome"], "harmful")
        self.assertEqual(caution["adaptation"], self.observation()["adaptation"])
        self.assertEqual(caution["ref"], observed["observations"][0]["ref"])
        self.assertEqual(after["score"], before["score"])
        self.assertTrue(after["eligible_for_probe"])
        self.assertTrue(after["counterexample_review_required"])

    def test_cross_domain_unknown_conditions_remain_explicit_caution(self):
        self.add(); self.observe()
        after = self.retrieve(domain="manufacturing")["candidates"][0]
        self.assertEqual(len(after["relevant_feedback"]), 1)
        caution = after["relevant_feedback"][0]
        self.assertEqual(caution["target_scope"], "cross-domain-unverified")
        self.assertEqual(caution["context_match"], "unknown")
        self.assertEqual(caution["unresolved_conditions"], ["signage-unclear"])
        self.assertEqual(after["score"], after["relevance_before_feedback"])
        self.assertTrue(after["eligible_for_probe"])
        self.assertTrue(after["counterexample_review_required"])

    def test_contradicting_feedback_conditions_do_not_poison_same_or_foreign_domain(self):
        self.add(); self.observe()
        for domain in ("events", "manufacturing"):
            with self.subTest(domain=domain):
                candidate = self.retrieve(domain=domain, facts={"stage-observable": True, "signage-unclear": False})["candidates"][0]
                self.assertEqual(candidate["relevant_feedback"], [])
                self.assertTrue(candidate["eligible_for_probe"])
                self.assertFalse(candidate["counterexample_review_required"])

    def test_foreign_helpful_feedback_does_not_claim_transfer_support(self):
        self.add(); self.observe(outcome="helpful", reviewer="fixture/reviewer")
        candidate = self.retrieve(domain="manufacturing")["candidates"][0]
        self.assertEqual(candidate["relevant_feedback"], [])
        self.assertFalse(candidate["counterexample_review_required"])
        self.assertEqual(candidate["experience"]["validation"], "hypothesis")

    def test_helpful_observation_retains_hypothesis_status(self):
        self.add()
        result = self.observe(outcome="helpful", reviewer="fixture/reviewer")
        self.assertEqual(result["experience"]["validation"], "hypothesis")
        self.assertEqual(result["observations"][0]["metadata"]["outcome"], "helpful")

    def test_review_declaration_and_new_task_required(self):
        self.add()
        for changes in ({"outcome": "helpful"}, {"outcome": "helpful", "reviewer": "FIXTURE/LEARNER"}, {"task_id": "software-01"}):
            with self.subTest(changes=changes):
                with self.assertRaises(ValueError): self.observe(**changes)
                self.assertEqual(transfer.status(self.root, "stages")["revision"], 0)
        with self.assertRaisesRegex(ValueError, "reviewer"):
            self.add("supported", validation="supported")

    def test_stale_writer_and_duplicate_id_do_not_write(self):
        self.add(); self.observe()
        before = transfer.status(self.root, "stages")
        with self.assertRaisesRegex(ValueError, "Stale revision"):
            self.observe("second", revision=0)
        with self.assertRaisesRegex(ValueError, "Duplicate observation"):
            self.observe(revision=1)
        self.assertEqual(transfer.status(self.root, "stages"), before)

    def test_source_artifact_drift_rejects_status_and_exposes_retrieval_error(self):
        self.add()
        (self.root / self.source["path"]).write_text("Changed source", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "Artifact changed"):
            transfer.status(self.root, "stages")
        result = self.retrieve()
        self.assertEqual(result["candidates"], [])
        self.assertIn("Artifact changed", result["errors"][0]["error"])

    def test_observation_artifact_drift_invalidates_snapshot(self):
        self.add(); result = self.observe()
        (self.root / self.result["path"]).write_text("Later overwritten output", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "Artifact changed"):
            transfer.verify_ref(self.root, result["snapshot_ref"])

    def test_forward_binding_detects_changed_experience_or_earlier_event(self):
        self.add(); self.observe(); self.observe("second", revision=1, task_id="event-02")
        path = self.root / "experience/mechanism/stages/observations/000001.md"
        raw = path.read_bytes(); path.write_bytes(raw + b"\nChanged notes\n")
        with self.assertRaisesRegex(ValueError, "binding changed"):
            transfer.status(self.root, "stages")
        path.write_bytes(raw)
        source = self.root / "experience/mechanism/stages/experience.md"
        source.write_bytes(source.read_bytes() + b"\nChanged source notes\n")
        with self.assertRaisesRegex(ValueError, "binding changed"):
            transfer.status(self.root, "stages")

    def test_holes_in_observation_journal_rejected(self):
        self.add(); self.observe()
        folder = self.root / "experience/mechanism/stages/observations"
        (folder / "000001.md").rename(folder / "000002.md")
        with self.assertRaisesRegex(ValueError, "Noncontiguous"):
            transfer.status(self.root, "stages")

    def test_path_escape_rejected(self):
        with self.assertRaises(ValueError): self.add("../escape")
        with self.assertRaisesRegex(ValueError, "Unsafe path"):
            self.add(artifacts=[{"path": "../outside.txt", "sha256": self.source["sha256"]}])

    def test_symlink_evidence_rejected(self):
        link = self.root / "evidence/link.txt"
        try:
            link.symlink_to(self.root / self.source["path"])
        except OSError as error:
            self.skipTest("Host cannot create a file symlink: " + str(error))
        with self.assertRaisesRegex(ValueError, "Symlink"):
            self.add(artifacts=[{"path": "evidence/link.txt", "sha256": self.source["sha256"]}])

    def test_normalized_labels_cross_language_are_explicit_and_duplicates_rejected(self):
        self.add(mechanisms=["共享资源"], problem_structure=["Sequential   Stages"])
        candidate = self.retrieve(mechanisms=["共享资源"], problem_structure=["ＳＥＱＵＥＮＴＩＡＬ stages"])["candidates"][0]
        self.assertEqual(candidate["matches"]["problem_structure"], ["sequential stages"])
        with self.assertRaisesRegex(ValueError, "Duplicate normalized"):
            self.add("duplicate", mechanisms=["Waiting", "WAITING"])

    def test_invalid_boolean_or_duplicate_metadata_rejected(self):
        with self.assertRaisesRegex(ValueError, "Condition must"):
            self.add(required_conditions={"stage-observable": 1})
        path = self.root / "broken.md"
        path.write_text('---\n{"id":"a","id":"b"}\n---\nbody\n', encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "Duplicate metadata"):
            transfer.add(self.root, path)

    def test_stable_ties_limit_and_legacy_files_untouched(self):
        self.add("zeta"); self.add("alpha")
        legacy = self.root / "experience/legacy.md"
        legacy.write_text("---\ntype: experience\n---\nLegacy YAML", encoding="utf-8")
        query = self.md("query.md", self.query())
        result = transfer.retrieve(self.root, query, limit=1)
        self.assertEqual(result["matched_count"], 2)
        self.assertEqual(result["candidates"][0]["id"], "alpha")
        self.assertEqual(legacy.read_text(encoding="utf-8"), "---\ntype: experience\n---\nLegacy YAML")
        for limit in (0, 51, True):
            with self.assertRaises(ValueError): transfer.retrieve(self.root, query, limit)

    def test_fresh_process_restores_same_markdown(self):
        self.add(); self.observe()
        script = Path(transfer.__file__).resolve()
        run = subprocess.run([sys.executable, "-B", str(script), "status", "--root", str(self.root), "--id", "stages"], capture_output=True, text=True)
        self.assertEqual(run.returncode, 0, run.stderr)
        self.assertEqual(json.loads(run.stdout)["revision"], 1)
        (self.root / self.result["path"]).write_text("Changed", encoding="utf-8")
        run = subprocess.run([sys.executable, "-B", str(script), "retrieve", "--root", str(self.root), "--query", str(self.md("query.md", self.query()))], capture_output=True, text=True)
        self.assertEqual(run.returncode, 2, run.stderr)
        self.assertTrue(json.loads(run.stdout)["errors"])


if __name__ == "__main__":
    unittest.main()
