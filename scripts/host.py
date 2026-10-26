#!/usr/bin/env python3
# Copyright 2026 KarmenLoop. SPDX-License-Identifier: AGPL-3.0-only
"""Persist task checkpoints, verify artifacts and hand responsibility to another host."""
from host_support import Database,need,identifier,content,stamp,file_record,atomic,schema,string,integer,array,main
import json

BASE={'task_id':string(80)}
TOOLS=[
 {'name':'growth_start','description':'Create a durable task owned by this configured host.','inputSchema':schema({**BASE,'goal':string(2000),'acceptance':string(2000)},['task_id','goal','acceptance'])},
 {'name':'growth_read','description':'Recover the current checkpoint and verify referenced artifact hashes.','inputSchema':schema(BASE,['task_id']),'annotations':{'readOnlyHint':True}},
 {'name':'growth_checkpoint','description':'Commit an evidence-backed checkpoint using the current writer and revision.','inputSchema':schema({**BASE,'expected_revision':integer(),'phase':string(100),'next_action':string(2000),'artifacts':array(string(300)),'observation':string(4000)},['task_id','expected_revision','phase','next_action','artifacts','observation'])},
 {'name':'growth_handoff','description':'Transfer write responsibility to a named host, preserving current evidence.','inputSchema':schema({**BASE,'expected_revision':integer(),'target_host':string(80)},['task_id','expected_revision','target_host'])},
 {'name':'growth_export','description':'Export the current checkpoint and evidence validation as a local handoff.','inputSchema':schema(BASE,['task_id'])}]

def read(db,key,workspace):
 p=db.get(key);need(p,'TASK_MISSING','Start this task first.');out=json.loads(json.dumps(p));issues=[]
 for old in p['artifacts']:
  try:
   current=file_record(workspace,old['path'])
   if current!=old:issues.append({'path':old['path'],'issue':'changed'})
  except ValueError:issues.append({'path':old['path'],'issue':'missing or outside workspace'})
 out['evidence_current']=not issues;out['evidence_issues']=issues;return out

def dispatch(name,a,args):
 db=Database(args.root);task=identifier(a['task_id']);key='task:'+task;host=identifier(args.host_id)
 try:
  if name=='growth_read':return read(db,key,args.workspace)
  if name=='growth_export':
   value=read(db,key,args.workspace);path=db.root/(task+'-handoff.json');atomic(path,json.dumps(value,indent=2)+'\n');return {'path':str(path),'revision':value['state_revision'],'evidence_current':value['evidence_current']}
  def update():
   value=db.get(key)
   if name=='growth_start':
    need(value is None,'TASK_EXISTS','The existing task was preserved.');value={'task_id':task,'goal':content(a['goal']),'acceptance':content(a['acceptance']),'goal_revision':1,'state_revision':1,'writer':host,'phase':'started','next_action':'Create the first evidence-backed checkpoint.','artifacts':[],'observations':[],'handoffs':[],'schedule':{'status':'not_registered','backend_id':None}};db.put(key,value);db.event('task.started',{'task':task,'host':host});return value
   need(value,'TASK_MISSING','Start this task first.');need(value['writer']==host,'NOT_CURRENT_WRITER','The configured host does not own the current task.');need(value['state_revision']==a['expected_revision'],'STALE_REVISION','Read the latest task before writing.')
   if name=='growth_checkpoint':
    files=[file_record(args.workspace,p) for p in a['artifacts']];value['artifacts']=files;value['phase']=content(a['phase']);value['next_action']=content(a['next_action']);value['observations'].append({'host':host,'at':stamp(),'text':content(a['observation']),'artifact_hashes':[x['sha256'] for x in files]})
   else:
    checked=read(db,key,args.workspace);need(checked['evidence_current'],'EVIDENCE_CHANGED','Recheck changed artifacts before handoff.');target=identifier(a['target_host']);need(target!=host,'SAME_HOST','Choose a different receiving host.');value['writer']=target;value['handoffs'].append({'from':host,'to':target,'at':stamp(),'read_revision':value['state_revision']})
   value['state_revision']+=1;db.put(key,value);db.event(name,{'task':task,'host':host,'revision':value['state_revision']});return value
  return db.transaction(update)
 finally:db.close()

if __name__=='__main__':raise SystemExit(main('personal_agent_growth','0.4.1',TOOLS,dispatch))
