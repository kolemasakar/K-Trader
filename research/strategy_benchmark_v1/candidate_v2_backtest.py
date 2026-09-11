#!/usr/bin/env python3
from __future__ import annotations

import bisect
import collections
import hashlib
import json
import math
import statistics
from datetime import datetime
from pathlib import Path

ROOT = Path('/data/research/phase11g/strategy_benchmark_v1')
FEE_BPS = 5.0
SLIPPAGE_BPS = {'base': 2.0, 'stress': 5.0}
TARGET_R = 3.0
MAX_HOLD_BARS = 32
BUFFER_ATR = 0.15
PULLBACK_WINDOW = 5


def ts(s):
    return datetime.fromisoformat(s.replace('Z', '+00:00'))


def sha_file(p: Path):
    h = hashlib.sha256()
    with p.open('rb') as f:
        for c in iter(lambda: f.read(1024 * 1024), b''):
            h.update(c)
    return h.hexdigest()


def load_bars(path: Path):
    out = []
    with path.open() as f:
        next(f)
        for line in f:
            d = json.loads(line)
            out.append({
                'open_time': d['open_time'], 'close_time': d['close_time'],
                'open_dt': ts(d['open_time']), 'close_dt': ts(d['close_time']),
                'open': float(d['open']), 'high': float(d['high']), 'low': float(d['low']), 'close': float(d['close']),
                'quote_volume': float(d.get('quote_volume') or 0),
            })
    return out


def load_funding(path: Path):
    d = json.loads(path.read_text())
    return [{'funding_ms': int(r['fundingTime']), 'rate': float(r['fundingRate']), 'mark': float(r['markPrice'])} for r in d['records']]


def ema(vals, n):
    out = [None] * len(vals)
    if len(vals) < n:
        return out
    a = 2.0 / (n + 1.0)
    e = sum(vals[:n]) / n
    out[n - 1] = e
    for i in range(n, len(vals)):
        e = a * vals[i] + (1-a) * e
        out[i] = e
    return out


def atr_wilder(bars, n=14):
    tr, prev = [], None
    for b in bars:
        x = b['high']-b['low'] if prev is None else max(b['high']-b['low'], abs(b['high']-prev), abs(b['low']-prev))
        tr.append(x); prev = b['close']
    out = [None] * len(bars)
    if len(tr) < n: return out
    a = sum(tr[:n])/n; out[n-1] = a
    for i in range(n, len(tr)):
        a = (a*(n-1)+tr[i])/n; out[i] = a
    return out


def rsi_wilder(vals, n=14):
    out = [None] * len(vals)
    if len(vals) <= n: return out
    gains=[]; losses=[]
    for i in range(1,n+1):
        d=vals[i]-vals[i-1]; gains.append(max(d,0)); losses.append(max(-d,0))
    ag=sum(gains)/n; al=sum(losses)/n
    def calc(g,l):
        if l == 0: return 100.0 if g > 0 else 50.0
        rs=g/l; return 100.0-100.0/(1.0+rs)
    out[n]=calc(ag,al)
    for i in range(n+1,len(vals)):
        d=vals[i]-vals[i-1]; g=max(d,0); l=max(-d,0)
        ag=(ag*(n-1)+g)/n; al=(al*(n-1)+l)/n; out[i]=calc(ag,al)
    return out


def prior_mean(vals,n):
    out=[None]*len(vals)
    for i in range(n,len(vals)):
        out[i]=sum(vals[i-n:i])/n
    return out


def indicators(bars):
    c=[b['close'] for b in bars]; q=[b['quote_volume'] for b in bars]
    return {'ema20':ema(c,20),'ema50':ema(c,50),'atr14':atr_wilder(bars,14),'rsi14':rsi_wilder(c,14),'qv20prev':prior_mean(q,20)}


def adverse(raw, side, entry, bps):
    s=bps/10000.0
    if entry: return raw*(1+s) if side==1 else raw*(1-s)
    return raw*(1-s) if side==1 else raw*(1+s)


def funding_pct(side, entry_price, entry_time, exit_time, funding):
    s=int(entry_time.timestamp()*1000); e=int(exit_time.timestamp()*1000); total=0.0
    for r in funding:
        if s <= r['funding_ms'] <= e:
            signed=r['rate']*r['mark']/entry_price
            total += signed if side==1 else -signed
    return total


