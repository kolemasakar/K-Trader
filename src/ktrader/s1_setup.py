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


def causal_candidate(*, level, side, bpu1, bpu2_observed, previous20, last_closed_m5,
                     confirmed_d1, confirmed_h1, confirmed_m5,
                     level_is_reviewed, strengthening_confirmed,
                     filtered_atr5, broker_point=None, tick_size=None,
                     no_compression=True, session_status="UNKNOWN"):
    """Check known S1 gates at T-30s of BPU2. No future BPU2 close permitted.

    bpu2_observed holds ONLY partial bar high/low at observation moment.
    Returns independent hard reject reasons; unsupported session rule is labelled.
    """
    reasons=[]
    side=int(side); level=d(level)
    if side not in (1,-1): raise ValueError("side")
    if not level_is_reviewed or not strengthening_confirmed:
        reasons.append("UNVERIFIED_LEVEL_OR_STRENGTH")
    required="DOWN" if side==1 else "UP"
    if (confirmed_d1,confirmed_h1,confirmed_m5)!=(required,required,required):
        reasons.append("TREND_MISALIGNMENT")
    if broker_point is None or tick_size is None or d(broker_point)<=0 or d(tick_size)<=0:
        reasons.append("MISSING_SYMBOL_POINT_TICK")
    if filtered_atr5 is None or d(filtered_atr5)<=0:
        reasons.append("UNKNOWN_FILTERED_ATR5")
    else:
        distance=max(d(0), d(side)*(d(last_closed_m5.close)-level))
        if d(filtered_atr5)-distance < d("0.60")*d(filtered_atr5):
            reasons.append("INSUFFICIENT_MOVE_RESERVE")
    if not no_compression: reasons.append("ACTIVE_COMPRESSION")
    k=activity(previous20,bpu2_observed)
    if k is None: reasons.append("UNKNOWN_BPU2_ACTIVITY")
    elif k>=2: reasons.append("BPU2_TOO_LARGE")
    # For stocks the first confirming bar must touch exactly and must not pierce.
    if side==1:
        if bpu1.low!=level: reasons.append("BPU1_NOT_EXACT_TOUCH")
        if bpu2_observed.low<level or bpu2_observed.low>level+abs(level)*d("0.0004"):
            reasons.append("BPU2_OUTSIDE_SUPPORT_LUFT")
    else:
        if bpu1.high!=level: reasons.append("BPU1_NOT_EXACT_TOUCH")
        if bpu2_observed.high>level or bpu2_observed.high<level-abs(level)*d("0.0004"):
            reasons.append("BPU2_OUTSIDE_RESISTANCE_LUFT")
    if session_status=="BLOCKED": reasons.append("SESSION_RESTRICTION")
    elif session_status=="UNKNOWN": pass
    elif session_status!="PASS": raise ValueError("session status")
    return {"eligible":not reasons,"reasons":reasons,"activity":str(k) if k is not None else None,
            "session_verified":session_status=="PASS"}
