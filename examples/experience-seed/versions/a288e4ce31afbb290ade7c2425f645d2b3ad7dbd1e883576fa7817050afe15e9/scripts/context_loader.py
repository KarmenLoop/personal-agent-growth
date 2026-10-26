"""Read the assigned skill and indexed lessons in one bounded, attributed operation."""
import argparse,hashlib,json
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--task',choices=['release','climate'],required=True);p.add_argument('--library',type=Path);a=p.parse_args()
strategy=Path(__file__).resolve().parents[1]
location=json.loads((strategy/'memory-location.json').read_text(encoding='utf-8'))
library=(a.library or (strategy / location['library'])).resolve()
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def indexed(relative):
 path=library/relative
 if path.is_symlink() or not path.resolve().is_relative_to(library):raise ValueError('Indexed path escapes library')
 return path
index=json.loads((library/'index.json').read_text(encoding='utf-8'));cards=[];observations=[];provenance={str(library/'index.json'):digest(library/'index.json')}
for entry in index['records'].values():
 if entry['domain'] not in {'offline-package-check','meta:cross-domain-evidence'}:continue
 path=indexed(entry['path'])
 if digest(path)!=entry['sha256']:raise ValueError('Experience record hash mismatch')
 card=json.loads(path.read_text(encoding='utf-8'));provenance[str(path)]=entry['sha256']
 cards.append({'domain':entry['domain'],'adopted':card.get('adopted'),'lessons':[{k:v for k,v in lesson.items() if k!='evidence'} for lesson in card.get('reflection',{}).get('lessons',[])],'generalization':card.get('generalization')})
for entry in index.get('observations',{}).values():
 if entry['domain'] not in {'offline-package-check','meta:cross-domain-evidence'}:continue
 path=indexed(entry['path'])
 if digest(path)!=entry['sha256']:raise ValueError('Observation hash mismatch')
 observation=json.loads(path.read_text(encoding='utf-8'));provenance[str(path)]=entry['sha256']
 observations.append({k:observation[k] for k in ['lesson','limitations','next_probe']})
profile=index['profiles'].get('offline-package-check');tool_binding={}
if profile:
 base=indexed(profile['path'])
 for name in ['batch_handoff.py','verify_handoff.py']:
  assigned=strategy/'scripts'/name;active=base/'scripts'/name
  tool_binding[name]={'assigned_sha256':digest(assigned),'active_sha256':digest(active)}
  if digest(assigned)!=digest(active):raise ValueError('Assigned package tool differs from the adopted profile')
result={'assigned_skill_path':str(strategy/'SKILL.md'),'assigned_skill':(strategy/'SKILL.md').read_text(encoding='utf-8'),'library_revision':index['revision'],'selected_prior_lessons':cards,'observations':observations,'source_hashes':provenance,'adopted_tool_binding':tool_binding,'task':a.task}
if a.task=='climate':result['source_notes']=Path('inputs/source-notes.md').read_text(encoding='utf-8');result['source_identity']=json.loads(Path('inputs/nasa-source.json').read_text(encoding='utf-8'))
print(json.dumps(result,ensure_ascii=False,indent=2))
