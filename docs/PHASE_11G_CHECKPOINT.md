# Phase 11G Checkpoint — Dataset Catalogue and Continuous Discovery

Updated: 2026-09-11

Status: **VERIFIED FOUNDATION / TWO CHAINS CATALOGUED / FAST TTL60 PRODUCTION / 24H PROSPECTIVE CONTROL COMPLETE / PROSPECTIVE TOOLING HARDENED / CONTINUOUS DISCOVERY ACTIVE**.

Detailed current transition evidence:

`docs/checkpoints/2026-09-11_PHASE11G_PROSPECTIVE_CONTROL_DEPLOYMENT.md`

Previous operational evidence:

`docs/checkpoints/2026-09-11_PHASE11G_24H_CONTROL_AND_RUNTIME_HARDENING.md`

## Canonical research chain

Phase 11G retains the deterministic `ktrader.dataset_catalogue.v1` audit chain:

```text
MTF bundle
-> universe archive
-> study cohort
-> replay study
-> study provenance
-> optional real WIN/LOSS outcome sample
-> dataset catalogue
```

All references remain fail-closed on provider/symbol/context identity, content hashes and artifact-root containment. `Setup Score` remains deterministic, not statistical probability. `estimated_probability` remains null/N/A.

## Current dataset catalogue

Path:

`/data/research/phase11g/catalogue.json`

Accepted state:

- schema: `ktrader.dataset_catalogue.v1`;
- entry count: `2`;
- symbols: `SUIUSDT`, `XRPUSDT`;
- no additional chain has been materialized;
- no binary outcome sample has been created without a real binary outcome.

Catalogue digest semantics are explicitly resolved: `catalogue_sha256` is the semantic digest over `{schema_version, entries}`; the raw serialized file has its own content hash. The two are not expected to match.

## Production research boundary

Current production runtime:

- deployed SHA/image: `a73ba261a3ca97d2df3deac20b1459b7b4c38fff`;
- approved GitHub Actions deployment run `34612617730`: SUCCESS;
- provider: `binance_usdm`;
- public/read-only runtime: healthy;
- provider REST/WebSocket: PASS;
- MTF API: PASS;
- Phase 10 public Action acceptance: PASS.

The repository-owned prospective-control utility is now present in the accepted production image. The deployment changed tooling availability only; FAST/M5 trading semantics and Phase 11G hard gates are unchanged.

FAST lifecycle is the only active production profile:

- setup interval: `5m`;
- `setup_max_age_bars=12`;
- TTL: `3600s`;
- exactly 60m remains valid;
- age strictly greater than 60m is rejected as `SETUP_EXPIRED`.

Research-only profiles remain inactive in production:

- INTRADAY/M15: universal TTL unresolved;
- MEDIUM/H1: `8-12h` is only a time-split validated lifecycle design band, not a profitability optimum;
- adaptive TTL tables are not approved.

## Runtime hardening deployed before this checkpoint

### D1 retry backoff

Young contracts with insufficient D1 history remain ineligible. Repeated bootstrap is deferred until the next UTC day boundary rather than being retried every scanner cycle.

This does not change D1 minimum history, shortlist ranking or any trading gate.

### Recent MTF contiguity heal

Recent required MTF windows are validated for contiguity during readiness. A recent gap triggers canonical bootstrap repair and the symbol remains fail-closed until valid.

Production verification after Deploy #11:

- `IOSTUSDT 15m`: contiguous 250-bar recent window;
- `DOTUSDT 15m`: contiguous 250-bar recent window;
- both repair bootstraps succeeded.

Current scanner observation:

- `DEGRADED` but usable;
- `17 ready / 3 failed`;
- only current failures: `牛来USDT`, `MARSCOINUSDT`, `PONSUSDT` with insufficient D1 history and deferred retry;
- `live_streaming=true`;
- `/v1/signals = 0`.

## Strict Phase 11G research policy

Unchanged:

- production research provider: `binance_usdm`;
- `max_context_age_seconds=300`;
- newest recorded universe snapshot at/before cutoff;
- no retroactive historical rank fabrication;
- no context-freshness widening merely to create samples;
- full canonical analyzer for live and replay;
- structural target only;
- no synthetic 3R target;
- `RR >= 3` hard gate;
- canonical ATR-used hard gate;
- HTF directional-alignment hard gate;
- STRONG/confirmed primary-level hard gate;
- no synthetic outcomes;
- WIN/LOSS sample only from real future bars;
- no probability calibration without separately approved methodology and sufficient out-of-sample evidence;
- no Phase 12 activation while continuous Phase 11G discovery remains open.

