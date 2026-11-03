#!/usr/bin/env python3
"""Controlled workshop fixture. Not a human-learning trial or reviewed delivery."""
import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--skill', required=True, type=Path)
    parser.add_argument('--work', required=True, type=Path)
    args = parser.parse_args()
    skill, work = args.skill.resolve(), args.work.resolve()
    if work.exists():
        parser.error('--work must be a new directory; retain earlier attempts')
    for filename in ['adaptive_learning.py', 'experience_transfer.py']:
        if not (skill/'scripts'/filename).is_file():
            parser.error('Skill directory does not contain both adaptive helpers')
    work.mkdir(parents=True)
    root = work/'learning'
    root.mkdir()
    def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
    def artifact(p): return {'path':str(p.relative_to(root)), 'sha256':digest(p)}
    def document(name, data, body):
        p = root/name
        p.write_text('---\n'+json.dumps(data,indent=2)+'\n---\n'+body+'\n')
        return p
    receipts = []
    def run(label, helper, command, *flags, expected=0):
        argv = [sys.executable, '-B', str(skill/'scripts'/helper), command, '--root', str(root), *map(str,flags)]
        begun, tick = dt.datetime.now(dt.timezone.utc).isoformat(), time.monotonic()
        process = subprocess.run(argv, capture_output=True)
        folder = work/label
        folder.mkdir()
        (folder/'stdout.txt').write_bytes(process.stdout)
        (folder/'stderr.txt').write_bytes(process.stderr)
        row = {'label':label,'argv':argv,'started_at':begun,'ended_at':dt.datetime.now(dt.timezone.utc).isoformat(),'seconds':time.monotonic()-tick,'exit':process.returncode,'expected_exit':expected,'program_sha256':digest(skill/'scripts'/helper),'stdout_sha256':digest(folder/'stdout.txt'),'stderr_sha256':digest(folder/'stderr.txt')}
        (folder/'receipt.json').write_text(json.dumps(row,indent=2)+'\n')
        receipts.append(row)
        print(f'{label}: exit {process.returncode} (expected {expected})', flush=True)
        if process.returncode != expected:
            raise RuntimeError(process.stderr.decode(errors='replace'))
        return json.loads(process.stdout) if process.returncode == 0 else None
    source = root/'fixture-source.txt'
    source.write_text('Controlled source fixture: a declared mechanism is a hypothesis.\n')
    exp = document('experience-input.md',{'id':'fixture-evidence-binding','type':'mechanism-experience','source_task_id':'fixture-source','domain':'software-validation','problem_structure':['changing-evidence'],'mechanisms':['evidence-binding'],'required_conditions':{'decision-can-be-revised':True},'exceptions':['Fixture data cannot prove human learning or a general causal mechanism.'],'intervention':'Bind a revisable decision to inspected source bytes.','explanation':'Controlled example for understanding retrieval fields.','validation':'hypothesis','executor':'workshop-fixture','reviewer':None,'artifacts':[artifact(source)]},'CONTROLLED FIXTURE: not an observed historical task.')
    run('01-add','experience_transfer.py','add','--experience',exp)
    query = document('query.md',{'id':'fixture-query','type':'transfer-query','task_id':'fixture-current','domain':'instructional-design','problem_structure':['changing-evidence'],'mechanisms':['evidence-binding'],'facts':{'decision-can-be-revised':True},'keywords':['source']},'Matching labels demonstrate retrieval only, not successful transfer.')
    retrieved=run('02-retrieve','experience_transfer.py','retrieve','--query',query)
    assert len(retrieved['candidates']) == 1 and retrieved['candidates'][0]['eligible_for_probe']
    request=document('request-input.md',{'id':'fixture-request','type':'learning-request','goal':'Check that start records intent and the host separately creates an artifact.','domain':'contributor-workshop','acceptance':['A real host action produces an evidence-bound observation.'],'budget_seconds':300,'max_actions':3,'max_plans':4,'allowed_actions':['experiment','reflect','deliver']},'Controlled practice. No human learning, independent review, or actual delivery is asserted.')
    run('03-init','adaptive_learning.py','init','--id','practice','--request',request)
    plan=document('plan-input.md',{'id':'fixture-plan','type':'learning-plan','based_on_revision':0,'unknowns':[{'id':'host-action','question':'Does start create the output file, or does the host need to act?','importance':1.0,'blocking':True}],'actions':[{'id':'write-evidence','kind':'experiment','question_ids':['host-action'],'description':'Start, inspect absent output, then have the host write it.','expected_information_gain':0.8,'estimated_seconds':30,'preconditions':[]}],'experience_refs':[retrieved['candidates'][0]['snapshot_ref']],'artifacts':[artifact(source)]},'Prediction: start will not create host-output.txt. The host must execute the action.')
    run('04-plan','adaptive_learning.py','plan','--id','practice','--proposal',plan,'--expected-revision','0')
    run('05-stale-start','adaptive_learning.py','start','--id','practice','--action','write-evidence','--expected-revision','0',expected=2)
    started=run('06-start','adaptive_learning.py','start','--id','practice','--action','write-evidence','--expected-revision','1')
    output=root/'host-output.txt'
    assert not output.exists(), 'Disconfirmed: output unexpectedly exists before host action'
    # This is the actual host action. The adaptive helper does not run it.
    host_start = dt.datetime.now(dt.timezone.utc).isoformat()
    output.write_text('The host wrote this file after the helper recorded start.\n')
    host_receipt=root/'host-action.json'
    host_receipt.write_text(json.dumps({'operation':'Path.write_text','target':'host-output.txt','started_at':host_start,'ended_at':dt.datetime.now(dt.timezone.utc).isoformat(),'output_sha256':digest(output),'result':'written and read back','readback':output.read_text()},indent=2)+'\n')
    observation=document('observation-input.md',{'id':'fixture-observation','type':'learning-observation','start_id':started['pending']['start_id'],'action_id':'write-evidence','outcome':'progress','finding':'After start the output was absent; an actual host file write created it and read it back.','hypothesis_change':'Retain the distinction between recorded start and host execution.','resolved_questions':['host-action'],'artifacts':[artifact(output),artifact(host_receipt)],'executor':'workshop-fixture','reviewer':None,'cost':{'tokens':None,'usd':None},'acceptance_checks':{}},'Actual local fixture execution only. Tokens and USD unknown. No delivery or teaching effectiveness is claimed.')
    run('07-observe','adaptive_learning.py','observe','--id','practice','--observation',observation,'--expected-revision','2')
    final=run('08-status','adaptive_learning.py','status','--id','practice')
    assert final['revision']==3 and final['state']=='active' and final['pending'] is None
    assert final['last_observation']['outcome']=='progress'
    (work/'summary.json').write_text(json.dumps({'scope':'controlled CLI practice, not a human-learning trial','commands':len(receipts),'expected_stale_failures':1,'final_revision':final['revision'],'final_state':final['state'],'source_program':{'path':str(Path(__file__).resolve()),'sha256':digest(Path(__file__))},'tokens':None,'usd':None},indent=2)+'\n')
    print('Practice complete: revision 3, active, progress; no reviewed delivery asserted.')
if __name__ == '__main__': main()
