"""Rebuilt high/low structural-level analysis, internal D1/W1 only.

A level is a confirmed D1/W1 local HIGH (resistance) or LOW (support).
Close price NEVER defines a level or its zone. Each zone begins at a
confirmed independent extreme; new confirmed extremes revise its geometry.
First future D1 high-low range intersection is an observation, not a
trade or a known intraday path. No ATR, no reserved external holdout.
"""
from collections import Counter
def rebuild(daily,pivots,gradient_module,identity_fn,band=.003,horizon=5):
    if not 0<band<.1 or horizon<1:raise ValueError("invalid parameters")
    independent={}
    for p in pivots:
        if p["tf"] not in ("1d","1w"):raise ValueError("D1/W1 only")
        k=identity_fn(p,daily)
        if k not in independent or p["confirmed_close_ms"]<independent[k]["confirmed_close_ms"]:
            q=dict(p);q["independent_event_id"]=repr(k);independent[k]=q
    events=sorted(independent.values(),key=lambda x:(x["confirmed_close_ms"],gradient_module.event_id(x),x["kind"],x["price"]))
    zones=[];cursor=0;revision_count=0;first_contact=set()
    counts=Counter();observations=[];changes=[]
    for i in range(len(daily)-horizon-1):
        asof=daily[i]["close_t"]
        while cursor<len(events) and events[cursor]["confirmed_close_ms"]<=asof:
            p=events[cursor];cursor+=1
            candidates=[z for z in zones if z["kind"]==p["kind"] and
                (max(z["geometry"]["high"],p["price"])-min(z["geometry"]["low"],p["price"]))/
                min(z["geometry"]["low"],p["price"])<=band]
            if candidates:
                z=min(candidates,key=lambda x:abs(x["geometry"]["center"]-p["price"]))
                old=z["geometry"];z["events"].append(p)
                new=gradient_module.revise(old,z["events"],asof);z["geometry"]=new
                revision_count+=1
                changes.append({"zone_id":new["zone_id"],"asof":asof,
                    "old_low":old["low"],"old_high":old["high"],
                    "new_low":new["low"],"new_high":new["high"],
                    "old_center":old["center"],"new_center":new["center"]})
            else:
                new=gradient_module.geometry([p],asof)
                zones.append({"kind":p["kind"],"events":[p],"geometry":new})
        bar=daily[i+1]
        for z in zones:
            geo=z["geometry"];low=geo["low"];high=geo["high"];center=geo["center"]
            if geo["zone_id"] in first_contact:continue
            if not (bar["l"]<=high and bar["h"]>=low):continue
            first_contact.add(geo["zone_id"])
            counts["first_contacts"]+=1
            singleton=low==high
            counts["singleton" if singleton else "nonzero"]+=1
            # D1 range shows that center was spanned, not that it reacted there.
            center_spanned=bar["l"]<=center<=bar["h"]
            if not singleton:
                counts["center_spanned" if center_spanned else "edge_only_range"]+=1
            # A candle's directional extreme may overshoot beyond the zone.
            extreme=bar["l"] if geo["kind"]=="support" else bar["h"]
            position=("below" if extreme<low else "above" if extreme>high
                      else "inside")
            counts["extreme_"+position]+=1
            future=daily[i+2:i+2+horizon]
            if len(future)!=horizon:continue
            # Use center as a descriptive common reference, NOT assumed entry.
            favorable=(max(x["h"] for x in future)/center-1 if geo["kind"]=="support"
                       else 1-min(x["l"] for x in future)/center)
            observations.append({"zone_id":geo["zone_id"],"kind":geo["kind"],
                "first_contact_close_ms":bar["close_t"],"asof_ms":asof,
                "revision":geo.get("revision",0),"low":low,"center":center,"high":high,
                "singleton":singleton,"center_spanned":center_spanned,
                "directional_extreme":extreme,"extreme_position":position,
                "favorable_move_from_center":favorable,
                "descriptive_move_1pct":favorable>=.01})
    return {"status":"REBUILT_HIGH_LOW_EXPLORATORY_NO_INTRABAR_CAUSALITY",
            "independent_extremes":len(events),"zones_created":len(zones),
            "geometry_revisions":revision_count,"counts":dict(counts),
            "changes":changes,"observations":observations}
