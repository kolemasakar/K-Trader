#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import pathlib
import statistics

BASE_PATH = pathlib.Path('/data/research/phase11g/strategy_benchmark_v1/harness/candidate_v2_backtest.py')
sp = importlib.util.spec_from_file_location('candidate_v2_base', BASE_PATH)
b = importlib.util.module_from_spec(sp)
sp.loader.exec_module(b)

ROOT = b.ROOT
MIN_H1_SEP_ATR = 0.20
MAX_SIGNAL_BODY_FRAC = 0.60
MIN_RISK_PCT = 0.0125

_base_signal = b.signal_at

def signal_at(i,m15,mx,h1,hx,h1cts):
    r = _base_signal(i,m15,mx,h1,hx,h1cts)
    if r is None:
        return None
    f = r['features']
    if f['h1_ema_sep_atr'] < MIN_H1_SEP_ATR:
        return None
    if f['signal_body_fraction'] > MAX_SIGNAL_BODY_FRAC:
        return None
    return r

b.signal_at = signal_at


def backtest_symbol(symbol,m15,h1,funding,start,end,bps):
    mx=b.indicators(m15); hx=b.indicators(h1); h1cts=[x['close_dt'] for x in h1]
    trades=[]; pos=None; pending=None; pending_exit=False; last_episode=set(); censored=0
    for i in range(max(1,start-1),end):
        bar=m15[i]
        if pos is not None and pending_exit:
            trades.append(b.finish(symbol,pos,i,bar['open_dt'],bar['open'],'TIME_EXIT',bps,funding)); pos=None; pending_exit=False
        if pos is None and pending is not None and i>=start:
            side=pending['side']; ep=b.adverse(bar['open'],side,True,bps); stop=pending['stop_raw']; dist=side*(ep-stop)
            risk_pct=dist/ep if ep>0 else 0.0
            if dist>0 and risk_pct>=MIN_RISK_PCT and pending['episode_key'] not in last_episode:
                pos={'side':side,'entry_i':i,'entry_time':bar['open_dt'],'entry':ep,'stop':stop,'target':ep+side*b.TARGET_R*dist,
                     'risk_pct':risk_pct,'episode_key':pending['episode_key'],'features':pending['features']}
                last_episode.add(pending['episode_key'])
            pending=None
        if pos is not None:
            gap_stop=(pos['side']==1 and bar['open']<=pos['stop']) or (pos['side']==-1 and bar['open']>=pos['stop'])
            gap_target=(pos['side']==1 and bar['open']>=pos['target']) or (pos['side']==-1 and bar['open']<=pos['target'])
            if gap_stop:
                trades.append(b.finish(symbol,pos,i,bar['open_dt'],bar['open'],'GAP_STOP',bps,funding)); pos=None
            elif gap_target:
                trades.append(b.finish(symbol,pos,i,bar['open_dt'],bar['open'],'GAP_TARGET',bps,funding)); pos=None
            else:
                sh=(pos['side']==1 and bar['low']<=pos['stop']) or (pos['side']==-1 and bar['high']>=pos['stop'])
                th=(pos['side']==1 and bar['high']>=pos['target']) or (pos['side']==-1 and bar['low']<=pos['target'])
                if sh:
                    trades.append(b.finish(symbol,pos,i,bar['close_dt'],pos['stop'],'STOP',bps,funding)); pos=None
                elif th:
                    trades.append(b.finish(symbol,pos,i,bar['close_dt'],pos['target'],'TARGET',bps,funding)); pos=None
        if i>=end-1:
            continue
        if pos is not None:
            if i-pos['entry_i']+1 >= b.MAX_HOLD_BARS:
                pending_exit=True
        elif pending is None:
            s=signal_at(i,m15,mx,h1,hx,h1cts)
            if s is not None and s['episode_key'] not in last_episode:
                pending=s
    if pos is not None:
        censored += 1
    return trades,censored


def metrics(trades,symbols,censored=0):
    m=b.metrics(trades,symbols,censored)
    rs=[t['net_R'] for t in trades]
    gp=sum(r for r in rs if r>0); gl=-sum(r for r in rs if r<0)
    m['profit_factor_R']=gp/gl if gl>0 else (999.0 if gp>0 else None)
    m['avg_win_R']=statistics.fmean([r for r in rs if r>0]) if any(r>0 for r in rs) else None
    m['avg_loss_R']=statistics.fmean([r for r in rs if r<0]) if any(r<0 for r in rs) else None
    return m


