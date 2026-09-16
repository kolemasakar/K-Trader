# K-Trader Prospective 14:15Z Continuity Checkpoint

Status: **ACCEPTED**

Cutoff: `2026-09-16T14:15:00Z`

## Scope

This checkpoint advances the accepted prospective state after resolver-v1.3 acceptance. It does not alter frozen strategy semantics, holdout authorization, production execution, RR, max hold, risk gates or direction filters.

## Capture

Run root:

`/data/research/phase11g/v2_2_shadow_20260916T141500Z`

- status: `VALID_SHADOW_CAPTURE`;
- provider: `binance_usdm`;
- panel: `19/19`;
- missing symbols: `0`;
- current-capture eligible setups: `48`;
- current-capture unique eligible families: `37`;
- event count: `298`;
- signal bars evaluated: `6574`;
- bundle set SHA256: `56e108731b61cfa1f5ef6d72cc3d5a14f95c5147e2a55a6c8dfd9ca50bc8b47d`;
- event file SHA256: `95f1256cb01c1ce720df4ef2f4974440df57678b2bc0653512f6e12c2bf27aa8`;
- shadow summary SHA256: `dbab78e36542e4471ca248d409f9dc0d2db2cb1aa89e65342b6018e5dcc27e90`;
- holdout opened: `false`;
- production action: `false`.

## Ledger

After rebuilding across all accepted snapshots:

- discovered snapshots: `21`;
- valid snapshots: `20`;
- rejected snapshots: `1` known historical infrastructure-invalid first attempt;
- eligible observations: `60`;
- unique primary families: `46`;
- ledger event-set SHA256: `06070917e913759c680b9a0e420742864ac7772e5796036b453be437223ac0a7`.

Relative to the previous 43-family state, three new primary families are present:

- TRUMPUSDT SHORT, entry `2026-09-16T12:30:00Z` — pre-prereg discovery/context only;
- ADAUSDT SHORT, entry `2026-09-16T13:15:00Z` — post-prereg confirmation sample;
- DOGEUSDT SHORT, entry `2026-09-16T13:15:00Z` — post-prereg confirmation sample.

The later TRUMPUSDT 13:15Z observation belongs to the already-primary 12:30Z TRUMP family and therefore does not create a post-prereg primary family.

## Funding

Persisted official Binance USD-M funding snapshot:

- symbol count: `19`;
- record count: `1859`;
- summary SHA256: `19ecb0e27938375970e62f344439e9978511f23f24b15cca322e565fcab2f979`.

## Resolver v1.3 continuity

Canonical output:

`/data/research/phase11g/strategy_benchmark_v1/combined_rules/prospective_v2_2_outcomes_offline_v1_3/20260916T141500Z`

Summary SHA256:

`0f71d5c954d3176565c5380c134049f00d107a2404a82f5a03cb2af99dad15e2`

State:

- eligible observations: `60`;
- unique primary families: `46`;
- resolved primary families: `39`;
- unresolved primary families: `7`;
- wins/losses: `9/30`;
- win rate: `23.0769230769%`;
- resolved expectancy: `-0.6482720085510278R`;
- evidence tier: `DIAGNOSTIC_30_49_RESOLVED_FAMILIES`;
- prior terminal observations reused: `50`;
- current-path revalidated: `44`;
- source-window-expired accepted outcomes preserved: `6`;
- max prior entry delta: `0.0`;
- max prior stop delta: `3.495449963004417e-9`;
- network used: `false`;
- holdout opened: `false`;
- production action: `false`.

Parity against all 50 previously accepted resolved observations:

- found: `50/50`;
- terminal/economic mismatches: `0`;
- result: **PASS**.

Resolver v1.3 remains unchanged and canonical. The earlier temporary fixed-`4e-9` diagnostic output created during investigation was explicitly discarded before the canonical run and is not accepted evidence.

## Post-prereg confirmation sample

Preregistered boundary:

`entry_time >= 2026-09-16T13:00:00Z`

Current post-prereg primary sample:

- ADAUSDT SHORT, entry `13:15Z`, unresolved, `h1_ema_sep_atr≈1.7236`;
- DOGEUSDT SHORT, entry `13:15Z`, unresolved, `h1_ema_sep_atr≈1.6144`.

Both are H1 `REST`, not `LOW` (`LOW < 0.9033277894201235`).

Confirmation counts:

- total post-prereg primary families: `2`;
- resolved: `0`;
- H1 LOW resolved: `0`;
- H1 REST resolved: `0`.

No preregistered hypothesis can yet be evaluated.

## Unresolved primary families at 14:15Z

Pre-prereg/discovery context:

- SUIUSDT SHORT `08:00Z`: `25/32` bars;
- XRPUSDT SHORT `08:00Z`: `25/32` bars;
- ADAUSDT SHORT `08:15Z`: `24/32` bars;
- DOGEUSDT SHORT `08:15Z`: `24/32` bars;
- TRUMPUSDT SHORT `12:30Z`: `7/32` bars.

Post-prereg confirmation:

- ADAUSDT SHORT `13:15Z`: `4/32` bars;
- DOGEUSDT SHORT `13:15Z`: `4/32` bars.

The four early families retain causal max-hold boundaries `16:00Z` and `16:15Z` if STOP/3R does not occur first.

## Diagnostics

Resolved sample remains `39`, therefore all findings remain diagnostic-only.

14:15Z descriptive report SHA256:

`29c636f0a4a8b01fb0fb4b24ee9588955b97700ca3bb698ac3b4fd66df485621`

14:15Z statistical report SHA256:

`8d8ad6f472a61beb32afbc7f0927cb213282939ef5b02e29a36a2bf07216c306`

Resolved metrics are unchanged. Portfolio diagnostics changed because more unresolved SHORT families coexist:

- max concurrent all: `7`;
- max concurrent SHORT: `7`;
- largest correlated cohort: `4`;
- multi-family correlated cohort count: `5`.

No diagnostic result authorizes an in-place frozen-v2.2 rule change.

## Governance

- Phase 11G remains **ACTIVE**;
- Phase 12 remains **FUTURE / NOT ACTIVE**;
- frozen v2.2 remains unchanged;
- holdout remains untouched and unauthorized;
- production remains read-only;
- K_Investigation_Forecast strategy-discovery work remains external and is not reopened inside K-Trader.

## Next work order

1. Continue causal prospective collection with canonical resolver v1.3.
2. Resolve the seven open primary families only after real STOP/3R or causal max hold.
3. Keep pre-13:00Z primary families excluded from prereg confirmation counts.
4. Track the two post-prereg REST families separately.
5. When the early four families reach their actual 16:00Z/16:15Z boundaries, run capture → funding → resolver → diagnostics and reassess the evidence tier.
