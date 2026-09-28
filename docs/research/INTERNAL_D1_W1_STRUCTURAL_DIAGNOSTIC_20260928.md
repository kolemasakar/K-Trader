# Internal D1/W1 structural diagnostic — 2026-09-28

Research only; **not a trade backtest, not an out-of-sample test**. Read-only run on K-Trader-owned `historical_expansion_v1_20260905T144500Z/bundles` inside the existing container through the authorized SentinelX one-off script. No AI_Trading_System/external holdout access, no live trading or production edits.

Algorithm in this execution: strict 3-left/3-right pivot on D1 and fully complete UTC Monday–Sunday W1, confirmation after right-hand bars; support and resistance clustered separately with complete price span <=0.3% of minimum price. Grouping is exploratory and not strength calibrated. Run returned code 0 and 19 results. This was an in-memory audit implementation of the same research concept; **do not represent it as executing the committed research runner or its tests**.

| Symbol | D1 pivots | W1 pivots | Zones | D1/W1 mixed |
|---|---:|---:|---:|---:|
| 1000PEPEUSDT | 104 | 11 | 96 | 11 |
| ADAUSDT | 95 | 12 | 91 | 12 |
| AKEUSDT | 67 | 9 | 64 | 8 |
| ARBUSDT | 91 | 11 | 84 | 11 |
| DOGEUSDT | 110 | 11 | 95 | 11 |
| DOTUSDT | 98 | 13 | 90 | 13 |
| ENAUSDT | 103 | 11 | 97 | 11 |
| ETHFIUSDT | 100 | 13 | 92 | 13 |
| IOSTUSDT | 96 | 13 | 91 | 13 |
| METUSDT | 65 | 7 | 60 | 7 |
| NEARUSDT | 103 | 15 | 90 | 13 |
| PUMPUSDT | 74 | 10 | 69 | 10 |
| RAYSOLUSDT | 97 | 11 | 86 | 11 |
| SUIUSDT | 101 | 11 | 95 | 11 |
| TRUMPUSDT | 95 | 14 | 85 | 14 |
| USELESSUSDT | 73 | 9 | 71 | 9 |
| VTHOUSDT | 102 | 12 | 93 | 12 |
| WLDUSDT | 101 | 13 | 91 | 13 |
| XRPUSDT | 99 | 13 | 79 | 13 |
| **TOTAL** | **1774** | **219** | **1619** | **216** |

Interpretation limits: near-coincident D1/W1 pivots may represent the same event rather than independent corroboration. Zone counts are sensitive to grouping bandwidth and sample duration. Current analysis counts all confirmed pivots using complete data; it does not construct time-varying as-of zone snapshots or measure post-formation retests, reactions, intraday entries, costs, or outcomes. The next gate is to run the committed modules' synthetic tests, compare parity with this audit, deduplicate same-event D1/W1 coincidences, and validate prospective as-of formation on own internal data before any reserved external holdout.

## Parity and tests (2026-09-28 continuation)
Fetched the actual three research Python modules from this branch and executed `internal_level_structure_diagnostics_v1.run` in a temporary directory inside the existing container against the 19 internal native D1 sources, read-only. Exit 0, 19/19 `EXPLORATORY_STRUCTURE_ONLY_NOT_BACKTEST`. Exact parity with earlier in-memory audit for all 19 symbols and all four reported metrics: 1,774 D1 pivots, 219 W1 pivots, 1,619 zones, 216 mixed D1/W1 zones.

Both host and container lack pytest. Without installing software, executed the **actual eight repository test functions** from `test_native_internal_d1_w1_v1.py` and `test_structural_level_clusters_v1.py` via an isolated Python harness supplying a minimal `pytest.raises` substitute and temporary path fixtures: 8/8 PASS. This is **not a full pytest suite run** and does not cover other repository tests. Next: same-event deduplication and causal as-of reaction validation before assessing trading performance. No external holdout or production modifications.

## Same-event D1/W1 deduplication (2026-09-28)
Added `scripts/research/internal_causal_level_reactions_v1.py` (commit `c1da90d`), which identifies exact same-kind, same-price D1/W1 events when the W1 extreme occurs at the D1 pivot price inside that UTC week. This is an **event identity diagnostic**, not independent evidence of zone strength. The 19-symbol read-only internal execution returned 1,993 raw pivots, 217 duplicate D1/W1 event records and 1,776 unique structural events. Note 217 duplicates is not identical to the 216 mixed clusters: zone grouping and exact event identity answer different questions. No source file or production service changed.