def run_segment(m15s,h1s,funds,segment,bps):
    alltr=[]; cens=0; syms=sorted(m15s)
    for s in syms:
        n=len(m15s[s]); d,v=b.split(n)
        if segment=='development': a,z=0,d
        elif segment=='validation': a,z=d,v
        elif segment=='non_holdout': a,z=0,v
        elif segment=='holdout': a,z=v,n
        else: raise ValueError(segment)
        tr,c=backtest_symbol(s,m15s[s],h1s[s],funds[s],a,z,bps); alltr.extend(tr); cens+=c
    return metrics(alltr,syms,cens),alltr


def main():
    manifest=json.loads((ROOT/'sources/sources_manifest.json').read_text()); protocol=json.loads((ROOT/'protocol.json').read_text()); syms=protocol['primary_panel']['symbols']
    m15s={}; h1s={}; funds={}
    for s in syms:
        m15s[s]=b.load_bars(pathlib.Path(manifest['merged_histories'][s]['15m']['path']))
        h1s[s]=b.load_bars(pathlib.Path(manifest['merged_histories'][s]['1h']['path']))
        funds[s]=b.load_funding(pathlib.Path(manifest['funding'][s]['path']))
    out={'schema_version':'ktrader.candidate_rule_set_v2_1_preholdout.v1','strategy_id':'candidate_rule_set_v2_1','holdout_opened':False,
         'parameters':{'target_r':b.TARGET_R,'max_hold_bars_m15':b.MAX_HOLD_BARS,'buffer_atr':b.BUFFER_ATR,'pullback_window':b.PULLBACK_WINDOW,
                       'min_h1_ema_sep_atr':MIN_H1_SEP_ATR,'max_signal_body_fraction':MAX_SIGNAL_BODY_FRAC,'min_risk_pct':MIN_RISK_PCT,
                       'fee_bps_per_side':b.FEE_BPS,'slippage_bps_base':2.0,'slippage_bps_stress':5.0},'segments':{}}
    trade_dir=ROOT/'combined_rules/v2_1_trades'; trade_dir.mkdir(parents=True,exist_ok=True)
    for seg in ('development','validation','non_holdout'):
        m,tr=run_segment(m15s,h1s,funds,seg,b.SLIPPAGE_BPS['base']); out['segments'][seg]=m
        with (trade_dir/f'{seg}.jsonl').open('w') as f:
            for t in sorted(tr,key=lambda x:(x['entry_time'],x['symbol'])): f.write(json.dumps(t,sort_keys=True)+'\n')
    stress,_=run_segment(m15s,h1s,funds,'non_holdout',b.SLIPPAGE_BPS['stress']); out['stress_non_holdout']=stress
    dev=out['segments']['development']; val=out['segments']['validation']; non=out['segments']['non_holdout']; reasons=[]
    if non['completed_trades']<100: reasons.append('NON_HOLDOUT_SAMPLE_LT_100')
    if val['completed_trades']<30: reasons.append('VALIDATION_SAMPLE_LT_30')
    for label,m in [('NON_HOLDOUT',non),('VALIDATION',val)]:
        if m['win_rate'] is None or m['win_rate']<0.50: reasons.append(label+'_WIN_RATE_LT_50')
        if m['expectancy_R'] is None or m['expectancy_R']<=0: reasons.append(label+'_EXPECTANCY_R_NONPOSITIVE')
        if m['profit_factor_R'] is None or m['profit_factor_R']<=1: reasons.append(label+'_PF_R_LE_1')
    if stress['expectancy_R'] is None or stress['expectancy_R']<=0: reasons.append('STRESS_EXPECTANCY_R_NONPOSITIVE')
    out['promotion_gate']={'pass':not reasons,'reasons':reasons,'holdout_authorized':not reasons}
    p=ROOT/'combined_rules/v2_1_preholdout_report.json'; p.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    print('REPORT',p,b.sha_file(p)); print(json.dumps(out['promotion_gate'],sort_keys=True))
    for k,v in out['segments'].items(): print(k,json.dumps(v,sort_keys=True))
    print('stress_non_holdout',json.dumps(stress,sort_keys=True))

if __name__=='__main__': main()
