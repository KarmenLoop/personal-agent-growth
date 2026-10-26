import argparse,json,sys
from pathlib import Path
from verify_handoff import verify
p=argparse.ArgumentParser();p.add_argument('--index',required=True,type=Path);a=p.parse_args()
base=a.index.resolve().parent
items=json.loads(a.index.read_text(encoding='utf-8'))['cases']
results=[]
for item in items:
    result,code=verify((base/item['archive']).resolve(),(base/item['manifest']).resolve())
    results.append({'case_id':item['case_id'],'result':result,'exit_code':code})
print(json.dumps({'results':results},ensure_ascii=False,indent=2))
