"""As-of structural price clustering for confirmed D1/W1 pivots.

No ATR, lower-timeframe levels, trade signals, or future reaction information.
The relative grouping band is a fixed research hypothesis, not a validated score.
"""
from collections import defaultdict

def cluster_confirmed(levels, as_of_ms, relative_band=0.003):
    if not 0 < relative_band < 0.1:
        raise ValueError("invalid research band")
    selected=[]
    for e in levels:
        if e["tf"] not in ("1d","1w"):
            raise ValueError("lower-timeframe level source prohibited")
        if e["confirmed_close_ms"]<=as_of_ms:
            selected.append(e)
    selected.sort(key=lambda x:(x["kind"],x["price"],x["confirmed_close_ms"]))
    groups=defaultdict(list)
    for e in selected:
        # Complete-link range bound prevents transitive merging into oversized zones.
        candidates=groups[e["kind"]]
        matches=[g for g in candidates if
                 (max(g["max_price"],e["price"])-min(g["min_price"],e["price"]))
                 / min(g["min_price"],e["price"])<=relative_band]
        if matches:
            g=min(matches,key=lambda g:abs(g["center"]-e["price"]))
            g["members"].append(e)
            g["min_price"]=min(g["min_price"],e["price"])
            g["max_price"]=max(g["max_price"],e["price"])
            g["center"]=sum(x["price"] for x in g["members"])/len(g["members"])
        else:
            candidates.append({"kind":e["kind"],"min_price":e["price"],
                               "max_price":e["price"],"center":e["price"],
                               "members":[e]})
    out=[]
    for kind,candidates in groups.items():
        for g in candidates:
            members=g["members"]
            out.append({"kind":kind,"low":g["min_price"],"high":g["max_price"],
                        "center":g["center"],"pivot_count":len(members),
                        "timeframes":sorted({x["tf"] for x in members}),
                        "first_known_ms":min(x["confirmed_close_ms"] for x in members),
                        "last_known_ms":max(x["confirmed_close_ms"] for x in members),
                        "status":"UNVALIDATED_STRUCTURAL_CLUSTER"})
    return sorted(out,key=lambda x:(x["kind"],x["center"]))
