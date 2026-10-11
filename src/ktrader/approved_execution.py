"""Fixed A/B scenario scheduler; independent paths, prefix observations only."""
from dataclasses import replace
from ktrader.approved_models import Bar, dec


def vertices(bar, scenario):
    if scenario=='A':
        return (bar.open,bar.high,bar.low,bar.close)
    if scenario=='B':
        return (bar.open,bar.low,bar.high,bar.close)
    raise ValueError('fixed scenario A or B required')


def prefix(bar, scenario, fraction):
    f=dec(fraction)
    if not 0<=f<=1:
        raise ValueError('fraction')
    points=vertices(bar,scenario)
    if f==1:
        return bar
    index=min(2,int(f*3))
    price=points[index]+(points[index+1]-points[index])*(f*3-index)
    visited=points[:index+1]+(price,)
    return Bar(points[0],max(visited),min(visited),price)


def replay_order(order, bars, scenario, *, activation=dec('.9'), cancel_at_close=None,
                 invalidate_level=False):
    """Fill protection starts at actual fill, with adverse SL gap at next Open.

    Each bar is a simulated continuous path. Unknown costs stay null. Limits
    use their planned price; favorable gap improvement is deliberately omitted.
    """
    filled=False
    for i,bar in enumerate(bars):
        points=vertices(bar,scenario)
        if filled and order.side*(bar.open-order.stop)<=0:
            return outcome('SL_GAP',order,bar.open,i)
        if filled and order.side*(bar.open-order.target)>=0:
            return outcome('TP',order,order.target,i)
        for j,(a,b) in enumerate(zip(points,points[1:])):
            lo,hi=dec(j)/3,dec(j+1)/3
            if i==0 and hi<=activation:
                continue
            if i==0 and lo<activation:
                a=a+(b-a)*(activation-lo)/(hi-lo)
            if not filled:
                if invalidate_level and order.side*(a-order.level)<0:
                    return {'status':'CANCELLED_PENETRATION','gross_r':None,'net_r':None,'bar':i}
                candidates=[]
                if order.kind=='LIMIT':
                    if order.side*(a-order.entry)<=0:
                        candidates.append((dec(0),'FILL'))
                    elif min(a,b)<=order.entry<=max(a,b) and order.side*(b-order.entry)<=0:
                        candidates.append(((order.entry-a)/(b-a),'FILL'))
                elif min(a,b)<=order.entry<=max(a,b) and order.side*(b-a)>0:
                    candidates.append(((order.entry-a)/(b-a),'FILL'))
                if invalidate_level and min(a,b)<=order.level<=max(a,b) and order.side*(b-order.level)<0:
                    candidates.append(((order.level-a)/(b-a),'CANCEL'))
                if not candidates:
                    continue
                _,kind=min(candidates,key=lambda x:(x[0],0 if x[1]=='CANCEL' else 1))
                if kind=='CANCEL':
                    return {'status':'CANCELLED_PENETRATION','gross_r':None,'net_r':None,'bar':i}
                filled=True
                a=order.entry
            if order.side*(a-order.stop)<=0:
                return outcome('SL',order,a,i)
            hits=[]
            for name,price in (('SL',order.stop),('TP',order.target)):
                if min(a,b)<=price<=max(a,b):
                    f=(price-a)/(b-a) if b!=a else dec(0)
                    hits.append((f,0 if name=='SL' else 1,name,price))
            if hits:
                _,_,name,price=min(hits)
                return outcome(name,order,price,i)
        if not filled and cancel_at_close and cancel_at_close(bar,order):
            return {'status':'CANCELLED_CLOSE','gross_r':None,'net_r':None,'bar':i}
    return {'status':'CENSORED' if filled else 'UNFILLED','gross_r':None,'net_r':None}


def outcome(status,order,price,index):
    return {'status':status,'gross_r':str(order.side*(price-order.entry)/order.distance),
            'net_r':None,'bar':index}