The new causal reaction prototype reconstructs zones using only pivots confirmed as of each D1 close, checks a subsequent D1 touch and measures descriptive movement in later completed D1 candles. Two isolated smoke assertions passed (exact same-event matching and no future pivot). **Causal reaction counts/rates have not been run or validated**. Important unresolved research issue: the prototype's zone-identity key can change as new pivots join a zone, so repeated touches may be double-counted. Freeze and test a stable first-formation zone ID and establish reaction control baselines before reporting rates or interpreting performance. W1 confirmation must retain its actual later timestamp even when same-event identity matches D1.

## Gradient integration and causal close-location audit
Research commits: c7a49b1 (integrated runner), ea38674 (integration tests). On 19 own historical D1 sources, temporary read-only execution of the committed modules returned 1,776 independent event identities, 1,602 created gradient zones and 153 geometry revisions. Using next-day D1 **close inside a nonzero-width zone**, gradient >=0.75 was classified center (6 observations), <=0.25 edge (12 observations); intermediate and zero-width cases excluded. Favorable displacement was examined over five subsequent completed D1 bars. Counts are insufficient for a center/edge superiority claim. A D1 close-location comparison does not capture intraday touch order or tradable entries. Three actual repository integration test functions passed using an isolated minimal pytest.raises shim, not full pytest. The experimental band is 0.3% for incremental cluster attachment; no ATR. Existing zone IDs persist on revisions, with no automatic split/merge resolution. First eligible classified close per zone only; this creates selection and sample-size limitations. No external holdout or production changes.

## Gradient opportunity funnel (19 internal symbols; same 5-day outcome eligibility)
Commit `5743035` adds `scripts/research/internal_gradient_opportunity_audit_v1.py`; commit `aebe3c9` adds five tests. Read-only run of the committed modules on the internal D1 panel: 385,793 zone-days overall; 25,926 nonzero-width zone-days; 1,317 D1 high-low zone intersections (1,284 include center, 33 edge-only), 37 D1 closes inside nonzero zones (7 center, 15 edge, 15 middle). Separately, singleton levels: 15,717 D1 range crossings and 55 exact closes. Counts include repeated zone-days and are NOT independent signals or P&L. All 5 new actual test functions passed in a temporary Python harness with minimal pytest.raises shim; full pytest remains unavailable. Fixed existing 0.3% research band, no ATR, no external holdout, no production edits. D1 OHLC cannot resolve intrabar path, so high-low intersection cannot be labeled a confirmed center/edge reaction; lower timeframe data may be used only for later reaction timing, not for identifying levels. Before reaction inference: prespecify first-contact cohort, singleton handling, and control baseline; verify M15/M30 source availability and causality without retuning on reserved holdout.

## Rebuilt confirmed High/Low level analysis (v2)
`internal_extreme_zone_rebuild_v2.py` (`6639db9`) rebuilds from D1/W1 local highs for resistance and local lows for support, strict 3-left/3-right confirmation. Clustering uses confirmed independent event extrema, not closes, with fixed exploratory 0.3% complete-link band. Next closed D1 high-low intersection determines first contact; the candle's directional low/high can extend beyond zone bounds. First contact is counted once per zone ID, including singleton first contacts; if a singleton later grows into a nonzero zone, its original contact remains consumed (important selection limitation). On 19 internal datasets, read-only v2 run: 1,776 independent extremes, 1,602 created zones/singletons, 153 geometry revisions; 1,347 first contacts (1,324 singleton, 23 nonzero), 22 of the 23 nonzero contacts span center and 1 is edge-only. These are not independent intraday reactions or trade entries. Later zone revisions are tracked, not backdated; split/merge lineage remains unresolved. Four actual repository tests passed in isolated minimal pytest shim (`e9269ab`), not full pytest. No ATR, no external holdout, no HP-OMEN or production modifications. Next: assess sensitivity of first-contact censoring, explicit version-level cohorts, and lower-timeframe contact ordering only after internal data-source availability is verified.
