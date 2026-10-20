"""Owner-authorized hypothetical S1 experiment, separate from verified admission.

Raw source levels/prices are never snapped to the assumed ORDER tick grid.
No human labels or historical verification flags are generated.
"""
from bisect import bisect_left, bisect_right
from collections import Counter
from datetime import datetime, timezone
from decimal import Decimal
import hashlib
import json
from ktrader.approved_models import Bar, Context, dec, luft
from ktrader.approved_replay import run_model
from ktrader.level_admission import fingerprint
from ktrader.level_semantic_audit import audit_panel
from ktrader.s1_equity_level_rows import completed_daily, completed_weekly
from ktrader.s1_atr5 import filtered_atr5


def epoch(value):
    return int(datetime.fromisoformat(value).replace(tzinfo=timezone.utc).timestamp()*1000)


def trend_prefixes(bars):
    """Exactly the strict 2+2 pivot rule, evaluated once per closed prefix."""
    highs=[];lows=[];directions=['UNKNOWN']
    for n in range(1,len(bars)+1):
        i=n-3
        if i>=2:
            if all(bars[i].high>bars[j].high for j in (i-2,i-1,i+1,i+2)):
                highs.append(bars[i].high)
            if all(bars[i].low<bars[j].low for j in (i-2,i-1,i+1,i+2)):
                lows.append(bars[i].low)
        direction='UNKNOWN'
        if len(highs)>=2 and len(lows)>=2:
            direction=('UP' if highs[-1]>highs[-2] and lows[-1]>lows[-2] else
                       'DOWN' if highs[-1]<highs[-2] and lows[-1]<lows[-2] else 'NEUTRAL')
        directions.append(direction)
    return directions


def validate_profile(profile):
    if (profile.get('mode')!='OWNER_AUTHORIZED_ENGINEERING'
            or profile.get('broker_symbol')!='ACHC.us'
            or profile.get('owner_approval_id')!='OWNER_20261020_POINT002_TICK002'
            or dec(profile.get('point'))!=dec('.02')
            or dec(profile.get('tick_size'))!=dec('.02')
            or profile.get('historical_price_geometry_verified') is not False
            or profile.get('level_universe_reviewed') is not False):
        raise ValueError('explicit approved engineering profile required')


def pool(panels, rows, d1, source_hash, cutoff):
    accepted=[];blocked=[]
    # W1 observations become available only after first closed D1 of later week.
    def availability(tf,index):
        end=rows[tf][index][6]+1
        if tf=='D1':
            return end
        return next((epoch(b['close_time']) for b in d1 if epoch(b['open_time'])>=end),cutoff+1)
    for p in panels:
        c=p['candidate'];tf=c['timeframe'];rr=rows[tf]
        if p['evidence_id']!=fingerprint(c) or p['source_sha256']!=source_hash:
            raise ValueError('panel identity/source mismatch')
        i=c['source_index']
        if rr[i][0]!=c['source_open_ms'] or dec(c['price']) not in (dec(rr[i][2]),dec(rr[i][3])):
            raise ValueError('origin mismatch')
        if p['witness_rows']!=[rr[j] for j in c['witness_indices']]:
            raise ValueError('witness mismatch')
        audit=audit_panel(p,rr,as_of_ms=cutoff)
        if audit['status']!='SHAPE_PASS_REVIEW_PENDING':
            blocked.append({'id':p['evidence_id'],'reason':audit['status']});continue
        proofs=[{'index':j,'available_at':availability(tf,j)}
                for j in audit['subsequent_exact_touch_indices']]
        proofs=[x for x in proofs if x['available_at']<=cutoff]
        if not proofs:
            blocked.append({'id':p['evidence_id'],'reason':'NO_SUBSEQUENT_EXACT_TOUCH'});continue
        accepted.append({'candidate':c,'id':p['evidence_id'],
                         'available_at':max(c['known_at_ms'],min(x['available_at'] for x in proofs)),
                         'proofs':proofs,'admission_basis':'PROVISIONAL_MACHINE_SHAPE_AND_TOUCH',
                         'historically_verified':False,'independent_human_review':False})
    return accepted,blocked


