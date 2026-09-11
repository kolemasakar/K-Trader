# Phase 11G Survivorship Diagnostic and Pre-Freeze Acceptance

Date: 2026-09-11

Status: ACCEPTED / PRODUCTION READ-ONLY / CONTINUOUS DISCOVERY ACTIVE / PHASE 12 INACTIVE

## Production identity

- canonical application/runtime SHA: `81b79b281a4cc330b7c11058d202e0d74fb6d70e`;
- PR #53: `Add Phase 11G unique-level survivorship diagnostic` — squash merged;
- PR-head CI #186 (`34624965946`): SUCCESS;
- post-merge CI #187 (`34625353779`): SUCCESS;
- Python 3.12/3.14, Docker amd64/arm64 and `canonical-merge-gate`: PASS;
- approved deployment run `34625823230`: SUCCESS;
- deployment used exact-SHA checkout, ARM64 identity verification and canonical rollback-capable `scripts/deploy.sh` acceptance;
- temporary deployment trigger was removed after success.

Production acceptance after deploy:

- `/opt/k-trader/DEPLOYED_SHA` = `81b79b281a4cc330b7c11058d202e0d74fb6d70e`;
- `/health`: `status=ok`, `mode=read_only`, `data_ready=true`;
- provider: `binance_usdm`;
- survivorship CLI packaged: PASS;
- no trading semantics changed.

## Capture continuity across deployment

Observed universe snapshots around deployment:

```text
2026-09-11T17:05:44.854669981Z
2026-09-11T17:07:15.255774374Z
2026-09-11T17:10:15.278970641Z
```

No interval exceeded the canonical `300s` context-age limit. The deployment therefore did not create a causal research-data hole.

## New incremental prospective-control window

Non-overlap window after the previously accepted `15:05Z` endpoint:

- logical window: `2026-09-11T15:10:00Z` -> `2026-09-11T16:40:00Z`;
- context archive begins at `15:05Z`;
- universe archive snapshots: `20`;
- universe archive SHA: `a6183c457496fb52a1cfa6f44ed2e5f648efe1ae2b7eed6129e8c2ba7fb549f1`;
- recorded top-20 union: `22` symbols;
- coherent MTF bundles: `19`;
- expected insufficient-history symbols: `MARSCOINUSDT`, `PONSUSDT`, `牛来USDT`;
- `METUSDT` entered the recorded universe and exported a full coherent bundle;
- prospective shard: `19/19` complete;
- shard SHA: `4776ee40f45b3419041537082ff24e5ff12fb8a9049e73b801596aebcb95e6d6`;
- prospective report SHA: `99646b51f0effeba21bfb9dac2c32b147018e570c2e3b358f59eb49d8305e713`.

Coverage:

```text
logical cutoffs         19
symbol slots           380
history pass           323
history fail            57
analysis errors          0
decision records      4853
tradable signals         0
```

Sequential funnel:

```text
HTF aligned              207
-> strong level           69
-> valid geometry         47
-> ATR <= 80               0
-> TTL60                    0
-> RR >= 3                  0
-> Grade A/A+               0
-> tradable                 0
```

Context selection remained fully causal:

- selected context: `19/19`;
- missing context: `0`;
- stale context: `0`;
- context age range: `75.166095s` -> `255.178031s`.

## Updated cumulative non-overlap evidence

Including the accepted 24h control, the 93-cutoff incremental control and the new 19-cutoff window:

```text
logical cutoffs          438
symbol slots            8760
history pass            7352
history fail            1391
analysis errors            17
decision records       90621
tradable records            0
```

Cumulative sequential funnel:

```text
HTF aligned             2374
-> strong level          740
-> valid geometry         527
-> ATR <= 80              229
-> TTL60                   20
-> RR >= 3                  0
-> Grade A/A+               0
-> tradable                 0
```

Machine-readable cumulative artifact:

- `/data/research/phase11g/pre_pause_20260911/cumulative_after_incremental_2.json`;
- SHA-256: `fd2d7a430e54152d8a568ad8c16371d603d672f1ea1fa75b087791953ae2d907`.