def finish(symbol,pos,exit_i,exit_time,raw_exit,reason,bps,funding):
    xp=adverse(raw_exit,pos['side'],False,bps)
    gross=(xp-pos['entry'])/pos['entry'] if pos['side']==1 else (pos['entry']-xp)/pos['entry']
    fee=(FEE_BPS/10000.0)*(1.0+xp/pos['entry'])
    fund=funding_pct(pos['side'],pos['entry'],pos['entry_time'],exit_time,funding)
    net=gross-fee-fund
    return {
        'symbol':symbol,'side':'LONG' if pos['side']==1 else 'SHORT','entry_time':pos['entry_time'].isoformat().replace('+00:00','Z'),
        'exit_time':exit_time.isoformat().replace('+00:00','Z'),'entry_price':pos['entry'],'exit_price':xp,'stop_price':pos['stop'],
        'target_price':pos['target'],'risk_pct':pos['risk_pct'],'net_return_pct':net,'net_R':net/pos['risk_pct'],
        'fee_pct':fee,'funding_pct':fund,'hold_bars':exit_i-pos['entry_i']+1,'exit_reason':reason,
        'episode_key':pos['episode_key'],'features':pos['features'],
    }


def h1_context(h1, hx, h1_close_times, decision_dt):
    k=bisect.bisect_right(h1_close_times,decision_dt)-1
    if k < 52 or k-3 < 0: return 0, None
    e20=hx['ema20'][k]; e50=hx['ema50'][k]; old=hx['ema20'][k-3]; atr=hx['atr14'][k]
    if None in (e20,e50,old,atr) or atr <= 0: return 0, None
    side=1 if e20>e50 and e20>old else (-1 if e20<e50 and e20<old else 0)
    feat={'h1_index':k,'h1_ema20':e20,'h1_ema50':e50,'h1_atr14':atr,'h1_ema_sep_atr':abs(e20-e50)/atr}
    return side, feat


def signal_at(i,m15,mx,h1,hx,h1cts):
    if i < max(52,PULLBACK_WINDOW): return None
    r=mx['rsi14'][i]; e20=mx['ema20'][i]; atr=mx['atr14'][i]
    if None in (r,e20,atr) or atr <= 0: return None
    side,hfeat=h1_context(h1,hx,h1cts,m15[i]['close_dt'])
    if side == 0: return None
    w=range(i-PULLBACK_WINDOW+1,i+1)
    if side==1:
        pulls=[j for j in w if (mx['ema20'][j] is not None and m15[j]['low'] <= mx['ema20'][j]) or (mx['rsi14'][j] is not None and mx['rsi14'][j] < 45)]
        trigger=bool(pulls) and m15[i]['close']>e20 and r>=50 and m15[i]['close']>m15[i-1]['high'] and m15[i]['close']>m15[i]['open']
        if not trigger: return None
        extreme=min(m15[j]['low'] for j in w); stop_raw=extreme-BUFFER_ATR*atr
    else:
        pulls=[j for j in w if (mx['ema20'][j] is not None and m15[j]['high'] >= mx['ema20'][j]) or (mx['rsi14'][j] is not None and mx['rsi14'][j] > 55)]
        trigger=bool(pulls) and m15[i]['close']<e20 and r<=50 and m15[i]['close']<m15[i-1]['low'] and m15[i]['close']<m15[i]['open']
        if not trigger: return None
        extreme=max(m15[j]['high'] for j in w); stop_raw=extreme+BUFFER_ATR*atr
    qv=mx['qv20prev'][i]
    body=abs(m15[i]['close']-m15[i]['open']); rng=max(1e-15,m15[i]['high']-m15[i]['low'])
    features={**hfeat,'m15_rsi14':r,'m15_atr14':atr,'pullback_depth_atr':abs(m15[i]['close']-extreme)/atr,
              'signal_body_fraction':body/rng,'relative_quote_volume':m15[i]['quote_volume']/qv if qv else None,'pullback_episode_index':max(pulls)}
    return {'side':side,'stop_raw':stop_raw,'episode_key':f"{side}:{max(pulls)}",'features':features}