def run_engineering(candles,panels,profile,source_hash,cutoff):
    validate_profile(profile)
    rows={'D1':completed_daily(candles['D1']),'W1':completed_weekly(candles['D1'])}
    accepted,blocked=pool(panels,rows,candles['D1'],source_hash,cutoff)
    bars={tf:[Bar.from_row(b) for b in values] for tf,values in candles.items()}
    times={tf:[epoch(b['close_time']) for b in values] for tf,values in candles.items()}
    daily_opens=[epoch(b['open_time']) for b in candles['D1']]
    weekly_available=[]
    for r in rows['W1']:
        following=bisect_left(daily_opens,r[6]+1)
        weekly_available.append(times['D1'][following] if following<len(daily_opens) else cutoff+1)
    row_closes={'D1':[r[6]+1 for r in rows['D1']],'W1':weekly_available}
    directions={tf:trend_prefixes(values) for tf,values in bars.items()}
    atrs={};records=[];diagnostics={};state_counts=Counter()
    def active(level,now):
        if level['available_at']>now:
            return False
        c=level['candidate'];rr=rows[c['timeframe']]
        n=bisect_right(row_closes[c['timeframe']],now)
        # Conservative provisional STATE rule: latest completed source-TF close
        # must defend the formation side. Crossing doesn't erase historical P.
        if not n:
            return False
        return n>0 and (dec(rr[n-1][4])>dec(c['price']) if c['side']=='SUPPORT'
                        else dec(rr[n-1][4])<dec(c['price']))
    for level in accepted:
        c=level['candidate'];price=dec(c['price']);side=1 if c['side']=='SUPPORT' else -1
        first=next((i for i,b in enumerate(candles['M5']) if i>=21 and epoch(b['open_time'])>=level['available_at']),None)
        if first is None:
            continue
        contexts={}
        def context_at(index,history):
            actual=first+index
            if actual in contexts:
                return contexts[actual]
            now=epoch(candles['M5'][actual]['open_time'])
            approach=epoch(candles['M5'][actual-1]['open_time'])
            dn=bisect_right(times['D1'],now);da=bisect_right(times['D1'],approach)
            hn=bisect_right(times['H1'],approach)
            if dn<5:
                contexts[actual]=None;return None
            if dn not in atrs:
                atrs[dn]=dec(filtered_atr5(candles['D1'][:dn]))
            current=active(level,now)
            others=[dec(x['candidate']['price']) for x in accepted if active(x,now)
                    and side*(dec(x['candidate']['price'])-price)>0]
            state_counts['DEFENDED_SOURCE_CLOSE' if current else 'SOURCE_SIDE_NOT_DEFENDED']+=1
            ctx=Context(price,side,luft(price,'us_equity',profile['point']),
                        dec(profile['tick_size']),dec(profile['point']),atrs[dn],'us_equity',
                        current,current,(directions['D1'][da],directions['H1'][hn],directions['M5'][actual-1]),
                        directions['D1'][dn],bool(others),
                        opposing_level=min(others,key=lambda x:abs(x-price)) if others else None)
            contexts[actual]=ctx;return ctx
        for scenario in ('A','B'):
            diag={}
            replay=run_model(bars['M5'][first:],'S1',context_at,scenario,
                             seed_history=bars['M5'][:first],diagnostics=diag)
            diagnostics[level['id']+':'+scenario]=diag
            for r in replay:
                r['logical_coordinates']={'basis':'SOURCE_M5_INDEX',
                    **{k:first+r[k] for k in ('created_bar','fill_bar','exit_bar') if k in r},
                    'activation_fraction':r['activation_fraction']}
                records.append({'level_id':level['id'],'scenario':scenario,**r})
    report={'schema':'ktrader.s1_engineering.v1','status':'COMPLETED_ENGINEERING_EXPERIMENT',
        'symbol':'ACHC.us','model':'S1','clock':'CONDITIONAL_BAR_COORDINATES',
        'scheduler_used':False,'session_binding':'NONE','assumed_point':profile['point'],
        'assumed_order_tick':profile['tick_size'],'raw_source_prices_unchanged':True,
        'historical_price_geometry_verified':False,'independent_human_review':False,
        'pool_policy':'SHAPE_PLUS_LATER_EXACT_TOUCH_AND_CURRENT_SOURCE_TF_DEFENDED_CLOSE',
        'target_space':'NEAREST_CURRENT_PROVISIONAL_LEVEL; NOT VERIFIED_COMPLETE_UNIVERSE',
        'level_grid_policy':'RAW_SOURCE_LEVELS_PRESERVED; ASSUMED_GRID_APPLIES_TO_ORDERS_ONLY',
        'provisional_levels':accepted,'blocked_levels':blocked,
        'pool_counts':{'accepted':len(accepted),'blocked':len(blocked)},
        'state_context_counts':dict(state_counts),'diagnostics':diagnostics,'orders':records,
        'summary':{s:dict(Counter(r['status'] for r in records if r['scenario']==s)) for s in ('A','B')},
        'net_results':None,'monetary_results':None,'verified_market_acceptance':False,
        'legacy_strategy_used':False,'validation_scope':'ENGINEERING_NOT_HOLDOUT_OR_BROKER_EXECUTION'}
    report['deterministic_sha256']=hashlib.sha256(json.dumps(report,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    return report
