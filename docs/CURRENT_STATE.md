# K-Trader Current State

Updated: 2026-09-11

Canonical transition checkpoint:

`docs/checkpoints/2026-09-11_PHASE11G_PROSPECTIVE_CONTROL_DEPLOYMENT.md`

Previous operational checkpoint:

`docs/checkpoints/2026-09-11_PHASE11G_24H_CONTROL_AND_RUNTIME_HARDENING.md`

Latest horizon research checkpoint:

`docs/checkpoints/2026-09-09_PHASE11G_HORIZON_TIMESPLIT_VALIDATION.md`

## Current phase boundary

- Phase 10: COMPLETE / current single-provider read-only product accepted;
- Phase 11A-11F: VERIFIED;
- Phase 11G dataset-catalogue foundation: VERIFIED;
- Phase 11G catalogue: two canonical chains, `SUIUSDT` + `XRPUSDT`;
- Phase 11G prospective-control tooling: CANONICAL / deterministic sharding+resume / explicit midnight fail-closed handling;
- FAST/M5 lifecycle: PRODUCTION, TTL `60m = 12 x M5 bars`;
- corrected FAST W1-W4 historical closure: COMPLETE / zero tradable signals;
- 2026-09-10→11 prospective 24h control: COMPLETE / zero tradable signals;
- provider-recorded prospective discovery: ACTIVE;
- INTRADAY/M15 lifecycle: RESEARCH ONLY / universal TTL unresolved;
- MEDIUM/H1 lifecycle: RESEARCH ONLY / `8-12h` lifecycle design band time-split validated, not profitability-optimal;
- Phase 12 multi-provider expansion: FUTURE / NOT ACTIVE.

## Production identity

Accepted runtime/deployment baseline:

- runtime SHA: `a73ba261a3ca97d2df3deac20b1459b7b4c38fff`;
- image: `k-trader:a73ba261a3ca97d2df3deac20b1459b7b4c38fff`;
- approved GitHub Actions deployment run `34612617730`: SUCCESS;
- host: Oracle Cloud Ampere A1 / Ubuntu 24.04 ARM64;
- production provider: `binance_usdm`;
- container: healthy;
- `/health`: `status=ok`, `data_ready=true`;
- provider REST/WebSocket acceptance: PASS;
- MTF API acceptance: PASS;
- public HTTPS / Phase 10 Action acceptance: PASS;
- application remains read-only;
- GitHub PR/CI/manual deployment remains the canonical source/activation path.

The canonical prospective-control utility is now deployed in production at `a73ba261a3ca97d2df3deac20b1459b7b4c38fff`. Deployment run `34612617730` checked out the exact approved SHA, passed ARM64 identity, canonical deploy acceptance, and left the service healthy/read-only.

## Runtime hardening accepted on 2026-09-11

Two operational defects were closed without changing trading semantics.

### D1 retry backoff — PR #45

Young contracts with insufficient D1 history are still rejected fail-closed, but the scanner no longer re-fetches the same impossible D1 requirement every cycle. Retry is deferred until the next UTC day boundary.

Unchanged:

- D1 minimum remains `250` for runtime readiness;
- universe ranking/analysis-limit semantics remain unchanged;
- no substitute symbol is promoted to manufacture a full eligible shortlist;
- RR, ATR, TTL, structure, target and scoring rules remain unchanged.

### Recent MTF gap heal — PR #46

The manual 24h control found recent persisted `15m` gaps for mature symbols `IOSTUSDT` and `DOTUSDT`, even though Binance deep history was contiguous.

Root cause: recent count/freshness could pass even when the required window was non-contiguous. PR #46 added recent-sequence contiguity validation to `_ensure_ready()` and routes failures through the existing canonical bootstrap-heal path.

Production acceptance after Deploy #11:

- `IOSTUSDT 15m`: 250 required recent bars, contiguous, gaps `[]`;
- `DOTUSDT 15m`: 250 required recent bars, contiguous, gaps `[]`;
- both bootstrap-healed successfully;
- no mature-symbol MTF gap remained in the accepted observation.

## Current scanner state

Post-deploy observation:

- scanner status: `DEGRADED`;
- `symbols_ready=17`;
- `symbols_failed=3`;
- `live_streaming=true`;
- current failures: `牛来USDT`, `MARSCOINUSDT`, `PONSUSDT`;
- reason: insufficient closed D1 history;
- retries correctly deferred until the next UTC day boundary;
- `/v1/signals`: `count=0`.

`DEGRADED` currently reflects expected young-contract ineligibility rather than a mature-symbol data-integrity defect.

## 24h prospective control

Control interval:

- start: `2026-09-10T04:15:00Z`;
- end: `2026-09-11T07:20:00Z`;
- logical M5 cutoffs: `326`;
- selected context cutoffs: `326/326`;
- unique selected snapshots: `326`;
- production analysis limit: top-20;
- provider: `binance_usdm`;
- context rule: newest recorded snapshot at/before cutoff, age `<=300s`.

Universe archive SHA:

`3048d9129a9667b1cb97124f25c7c9deccc082cc8a5a7d4cd975081c45676a57`

Scanner-config SHA:

`2ad4b4369f3276eb081b02fe44c9b05bec49bf05a7ae4f146dcbe66ff594bff0`

