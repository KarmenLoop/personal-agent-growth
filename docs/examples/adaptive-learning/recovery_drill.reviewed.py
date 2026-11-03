#!/usr/bin/env python3
"""Controlled local recovery exercise; no production incident or delivery claim.
Python 3.11+, standard library. Run from anywhere with --skill and fresh --work.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys


def utc():
    return datetime.now(timezone.utc).isoformat()


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--skill', type=Path, required=True)
    parser.add_argument('--work', type=Path, required=True)
    args = parser.parse_args()
    skill, work = args.skill.resolve(), args.work.resolve()
    helper = skill / 'scripts' / 'adaptive_learning.py'
    if not helper.is_file():
        parser.error('--skill must contain scripts/adaptive_learning.py')
    if sys.version_info < (3, 11):
        parser.error('Python 3.11+ is required')
    if work == skill or skill in work.parents:
        parser.error('--work must be outside the skill checkout')
    work.mkdir(parents=True, exist_ok=False)  # Never overwrite an earlier attempt.
    memory = work / 'memory'
    inputs = work / 'inputs'
    receipts = work / 'receipts'
    inputs.mkdir(); receipts.mkdir(); memory.mkdir()
    started = utc()
    sequence = 0
    calls = []

    def save(name, item):
        path = inputs / (name + '.md')
        path.write_text('---\n' + json.dumps(item, indent=2) + '\n---\nControlled local drill.\n', encoding='utf-8')
        return path

    def call(label, run, command, *extra, expected=0, expected_error=None):
        nonlocal sequence
        sequence += 1
        folder = receipts / f'{sequence:02d}-{label}'
        folder.mkdir()
        argv = [sys.executable, '-B', str(helper), command, '--root', str(memory), '--id', run, *map(str, extra)]
        begin = utc()
        result = subprocess.run(argv, capture_output=True, text=True, timeout=30)
        end = utc()
        (folder / 'stdout.txt').write_text(result.stdout, encoding='utf-8')
        (folder / 'stderr.txt').write_text(result.stderr, encoding='utf-8')
        receipt = {'argv': argv, 'start_utc': begin, 'end_utc': end,
                   'exit_code': result.returncode, 'expected_exit': expected,
                   'helper_sha256': sha(helper), 'stdout_sha256': sha(folder / 'stdout.txt'),
                   'stderr_sha256': sha(folder / 'stderr.txt')}
        (folder / 'receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
        calls.append({'label': label, 'exit_code': result.returncode, 'expected_exit': expected})
        if result.returncode != expected:
            raise RuntimeError(f'{label}: unexpected exit {result.returncode}; see {folder}')
        if expected_error is not None:
            actual_error = json.loads(result.stderr).get('error')
            if actual_error != expected_error:
                raise RuntimeError(f'{label}: wrong rejection diagnostic {actual_error!r}')
        return json.loads(result.stdout) if result.stdout.strip() else None

    def initialize(run):
        request = save(run + '-request', {'id': run, 'type': 'learning-request',
            'goal': 'Reconcile one controlled file effect without repeating it', 'domain': 'operations-drill',
            'acceptance': ['single effect reconciled'], 'budget_seconds': 300, 'max_actions': 1,
            'allowed_actions': ['tool']})
        initial = call(run + '-init', run, 'init', '--request', request)
        assert initial['state'] == 'active' and initial['pending'] is None
        plan = save(run + '-plan', {'id': run + '-plan', 'type': 'learning-plan', 'based_on_revision': 0,
            'unknowns': [{'id': 'effect', 'question': 'Did the single intended file effect occur?', 'importance': 1}],
            'actions': [{'id': 'write-once', 'kind': 'tool', 'question_ids': ['effect'],
                'description': 'Host writes one local effect with its start token', 'expected_information_gain': 1,
                'estimated_seconds': 1, 'preconditions': []}], 'experience_refs': [], 'artifacts': []})
        call(run + '-plan', run, 'plan', '--proposal', plan, '--expected-revision', 0)
        result = call(run + '-start', run, 'start', '--action', 'write-once', '--expected-revision', 1)
        assert result['state'] == 'awaiting_observation'
        return result, plan

    try:
        state, plan = initialize('recovery')
        original_start = state['pending']['start_id']
        effect = memory / 'effect.jsonl'
        assert not effect.exists(), 'start must not execute the file write'
        payload = {'start_id': original_start, 'operation': 'create-local-recovery-receipt', 'effect_count': 1}
        with effect.open('x', encoding='utf-8') as handle:
            handle.write(json.dumps(payload, sort_keys=True) + '\n')
            handle.flush()
            os.fsync(handle.fileno())
        initial_hash = sha(effect)
        (work / 'controlled-uncertainty.json').write_text(json.dumps({
            'at': utc(), 'kind': 'deliberately-withheld-outcome-observation',
            'explanation': 'The host wrote a real local file. We deliberately mark the result unknown before recovery inspection. No real crash, network loss, or infrastructure loss occurred.',
            'start_id': original_start}, indent=2) + '\n')
        def observation(name, token, outcome, finding, artifacts, resolved):
            return save(name, {'id': name, 'type': 'learning-observation', 'start_id': token,
                'action_id': 'write-once', 'outcome': outcome, 'finding': finding,
                'hypothesis_change': 'Inspect the actual effect before deciding whether anything may run again.',
                'resolved_questions': resolved, 'artifacts': artifacts, 'executor': 'controlled-drill-host',
                'reviewer': None, 'cost': {'tokens': None, 'usd': None}, 'acceptance_checks': {}})
        unknown = observation('original-unknown', original_start, 'unknown',
            'Controlled uncertainty: outcome observation deliberately withheld pending recovery inspection.', [], [])
        state = call('record-unknown', 'recovery', 'observe', '--observation', unknown, '--expected-revision', 2)
        assert state['state'] == 'needs_reconciliation' and state['pending']['start_id'] == original_start
        pending_before = state['pending']
        pending_proposal = json.loads(plan.read_text(encoding='utf-8').split('---', 2)[1])
        pending_proposal['id'] = 'recovery-pending-plan'
        pending_proposal['based_on_revision'] = 3
        pending_plan = save('recovery-pending-plan', pending_proposal)
        call('replan-while-unknown-rejected', 'recovery', 'plan', '--proposal', pending_plan, '--expected-revision', 3, expected=2, expected_error='Run cannot accept a new plan')
        foreign, _ = initialize('foreign-token')
        foreign_start = foreign['pending']['start_id']
        assert foreign_start != original_start
        # This second run only provides a genuine different start token. It has no file effect.
        wrong = observation('foreign-token-observation', foreign_start, 'unknown', 'This token belongs to another controlled run.', [], [])
        call('foreign-token-rejected', 'recovery', 'observe', '--observation', wrong, '--expected-revision', 3, expected=2, expected_error='Observation does not match the pending start token')
        unchanged = call('verify-rejection-no-mutation', 'recovery', 'status')
        assert unchanged['revision'] == 3 and unchanged['pending'] == pending_before
        assert unchanged['last_observation']['id'] == 'original-unknown'
        # Recovery reads actual file identity/content. It never calls the write operation again.
        rows = effect.read_text(encoding='utf-8').splitlines()
        assert len(rows) == 1 and json.loads(rows[0]) == payload and sha(effect) == initial_hash
        inspect = {'at': utc(), 'effect_path': 'memory/effect.jsonl', 'start_id': original_start,
                   'row_count': len(rows), 'effect_sha256': sha(effect),
                   'finding': 'Exactly one expected local effect is present and matches the original pending start.'}
        (work / 'effect-inspection.json').write_text(json.dumps(inspect, indent=2) + '\n')
        settled = observation('settle-original-start', original_start, 'progress',
            'Read one exact matching file effect. Reconcile the original pending action without executing it again.',
            [{'path': 'effect.jsonl', 'sha256': sha(effect)}], ['effect'])
        final = call('settle-original', 'recovery', 'observe', '--observation', settled, '--expected-revision', 3)
        assert final['pending'] is None and final['actions_started'] == 1 and final['state'] == 'action_limit'
        assert sha(effect) == initial_hash and len(effect.read_text().splitlines()) == 1
        # Settle the foreign fixture truthfully: the host intentionally performed no external effect.
        no_effect = memory / 'foreign-no-effect.txt'
        no_effect.write_text('Controlled foreign run: no intended external effect was attempted.\n')
        failed = observation('foreign-not-executed', foreign_start, 'failed', 'Token fixture only; external action was deliberately not executed.',
            [{'path': no_effect.name, 'sha256': sha(no_effect)}], [])
        call('close-foreign-fixture', 'foreign-token', 'observe', '--observation', failed, '--expected-revision', 2)
        summary = {'started_at': started, 'ended_at': utc(), 'controlled_scenario': True,
            'native_tokens': None, 'native_usd': None, 'calls': calls,
            'checks': {'unique_start_binding': True, 'pending_gate_diagnostic_verified': True, 'same_pending_start_during_unknown': True,
                'foreign_token_rejected_without_mutation': True, 'unknown_journal_event_retained': True,
                'one_file_effect_no_repeat': True, 'settled_original_start': True,
                'action_limit_after_settlement': True},
            'final_state': final['state'], 'final_revision': final['revision'], 'original_start': original_start,
            'foreign_start': foreign_start, 'effect_sha256_before': initial_hash, 'effect_sha256_after': sha(effect),
            'scope': 'Controlled local file effect and actual helper behavior only. No production failure, human learning, native wakeup, authenticated reviewer, or delivered-run claim.'}
        (work / 'summary.json').write_text(json.dumps(summary, indent=2) + '\n')
        manifest = {p.relative_to(work).as_posix(): sha(p) for p in sorted(work.rglob('*')) if p.is_file()}
        (work / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
        print(json.dumps(summary, indent=2))
    except BaseException as exc:
        (work / 'failure.json').write_text(json.dumps({'at': utc(), 'type': type(exc).__name__, 'message': str(exc), 'calls': calls}, indent=2) + '\n')
        raise


if __name__ == '__main__':
    main()
