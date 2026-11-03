# Copyright (C) 2026 KARMENLOOP Official Team
# SPDX-License-Identifier: AGPL-3.0-only
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import blind_trials as blind
import capability_ledger as store


class BlindTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        for arm in ("baseline", "general", "domain"):
            path = self.root/"strategies"/arm; path.mkdir(parents=True)
            (path/"SKILL.md").write_text("Controlled "+arm)
        self.plan = {"id": "blind-test", "type": "blind-plan",
                     "arms": {a: "strategies/"+a for a in ("baseline", "general", "domain")},
                     "model_config": {"model": "fixture", "training": False}, "repetitions": 3,
                     "seed": 47, "deadline_seconds": 120, "metric": "native_tokens"}
        self.file = self.md("plan.md", self.plan)

    def md(self, name, value):
        file = self.root/name; file.write_bytes(store.encode(value, "Controlled consistency fixture, not actual Agent work.")); return file

    def target(self, key="task-a", **changes):
        public = self.root/key/"public"; public.mkdir(parents=True)
        (public/"task.md").write_text("Produce a useful artifact from raw inputs")
        private = self.root/key/"private"; private.mkdir()
        evaluator = private/"grader.py"; evaluator.write_text("print('Independent fixture grader')")
        provenance = private/"provenance.md"; provenance.write_text("Controlled source")
        ref = lambda p: {"path": p.relative_to(self.root).as_posix(), "sha256": store.sha(p.read_bytes())}
        value = {"id": key, "type": "blind-task", "domain": "fixture-domain", "role": "holdout",
                 "public_dir": key+"/public", "evaluator": ref(evaluator), "provenance": ref(provenance), **changes}
        return self.md(key+".md", value)

    def test_targets_are_released_after_strategy_freeze(self):
        task = self.target()
        with self.assertRaises(ValueError): blind.release(self.root, "blind-test", task)
        blind.freeze(self.root, self.file)
        result = blind.release(self.root, "blind-test", task)
        self.assertEqual(result["record"]["task"]["role"], "holdout")
        self.assertEqual(len(blind.schedule(self.root, "blind-test")["runs"]), 9)

    def test_seeded_blocks_have_all_arms_and_repetitions(self):
        blind.freeze(self.root, self.file)
        for name in ("task-a", "task-b"): blind.release(self.root, "blind-test", self.target(name))
        first = blind.schedule(self.root, "blind-test")["runs"]
        self.assertEqual(first, blind.schedule(self.root, "blind-test")["runs"])
        self.assertEqual(len({r["id"] for r in first}), 18)
        for offset in range(0, 18, 3):
            block = first[offset:offset+3]
            self.assertEqual(len({(r["task_id"],r["replicate"]) for r in block}), 1)
            self.assertEqual({r["arm"] for r in block}, set(self.plan["arms"]))

    def test_strategy_or_target_or_grader_drift_blocks_schedule(self):
        blind.freeze(self.root, self.file); blind.release(self.root, "blind-test", self.target())
        paths = [self.root/"strategies/domain/SKILL.md", self.root/"task-a/public/task.md", self.root/"task-a/private/grader.py"]
        for path in paths:
            before = path.read_bytes(); path.write_text("changed")
            with self.assertRaises(ValueError): blind.schedule(self.root, "blind-test")
            path.write_bytes(before)

    def test_existing_release_and_freeze_cannot_be_overwritten(self):
        blind.freeze(self.root, self.file)
        with self.assertRaises(FileExistsError): blind.freeze(self.root, self.file)
        task = self.target(); blind.release(self.root, "blind-test", task)
        with self.assertRaises(FileExistsError): blind.release(self.root, "blind-test", task)

    def test_evaluator_must_be_outside_executor_inputs(self):
        blind.freeze(self.root, self.file)
        task = self.target(); value, _, _ = store.read_md(task)
        data = (self.root/value["evaluator"]["path"]).read_bytes()
        (self.root/"task-a/public/copied.py").write_bytes(data)
        with self.assertRaises(ValueError): blind.release(self.root, "blind-test", task)

    def test_escape_and_symlink_strategy_rejected(self):
        value = dict(self.plan); value["arms"] = {"baseline":"../escape", "general":"strategies/general"}
        with self.assertRaises(ValueError): blind.freeze(self.root, self.md("bad.md", value))
        try: (self.root/"strategies/domain/link").symlink_to(self.root/"strategies/general/SKILL.md")
        except OSError: self.skipTest("Native symlinks unavailable")
        with self.assertRaises(ValueError): blind.freeze(self.root, self.file)

    def test_visible_model_and_timing_replication_required(self):
        for changes in ({"model_config": {"model":"fixture", "training":True}},
                        {"metric":"complete_task_seconds", "repetitions":1}, {"seed":True}):
            with self.assertRaises(ValueError): blind.freeze(self.root, self.md("bad.md", {**self.plan, **changes}))


if __name__ == "__main__": unittest.main()