def backtest_symbol(symbol,m15,h1,funding,start,end,bps):
    mx=indicators(m15); hx=indicators(h1); h1cts=[b['close_dt'] for b in h1]
    trades=[]; pos=None; pending=None; pending_exit=False; last_episode=set(); censored=0
    for i in range(max(1,start-1),end):
        b=m15[i]
        if pos is not None and pending_exit:
            trades.append(finish(symbol,pos,i,b['open_dt'],b['open'],'TIME_EXIT',bps,funding)); pos=None; pending_exit=False
        if pos is None and pending is not None and i>=start:
            side=pending['side']; ep=adverse(b['open'],side,True,bps); stop=pending['stop_raw']; dist=side*(ep-stop)
            if dist>0 and pending['episode_key'] not in last_episode:
                pos={'side':side,'entry_i':i,'entry_time':b['open_dt'],'entry':ep,'stop':stop,'target':ep+side*TARGET_R*dist,
                     'risk_pct':dist/ep,'episode_key':pending['episode_key'],'features':pending['features']}
                last_episode.add(pending['episode_key'])
            pending=None
        if pos is not None:
            gap_stop=(pos['side']==1 and b['open']<=pos['stop']) or (pos['side']==-1 and b['open']>=pos['stop'])
            gap_target=(pos['side']==1 and b['open']>=pos['target']) or (pos['side']==-1 and b['open']<=pos['target'])
            if gap_stop:
                trades.append(finish(symbol,pos,i,b['open_dt'],b['open'],'GAP_STOP',bps,funding)); pos=None
            elif gap_target:
                trades.append(finish(symbol,pos,i,b['open_dt'],b['open'],'GAP_TARGET',bps,funding)); pos=None
            else:
                sh=(pos['side']==1 and b['low']<=pos['stop']) or (pos['side']==-1 and b['high']>=pos['stop'])
                th=(pos['side']==1 and b['high']>=pos['target']) or (pos['side']==-1 and b['low']<=pos['target'])
                if sh:
                    trades.append(finish(symbol,pos,i,b['close_dt'],pos['stop'],'STOP',bps,funding)); pos=None
                elif th:
                    trades.append(finish(symbol,pos,i,b['close_dt'],pos['target'],'TARGET',bps,funding)); pos=None
        if i>=end-1: continue
        if pos is not None:
            if i-pos['entry_i']+1 >= MAX_HOLD_BARS: pending_exit=True
        elif pending is None:
            s=signal_at(i,m15,mx,h1,hx,h1cts)
            if s is not None and s['episode_key'] not in last_episode: pending=s
    if pos is not None: censored+=1
    return trades,censored


def wilson(w,n,z=1.959963984540054):
    if n==0:return [None,None]
    p=w/n; den=1+z*z/n; center=(p+z*z/(2*n))/den; half=z*math.sqrt((p*(1-p)+z*z/(4*n))/n)/den
    return [max(0,center-half),min(1,center+half)]


def metrics(trades,symbols,censored=0):
    n=len(trades); wins=sum(t['net_return_pct']>0 for t in trades); pos=sum(max(0,t['net_return_pct']) for t in trades); neg=-sum(min(0,t['net_return_pct']) for t in trades)
    rs=[t['net_R'] for t in trades]; rets=[t['net_return_pct'] for t in trades]; by=collections.Counter(t['symbol'] for t in trades)
    running=peak=ddr=0.0
    for t in sorted(trades,key=lambda x:(x['exit_time'],x['symbol'])):
        running+=t['net_R']; peak=max(peak,running); ddr=max(ddr,peak-running)
    return {'completed_trades':n,'censored_open_positions':censored,'wins':wins,'losses':n-wins,'win_rate':wins/n if n else None,
            'wilson_95_ci':wilson(wins,n),'expectancy_R':statistics.fmean(rs) if rs else None,
            'net_expectancy_pct_per_trade':statistics.fmean(rets) if rets else None,'profit_factor':pos/neg if neg>0 else (None if pos==0 else 999.0),
            'max_drawdown_R_trade_stream':ddr,'median_hold_bars':statistics.median([t['hold_bars'] for t in trades]) if trades else None,
            'long_count':sum(t['side']=='LONG' for t in trades),'short_count':sum(t['side']=='SHORT' for t in trades),
            'top_symbol_trade_share':max(by.values())/n if n else None,'per_symbol_trade_count':dict(sorted(by.items())),
            'fee_pct_sum':sum(t['fee_pct'] for t in trades),'funding_pct_sum':sum(t['funding_pct'] for t in trades)}