## Unique-primary-level survivorship diagnostic

The canonical prospective report intentionally counts decision records per cutoff. Repeated M5 observations of the same structural level are therefore causal records but are not necessarily independent research samples.

PR #53 adds a research-only complementary diagnostic keyed by:

```text
(canonical_symbol, primary_level_id)
```

It does not modify the canonical prospective report, its hashes, or any trading gate.

Production functional acceptance used the four shards from the 93-cutoff window plus the one shard from the new 19-cutoff window.

Combined recent-window evidence:

```text
record funnel:       852 -> 309 -> 216 -> 40 -> 10 -> 0 -> 0 -> 0
unique-level funnel:  28 ->  12 ->   8 ->  4 ->  3 -> 0 -> 0 -> 0
```

Interpretation:

- `216` geometry-valid per-cutoff records correspond to only `8` distinct primary levels;
- `40` ATR-pass records correspond to `4` distinct primary levels;
- `10` TTL-pass records correspond to `3` distinct primary levels;
- no level survives the sequential RR gate;
- recent TTL-pass evidence is concentrated in `ETHFIUSDT`, grade `C`, score `69`, with RR below `3`;
- natural pre-ATR geometry records with `RR>=3` were concentrated in one repeated `VTHOUSDT` D1 support and failed ATR badly (~456% ATR-used), also grade `C`/score `69`;
- therefore record counts materially overstate independent structural evidence if interpreted without level deduplication.

Accepted survivorship artifact:

- `/data/research/phase11g/pre_pause_20260911/survivorship_recent_windows.json`;
- schema: `ktrader.prospective_survivorship.v1`;
- analysis SHA: `24688a3892e4edd583cdbc8ba41be604a87588cfd448f311b5f91b746dc7ae96`.

Earlier ad-hoc diagnostic artifact retained for audit:

- `/data/research/phase11g/pre_pause_20260911/recent_survivorship_diagnostic.json`;
- SHA-256: `ee7b67acc3af9780f8464af4f7b010f3e487e548fa01075bc98e24335995a72d`.

## Methodological conclusion

No evidence supports weakening any hard gate.

In particular:

- the `10` recent TTL-pass records are only `3` distinct structural levels and all are grade `C` / score `69`;
- relaxing RR alone would not have produced an A/A+ signal;
- the observed `RR>=3` geometry records fail ATR by a very large margin and are also grade `C`;
- future Phase 11G interpretation must report both causal record counts and distinct-primary-level survivorship before making threshold-change proposals.

## Planned technical freeze

Development freeze remains:

```text
2026-09-12 09:00 Kyiv
-> 2026-09-13 09:00 Kyiv
```

Equivalent UTC observation window:

```text
2026-09-12T06:00:00Z <= t < 2026-09-13T06:00:00Z
```

Expected clean replay target:

- `288` M5 logical cutoffs;
- up to `5760` top-20 slots before readiness accounting.

During the freeze:

- production read-only universe capture: ACTIVE;
- health/freshness monitoring: ACTIVE;
- provider data accumulation: ACTIVE;
- code changes: FROZEN;
- config changes: FROZEN;
- deployments: FROZEN except emergency recovery;
- heavy production-host replay: FROZEN;
- Phase 12: INACTIVE.

After the observation window, the first analysis should run the canonical prospective-control replay and the new survivorship diagnostic together.

## Hard rules unchanged

- structural target only;
- no synthetic 3R target;
- `RR >= 3`;
- ATR-used `<=80%`;
- HTF directional alignment;
- STRONG/confirmed primary level;
- FAST/M5 TTL `60m`, reject only when age is strictly greater than 60m;
- no lower-ranked substitution for selected-symbol history failure;
- no synthetic outcomes;
- no fabricated probability;
- `estimated_probability` remains null/N/A;
- canonical catalogue remains `SUIUSDT` + `XRPUSDT`;
- Phase 12 remains FUTURE / NOT ACTIVE.
