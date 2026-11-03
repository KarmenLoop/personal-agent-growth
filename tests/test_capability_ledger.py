# Copyright (C) 2026 KARMENLOOP Official Team
# SPDX-License-Identifier: AGPL-3.0-only
"""Real filesystem protocol tests; synthetic observations are NOT Agent evidence."""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SPEC = importlib.util.spec_from_file_location("capability_ledger", Path(__file__).resolve().parents[1] / "scripts/capability_ledger.py")
ledger = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(ledger)


class CapabilityTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="growth-capability-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "知识 memory"
        self.start = datetime(2026, 1, 1, tzinfo=timezone.utc)
        ledger.init(self.root, "writing", "Write useful source-backed guides", "writing", now=self.start)
        (self.root / "evidence").mkdir()
        self.teacher = self.artifact("teacher.md", "Synthetic teacher output\n")
        self.learner = self.artifact("learner.md", "Synthetic independently produced learner output\n")

    def artifact(self, name, text):
        path = self.root / "evidence" / name
        path.write_text(text, encoding="utf-8")
        return {"path": "evidence/" + name, "sha256": ledger.sha(path.read_bytes())}

    def observation(self, event_id="one", kind="apply", at=None, **changes):
        item = {"id": event_id, "kind": kind, "task_id": "task-one", "executor": "synthetic-executor",
                "reviewer": "synthetic-reviewer", "outcome": "pass", "observed_at": (at or self.start).isoformat(),
                "summary": "Controlled filesystem fixture, not a real Agent run", "artifacts": [self.teacher],
                "cost": {"wall_seconds": 1.5, "tokens": None, "usd": None}}
        item.update(changes)
        return item

    def write(self, item, name="observation.md"):
        path = Path(self.temp.name) / name
        path.write_bytes(ledger.encode(item, "# Synthetic fixture\n\nThese declarations test the gate only."))
        return path

    def record(self, item, revision=0, now=None):
        return ledger.record(self.root, "writing", self.write(item), revision, now=now or self.start)

    def test_md_only_replay_and_unknown_cost(self):
        result = self.record(self.observation())
        self.assertEqual(result["revision"], 1)
        self.assertEqual(result["dimensions"]["apply"]["state"], "pass")
        self.assertIn("teach", result["missing_gates"])
        self.assertEqual(result["assessment"], "incomplete_or_review_due")
        self.assertIsNone(result["cost"]["tokens"]["total"])
        self.assertEqual(result["cost"]["wall_seconds"]["total"], 1.5)
        self.assertFalse(result["scheduler_registered"])
        self.assertEqual(ledger.status(self.root, "writing", now=self.start), result)
        files = sorted(p.relative_to(self.root).as_posix() for p in self.root.rglob("*") if p.is_file())
        self.assertEqual(files, ["capabilities/writing/attempts/000001.md", "capabilities/writing/capability.md",
                                 "evidence/learner.md", "evidence/teacher.md"])

    def test_future_and_before_init_rejected_without_journal_write(self):
        for at in (self.start + timedelta(seconds=1), self.start - timedelta(seconds=1)):
            with self.subTest(at=at), self.assertRaisesRegex(ValueError, "before initialization or in the future"):
                self.record(self.observation(at=at))
        self.assertEqual(ledger.status(self.root, "writing", now=self.start)["revision"], 0)

    def test_stale_revision_and_duplicate_event_preserve_first(self):
        self.record(self.observation())
        first = (self.root / "capabilities/writing/attempts/000001.md").read_bytes()
        with self.assertRaisesRegex(ValueError, "Stale revision"):
            self.record(self.observation("two"))
        with self.assertRaisesRegex(ValueError, "Duplicate event"):
            self.record(self.observation(), revision=1)
        self.assertEqual((self.root / "capabilities/writing/attempts/000001.md").read_bytes(), first)
        self.assertFalse((self.root / "capabilities/writing/.writer.lock").exists())

    def test_concurrent_writers_commit_one(self):
        paths = [self.write(self.observation(str(i)), name=str(i) + ".md") for i in (1, 2)]
        def attempt(path):
            try:
                return ledger.record(self.root, "writing", path, 0, now=self.start)["revision"]
            except (ValueError, FileExistsError):
                return "rejected"
        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(attempt, paths))
        self.assertEqual(results.count(1), 1)
        self.assertEqual(results.count("rejected"), 1)
        self.assertEqual(ledger.status(self.root, "writing", now=self.start)["revision"], 1)

    def test_later_failure_unknown_and_recovery_are_retained(self):
        self.record(self.observation())
        failed = self.record(self.observation("failed", outcome="fail", reviewer=None, artifacts=[]), 1)
        self.assertEqual(failed["dimensions"]["apply"]["state"], "fail")
        self.assertEqual(failed["next_actions"][0]["action"], "remediate")
        unknown = self.record(self.observation("unknown", outcome="unknown", reviewer=None, artifacts=[]), 2)
        self.assertEqual(unknown["next_actions"][0]["action"], "verify")
        result = self.record(self.observation("recovered"), 3)
        self.assertEqual([item["outcome"] for item in result["history"]], ["pass", "fail", "unknown", "pass"])
        self.assertEqual(result["dimensions"]["apply"]["state"], "pass")

    def test_hash_forgery_and_artifact_changes_fail_closed(self):
        with self.assertRaisesRegex(ValueError, "Artifact changed"):
            self.record(self.observation(artifacts=[{**self.teacher, "sha256": "0" * 64}]))
        self.record(self.observation())
        (self.root / self.teacher["path"]).write_text("changed", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "Artifact changed"):
            ledger.status(self.root, "writing", now=self.start)
        result = ledger.due(self.root, now=self.start)
        self.assertTrue(result["errors"])
        self.assertEqual(result["tasks"], [])
        self.assertTrue((self.root / "capabilities/writing/attempts/000001.md").exists())

    def test_pass_requires_independent_reviewer_and_artifact(self):
        for change in ({"reviewer": None}, {"reviewer": "synthetic-executor"}, {"artifacts": []}):
            with self.subTest(change=change), self.assertRaises(ValueError):
                self.record(self.observation(**change))

    def test_transfer_requires_prior_apply_and_distinct_task(self):
        self.record(self.observation())
        with self.assertRaisesRegex(ValueError, "new task"):
            self.record(self.observation("transfer", "transfer", source_attempt="one"), 1)
        with self.assertRaisesRegex(ValueError, "prior passed"):
            self.record(self.observation("transfer", "transfer", task_id="new-task", source_attempt="missing"), 1)
        result = self.record(self.observation("transfer", "transfer", task_id="new-task", source_attempt="one"), 1)
        self.assertEqual(result["dimensions"]["transfer"]["state"], "pass")

    def test_source_failure_invalidates_dependent_pass_and_blocks_reuse(self):
        self.record(self.observation())
        self.record(self.observation("transfer", "transfer", task_id="new-task", source_attempt="one"), 1)
        result = self.record(self.observation("failed", outcome="fail", reviewer=None, artifacts=[]), 2)
        self.assertEqual(result["dimensions"]["transfer"]["state"], "source_invalidated")
        self.assertIn("transfer", result["missing_gates"])
        with self.assertRaisesRegex(ValueError, "invalidated"):
            self.record(self.observation("transfer-again", "transfer", task_id="another", source_attempt="one"), 3)
        # New successful application is a new source; it does not rewrite old dependencies.
        self.record(self.observation("repaired", task_id="repaired-task", artifacts=[self.learner]), 3)
        result = self.record(self.observation("transfer-repaired", "transfer", task_id="another", source_attempt="repaired"), 4)
        self.assertEqual(result["dimensions"]["transfer"]["state"], "pass")

    def test_recall_does_not_revalidate_an_invalidated_parent_chain(self):
        self.record(self.observation())
        self.record(self.observation("transfer", "transfer", task_id="new-task", source_attempt="one"), 1)
        self.record(self.observation("unknown", outcome="unknown", reviewer=None, artifacts=[]), 2)
        at = self.start + timedelta(days=1)
        with self.assertRaisesRegex(ValueError, "invalidated"):
            self.record(self.observation("recall", "recall", at=at, source_attempt="transfer", no_answer_visible=True), 3, now=at)

    def test_teaching_requires_independent_learner_and_output(self):
        item = self.observation("teach", "teach", learner="synthetic-learner", learner_task_id="learner-task", learner_artifacts=[self.learner])
        for change in ({"learner": "synthetic-executor"}, {"learner": "synthetic-reviewer"},
                       {"learner_task_id": "task-one"}, {"learner_artifacts": []}, {"learner_artifacts": [self.teacher]}):
            with self.subTest(change=change), self.assertRaises(ValueError):
                self.record({**item, **change})
        result = self.record(item)
        self.assertEqual(result["dimensions"]["teach"]["state"], "pass")
        self.assertIn("apply", result["missing_gates"])

    def test_delayed_recall_uses_elapsed_time_not_dates_or_simulated_cli(self):
        self.record(self.observation())
        at = self.start + timedelta(hours=23, minutes=59)
        recall = self.observation("recall", "recall", at=at, source_attempt="one", no_answer_visible=True)
        with self.assertRaisesRegex(ValueError, "interval has not elapsed"):
            self.record(recall, 1, now=at)
        at = self.start + timedelta(days=1)
        recall["observed_at"] = at.isoformat()
        with self.assertRaisesRegex(ValueError, "closed book"):
            self.record({**recall, "no_answer_visible": False}, 1, now=at)
        result = self.record(recall, 1, now=at)
        self.assertEqual(result["dimensions"]["recall"]["state"], "pass")
        self.assertEqual(result["dimensions"]["apply"]["state"], "review_due")
        self.assertFalse(result["scheduler_registered"])

    def test_due_intervals_and_expired_evidence(self):
        self.record(self.observation())
        self.assertEqual(ledger.due(self.root, now=self.start)["tasks"], [])
        self.assertEqual(ledger.due(self.root, now=self.start + timedelta(days=1))["tasks"][0]["action"], "closed_book_review")
        result = self.record(self.observation("second", task_id="task-two", artifacts=[self.learner]), 1)
        self.assertEqual(result["next_actions"][0]["due_at"], (self.start + timedelta(days=3)).isoformat())
        third = self.artifact("third.md", "Third different controlled output")
        self.record(self.observation("third", task_id="task-three", artifacts=[third]), 2)
        result = ledger.status(self.root, "writing", now=self.start + timedelta(days=7))
        self.assertEqual(result["dimensions"]["apply"]["state"], "review_due")
        self.assertIn("apply", result["missing_gates"])

    def test_duplicate_task_or_output_does_not_extend_review_interval(self):
        self.record(self.observation())
        self.record(self.observation("same-task", artifacts=[self.learner]), 1)
        result = self.record(self.observation("same-output", task_id="task-two", artifacts=[self.learner]), 2)
        # The distinct first output/first task and latest task form two evidence groups.
        self.assertEqual(result["next_actions"][0]["due_at"], (self.start + timedelta(days=3)).isoformat())
        result = self.record(self.observation("duplicate", task_id="task-two", artifacts=[self.learner]), 3)
        self.assertEqual(result["next_actions"][0]["due_at"], (self.start + timedelta(days=3)).isoformat())

    def test_old_event_edits_break_the_forward_binding(self):
        self.record(self.observation())
        self.record(self.observation("two"), 1)
        first = self.root / "capabilities/writing/attempts/000001.md"
        first.write_bytes(first.read_bytes() + b"\nChanged human notes\n")
        with self.assertRaisesRegex(ValueError, "binding changed"):
            ledger.status(self.root, "writing", now=self.start)

    def test_repeated_evidence_cannot_refresh_its_due_date(self):
        self.record(self.observation())
        at = self.start + timedelta(hours=23)
        result = self.record(self.observation("repeated", at=at), 1, now=at)
        self.assertEqual(result["dimensions"]["apply"]["review_at"],
                         (self.start + timedelta(days=1)).isoformat())
        later = self.start + timedelta(hours=25)
        self.assertEqual(ledger.status(self.root, "writing", now=later)["dimensions"]["apply"]["state"], "review_due")
        self.assertTrue(ledger.due(self.root, now=later)["tasks"])

    def test_invalidated_transfer_cannot_extend_a_repaired_streak(self):
        self.record(self.observation())
        self.record(self.observation("transfer-one", "transfer", task_id="transfer-one", source_attempt="one"), 1)
        self.record(self.observation("failed", outcome="fail", reviewer=None, artifacts=[]), 2)
        self.record(self.observation("repaired", task_id="new-apply", artifacts=[self.learner]), 3)
        result = self.record(self.observation("transfer-two", "transfer", task_id="transfer-two", source_attempt="repaired", artifacts=[self.learner]), 4)
        self.assertEqual(result["dimensions"]["transfer"]["review_at"],
                         (self.start + timedelta(days=1)).isoformat())

    def test_teaching_review_requires_new_learner_work(self):
        first = self.observation("teach-one", "teach", learner="synthetic-learner",
                                 learner_task_id="learner-one", learner_artifacts=[self.learner])
        self.record(first)
        at = self.start + timedelta(hours=23)
        revised = self.artifact("revised-lesson.md", "Another synthetic teaching document")
        result = self.record({**first, "id": "teach-two", "task_id": "changed-teacher-task",
                              "artifacts": [revised], "observed_at": at.isoformat()}, 1, now=at)
        self.assertEqual(result["dimensions"]["teach"]["review_at"],
                         (self.start + timedelta(days=1)).isoformat())
        new_work = self.artifact("new-learner-work.md", "Different independent learner exercise")
        result = self.record({**first, "id": "teach-three", "learner_task_id": "learner-two",
                              "learner_artifacts": [new_work], "observed_at": at.isoformat()}, 2, now=at)
        self.assertEqual(result["dimensions"]["teach"]["review_at"], (at + timedelta(days=3)).isoformat())

    def test_finite_individual_cost_overflow_is_explicit_not_zero(self):
        cost = {"wall_seconds": 1e308, "tokens": None, "usd": None}
        self.record(self.observation(cost=cost))
        result = self.record(self.observation("two", cost=cost), 1)
        self.assertTrue(result["cost"]["wall_seconds"]["aggregation_overflow"])
        self.assertIsNone(result["cost"]["wall_seconds"]["total"])
        json.dumps(result, allow_nan=False)

    def test_configuration_edits_invalidate_bound_history(self):
        self.record(self.observation())
        path = self.root / "capabilities/writing/capability.md"
        meta, body, _ = ledger.read_md(path)
        meta["policy"]["review_days"] = [2, 4, 8]
        path.write_bytes(ledger.encode(meta, body))
        with self.assertRaisesRegex(ValueError, "configuration binding changed"):
            ledger.status(self.root, "writing", now=self.start)
        with self.assertRaisesRegex(ValueError, "already exists"):
            ledger.init(self.root, "writing", "Other goal", "other", now=self.start)

    def test_invalid_policy_cost_ids_and_timestamp(self):
        for policy in ({"recall_min_hours": 1, "review_days": [1, 3, 7]}, {"recall_min_hours": 24, "review_days": [True]}):
            with self.assertRaises(ValueError):
                ledger.init(self.root, "other", "goal", "domain", policy=policy, now=self.start)
        for value in (True, -1, float("inf"), float("nan")):
            with self.subTest(value=value), self.assertRaises(ValueError):
                self.record(self.observation(cost={"wall_seconds": value, "tokens": None, "usd": None}))
        for value in ("../escape", "C:drive", "CON", "AUX", "x/y", "", "x."):
            with self.subTest(value=value), self.assertRaises(ValueError):
                ledger.status(self.root, value, now=self.start)
        with self.assertRaisesRegex(ValueError, "UTC"):
            self.record(self.observation(observed_at="2026-01-01T00:00:00"))

    def test_duplicate_nested_keys_and_nonfinite_metadata(self):
        for metadata in ('{"id":"a","id":"b"}', '{"cost":{"tokens":1,"tokens":2}}', '{"cost":NaN}'):
            with self.subTest(metadata=metadata), self.assertRaises(ValueError):
                ledger.decode(("---\n" + metadata + "\n---\n").encode())

    def test_path_escape_and_symlink_rejected(self):
        for path in ("../outside", "/outside", "C:/outside", "a\\b", "evidence/../teacher.md"):
            with self.subTest(path=path), self.assertRaisesRegex(ValueError, "Unsafe path"):
                self.record(self.observation(artifacts=[{**self.teacher, "path": path}]))
        if sys.platform != "win32":
            link = self.root / "evidence/link.md"
            link.symlink_to(self.root / self.teacher["path"])
            with self.assertRaisesRegex(ValueError, "Symlink"):
                self.record(self.observation(artifacts=[{**self.teacher, "path": "evidence/link.md"}]))

    def test_chronology_revision_gap_and_bool_revision(self):
        after = self.start + timedelta(minutes=1)
        self.record(self.observation(at=after), now=after)
        with self.assertRaisesRegex(ValueError, "chronological"):
            self.record(self.observation("earlier"), 1, now=after)
        with self.assertRaisesRegex(ValueError, "Invalid expected revision"):
            self.record(self.observation("boolean"), True, now=after)
        folder = self.root / "capabilities/writing/attempts"
        (folder / "000001.md").rename(folder / "000002.md")
        with self.assertRaisesRegex(ValueError, "revision gap"):
            ledger.status(self.root, "writing", now=after)

    def test_cli_has_real_clock_and_no_time_override(self):
        script = str(Path(ledger.__file__))
        cli_root = Path(self.temp.name) / "cli"
        result = subprocess.run([sys.executable, script, "init", "--root", str(cli_root), "--id", "cli",
                                 "--goal", "CLI fixture", "--domain", "testing"], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(json.loads(result.stdout)["scheduler_registered"])
        result = subprocess.run([sys.executable, script, "due", "--root", str(cli_root), "--now", self.start.isoformat()],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)
        self.assertIn("unrecognized arguments", result.stderr)


if __name__ == "__main__":
    unittest.main()