def split(n): return int(math.floor(n*.60)),int(math.floor(n*.80))


def run_segment(m15s,h1s,funds,segment,bps):
    alltr=[]; cens=0; syms=sorted(m15s)
    for s in syms:
        n=len(m15s[s]); d,v=split(n)
        if segment=='development': a,b=0,d
        elif segment=='validation': a,b=d,v
        elif segment=='non_holdout': a,b=0,v
        elif segment=='holdout': a,b=v,n
        else: raise ValueError(segment)
        tr,c=backtest_symbol(s,m15s[s],h1s[s],funds[s],a,b,bps); alltr.extend(tr); cens+=c
    return metrics(alltr,syms,cens),alltr


def main():
    manifest=json.loads((ROOT/'sources/sources_manifest.json').read_text()); protocol=json.loads((ROOT/'protocol.json').read_text()); syms=protocol['primary_panel']['symbols']
    m15s={}; h1s={}; funds={}
    for s in syms:
        m15s[s]=load_bars(Path(manifest['merged_histories'][s]['15m']['path']))
        h1s[s]=load_bars(Path(manifest['merged_histories'][s]['1h']['path']))
        funds[s]=load_funding(Path(manifest['funding'][s]['path']))
    out={'schema_version':'ktrader.candidate_rule_set_v2_preholdout.v1','strategy_id':'candidate_rule_set_v2','holdout_opened':False,
         'parameters':{'target_r':TARGET_R,'max_hold_bars_m15':MAX_HOLD_BARS,'buffer_atr':BUFFER_ATR,'pullback_window':PULLBACK_WINDOW,'fee_bps_per_side':FEE_BPS,'slippage_bps_base':2.0,'slippage_bps_stress':5.0},
         'segments':{}}
    trade_dir=ROOT/'combined_rules/v2_trades'; trade_dir.mkdir(parents=True,exist_ok=True)
    for seg in ('development','validation','non_holdout'):
        m,tr=run_segment(m15s,h1s,funds,seg,SLIPPAGE_BPS['base']); out['segments'][seg]=m
        with (trade_dir/f'{seg}.jsonl').open('w') as f:
            for t in sorted(tr,key=lambda x:(x['entry_time'],x['symbol'])): f.write(json.dumps(t,sort_keys=True)+'\n')
    stress,_=run_segment(m15s,h1s,funds,'non_holdout',SLIPPAGE_BPS['stress']); out['stress_non_holdout']=stress
    dev=out['segments']['development']; val=out['segments']['validation']; non=out['segments']['non_holdout']
    reasons=[]
    if non['completed_trades']<100: reasons.append('NON_HOLDOUT_SAMPLE_LT_100')
    if val['completed_trades']<30: reasons.append('VALIDATION_SAMPLE_LT_30')
    for label,m in [('NON_HOLDOUT',non),('VALIDATION',val)]:
        if m['win_rate'] is None or m['win_rate']<0.50: reasons.append(label+'_WIN_RATE_LT_50')
        if m['expectancy_R'] is None or m['expectancy_R']<=0: reasons.append(label+'_EXPECTANCY_NONPOSITIVE')
        if m['profit_factor'] is None or m['profit_factor']<=1: reasons.append(label+'_PF_LE_1')
    if stress['expectancy_R'] is None or stress['expectancy_R']<=0: reasons.append('STRESS_EXPECTANCY_NONPOSITIVE')
    out['promotion_gate']={'pass':not reasons,'reasons':reasons,'holdout_authorized':not reasons}
    p=ROOT/'combined_rules/v2_preholdout_report.json'; p.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    print('REPORT',p,sha_file(p)); print(json.dumps(out['promotion_gate'],sort_keys=True));
    for k,v in out['segments'].items(): print(k,json.dumps(v,sort_keys=True))
    print('stress_non_holdout',json.dumps(stress,sort_keys=True))

if __name__=='__main__': main()
