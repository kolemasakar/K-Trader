"""Internal D1/W1 causal gradient research; read-only, no ATR or trade claims.

Event-ledger zones: attach each newly confirmed independent event to an existing
same-kind zone if complete-link span <= band; otherwise create a new zone.
Existing zone ID is anchored to first event; splits/merges are deliberately
not inferred. Compare CLOSE location on next D1 bar (not intrabar touch).
"""
from collections import defaultdict
from hashlib import sha256

def identity(p, daily):
    if p["tf"]=="1d":
        return (p["kind"],p["pivot_open_ms"],p["price"])
    week=p["pivot_open_ms"]
    key="h" if p["kind"]=="resistance" else "l"
    matches=[b for b in daily if week<=b["t"]<week+7*86400000 and b[key]==p["price"]]
    return (p["kind"],matches[0]["t"],p["price"]) if matches else (
        p["kind"],week,p["price"],"W1_UNMATCHED")

def run(daily, pivots, gradient_module, band=.003, horizon=5):
    if not 0<band<.1 or horizon<1: raise ValueError("invalid parameters")
    # Each identity is represented only once, at its earliest actual confirmation.
    unique={}
    for p in pivots:
        key=identity(p,daily)
        if key not in unique or p["confirmed_close_ms"]<unique[key]["confirmed_close_ms"]:
            q=dict(p);q["independent_event_id"]=repr(key);unique[key]=q
    incoming=sorted(unique.values(),key=lambda p:(p["confirmed_close_ms"],p["kind"],p["price"]))
    zones=[];cursor=0;observations=[];revisions=0;seen=set()
    for i in range(len(daily)-horizon-1):
        as_of=daily[i]["close_t"]
        while cursor<len(incoming) and incoming[cursor]["confirmed_close_ms"]<=as_of:
            p=incoming[cursor];cursor+=1
            matches=[z for z in zones if z["kind"]==p["kind"] and
                (max(z["high"],p["price"])-min(z["low"],p["price"]))/
                min(z["low"],p["price"])<=band]
            if matches:
                z=min(matches,key=lambda z:abs(z["center"]-p["price"]))
                z["events"].append(p)
                newer=gradient_module.revise(z["geometry"],z["events"],as_of)
                z.update(geometry=newer,low=newer["low"],center=newer["center"],high=newer["high"])
                revisions+=1
            else:
                g=gradient_module.geometry([p],as_of)
                zones.append(dict(kind=p["kind"],events=[p],geometry=g,
                                  low=g["low"],center=g["center"],high=g["high"]))
        bar=daily[i+1]
        for z in zones:
            g=z["geometry"]
            # Zero-width singleton cannot support center-vs-edge comparisons.
            if g["low"]==g["high"]:continue
            if g["zone_id"] in seen:continue
            close=bar["c"]
            if not g["low"]<=close<=g["high"]:continue
            score=gradient_module.gradient(g,close)
            # Exclude intermediate observations from the two-group comparison.
            group="center" if score>=.75 else "edge" if score<=.25 else None
            if group is None:continue
            seen.add(g["zone_id"])
            future=daily[i+2:i+2+horizon]
            if len(future)!=horizon:continue
            move=(max(x["h"] for x in future)/close-1 if g["kind"]=="support"
                  else 1-min(x["l"] for x in future)/close)
            observations.append(dict(zone_id=g["zone_id"],kind=g["kind"],
                 known_ms=as_of,observation_close_ms=bar["close_t"],
                 geometry_revision=g.get("revision",0),gradient=score,group=group,
                 favorable_move=move,reaction_1pct=move>=.01))
    stats={}
    for group in ("center","edge"):
        subset=[x for x in observations if x["group"]==group]
        stats[group]=dict(n=len(subset),reaction_1pct=sum(x["reaction_1pct"] for x in subset),
                          mean_favorable_move=sum(x["favorable_move"] for x in subset)/len(subset)
                          if subset else None)
    return dict(independent_events=len(unique),zones_created=len(zones),
                geometry_revisions=revisions,observations=observations,stats=stats,
                status="EXPLORATORY_DESCRIPTIVE_NOT_TRADING_PERFORMANCE")
