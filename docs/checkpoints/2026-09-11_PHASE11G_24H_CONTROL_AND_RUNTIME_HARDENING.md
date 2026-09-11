# Phase 11G Checkpoint — 24h Prospective Control and Runtime Hardening

Updated: 2026-09-11

Status: **CONTROL COMPLETE / RUNTIME HARDENING DEPLOYED / CONTINUOUS DISCOVERY ACTIVE**.

## Canonical identities

- repository: `kolemasakar/K-Trader`;
- canonical `main` after PR #46: `30119a44fa82b1029d2de6e3a6f76320a7705079`;
- production deployed SHA: `30119a44fa82b1029d2de6e3a6f76320a7705079`;
- deployed image: `k-trader:30119a44fa82b1029d2de6e3a6f76320a7705079`;
- GitHub Actions deployment: `Deploy Production #11` — SUCCESS;
- deployment event: manual `workflow_dispatch` on `main`;
- production provider: `binance_usdm`;
- production profile: FAST / setup interval `5m` / TTL `60m = 12 x M5 bars`.

No direct production source mutation was used. PR/CI/Deploy Production remained the only canonical activation path.

## Repository hardening accepted before deployment

### PR #45 — D1 history retry backoff

The scanner previously re-ran provider bootstrap almost every cycle for young contracts that could not possibly gain enough D1 history before the next UTC day boundary.

Accepted behavior:

- `D1=250` remains mandatory;
- insufficient-D1 symbols remain fail-closed and ineligible;
- no replacement symbol is promoted merely to fill the top-20 analysis shortlist;
- after `Insufficient closed 1d bars`, the next bootstrap attempt is deferred until the next UTC day boundary;
- trading rules, universe ranking, RR, ATR, TTL, structure, scoring, target and probability semantics are unchanged.

Pre-merge validation included targeted tests and repository-wide regression; PR #45 merged before PR #46.

### PR #46 — recent MTF gap heal

The 24h control found persistent recent `15m` holes for mature symbols, notably `IOSTUSDT` and `DOTUSDT`, while Binance deep history for the same intervals was contiguous.

Root cause:

- live REST reconciliation can restore missing `5m` children;
- an already-finished parent bucket may not be rebuilt immediately;
- the previous `_ensure_ready()` checked recent count + freshness, but not recent contiguity;
- a recent `15m` gap could therefore survive until later analysis rejected the sequence.

PR #46 changed readiness only:

- recent required MTF windows are validated for contiguity before analysis;
- non-contiguous recent history triggers the existing canonical bootstrap-heal path;
- the symbol remains fail-closed until valid history is restored;
- D1 retry backoff from PR #45 is retained;
- no trading-engine threshold or setup rule changes.

Validation before merge:

- focused gap/runtime suite: `12 passed`;
- full temporary regression: `204 passed`;
- PR #46 CI: Python 3.12 PASS, Python 3.14 PASS, Docker amd64 PASS, Docker arm64 PASS, `canonical-merge-gate` PASS;
- PR #46 squash merge: `30119a44fa82b1029d2de6e3a6f76320a7705079`.

## Production rollout acceptance

`Deploy Production #11` checked out exact `main` SHA `30119a44fa82b1029d2de6e3a6f76320a7705079` and completed successfully.

Deployment evidence:

- Oracle production architecture gate: PASS;
- image build: PASS;
- K-Trader container: healthy;
- provider REST/WebSocket acceptance: PASS;
- runtime data readiness: PASS;
- MTF API acceptance: PASS;
- public HTTPS / Phase 10 Action live acceptance: PASS;
- `/opt/k-trader/DEPLOYED_SHA`: `30119a44fa82b1029d2de6e3a6f76320a7705079`;
- `/opt/k-trader/current`: `/opt/k-trader/releases/30119a44fa82b1029d2de6e3a6f76320a7705079`.

Post-deploy gap-heal verification:

- `IOSTUSDT 15m`: latest required 250 bars contiguous, gaps `[]`;
- `DOTUSDT 15m`: latest required 250 bars contiguous, gaps `[]`;
- both received successful bootstrap repair.

Post-deploy retry-backoff verification:

- young contracts remain fail-closed;
- scanner reports deferred retries until `2026-09-12T00:00:00Z` for `牛来USDT`, `MARSCOINUSDT`, and `PONSUSDT`;
- after deployment the prior every-cycle failed-bootstrap storm did not recur;
- subsequent bootstrap activity observed during acceptance was successful only.

Current scanner state during post-deploy observation:

- `/health`: `status=ok`, `data_ready=true`;
- scanner: `DEGRADED`;
- `symbols_ready=17`, `symbols_failed=3`;
- the three current failures are the expected young-contract insufficient-D1/deferred-retry cases;
- `live_streaming=true`;
- `/v1/signals`: `count=0`.

`DEGRADED` therefore does not currently indicate a mature-symbol MTF gap defect.

## Accumulation/control window

The operator explicitly held the system in provider-recorded accumulation mode for approximately one day before manual control.

Control interval:

- start: `2026-09-10T04:15:00Z`;
- end: `2026-09-11T07:20:00Z`;
- logical M5 cutoffs: `326`;
- selected context cutoffs: `326/326`;
- unique selected recorded snapshots: `326`;
- context policy: newest recorded snapshot at or before cutoff, age `<=300s`;
- provider: `binance_usdm`;
- analysis limit: production top-20.

Universe archive SHA:

`3048d9129a9667b1cb97124f25c7c9deccc082cc8a5a7d4cd975081c45676a57`

Scanner-config SHA:

`2ad4b4369f3276eb081b02fe44c9b05bec49bf05a7ae4f146dcbe66ff594bff0`

The dynamic top-20 population contained 26 distinct symbols during the interval. Deep provider-history export succeeded for 22 symbols with the requested research depths. Four young contracts were intentionally fail-closed for insufficient D1 history rather than fabricated or backfilled with synthetic context.

## 24h causal prospective replay

The causal replay used:

- recorded production universe snapshots;
- newest context snapshot at/before each cutoff;
- `max_context_age_seconds=300`;
- verified provider deep history;
- the same canonical `analyze_candle_snapshot()` path used by live analysis;
- production FAST lifecycle `M5 / 60m`;
- unchanged structural target, RR, ATR, HTF, strength and grading gates.

Coverage/result:

- symbol slots: `6520`;
- history-pass/analyzed slots: `5448`;
- history-fail slots: `1055`;
- analysis-error slots: `17`;
- decision records: `67822`;
- best decision side: `NO_TRADE` for all `5448` analyzed symbol-cutoffs;
- unique tradable signals: `0`.

History failures were concentrated in young contracts:

- `MARSCOINUSDT`: `326` slots;
- `PONSUSDT`: `326` slots;
- `牛来USDT`: `326` slots;
- `KATUSDT`: `77` slots.

The `17` analysis errors were `ValueError: 5m day sequence is empty`. These are recorded as a prospective-report/control-utility edge case and are not silently converted into valid decisions.

Decision setup types:

- `TRAP_LEVEL_CONFIRMATION`: `66868`;
- `TRAP_VSA_CONFIRMATION`: `741`;
- `VSA_LEVEL_CONFIRMATION`: `213`.

Observed rejection-reason occurrences include:

- `HTF_CONTEXT_MISMATCH`: `66300`;
- `PRIMARY_LEVEL_NOT_STRONG`: `42934`;
- `INVALID_GEOMETRY`: `40288`;
- `SETUP_EXPIRED`: `23670`;
- `RR_BELOW_3`: `15835`;
- `ATR_USED_OVER_80`: `10134`;
- `NO_STRUCTURAL_TARGET`: `604`.

Reason counts overlap and are not a disjoint funnel.

## Sequential hard-gate funnel

For non-`NO_SETUP` decisions, the causal sequential funnel was:

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

- the system did produce setups that survived HTF, level, geometry, ATR and TTL gates;
- none of the final 10 TTL-valid survivors had structural `RR >= 3`;
- therefore no threshold weakening is justified;
- no candidate was promoted to a signal by score alone;
- no synthetic 3R target, synthetic outcome or probability was introduced.

Prospective control report SHA:

`dcbacc311c722ce1dea7313b80df38271f0ba1404cd0bd2f166a8399f8b14e7d`

Artifact root:

`/data/research/phase11g/prospective_control_20260910_11/`

## Live control snapshot before rollout

The final live control before hardening deployment also showed zero tradable signals.

At that snapshot:

- candidate records: `156`;
- grade C: `156/156`;
- side `NO_TRADE`: `156/156`;
- `HTF_CONTEXT_MISMATCH`: `156/156`;
- only three candidates had `RR >= 3`: SUIUSDT, PUMPUSDT and ENAUSDT;
- all three still failed other immutable gates, including HTF mismatch and non-STRONG primary level; the observed SUI/PUMP/ENA cases were not tradable.

No signal materialization was justified.

## Catalogue and outcome state

Canonical Phase 11G dataset catalogue remains unchanged:

- schema: `ktrader.dataset_catalogue.v1`;
- entry count: `2`;
- symbols: `SUIUSDT`, `XRPUSDT`;
- no new chain was materialized during this control;
- no new binary outcome sample exists;
- `estimated_probability` remains null/N/A.

The previously questioned catalogue SHA difference is resolved: the stored `catalogue_sha256` is the semantic digest of `{schema_version, entries}`, while the raw serialized JSON file has a separate file-content SHA by design. This is not catalogue corruption.

## Horizon state

No non-FAST profile is activated by this checkpoint.

- FAST: `M5 / 60m` — **PRODUCTION**;
- INTRADAY/M15 — **RESEARCH ONLY**, universal TTL unresolved;
- MEDIUM/H1 — **RESEARCH ONLY**, `8-12h` validated only as a lifecycle design band, not as a profitability optimum;
- adaptive TTL by symbol/evidence/primary-level timeframe is not approved.

## Hard rules unchanged

This checkpoint does not alter:

- `RR >= 3`;
- structural SL / nearest structural target contract;
- no synthetic 3R target;
- canonical ATR-used gate;
- HTF directional alignment;
- STRONG/confirmed primary-level requirement;
- context provenance and freshness;
- D1/history requirements;
- setup grading semantics;
- no probability fabrication;
- catalogue/outcome integrity requirements.

## Current project boundary

Phase 11G remains **ACTIVE continuous discovery**.

Phase 12 remains **FUTURE / NOT ACTIVE**.

Next work after chat transition:

1. keep provider-recorded production capture active;
2. continue natural prospective discovery under unchanged FAST hard gates;
3. do not materialize a new dataset chain until a naturally occurring LONG/SHORT setup survives every hard gate;
4. when the first natural signal exists, capture exact provider/context/bundle/config provenance, replay it deterministically, then evaluate outcome only from subsequent real bars;
5. separately improve the prospective-report utility so the `5m day sequence is empty` edge is handled explicitly and long control runs are resumable/sharded without changing trading semantics;
6. keep M15/H1 research-only and Phase 12 inactive unless a later explicit gate changes that boundary.