## Corrected historical FAST baseline

The accepted corrected W1-W4 FAST replay remains historical reference evidence:

- analyzed symbol-cutoffs: `2445`;
- decision records: `29508`;
- `SETUP_EXPIRED` reason occurrences: `23952`;
- HTF-aligned decisions: `1987`;
- strong primary-level stage: `944`;
- tradable decisions: `0`.

Corrected W4 reproduced the historical pre-TTL population through the strong-level stage and produced the conditional funnel:

```text
435 -> 202 -> 168 -> 142 -> 0 -> 0
HTF -> strong -> geometry -> ATR -> TTL60 -> RR>=3
```

No hard threshold was relaxed.

## Horizon validation state

Time-separated research established:

- M15 4-6h does not generalize as a universal TTL across the broader panel;
- setup/evidence type and primary-level timeframe do not currently justify adaptive TTL;
- H1 8-12h geometry survival is comparatively stable across the tested time split, but this is lifecycle-design evidence only;
- all horizon samples still produced zero tradable signals.

Therefore no non-FAST profile is production-approved.

## 2026-09-10→11 prospective control

Causal control interval:

- `2026-09-10T04:15:00Z` through `2026-09-11T07:20:00Z`;
- 326 logical M5 cutoffs;
- 326/326 causal recorded context selections;
- production top-20 analysis semantics;
- provider deep history;
- unchanged FAST hard gates.

Artifact identities:

- universe archive SHA: `3048d9129a9667b1cb97124f25c7c9deccc082cc8a5a7d4cd975081c45676a57`;
- scanner config SHA: `2ad4b4369f3276eb081b02fe44c9b05bec49bf05a7ae4f146dcbe66ff594bff0`;
- prospective report SHA: `dcbacc311c722ce1dea7313b80df38271f0ba1404cd0bd2f166a8399f8b14e7d`.

Coverage:

- symbol slots: `6520`;
- history-pass/analyzed slots: `5448`;
- history-fail slots: `1055`;
- explicit analysis errors: `17` (`5m day sequence is empty` UTC-midnight edge);
- decision records: `67822`;
- unique tradable signals: `0`.

Sequential funnel:

```text
HTF aligned               1522
-> STRONG confirmed level  431
-> valid geometry           311
-> ATR <= 80%               189
-> TTL60 pass                10
-> RR >= 3                    0
-> grade A/A+                  0
-> tradable LONG/SHORT         0
```

This is positive evidence that the engine does not fail exclusively at one early gate: natural setups reached the TTL-valid stage. The final 10 still failed structural `RR >= 3`, so no threshold reduction is justified.

## Canonical prospective-control tooling

PR #48 moves the long-run prospective-control methodology from temporary scripts into repository-owned code.

Canonical components:

- `src/ktrader/replay/prospective.py`;
- `scripts/run_prospective_control.py`;
- `docs/PROSPECTIVE_CONTROL_SPEC.md`;
- `tests/test_phase11g_prospective_control.py`.

Accepted behavior:

- deterministic interval-aligned logical cutoffs;
- newest recorded snapshot at/before cutoff, with exact `300s` accepted and `>300s` stale;
- exact recorded top-N selection with no history-failure substitution;
- causal `slice_datasets_asof()` candle snapshots;
- same canonical `analyze_candle_snapshot()` analyzer;
- UTC-midnight empty-current-day-M5 slots become explicit `ANALYSIS_ERROR` without analyzer invocation or synthetic day-range/decision;
- deterministic modulo sharding;
- atomic checkpoint/resume with strict provenance equality;
- merge requires complete coherent shard coverage;
- equivalent monolithic and sharded/resumed execution yields the same report/hash.

Focused regression: `4 passed`. Repository-wide Python 3.12 regression: `208 passed`; Python 3.14: PASS. Final acceptance remains subject to the active `canonical-merge-gate` including amd64/arm64 image checks.

## Next Phase 11G work

- keep provider-recorded production capture active;
- use the canonical prospective-control utility for future long-window controls instead of temporary ad-hoc scripts;
- continue natural prospective discovery under unchanged FAST rules;
- materialize a new chain only after a natural LONG/SHORT setup survives every hard gate;
- capture exact provider/context/config/bundle/replay provenance for any such signal;
- evaluate outcome only from later real bars;
- keep M15/H1 research-only;
- keep Phase 12 inactive until an explicit later gate.