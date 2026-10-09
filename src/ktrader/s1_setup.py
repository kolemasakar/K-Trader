"""Research-only S1 strategy preflight. No fabricated approved levels/trades."""
from dataclasses import dataclass
from decimal import Decimal

def d(x): return Decimal(str(x))

@dataclass(frozen=True)
class Bar:
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal

def trend(bars):
    """Approved causal two-left/two-right confirmed swing structure."""
    if len(bars)<9: return "UNKNOWN"
    hi=[]; lo=[]
    for i in range(2,len(bars)-2):
        v=bars[i]
        if all(v.high>bars[j].high for j in (i-2,i-1,i+1,i+2)): hi.append(v.high)
        if all(v.low<bars[j].low for j in (i-2,i-1,i+1,i+2)): lo.append(v.low)
    if len(hi)<2 or len(lo)<2: return "UNKNOWN"
    if hi[-1]>hi[-2] and lo[-1]>lo[-2]: return "UP"
    if hi[-1]<hi[-2] and lo[-1]<lo[-2]: return "DOWN"
    return "NEUTRAL"

def atr5_preliminary(bars):
    """Only a preliminary 5-bar baseline, NOT approved fully filtered ATR5 v2."""
    if len(bars)<5: return None
    return sum((x.high-x.low for x in bars[-5:]),d(0))/5

def compression(closes,level,side):
    if len(closes)<3: return False
    a,b,c=closes[-3:]
    if side==1: return a>b>c>=level
    if side==-1: return a<b<c<=level
    raise ValueError("side")

def activity(previous20, candidate):
    if len(previous20)!=20: return None
    av=sum((b.high-b.low for b in previous20),d(0))/20
    if av<=0: return None
    return (candidate.high-candidate.low)/av

def inspect_readiness(m5,h1,d1,*, reviewed_levels=None,broker_point=None,tick_size=None):
    """Structured rejection rather than manufacturing S1 signals from bare OHLC."""
    reasons=[]
    if not reviewed_levels: reasons.append("NO_APPROVED_REVIEWED_LEVELS")
    if broker_point is None or tick_size is None: reasons.append("MISSING_BROKER_POINT_OR_TICK_SIZE")
    if len(m5)<21 or len(h1)<9 or len(d1)<9: reasons.append("INSUFFICIENT_MULTITF_HISTORY")
    reasons.append("ATR5_V2_NOT_INTEGRATED")
    reasons.append("BPU2_30SEC_CAUSAL_SIGNAL_GENERATOR_NOT_INTEGRATED")
    return {"eligible":not reasons,"reasons":reasons,"series_counts":{"M5":len(m5),"H1":len(h1),"D1":len(d1)}}
