"""S1 research-only OHLC/OLHC event simulator; no trading connectivity."""
from dataclasses import dataclass
from decimal import Decimal

def dec(x): return Decimal(str(x))

@dataclass(frozen=True)
class Order:
    side: int
    entry: Decimal
    stop: Decimal
    target: Decimal
    def __post_init__(self):
        if self.side not in (-1,1) or self.side*(self.entry-self.stop)<=0 or self.side*(self.target-self.entry)<=0:
            raise ValueError("invalid S1 order geometry")

def points(row, scenario):
    o,h,l,c=[dec(row[k]) for k in ("open","high","low","close")]
    if l>min(o,c) or h<max(o,c): raise ValueError("invalid OHLC")
    if scenario=="A": return (o,h,l,c)
    if scenario=="B": return (o,l,h,c)
    raise ValueError("unknown scenario")

def crossing(a,b,v):
    return (v-a)/(b-a) if a!=b and min(a,b)<=v<=max(a,b) else (dec(0) if a==b==v else None)

def replay(order, bars, scenario, activation_fraction=dec("0.9")):
    """Caller supplies already validated S1 order, after causal signal checks."""
    activation_fraction=dec(activation_fraction)
    if not dec(0)<=activation_fraction<=dec(1): raise ValueError("activation")
    filled=False
    for i,bar in enumerate(bars):
        p=points(bar,scenario)
        for j,(a,b) in enumerate(zip(p,p[1:])):
            lo=dec(j)/3; hi=dec(j+1)/3
            if i==0 and hi<=activation_fraction: continue
            if i==0 and lo<activation_fraction:
                a=a+(b-a)*(activation_fraction-lo)/(hi-lo)
            if not filled:
                eligible=(a<=order.entry if order.side==1 else a>=order.entry)
                if not eligible:
                    f=crossing(a,b,order.entry)
                    if f is None or not (b<=order.entry if order.side==1 else b>=order.entry): continue
                filled=True
                a=order.entry
            if order.side*(a-order.stop)<=0:
                return {"status":"SL","gross_r":str(order.side*(a-order.entry)/abs(order.entry-order.stop)),"net_r":None}
            hits=[]
            for kind,v in (("SL",order.stop),("TP",order.target)):
                f=crossing(a,b,v)
                if f is not None: hits.append((f,0 if kind=="SL" else 1,kind))
            if hits:
                kind=min(hits)[2]
                price=order.stop if kind=="SL" else order.target
                return {"status":kind,"gross_r":str(order.side*(price-order.entry)/abs(order.entry-order.stop)),"net_r":None}
    return {"status":"CENSORED" if filled else "UNFILLED","gross_r":None,"net_r":None}
