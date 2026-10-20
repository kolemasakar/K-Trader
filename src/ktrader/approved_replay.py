"""Sequential historical replay. Caller supplies causal verified contexts.

Crossings are evaluated in historical order inside fixed A/B segments. Price context
contains only a prefix, and cash fields remain unknown without a risk profile.
"""
from dataclasses import replace
from ktrader.approved_models import Bar,ModelState,dec,round_price
from ktrader.approved_execution import vertices,prefix
from ktrader.research_risk import size_position


def run_model(bars, model, context_at, scenario, *, seed_history=(),deposit=None,risk_profile=None,diagnostics=None):
    """context_at(index, history) uses only completed data at current bar open.

    Returns all setups, fills, cancellations, exits and censored positions.
    Distinct models/variants are separate experiments, never stacked orders.
    """
    history=list(seed_history)
    state=None
    orders=[]
    active=[]
    compressed=False
    compression_since=-1
    def count(reason):
        if diagnostics is not None:
            diagnostics[reason]=diagnostics.get(reason,0)+1
    for index,bar in enumerate(bars):
        count('BARS_VISITED')
        ctx=context_at(index,tuple(history))
        if ctx is None:
            count('CONTEXT_UNAVAILABLE')
            if state is not None and state.phase not in ('FILLED','CANCELLED'):
                state.cancel('CONTEXT_UNAVAILABLE')
            # Already filled protection must still run even when context disappears.
        if state is None or state.phase=='CANCELLED' or (state.phase=='FILLED'):
            state=ModelState(model,ctx) if ctx else None
        elif ctx:
            # S3 keeps initial approach direction through the correcting retest.
            if model=='S3' and state.phase=='RETEST_WAIT':
                ctx=replace(ctx,approach=state.ctx.approach)
            state.ctx=ctx
        if state and model in ('S2A','S2B','S3') and state.phase=='IDLE' and history:
            state.on_closed(history)
        if state and model=='S4' and state.phase!='PENDING':
            state=ModelState(model,ctx)
        points=vertices(bar,scenario)
        fractions={dec(0),dec(1)/3,dec(2)/3,dec('.9'),dec(1)}
        if ctx:
            values=[ctx.level,ctx.level-ctx.tick,ctx.level+ctx.tick,
                    round_price(ctx.level+ctx.side*ctx.delta,ctx.tick,ctx.side==1)]
            if model=='S5B' and ctx.breakout_next_level is not None:
                values.append(ctx.breakout_next_level)
            if state and state.frozen_bounds:
                anchor=max(ctx.level,state.frozen_bounds[1]) if ctx.side==1 else min(ctx.level,state.frozen_bounds[0])
                values.append(round_price(anchor+ctx.side*ctx.delta,ctx.tick,ctx.side==1))
            for j,(a,b) in enumerate(zip(points,points[1:])):
                if a!=b:
                    for value in values:
                        if min(a,b)<=value<=max(a,b):
                            fractions.add((dec(j)+(value-a)/(b-a))/3)
        previous=bar.open
        previous_fraction=dec(0)
        for fraction in sorted(fractions):
            observed=prefix(bar,scenario,fraction)
            price=observed.close
            # All active positions see this segment, including gaps at fraction 0.
            for record in list(active):
                order=record['order']
                if not record['filled']:
                    if state is None or state.phase=='CANCELLED':
                        record['status']='CANCELLED';active.remove(record);continue
                    if order.kind=='LIMIT' and order.side*(price-order.level)<0:
                        state.cancel('CONFIRMATION_PENETRATION')
                        record['status']='CANCELLED';active.remove(record);continue
                    eligible=(order.side*(price-order.entry)<=0 if order.kind=='LIMIT' else order.side*(price-order.entry)>=0)
                    if not eligible:
                        continue
                    record['filled']=True;record['status']='OPEN';record['fill_bar']=index
                    state.phase='FILLED'
                    # Modeled fill at planned entry. No favorable improvement claims.
                    start=order.entry
                else:
                    start=previous
                if fraction==0:
                    # A limit gap through protection exits at adverse Open.
                    if order.side*(price-order.stop)<=0:
                        finish(record,'SL_GAP',price,index);active.remove(record);continue
                if fraction==0 and record['fill_bar']<index:
                    if order.side*(price-order.stop)<=0:
                        finish(record,'SL_GAP',price,index);active.remove(record);continue
                    if order.side*(price-order.target)>=0:
                        finish(record,'TP',order.target,index);active.remove(record);continue
                hits=[]
                for name,value in (('SL',order.stop),('TP',order.target)):
                    if min(start,price)<=value<=max(start,price):
                        f=(value-start)/(price-start) if price!=start else dec(0)
                        hits.append((f,0 if name=='SL' else 1,name,value))
                if hits:
                    _,_,name,value=min(hits);finish(record,name,value,index);active.remove(record)
            if state and state.phase not in ('FILLED','CANCELLED') and history and fraction<1:
                if model in ('S1','CHANNEL') and compressed:
                    count('COMPRESSION_PREFIX_BLOCKED')
                    # No recovery of an old confirmation whose BPU1 predates equalization.
                    continue
                before=state.order
                try:
                    next_level_hit=(model=='S5B' and state.ctx.breakout_next_level is not None
                                    and state.ctx.side*((observed.low if state.ctx.side==1 else observed.high)
                                                       -state.ctx.breakout_next_level)<=0)
                    order=state.on_prefix(history,observed,previous,price,fraction,
                                          next_level_hit=next_level_hit)
                except ValueError as exc:
                    count('ORDER_GEOMETRY:'+str(exc))
                    state.cancel('ORDER_GEOMETRY:'+str(exc));order=None
                if fraction == dec('.9') and order is None:
                    for reason in state.reasons:
                        count('ACTIVATION_REJECT:'+reason)
                if order is not None and before is None:
                    record={'order':order,'created_bar':index,'activation_fraction':str(fraction),
                            'filled':False,'status':'PENDING','gross_r':None,'net_r':None,
                            'size':size_position(order.distance,deposit,risk_profile) if deposit is not None else {'status':'UNKNOWN_DEPOSIT','volume':None}}
                    orders.append(record);active.append(record)
                    count('ORDERS_CREATED')
                    if order.kind=='PROGRAMMATIC_STOP' or order.side*(price-order.entry)<=0:
                        record['filled']=True;record['status']='OPEN';record['fill_bar']=index;state.phase='FILLED'
            previous=price
            previous_fraction=fraction
        history.append(bar)
        if state:
            state.on_closed(history)
            if state.phase=='CANCELLED':
                for record in list(active):
                    if not record['filled']:
                        record['status']='CANCELLED';record['cancel_reasons']=list(state.reasons);active.remove(record)
            if model in ('S1','CHANNEL') and ctx:
                from ktrader.approved_models import squeeze
                if squeeze(history,ctx.level,-ctx.side):
                    compressed=True;compression_since=index
                elif compressed and len(history)>=2 and abs(bar.close-ctx.level)>abs(history[-2].close-ctx.level):
                    compressed=False
            if state.phase=='FILLED' and not active:
                state=None
    for record in active:
        record['status']='CENSORED' if record['filled'] else 'UNFILLED'
    return [{**{k:v for k,v in r.items() if k!='order'},'order':{
        k:str(v) if hasattr(v,'as_tuple') else v for k,v in r['order'].__dict__.items()}}
        for r in orders]


def finish(record,status,price,index):
    order=record['order']
    record.update(status=status,exit_bar=index,
                  gross_r=str(order.side*(price-order.entry)/order.distance))
