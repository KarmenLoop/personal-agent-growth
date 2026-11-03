# Copyright (C) 2026 KARMENLOOP Official Team
# SPDX-License-Identifier: AGPL-3.0-only
"""Controlled utility fixtures; these tests are not Agent learning trials."""
from datetime import datetime, timedelta, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import adaptive_learning as loop
import capability_ledger as md


class AdaptiveTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.now = datetime(2026, 11, 3, tzinfo=timezone.utc)
        self.request = {"id": "request", "type": "learning-request", "goal": "Analyze a novel controlled workflow",
                        "domain": "never-predefined", "acceptance": ["artifact correct"], "budget_seconds": 300,
                        "max_actions": 10, "allowed_actions": sorted(loop.KINDS)}
        loop.init(self.root, "one", self.write("request", self.request), now=self.now)
        self.evidence = self.artifact("result.txt", "Controlled fixture output, not an Agent transcript")

    def write(self, name, item):
        p = self.root / (name + ".md"); p.write_bytes(md.encode(item, "Controlled test fixture")); return p

    def artifact(self, name, text):
        p = self.root / name; p.write_text(text, encoding="utf-8")
        return {"path": name, "sha256": hashlib.sha256(p.read_bytes()).hexdigest()}

    def proposal(self, revision=0, name="plan", **changes):
        item = {"id": name, "type": "learning-plan", "based_on_revision": revision,
                "unknowns": [{"id": "cause", "question": "Which condition explains delay?", "importance": 1, "blocking": True}],
                "actions": [self.action("inspect", "research", 0.8, 10), self.action("speculate", "reflect", 0.2, 30)],
                "experience_refs": [], "artifacts": []}
        return {**item, **changes}

    def action(self, name, kind, gain, seconds, questions=None, preconditions=None):
        return {"id": name, "kind": kind, "description": "Controlled " + name,
                "question_ids": ["cause"] if questions is None else questions,
                "expected_information_gain": gain, "estimated_seconds": seconds,
                "preconditions": [] if preconditions is None else preconditions}

    def plan(self, item=None, revision=0, at=None):
        item = item or self.proposal(revision)
        return loop.plan(self.root, "one", self.write(item["id"], item), revision, now=at or self.now)

    def start(self, revision=1, name="inspect", at=None):
        return loop.start(self.root, "one", name, revision, now=at or self.now)

    def observation(self, start, name="observed", **changes):
        return {**{"id": name, "type": "learning-observation", "start_id": start["pending"]["start_id"],
                   "action_id": start["pending"]["action"]["id"], "outcome": "progress", "finding": "Input contradicts original guess",
                   "hypothesis_change": "Replaced the unsupported cause", "resolved_questions": ["cause"],
                   "artifacts": [self.evidence], "executor": "fixture-executor", "reviewer": None,
                   "cost": {"tokens": None, "usd": None}, "acceptance_checks": {}}, **changes}

    def observe(self, item, revision=2, at=None):
        return loop.observe(self.root, "one", self.write(item["id"], item), revision, now=at or self.now)

    def journal_bytes(self):
        return {p.name: p.read_bytes() for p in (self.root / "learning-runs/one/events").glob("*.md")}

    def test_novel_domain_and_feedback_require_fresh_plan(self):
        result = self.plan(); self.assertEqual(result["recommended_action"], "inspect")
        started = self.start(); result = self.observe(self.observation(started))
        self.assertEqual(result["unresolved_questions"], []); self.assertEqual(result["ranked_actions"], [])
        with self.assertRaisesRegex(ValueError, "No current plan"):
            self.start(3)
        new = self.proposal(3, "second", unknowns=[{"id": "new", "question": "What did the changed constraints reveal?", "importance": 0.9}],
                            actions=[self.action("new-test", "experiment", 0.9, 20, ["new"])])
        self.assertEqual(self.plan(new, 3)["recommended_action"], "new-test")

    def test_unknown_pending_is_reconciled_without_reexecution_even_after_deadline(self):
        self.plan(); started = self.start()
        unknown = self.observation(started, "lost", outcome="unknown", resolved_questions=[], artifacts=[])
        result = self.observe(unknown)
        self.assertEqual(result["state"], "needs_reconciliation")
        with self.assertRaisesRegex(ValueError, "No active plan"):
            self.start(3)
        result = self.observe(self.observation(started, "recovered"), 3, self.now + timedelta(seconds=400))
        self.assertEqual(result["actions_started"], 1); self.assertEqual(result["state"], "budget_exhausted")
        self.assertTrue(result["budget_overrun"])

    def test_old_async_receipt_cannot_match_reused_action_name(self):
        self.plan(); old = self.start(); self.observe(self.observation(old, resolved_questions=[]))
        self.plan(self.proposal(3, "second"), 3); current = self.start(4)
        self.assertNotEqual(old["pending"]["start_id"], current["pending"]["start_id"])
        before = self.journal_bytes()
        with self.assertRaisesRegex(ValueError, "start token"):
            self.observe(self.observation(old, "late-old"), 5)
        self.assertEqual(before, self.journal_bytes())

    def test_stale_writer_and_plan_leave_no_event(self):
        self.plan(); before = self.journal_bytes()
        with self.assertRaisesRegex(ValueError, "Stale writer"):
            self.start(0)
        with self.assertRaisesRegex(ValueError, "Stale plan"):
            self.plan(self.proposal(0, "stale"), 1)
        self.assertEqual(before, self.journal_bytes())

    def test_unresolved_question_cannot_be_erased_or_reclassified(self):
        self.plan()
        for questions in [[], [{"id": "cause", "question": "Which condition explains delay?", "importance": 1, "blocking": False}]]:
            with self.assertRaises(ValueError):
                self.plan(self.proposal(1, "drop", unknowns=questions,
                                        actions=[self.action("finish", "deliver", 1, 1, [])]), 1)

    def test_unmet_precondition_and_oversized_action_cannot_start(self):
        actions=[self.action("blocked", "tool", 1, 1, preconditions=["Need observed input identity"]),
                 self.action("too-long", "research", 1, 301), self.action("inspect", "research", 0.2, 10)]
        result = self.plan(self.proposal(actions=actions))
        self.assertEqual(result["recommended_action"], "inspect")
        for name in ["blocked", "too-long"]:
            with self.assertRaises(ValueError): self.start(name=name)

    def test_budget_includes_planning_and_waiting(self):
        self.plan()
        result = loop.status(self.root, "one", now=self.now+timedelta(seconds=301))
        self.assertEqual(result["state"], "budget_exhausted")
        with self.assertRaises(ValueError): self.start(at=self.now+timedelta(seconds=301))

    def test_plan_limit_stops_unbounded_replanning(self):
        request = {**self.request, "max_plans": 1}
        loop.init(self.root, "limited", self.write("limited-request", request), now=self.now)
        loop.plan(self.root, "limited", self.write("p1", self.proposal()), 0, now=self.now)
        with self.assertRaisesRegex(ValueError, "Plan limit"):
            loop.plan(self.root, "limited", self.write("p2", self.proposal(1, "p2")), 1, now=self.now)

    def test_repeated_no_progress_pauses_without_claiming_mastery(self):
        revision=0
        for i in range(3):
            self.plan(self.proposal(revision, "plan"+str(i)), revision); started=self.start(revision+1)
            result=self.observe(self.observation(started, "o"+str(i), outcome="no_progress", resolved_questions=[]), revision+2)
            revision+=3
        self.assertEqual(result["state"], "paused_no_progress")
        with self.assertRaises(ValueError): self.plan(self.proposal(revision, "fourth"), revision)

    def test_delivery_needs_acceptance_independent_review_and_no_blockers(self):
        self.plan(self.proposal(actions=[self.action("finish", "deliver", 1, 1, [])]))
        with self.assertRaisesRegex(ValueError, "blocking"):
            self.start(name="finish")
        self.plan(self.proposal(1,"research"),1); started=self.start(2)
        self.observe(self.observation(started),3)
        self.plan(self.proposal(4,"delivery",unknowns=[],actions=[self.action("finish","deliver",1,1,[])]),4)
        started=self.start(5,"finish")
        final=self.observation(started,"done",outcome="delivered",resolved_questions=[],acceptance_checks={"artifact correct":True},reviewer="fixture-reviewer")
        for change in [{"reviewer": "fixture-executor"},{"acceptance_checks":{}},{"acceptance_checks":{"artifact correct":None}}]:
            with self.assertRaises(ValueError):self.observe({**final,**change},6)
        result=self.observe(final,6,self.now+timedelta(seconds=50))
        self.assertEqual(result["state"],"delivered")
        later=loop.status(self.root,"one",now=self.now+timedelta(days=2))
        self.assertEqual(later["elapsed_seconds_since_init"],50)
        self.assertFalse(later["budget_overrun"])

    def test_optional_exploration_does_not_block_delivery(self):
        self.plan(self.proposal(unknowns=[{"id":"nice","question":"Optional new connection?","importance":0.1,"blocking":False}],
                                actions=[self.action("finish","deliver",1,1,[])]))
        started=self.start(name="finish")
        result=self.observe(self.observation(started,"done",outcome="delivered",resolved_questions=[],reviewer="reviewer",
                                            acceptance_checks={"artifact correct":True}))
        self.assertEqual(result["state"],"delivered")
        self.assertEqual(len(result["unresolved_questions"]),1)

    def test_artifact_drift_rejected_before_start(self):
        self.plan(self.proposal(artifacts=[self.evidence]))
        (self.root/self.evidence["path"]).write_text("changed")
        with self.assertRaisesRegex(ValueError,"Artifact changed"):self.start()
        self.assertEqual(len(self.journal_bytes()),1)

    def test_hash_chain_detects_old_notes_change(self):
        self.plan();self.start()
        p=self.root/'learning-runs/one/events/000001.md';p.write_bytes(p.read_bytes()+b'\nEdited\n')
        with self.assertRaisesRegex(ValueError,"binding changed"):loop.status(self.root,"one",now=self.now)

    def test_journal_gap_and_duplicate_identity_rejected(self):
        self.plan();started=self.start()
        with self.assertRaisesRegex(ValueError,"Duplicate event"):
            self.observe(self.observation(started,"plan"))
        p=self.root/'learning-runs/one/events/000002.md';p.rename(p.with_name('000003.md'))
        with self.assertRaisesRegex(ValueError,"sequence gap"):loop.status(self.root,"one",now=self.now)

    def test_invalid_estimates_and_costs_are_not_silently_accepted(self):
        for value in [True,-1,float('nan')]:
            item=self.proposal();item['actions'][0]['estimated_seconds']=value
            with self.assertRaises(ValueError):self.plan(item)
        self.plan();started=self.start()
        with self.assertRaises(ValueError):self.observe(self.observation(started,cost={'tokens':True,'usd':0}))

    def test_experience_binding_calls_fresh_verifier_at_start(self):
        # Concrete transfer integration is exercised by test_adaptive_transfer.py.
        import types
        from unittest.mock import patch
        original=self.artifact('experience.md','Controlled immutable experience')
        ref={**original,'revision':0,'head_sha256':original['sha256']}
        fake=types.SimpleNamespace(verify_ref=lambda root,reference:reference)
        with patch.dict(sys.modules,{'experience_transfer':fake}):self.plan(self.proposal(experience_refs=[ref]))
        def changed(root,reference):raise ValueError('Experience feedback changed')
        fake.verify_ref=changed
        with patch.dict(sys.modules,{'experience_transfer':fake}):
            with self.assertRaisesRegex(ValueError,'feedback changed'):self.start()

    def test_cli_recovers_state_from_markdown_in_fresh_process(self):
        # Use real clock for CLI; the fixtures above never count as delayed review.
        script=Path(loop.__file__)
        request=self.write('cli-request',self.request)
        init=subprocess.run([sys.executable,str(script),'init','--root',str(self.root),'--id','cli','--request',str(request)],capture_output=True,text=True)
        self.assertEqual(init.returncode,0,init.stderr)
        read=subprocess.run([sys.executable,str(script),'status','--root',str(self.root),'--id','cli'],capture_output=True,text=True)
        self.assertEqual(read.returncode,0,read.stderr);self.assertEqual(json.loads(read.stdout)['revision'],0)
        invalid=subprocess.run([sys.executable,str(script),'status','--root',str(self.root),'--id','cli','--now','2099'],capture_output=True,text=True)
        self.assertEqual(invalid.returncode,2)

    def test_wrapped_event_size_rejected_before_journal_write(self):
        proposal=self.proposal()
        raw=md.encode(proposal,'')
        input_path=self.root/'large-plan.md'
        input_path.write_bytes(raw+b'x'*(1024*1024-len(raw)))
        with self.assertRaises(ValueError):loop.plan(self.root,'one',input_path,0,now=self.now)
        self.assertEqual(self.journal_bytes(),{})
        self.assertEqual(loop.status(self.root,'one',now=self.now)['revision'],0)

    def test_plan_exhaustion_reports_actionable_terminal_state(self):
        request={**self.request,'max_plans':1}
        loop.init(self.root,'limited',self.write('limited-request',request),now=self.now)
        loop.plan(self.root,'limited',self.write('p1',self.proposal()),0,now=self.now)
        started=loop.start(self.root,'limited','inspect',1,now=self.now)
        result=loop.observe(self.root,'limited',self.write('limited-observation',self.observation(started,resolved_questions=[])),2,now=self.now)
        self.assertEqual(result['state'],'plan_limit')

    def test_stopped_action_limit_freezes_time_and_reason(self):
        request={**self.request,'max_actions':1}
        loop.init(self.root,'limited',self.write('limited-request',request),now=self.now)
        loop.plan(self.root,'limited',self.write('p1',self.proposal()),0,now=self.now)
        started=loop.start(self.root,'limited','inspect',1,now=self.now)
        loop.observe(self.root,'limited',self.write('limit-observation',self.observation(started)),2,now=self.now+timedelta(seconds=10))
        later=loop.status(self.root,'limited',now=self.now+timedelta(days=2))
        self.assertEqual(later['state'],'action_limit')
        self.assertEqual(later['elapsed_seconds_since_init'],10)
        self.assertFalse(later['budget_overrun'])

    def test_tiny_duration_cannot_publish_unserializable_ranking(self):
        proposal=self.proposal();proposal['actions'][0]['estimated_seconds']=1e-320
        with self.assertRaises(ValueError):self.plan(proposal)
        self.assertEqual(self.journal_bytes(),{})


if __name__=='__main__':unittest.main()
