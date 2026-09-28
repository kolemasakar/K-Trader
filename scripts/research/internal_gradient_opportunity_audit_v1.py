"""Read-only diagnostic of why D1 close-location gradient samples are sparse.

Reports opportunity counts, NOT trades. D1 high-low intersection cannot
establish intraday path or center-first/edge-first ordering.
"""
def classify(zone, bar):
    low,center,high=(zone[k] for k in ("low","center","high"))
    if not (0<low<=center<=high):raise ValueError("invalid zone")
    if low==high:
        return {"width":"singleton","range_cross":bar["l"]<=center<=bar["h"],
                "close_inside":bar["c"]==center,"range_center_cross":None,
                "range_edge_only":None}
    intersects=bar["l"]<=high and bar["h"]>=low
    center_cross=intersects and bar["l"]<=center<=bar["h"]
    close=low<=bar["c"]<=high
    score=(bar["c"]-low)/(center-low) if bar["c"]<center else (
        (high-bar["c"])/(high-center) if bar["c"]>center else 1.0)
    return {"width":"nonzero","range_cross":intersects,"close_inside":close,
            "range_center_cross":center_cross,
            "range_edge_only":intersects and not center_cross,
            "close_group":("center" if score>=.75 else "edge" if score<=.25
                           else "middle") if close else None}

def count_opportunities(daily,pivots,gradient_module,identity_fn,band=.003,horizon=5):
    """Incremental confirmed-event ledger, including repeat zone-days.

    Excludes last horizon days to match the existing reaction study's window.
    Does not compute reaction performance or use future pivots.
    """
    if not 0<band<.1 or horizon<1:raise ValueError("invalid parameters")
    unique={}
    for p in pivots:
        k=identity_fn(p,daily)
        if k not in unique or p["confirmed_close_ms"]<unique[k]["confirmed_close_ms"]:
            q=dict(p);q["independent_event_id"]=repr(k);unique[k]=q
    incoming=sorted(unique.values(),key=lambda p:(p["confirmed_close_ms"],p["kind"],p["price"]))
    zones=[];cursor=0
    counters={k:0 for k in ("all_zone_days","nonzero_zone_days","range_intersects",
              "range_center_cross","range_edge_only","close_in_zone","close_center",
              "close_edge","close_middle","singleton_range_cross","singleton_close_exact")}
    for i in range(len(daily)-horizon-1):
        asof=daily[i]["close_t"]
        while cursor<len(incoming) and incoming[cursor]["confirmed_close_ms"]<=asof:
            p=incoming[cursor];cursor+=1
            matches=[z for z in zones if z["kind"]==p["kind"] and
                     (max(z["high"],p["price"])-min(z["low"],p["price"]))/
                     min(z["low"],p["price"])<=band]
            if matches:
                z=min(matches,key=lambda z:abs(z["center"]-p["price"]))
                z["events"].append(p)
                updated=gradient_module.revise(z["geometry"],z["events"],asof)
                z.update(geometry=updated,low=updated["low"],
                         center=updated["center"],high=updated["high"])
            else:
                geo=gradient_module.geometry([p],asof)
                zones.append(dict(kind=p["kind"],events=[p],geometry=geo,
                                  low=geo["low"],center=geo["center"],high=geo["high"]))
        for z in zones:
            counters["all_zone_days"]+=1
            result=classify(z,daily[i+1])
            if result["width"]=="singleton":
                counters["singleton_range_cross"]+=int(result["range_cross"])
                counters["singleton_close_exact"]+=int(result["close_inside"])
                continue
            counters["nonzero_zone_days"]+=1
            counters["range_intersects"]+=int(result["range_cross"])
            counters["range_center_cross"]+=int(result["range_center_cross"])
            counters["range_edge_only"]+=int(result["range_edge_only"])
            counters["close_in_zone"]+=int(result["close_inside"])
            if result["close_inside"]:
                counters["close_"+result["close_group"]]+=1
    return {"status":"OPPORTUNITY_DIAGNOSTIC_NOT_TRADING_PERFORMANCE",
            "counts":counters,"unique_event_count":len(unique),
            "note":"D1 range crossing does not establish intrabar sequence"}