Prospective report SHA:

`dcbacc311c722ce1dea7313b80df38271f0ba1404cd0bd2f166a8399f8b14e7d`

Coverage:

- symbol slots: `6520`;
- fully analyzed/history-pass slots: `5448`;
- history-fail slots: `1055`;
- analysis-error slots: `17`;
- decision records: `67822`;
- unique tradable signals: `0`.

History failures were concentrated in insufficient-history young contracts:

- `MARSCOINUSDT`: `326`;
- `PONSUSDT`: `326`;
- `牛来USDT`: `326`;
- `KATUSDT`: `77`.

The 17 analysis errors were explicit `ValueError: 5m day sequence is empty` records at the UTC-day boundary. They were not converted into decisions.

## Canonical prospective-control hardening

PR #48 converts the temporary long-run control methodology into repository-owned tooling:

- core: `src/ktrader/replay/prospective.py`;
- CLI: `scripts/run_prospective_control.py`;
- contract: `docs/PROSPECTIVE_CONTROL_SPEC.md`;
- focused tests: `tests/test_phase11g_prospective_control.py`.

Canonical behavior:

- logical cutoffs are deterministic and interval-aligned;
- context is newest recorded universe snapshot `<= cutoff`, exact `300s` still valid, `>300s` stale;
- recorded top-N ranking is preserved with no lower-ranked substitution for history failures;
- candles come only from `slice_datasets_asof()` and therefore cannot include future closes;
- the same `analyze_candle_snapshot()` remains the analysis implementation;
- empty current-UTC-day M5 state is recorded as `ANALYSIS_ERROR` before analyzer invocation, with no synthetic range/candle/decision;
- slot accounting is explicit as `ANALYZED`, `HISTORY_FAIL`, or `ANALYSIS_ERROR`;
- deterministic modulo sharding supports atomic checkpoints and strict-provenance resume;
- merge requires complete coherent shard coverage and yields the same final report/hash as equivalent monolithic execution.

Focused acceptance evidence: `4 passed`; repository-wide Python 3.12 regression: `208 passed`; Python 3.14 regression: PASS. Canonical merge remains governed by `canonical-merge-gate`, including amd64/arm64 image validation.

## 24h sequential hard-gate funnel

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

Interpretation:

- natural deterministic setups did survive through TTL during the window;
- none of the 10 final TTL-valid survivors had structural `RR >= 3`;
- no evidence supports weakening RR, ATR, TTL, HTF, level-strength or structural-target rules;
- no signal was materialized.

## Strict Phase 11G policy

Unchanged controls:

- current production research provider: `binance_usdm`;
- `max_context_age_seconds=300`;
- historical context uses newest recorded snapshot at/before cutoff;
- no historical rank/context fabrication;
- no freshness widening to manufacture samples;
- live and replay use the same canonical analyzer;
- structural target only; no synthetic 3R target;
- `RR >= 3` hard gate;
- canonical ATR-used hard gate;
- HTF directional-alignment hard gate;
- STRONG/confirmed primary-level gate;
- FAST TTL: `60m`, hard reject only when age is strictly greater than 60m;
- outcome samples only from real binary WIN/LOSS outcomes;
- no synthetic outcomes;
- no probability calibration;
- `estimated_probability` remains null/N/A;
- no Phase 12 activation while Phase 11G continuous discovery is open.

## Dataset catalogue

Canonical persisted catalogue remains:

- `/data/research/phase11g/catalogue.json`;
- schema: `ktrader.dataset_catalogue.v1`;
- entries: `2`;
- symbols: `SUIUSDT`, `XRPUSDT`;
- no new chain from the 24h control;
- no new outcome sample.

Catalogue SHA semantics are resolved: `catalogue_sha256` is the semantic digest of `{schema_version, entries}`. The serialized `catalogue.json` file has a separate raw content hash by design; the difference is not corruption.

## Horizon profiles

| Profile | Setup interval | Lifecycle | State |
| --- | --- | --- | --- |
| FAST | M5 | 60m | PRODUCTION |
| INTRADAY | M15 | unresolved | RESEARCH ONLY |
| MEDIUM | H1 | 8-12h design band | RESEARCH ONLY |

No adaptive TTL table by symbol/evidence/primary-level timeframe is approved.

## Operational access

Policy-constrained SentinelX access to `k-trader-prod-vnic` remains the accepted direct diagnostic/maintenance channel.

Security boundary remains:

- no arbitrary root execution;
- no unrestricted `NOPASSWD: ALL`;
- structured K-Trader filesystem access is read-only;
- SSH remains independent recovery/bootstrap;
- repository source mutation and production activation continue through GitHub PR/CI/deploy rather than direct host edits.

Canonical details: `docs/SENTINELX_REMOTE_ACCESS.md`.

## Next action

1. keep provider-recorded production capture active;
2. use the canonical prospective-control utility for future long-window controls instead of temporary ad-hoc scripts;
3. continue natural prospective discovery under unchanged FAST/M5 hard gates;
4. materialize/register a new Phase 11G chain only after a natural LONG/SHORT signal survives every hard gate and exact provenance is captured;
5. evaluate outcomes only from subsequent real bars;
6. keep M15/H1 research-only and Phase 12 inactive until a later explicit approval gate.