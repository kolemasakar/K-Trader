import json,hashlib,datetime
from pathlib import Path
from scripts.research.gerchik_cohort_readiness_v0_1 import rebuild_closed_weeks
from scripts.research.gerchik_historical_candidates_v0_1 import detect, inspect_later
import argparse
parser=argparse.ArgumentParser(description='Read-only historical candidate replay; JSON to stdout')
parser.add_argument('--data-root', required=True)
args=parser.parse_args()
root=Path(args.data_root)
report={'schema':'historical_candidates_v0.1','evaluated_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'period':['2025-09-25','2026-09-25'],'manifest_sha256':hashlib.sha256((root/'manifest.json').read_bytes()).hexdigest(),'scope':['LIMIT','CONSOLIDATION'],'series':[],'candidates':[],'prefix_checks':0,'prefix_failures':0,'independently_confirmed_levels':0,'strength_scores':None}
for symbol in ['BTCUSDT','ETHUSDT','SOLUSDT','XRPUSDT','BNBUSDT','ADAUSDT','DOGEUSDT']:
 path=root/'bundles'/symbol/'1d.jsonl'
 raw=path.read_bytes(); daily=[json.loads(x) for x in raw.splitlines() if x.strip()]
 weekly=rebuild_closed_weeks(daily,end_exclusive_ms=1790294400000)
 for tf,rows in [('D1',daily),('W1',weekly)]:
  candidates=detect(rows,tf)
  for n in range(1,len(rows)+1):
   expected=[x for x in candidates if x['known_at_ms']<=rows[n-1][6]+1]
   if detect(rows[:n],tf)!=expected: report['prefix_failures']+=1
   report['prefix_checks']+=1
  counts={kind:sum(x['primary_type']==kind for x in candidates) for kind in ['LIMIT','CONSOLIDATION','AMBIGUOUS']}
  report['series'].append(dict(symbol=symbol,timeframe=tf,bars=len(rows),counts=counts,d1_sha256=hashlib.sha256(raw).hexdigest()))
  for x in candidates:
   start=next(j for j,r in enumerate(rows) if r[0]==x['source_open_ms'])
   report['candidates'].append(dict(symbol=symbol,**x,formation_bars=rows[start:x['confirmation_index']+1],later_bars_observed=len(rows)-x['confirmation_index']-1,later=inspect_later(rows,x)))
print(json.dumps(report,sort_keys=True))
