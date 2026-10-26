"""Compute descriptive annual-series facts; no expected answers or verdicts."""
import argparse,csv,json,hashlib,statistics
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('source',type=Path);p.add_argument('output',type=Path);a=p.parse_args()
rows=list(csv.DictReader(a.source.read_text().splitlines()[1:])); pairs=[];missing=[]
for r in rows:
 y=int(r['Year'])
 if y<1990: continue
 v=None if r['J-D']=='***' else float(r['J-D'])
 pairs.append((y,v))
 if v is None:missing.append(y)
valid=[(y,v) for y,v in pairs if v is not None]; xs,ys=zip(*valid)
xbar=statistics.mean(xs);ybar=statistics.mean(ys)
slope=sum((x-xbar)*(y-ybar) for x,y in valid)/sum((x-xbar)**2 for x in xs)*10
means={str(lo)+'-'+str(lo+9):statistics.mean(v for y,v in valid if lo<=y<=lo+9) for lo in [2000,2010]}
a.output.mkdir(parents=True,exist_ok=True)
with (a.output/'annual.csv').open('w',newline='') as f:
 w=csv.writer(f);w.writerow(['year','annual_anomaly_c']);w.writerows((y,'' if v is None else v) for y,v in pairs)
result={'source_sha256':hashlib.sha256(a.source.read_bytes()).hexdigest(),'unit':'degrees Celsius anomaly','reference_period':'1951-1980','latest_complete_year':max(xs),'decade_means_c':means,'decade_difference_c':means['2010-2019']-means['2000-2009'],'trend_c_per_decade':slope,'trend_start_year':1990,'trend_end_year':max(xs),'incomplete_years':missing,'trend_method':'ordinary least squares on complete annual J-D values; intercept included'}
(a.output/'climate-summary.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result))
