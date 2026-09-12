#!/usr/bin/env python3
from __future__ import annotations

import argparse, glob, hashlib, json, pathlib, statistics, time, urllib.parse, urllib.request
from collections import defaultdict
from datetime import datetime, timezone

BASE=pathlib.Path('/data/research/phase11g')
LEDGER=BASE/'strategy_benchmark_v1/combined_rules/prospective_v2_2_ledger'
OUT=BASE/'strategy_benchmark_v1/combined_rules/prospective_v2_2_outcomes'
TARGET_R=3.0; MAX_HOLD=32; FEE_BPS=5.0; SLIP_BPS=2.0
ENDPOINT='https://fapi.binance.com/fapi/v1/fundingRate'

def utc(s):
 d=datetime.fromisoformat(s[:-1]+'+00:00' if s.endswith('Z') else s)
 if d.tzinfo is None or d.utcoffset() is None or d.utcoffset().total_seconds()!=0: raise ValueError('UTC required')
 return d.astimezone(timezone.utc)
def z(d): return d.astimezone(timezone.utc).isoformat().replace('+00:00','Z')
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def load_jsonl(p):
 with p.open() as f:return [json.loads(x) for x in f if x.strip()]
def load_bars(p):
 out=[]
 with p.open() as f:
  m=json.loads(next(f)); assert m.get('record_type')=='manifest'
  for line in f:
   d=json.loads(line);out.append({'open_time':utc(d['open_time']),'close_time':utc(d['close_time']),'open':float(d['open']),'high':float(d['high']),'low':float(d['low']),'close':float(d['close'])})
 return out
def adverse(raw,side,entry):
 s=SLIP_BPS/10000
 if entry:return raw*(1+s) if side==1 else raw*(1-s)
 return raw*(1-s) if side==1 else raw*(1+s)
def raw_entry(executed,side):
 s=SLIP_BPS/10000
 return executed/(1+s) if side==1 else executed/(1-s)
def funding(symbol,start,end):
 a=int(start.timestamp()*1000);b=int(end.timestamp()*1000);cursor=a;rows={}
 while cursor<=b:
  q=urllib.parse.urlencode({'symbol':symbol,'startTime':cursor,'endTime':b,'limit':1000});req=urllib.request.Request(ENDPOINT+'?'+q,headers={'User-Agent':'K-Trader-Research/1.0'})
  last_exc=None
  for n in range(4):
   try:
    with urllib.request.urlopen(req,timeout=20) as r: page=json.load(r)
    break
   except Exception as exc:
    last_exc=exc
    if n==3: raise
    time.sleep(.5*(2**n))
  if not page:break
  for r in page:
   t=int(r['fundingTime'])
   if a<=t<=b:rows[t]=r
  last=max(int(r['fundingTime']) for r in page);nxt=last+1
  if nxt<=cursor:raise RuntimeError('funding pagination stalled')
  cursor=nxt
  if len(page)<1000:break
 return [rows[k] for k in sorted(rows)]
def funding_cost(side,entry,start,end,rows):
 a=int(start.timestamp()*1000);b=int(end.timestamp()*1000);total=0.0
 for r in rows:
  t=int(r['fundingTime'])
  if a<=t<=b:
   x=float(r['fundingRate'])*float(r['markPrice'])/entry;total+=x if side==1 else -x
 return total
def latest_snapshot(as_of):
 xs=[]
 for raw in glob.glob(str(BASE/'v2_2_shadow_*/shadow_v1_1/summary.json')):
  p=pathlib.Path(raw);d=json.loads(p.read_text());prov=d.get('bundle_provenance') or {}
  if d.get('missing_symbols') or len(prov)!=int(d.get('panel_size') or 0):continue
  times=[utc(x['as_of']) for x in prov.values() if x.get('as_of')]
  if times and min(times)<=as_of:xs.append((min(times),p,d))
 if not xs:raise RuntimeError('no valid snapshot')
 xs.sort(key=lambda x:(x[0],str(x[1])));_,p,d=xs[-1];return p.parent.parent/'bundles',d
