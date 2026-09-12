#!/usr/bin/env python3
from __future__ import annotations

import json, pathlib, statistics
from collections import defaultdict
from datetime import datetime

DATASET=pathlib.Path('/data/research/phase11g/profile_research_dataset_v0_20260911T204500Z_adaptive')
ROOT=pathlib.Path('/data/research/phase11g/profile_baselines_v0')

def ts(s):return datetime.fromisoformat(s.replace('Z','+00:00'))
def load_jsonl(p):
 with p.open() as f:return [json.loads(x) for x in f if x.strip()]
def load_bars(p):
 out=[]
 with p.open() as f:
  next(f)
  for line in f:
   d=json.loads(line);out.append({'open_time':ts(d['open_time']),'close_time':ts(d['close_time']),'high':float(d['high']),'low':float(d['low'])})
 return out
def stats(rows):
 rs=[r['net_R'] for r in rows];wins=[x for x in rs if x>0];loss=[x for x in rs if x<=0];gp=sum(wins);gl=-sum(loss)
 return {'n':len(rows),'win_rate':len(wins)/len(rows) if rows else None,'expectancy_R':statistics.fmean(rs) if rs else None,'PF_R':gp/gl if gl>0 else (999.0 if gp>0 else None),'median_MFE_R':statistics.median([r['mfe_R'] for r in rows]) if rows else None,'median_MAE_R':statistics.median([r['mae_R'] for r in rows]) if rows else None,'median_giveback_from_MFE_R':statistics.median([r['mfe_R']-r['net_R'] for r in rows]) if rows else None}
def enrich(profile,trades):
 tf='5m' if profile=='FAST' else '1h';cache={};out=[]
 for t in trades:
  s=t['symbol'];side=1 if t['side']=='LONG' else -1;entry=float(t['entry_price']);stop=float(t['stop_price']);risk=side*(entry-stop);et=ts(t['entry_time']);xt=ts(t['exit_time'])
  if s not in cache:cache[s]=load_bars(DATASET/'bundles'/s/f'{tf}.jsonl')
  mfe=mae=0.0;first={'.5R':None,'1R':None,'2R':None,'3R':None};bars_seen=0
  for b in cache[s]:
   if b['open_time']<et:continue
   if t['exit_reason'] in ('TIME_EXIT','GAP_STOP','GAP_TARGET'):
    if b['open_time']>=xt:break
   elif b['close_time']>xt:break
   fav=max(0,(b['high']-entry)/risk) if side==1 else max(0,(entry-b['low'])/risk);adv=max(0,(entry-b['low'])/risk) if side==1 else max(0,(b['high']-entry)/risk);bars_seen+=1;mfe=max(mfe,fav);mae=max(mae,adv)
   for val,key in ((.5,'.5R'),(1,'1R'),(2,'2R'),(3,'3R')):
    if first[key] is None and fav>=val:first[key]=bars_seen
  r=dict(t);r['mfe_R']=mfe;r['mae_R']=mae;r['first_reach_bar']=first;out.append(r)
 return out
def main():
 report={'schema_version':'ktrader.profile_baseline_diagnostics.v0','diagnostic_only':True,'holdout_opened':False,'production_action':False,'profiles':{}}
 for profile in ('FAST','SWING'):
  trades=enrich(profile,load_jsonl(ROOT/profile.lower()/'non_holdout_trades.jsonl'));by_reason=defaultdict(list);by_side=defaultdict(list)
  for r in trades:by_reason[r['exit_reason']].append(r);by_side[r['side']].append(r)
  loo={}
  for s in sorted({r['symbol'] for r in trades}):loo[s]=stats([r for r in trades if r['symbol']!=s])
  target=[r for r in trades if r['exit_reason'] in ('TARGET','GAP_TARGET')];stop=[r for r in trades if r['exit_reason'] in ('STOP','GAP_STOP')];time_exit=[r for r in trades if r['exit_reason']=='TIME_EXIT']
  report['profiles'][profile]={'overall':stats(trades),'by_exit_reason':{k:stats(v) for k,v in sorted(by_reason.items())},'by_side':{k:stats(v) for k,v in sorted(by_side.items())},'target_count':len(target),'stop_count':len(stop),'time_exit_count':len(time_exit),'target_median_time_to_1R_bars':statistics.median([r['first_reach_bar']['1R'] for r in target if r['first_reach_bar']['1R'] is not None]) if target else None,'stop_reached_0_5R_share':sum(r['first_reach_bar']['.5R'] is not None for r in stop)/len(stop) if stop else None,'time_exit_positive_share':sum(r['net_R']>0 for r in time_exit)/len(time_exit) if time_exit else None,'leave_one_symbol_out':loo,'interpretation':'diagnostic only; no subgroup/threshold promotion from this report'}
 p=ROOT/'diagnostics_v0.json';p.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n');print(json.dumps({k:{'overall':v['overall'],'target_count':v['target_count'],'stop_count':v['stop_count'],'time_exit_count':v['time_exit_count'],'stop_reached_0_5R_share':v['stop_reached_0_5R_share'],'time_exit_positive_share':v['time_exit_positive_share']} for k,v in report['profiles'].items()},indent=2,sort_keys=True))
if __name__=='__main__':main()
