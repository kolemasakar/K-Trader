"""Experimental gradient structural zones; no ATR or trading decisions.

Stable ID comes from the first confirmed independent structural event.
Revisions keep that ID and preserve the earlier geometry.
"""
import hashlib
import math

def event_id(p):
    required=("kind","pivot_open_ms","price")
    if any(k not in p for k in required): raise ValueError("missing event identity")
    if p["kind"] not in ("support","resistance") or not math.isfinite(p["price"]) or p["price"]<=0:
        raise ValueError("invalid event")
    # Caller supplies an independent-event ID when D1 and W1 are the same event.
    if p.get("independent_event_id"):
        return str(p["independent_event_id"])
    return hashlib.sha256(repr((p["kind"],p["pivot_open_ms"],p["price"])).encode()).hexdigest()[:20]

def geometry(events, as_of_ms):
    """One event, one contribution. W1 recognition never backdates availability."""
    known={}
    for p in events:
        if p["confirmed_close_ms"]>as_of_ms: continue
        key=event_id(p)
        if key not in known or p["confirmed_close_ms"]<known[key]["confirmed_close_ms"]:
            known[key]=p
    if not known: raise ValueError("no confirmed events")
    kinds={p["kind"] for p in known.values()}
    if len(kinds)!=1: raise ValueError("mixed support and resistance")
    ordered=sorted(known.values(),key=lambda p:(p["confirmed_close_ms"],event_id(p)))
    prices=[p["price"] for p in ordered]
    # Equal weights until an independent calibration protocol is approved.
    low=min(prices);high=max(prices);center=sum(prices)/len(prices)
    first=ordered[0]
    zone_id=hashlib.sha256(repr((first["kind"],event_id(first))).encode()).hexdigest()[:24]
    return {"zone_id":zone_id,"as_of_ms":as_of_ms,"first_known_ms":first["confirmed_close_ms"],
            "kind":first["kind"],"low":low,"center":center,"high":high,
            "independent_event_count":len(ordered),"event_ids":sorted(known),
            "status":"EXPERIMENTAL_GRADIENT_ZONE"}

def gradient(zone, price):
    if not math.isfinite(price): raise ValueError("non-finite price")
    low,center,high=(zone[k] for k in ("low","center","high"))
    if not (0<low<=center<=high): raise ValueError("invalid geometry")
    if low==high: return 1.0 if price==center else 0.0
    if price<low or price>high: return 0.0
    if price==center:return 1.0
    if price<center:return (price-low)/(center-low) if center>low else 0.0
    return (high-price)/(high-center) if high>center else 0.0

def revise(previous, events, as_of_ms):
    updated=geometry(events,as_of_ms)
    if previous["zone_id"]!=updated["zone_id"]:
        raise ValueError("first-event identity changed: cannot silently reuse zone ID")
    if as_of_ms<previous["as_of_ms"]:raise ValueError("revision cannot backdate")
    updated["revision"]=previous.get("revision",0)+1
    updated["previous_geometry"]={k:previous[k] for k in ("low","center","high","as_of_ms")}
    return updated