def resolve(e,bars,frows,as_of):
 side=1 if e['side']=='LONG' else -1;entry=float(e['entry_price']);stop=float(e['stop_price']);et=utc(e['entry_time']);risk=side*(entry-stop);target=entry+side*TARGET_R*risk
 if risk<=0:raise RuntimeError('bad risk')
 idx={b['open_time']:i for i,b in enumerate(bars)}
 if et not in idx:return {'setup_family_id':e['setup_family_id'],'status':'SOURCE_ENTRY_BAR_UNAVAILABLE','resolved':False}
 ei=idx[et];avail=[b for b in bars[ei:] if b['open_time']<as_of and b['close_time']<as_of];mfe=mae=0.0;times={k:None for k in ('0.5R','1R','2R','3R')};term=rx=xt=xi=None
 for off,b in enumerate(avail):
  j=ei+off
  if off>=MAX_HOLD:term,rx,xt,xi='TIME_EXIT',b['open'],b['open_time'],j;break
  if side==1:
   fav=max(0,(b['high']-entry)/risk);adv=max(0,(entry-b['low'])/risk);gs=b['open']<=stop;gt=b['open']>=target;sh=b['low']<=stop;th=b['high']>=target
  else:
   fav=max(0,(entry-b['low'])/risk);adv=max(0,(b['high']-entry)/risk);gs=b['open']>=stop;gt=b['open']<=target;sh=b['high']>=stop;th=b['low']<=target
  mfe=max(mfe,fav);mae=max(mae,adv)
  for v in (.5,1,2,3):
   k=f'{v:g}R'
   if times[k] is None and fav>=v:times[k]=z(b['close_time'])
  if gs:term,rx,xt,xi='GAP_STOP',b['open'],b['open_time'],j;break
  if gt:term,rx,xt,xi='GAP_TARGET',b['open'],b['open_time'],j;break
  if sh:term,rx,xt,xi='STOP',stop,b['close_time'],j;break
  if th:term,rx,xt,xi='TARGET',target,b['close_time'],j;break
 out={'schema_version':'ktrader.candidate_v2_2.prospective_outcome.v1','strategy_id':'candidate_rule_set_v2_2','symbol':e['symbol'],'side':e['side'],'setup_family_id':e['setup_family_id'],'signal_bar_open_time':e['signal_bar_open_time'],'entry_time':e['entry_time'],'entry_price':entry,'stop_price':stop,'target_price_3R':target,'initial_risk_pct':risk/entry,'bars_observed':len(avail),'mfe_R':mfe,'mae_R':mae,'time_to_R':times,'terminal_state':term,'resolved':term is not None,'as_of':z(as_of),'holdout_opened':False,'production_action':False,'clean_break_no_revisit':e.get('clean_break_no_revisit'),'level_v2_h1_open_space':e.get('level_v2_h1_open_space'),'level_v2_h1_next_level_R':e.get('level_v2_h1_next_level_R')}
 if term is None:out['outcome_status']='CENSORED_OPEN';return out
 xp=adverse(rx,side,False);gross=(xp-entry)/entry if side==1 else (entry-xp)/entry;fee=FEE_BPS/10000*(1+xp/entry);fund=funding_cost(side,entry,et,xt,frows);net=gross-fee-fund;re=raw_entry(entry,side);rawgross=(rx-re)/re if side==1 else (re-rx)/re
 out.update({'outcome_status':'RESOLVED','exit_time':z(xt),'raw_exit_price':rx,'executed_exit_price':xp,'hold_bars':xi-ei+1,'gross_return_pct':gross,'fee_pct':fee,'funding_pct':fund,'slippage_return_drag_pct':rawgross-gross,'net_return_pct':net,'realized_R':net/(risk/entry),'win_net':net>0});return out
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--as-of',required=True);args=ap.parse_args();as_of=utc(args.as_of);OUT.mkdir(parents=True,exist_ok=True)
 events=[x for x in load_jsonl(LEDGER/'deduplicated_events.jsonl') if x.get('status')=='ELIGIBLE_SHADOW_SETUP'];groups=defaultdict(list)
 for e in events:groups[e['setup_family_id']].append(e)
 for rows in groups.values():rows.sort(key=lambda e:(e.get('entry_time') or '',e.get('signal_bar_open_time') or '',e.get('symbol') or '',e.get('side') or ''))
 bundle_root,snap=latest_snapshot(as_of);bars_cache={};fund_cache={};obs=[]
 for fid in sorted(groups):
  for i,e in enumerate(groups[fid]):
   s=e['symbol']
   if s not in bars_cache:bars_cache[s]=load_bars(bundle_root/s/'15m.jsonl')
   if s not in fund_cache:fund_cache[s]=funding(s,min(utc(x['entry_time']) for x in events if x['symbol']==s),as_of)
   r=resolve(e,bars_cache[s],fund_cache[s],as_of);r['family_role']='PRIMARY_REPRESENTATIVE' if i==0 else 'CORRELATED_DIAGNOSTIC_ONLY';r['counts_as_independent_family_evidence']=i==0;obs.append(r)
 families=[]
 for fid in sorted(groups):
  members=[x for x in obs if x['setup_family_id']==fid];p=next(x for x in members if x['family_role']=='PRIMARY_REPRESENTATIVE');families.append({'setup_family_id':fid,'primary_symbol':p['symbol'],'primary_side':p['side'],'primary_entry_time':p['entry_time'],'observation_count':len(members),'resolved':p['resolved'],'terminal_state':p.get('terminal_state'),'realized_R':p.get('realized_R'),'mfe_R':p.get('mfe_R'),'mae_R':p.get('mae_R'),'family_evidence_status':'RESOLVED_PRIMARY' if p['resolved'] else 'UNRESOLVED_PRIMARY'})
 op=OUT/'observations.jsonl';fp=OUT/'families.jsonl'
 with op.open('w') as f:
  for r in sorted(obs,key=lambda x:(x.get('entry_time',''),x.get('symbol',''))):f.write(json.dumps(r,sort_keys=True)+'\n')
 with fp.open('w') as f:
  for r in families:f.write(json.dumps(r,sort_keys=True)+'\n')
 resolved=[x for x in families if x['resolved']];rs=[x['realized_R'] for x in resolved if x.get('realized_R') is not None];wins=sum(x>0 for x in rs);ls=json.loads((LEDGER/'ledger_summary.json').read_text())
 report={'schema_version':'ktrader.candidate_v2_2.prospective_family_outcomes.v1','strategy_id':'candidate_rule_set_v2_2','as_of':z(as_of),'holdout_opened':False,'production_action':False,'family_semantics':'earliest eligible entry is immutable primary representative','target_R':TARGET_R,'max_hold_bars_m15':MAX_HOLD,'fee_bps_per_side':FEE_BPS,'slippage_bps_per_execution_side':SLIP_BPS,'latest_bundle_root':str(bundle_root),'latest_bundle_set_sha256':snap.get('bundle_set_sha256'),'frozen_harness_sha256_values':ls.get('frozen_harness_sha256_values'),'protocol_sha256_values':ls.get('protocol_sha256_values'),'eligible_observation_count':len(obs),'unique_family_count':len(families),'resolved_primary_family_count':len(resolved),'unresolved_primary_family_count':len(families)-len(resolved),'resolved_win_count':wins,'resolved_loss_count':len(rs)-wins,'resolved_win_rate':wins/len(rs) if rs else None,'resolved_expectancy_R':statistics.fmean(rs) if rs else None,'observation_sha256':sha(op),'family_sha256':sha(fp),'evidence_status':'OBSERVATION_ONLY_LT_30_RESOLVED_FAMILIES' if len(resolved)<30 else ('DIAGNOSTIC_30_49_RESOLVED_FAMILIES' if len(resolved)<50 else ('HYPOTHESIS_ONLY_50_99_RESOLVED_FAMILIES' if len(resolved)<100 else 'RECALIBRATION_PROPOSAL_ELIGIBLE_BY_SAMPLE_ONLY'))}
 sp=OUT/'summary.json';sp.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n');print(json.dumps(report,indent=2,sort_keys=True));print('REPORT',sp,sha(sp))
if __name__=='__main__':main()
