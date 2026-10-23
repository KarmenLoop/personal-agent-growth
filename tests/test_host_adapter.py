import json,subprocess,sys,tempfile,unittest,time,os
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SCRIPT=ROOT/'scripts/host.py'
class HostTest(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.base=Path(self.tmp.name);self.workspace=self.base/'workspace';self.workspace.mkdir();self.data=self.base/'private'
 def tearDown(self):self.tmp.cleanup()
 def argv(self,host='codex',subject=None):return [sys.executable,str(SCRIPT),'--root',str(self.data),'--workspace',str(self.workspace),'--host-id',host]+(['--subject',subject] if subject else [])
 def call(self,name,value,host='codex',subject=None,code=0):
  p=subprocess.run(self.argv(host,subject)+['call',name],input=json.dumps(value),text=True,capture_output=True,timeout=80)
  self.assertEqual(p.returncode,code,p.stdout+p.stderr);return json.loads(p.stdout if code==0 else p.stderr)

 def test_handoff_recovery_writer_and_evidence(self):
  self.call('growth_start',{'task_id':'tutorial','goal':'Verify real delivery','acceptance':'Artifact remains readable'})
  (self.workspace/'result.txt').write_text('real artifact')
  self.call('growth_checkpoint',{'task_id':'tutorial','expected_revision':1,'phase':'verified','next_action':'Review in Cursor','artifacts':['result.txt'],'observation':'The command produced this artifact.'})
  self.call('growth_handoff',{'task_id':'tutorial','expected_revision':2,'target_host':'cursor'})
  r=self.call('growth_read',{'task_id':'tutorial'},host='cursor');self.assertEqual(r['writer'],'cursor');self.assertTrue(r['evidence_current'])
  a={'task_id':'tutorial','expected_revision':3,'phase':'reviewed','next_action':'Export','artifacts':['result.txt'],'observation':'Read from the receiving host.'}
  self.assertEqual(self.call('growth_checkpoint',a,code=2)['code'],'NOT_CURRENT_WRITER')
  a['expected_revision']=2;self.assertEqual(self.call('growth_checkpoint',a,host='cursor',code=2)['code'],'STALE_REVISION');a['expected_revision']=3;self.call('growth_checkpoint',a,host='cursor')
  export=self.call('growth_export',{'task_id':'tutorial'},host='cursor');self.assertTrue(Path(export['path']).is_file())
  (self.workspace/'result.txt').write_text('tampered');self.assertFalse(self.call('growth_read',{'task_id':'tutorial'})['evidence_current'])
  self.assertEqual(self.call('growth_handoff',{'task_id':'tutorial','expected_revision':4,'target_host':'codex'},host='cursor',code=2)['code'],'EVIDENCE_CHANGED')

if __name__=='__main__':unittest.main()
