# Copyright (C) 2026 KARMENLOOP Official Team
# SPDX-License-Identifier: AGPL-3.0-only
"""Controlled capacity-boundary journals; not repeated real Agent executions."""
from datetime import datetime, timedelta, timezone
import hashlib
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import adaptive_learning as loop
import capability_ledger as md


class AdaptiveCapacityTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.now = datetime(2026, 11, 3, tzinfo=timezone.utc)
        request = {"id": "request", "type": "learning-request", "goal": "Reconcile a controlled pending action",
                   "domain": "controlled-capacity", "acceptance": ["artifact checked"],
                   "budget_seconds": 300, "max_actions": 10, "allowed_actions": sorted(loop.KINDS)}
        loop.init(self.root, "run", self.write("request", request), now=self.now)
        loop.plan(self.root, "run", self.write("initial-plan", self.proposal("initial-plan", 0)), 0, now=self.now)
        started = loop.start(self.root, "run", "inspect", 1, now=self.now)
        self.start_id = started["pending"]["start_id"]
        self.folder = self.root / "learning-runs/run"
        self.journal = self.folder / "events"
        self.config_hash = md.sha((self.folder / "request.md").read_bytes())
        artifact = self.root / "receipt.txt"
        artifact.write_text("Controlled recovered receipt, not a host Agent transcript", encoding="utf-8")
        self.evidence = {"path": artifact.name, "sha256": md.sha(artifact.read_bytes())}

    def write(self, name, item):
        path = self.root / (name + ".md")
        path.write_bytes(md.encode(item, "Controlled fixture"))
        return path

    def proposal(self, name, revision):
        return {"id": name, "type": "learning-plan", "based_on_revision": revision,
                "unknowns": [{"id": "q", "question": "What does the actual receipt establish?", "importance": 1}],
                "actions": [{"id": "inspect", "kind": "research", "question_ids": ["q"],
                             "description": "Inspect controlled evidence", "expected_information_gain": 1,
                             "estimated_seconds": 1, "preconditions": []}],
                "experience_refs": [], "artifacts": []}

    def observation(self, name, outcome="unknown", resolve=False):
        return {"id": name, "type": "learning-observation", "start_id": self.start_id, "action_id": "inspect",
                "outcome": outcome, "finding": "Controlled receipt observation", "hypothesis_change": "Controlled finding",
                "resolved_questions": ["q"] if resolve else [],
                "artifacts": [] if outcome == "unknown" else [self.evidence],
                "executor": "fixture-executor", "reviewer": None,
                "cost": {"tokens": None, "usd": None}, "acceptance_checks": {}}

    def seed(self, revision, kind, item):
        # Build a valid large fixture directly to avoid quadratic setup. Every test
        # then exercises real Markdown parsing, hash-chain replay and public APIs.
        previous = md.sha((self.journal / f"{revision - 1:06d}.md").read_bytes())
        event = {"schema": 1, "type": "learning-event", "id": item["id"], "kind": kind,
                 "at": self.now.isoformat(), "request_sha256": self.config_hash,
                 "previous_sha256": previous, "data": item}
        (self.journal / f"{revision:06d}.md").write_bytes(md.encode(event, "Controlled seeded capacity fixture"))

    def unknowns_through(self, revision):
        for index in range(3, revision + 1):
            self.seed(index, "observe", self.observation("unknown-" + str(index)))

    def inventory(self):
        return {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in self.journal.glob("*.md")}

    def test_last_slot_accepts_actual_reconciliation(self):
        self.unknowns_through(999)
        before = loop.status(self.root, "run", now=self.now)
        self.assertEqual(before["revision"], 999)
        self.assertEqual(before["state"], "needs_reconciliation")
        result = loop.observe(self.root, "run", self.write("recovered", self.observation("recovered", "progress", True)),
                              999, now=self.now + timedelta(seconds=10))
        self.assertEqual(result["revision"], 1000)
        self.assertIsNone(result["pending"])
        self.assertEqual(result["unresolved_questions"], [])
        self.assertEqual(result["state"], "journal_limit")
        later = loop.status(self.root, "run", now=self.now + timedelta(days=2))
        self.assertEqual(later["revision"], 1000)
        self.assertEqual(later["state"], "journal_limit")
        self.assertEqual(later["elapsed_seconds_since_init"], 10)
        self.assertFalse(later["budget_overrun"])

    def test_repeated_unknown_cannot_consume_reserved_terminal_slot(self):
        self.unknowns_through(999)
        before = self.inventory()
        with self.assertRaisesRegex(ValueError, "(?i)(capacity|event limit)"):
            loop.observe(self.root, "run", self.write("still-unknown", self.observation("still-unknown")), 999, now=self.now)
        self.assertEqual(before, self.inventory())

    def test_abandoned_publication_file_does_not_consume_reconciliation_capacity(self):
        self.unknowns_through(999)
        orphan = self.journal / ".pending-interrupted-publication"
        orphan.write_text("Interrupted temporary publication, not an accepted event", encoding="utf-8")
        result = loop.observe(self.root, "run", self.write("recovered", self.observation("recovered", "progress", True)),
                              999, now=self.now)
        self.assertEqual(result["revision"], 1000)
        self.assertEqual(result["state"], "journal_limit")
        self.assertIsNone(result["pending"])
        self.assertTrue(orphan.exists())
        self.assertEqual(loop.status(self.root, "run", now=self.now)["revision"], 1000)

    def test_new_plan_is_rejected_before_capacity_can_strand_an_action(self):
        self.unknowns_through(997)
        self.seed(998, "observe", self.observation("settled", "progress"))
        before = self.inventory()
        self.assertEqual(loop.status(self.root, "run", now=self.now)["revision"], 998)
        with self.assertRaisesRegex(ValueError, "(?i)(capacity|event limit)"):
            loop.plan(self.root, "run", self.write("late-plan", self.proposal("late-plan", 998)), 998, now=self.now)
        self.assertEqual(before, self.inventory())
        later = loop.status(self.root, "run", now=self.now + timedelta(days=2))
        self.assertEqual(later["state"], "journal_limit")
        self.assertEqual(later["elapsed_seconds_since_init"], 0)

    def test_new_start_is_rejected_before_reserved_capacity(self):
        self.unknowns_through(996)
        self.seed(997, "observe", self.observation("settled", "progress"))
        self.seed(998, "plan", self.proposal("last-plan", 997))
        before = self.inventory()
        self.assertEqual(loop.status(self.root, "run", now=self.now)["revision"], 998)
        with self.assertRaisesRegex(ValueError, "(?i)(capacity|event limit)"):
            loop.start(self.root, "run", "inspect", 998, now=self.now)
        self.assertEqual(before, self.inventory())
        later = loop.status(self.root, "run", now=self.now + timedelta(days=2))
        self.assertEqual(later["state"], "journal_limit")
        self.assertEqual(later["elapsed_seconds_since_init"], 0)


if __name__ == "__main__":
    unittest.main()
