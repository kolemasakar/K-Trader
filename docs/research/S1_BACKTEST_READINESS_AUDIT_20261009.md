# K-Trader — S1 / MT4 backtest readiness audit and implementation ledger (2026-10-09)

Status: **DOCUMENTED / INTEGRATION PARTIAL / FULL S1 BACKTEST NOT YET EXECUTED**.
Scope: read-only verified K_AI MT4 copy on independent K-Trader host. No use of HP-OMEN, no broker/order endpoints and no production rollout. This is the implementation record, not a claim of final strategy profitability or independently verified holdout.

## 1. Sources of authority, precedence

1. **S1 owner-approved final specification**: `docs/research/GERCHIK_S1_REJECTION_APPROVED_2026-10-05.md` (research branch `research/dual-market-historical-levels-v0-1`). Explicit S1 strategy/scenario approved 2026-10-05. This overrides previous proposals and obsolete 1R/next-open assumptions.
2. `docs/research/GERCHIK_STRATEGY_OWNER_GATE_2026-10-04.json` — S1 owner-approved entries; older nested `market_runs_authorized:false` records denote intermediate states and must not override the later approved final S1 revision. Overall summary contains older values; verify latest timestamped decision and final strategy text, not a standalone boolean.
3. `docs/research/GERCHIK_FIXED_LEVEL_CLASSIFICATION_CONTRACT_V0_1.md` — 7 Gerchik pattern identities, D1/W1 High/Low-only source, one immutable primary type, reviewed strengthening evidence, no ATR in level formation.
4. `docs/research/GERCHIK_SEVEN_TYPE_IMPLEMENTATION_2026-10-04.md` — 7 **research candidate** detectors; not independently validated formation classifications.
5. `docs/research/GERCHIK_LEVEL_STRENGTH_V0_1_2026-10-04.md` and `GERCHIK_LEVEL_VERIFICATION_1_7_2026-10-04.json` — research rating and 77 prior local tests, 21 unlabelled review panels; independent human review and real-label replay remain pending. Score>=60 is **not** an S1 entry gate.
6. `docs/research/S1_ACHC_FIRST_BACKTEST_GATE_20261009.md` and `docs/research/KAI_MT4_READONLY_ADAPTER.md` in this branch.
7. Existing Phase 11G `docs/CURRENT_STATE.md` is an older snapshot, not definitive for October strategy approvals. The K-Trader HP-OMEN restriction remains: operate only on the separately transferred server-side frozen copy.

## 2. Data access and selected asset: VERIFIED

Host: `k-trader-prod-vnic`; approved route `SentinelX -> sudo docker exec k-trader-ktrader-1`.
Container verified corpus: `/data/kif_research/external/kai_mt4_20261009/` immutable. Results area: `/data/research`, writable as container UID/GID 1002:1002. Dataset source is readable and not writable as that user. SentinelX does not require direct access to host private data directory.

Transfer acceptance supplied by K_Sentinel: 280 assets, 840 D1/H1/M5 series, 3,881,201 closed candles, 12,387 files, 1,571,533,231 bytes; 4 control SHA256 match; owner/group ktrader:ktrader, dirs 550/files 440. Direct server inventory confirms 840 PASS rows, 280 broker symbols, 3,881,201 candles, no reported quality hard errors or populated quality_missing_intervals fields. A missing-interval CSV field is not a fully independent session-aware calendar audit.

Asset #9 in both manifest order and alphabetical broker-symbol order: **ACHC.us**, US equity:
- D1: 2,175 candles, 2018-02-06 to 2026-10-05.
- H1: 2,061 candles, 2025-08-04 to 2026-10-06.
- M5: 2,198 candles, 2026-08-26 to 2026-10-06. **Limited history**; no 1-year M5 test claim.
- Asset source `research_max_available/normalized/MAXAVAIL_ACHC_us_A1_20261006/ACHC/`.
Archive-wide M5: 6 series >=365 days, 274 shorter than 365 days.

## 3. Implemented/reused components and real status

| Component | Found / implemented | Remaining acceptance |
|---|---|---|
| Source transfer and read-only access | K_Sentinel transfer PASS; container read PASS | Immutable source maintained, no host-to-HP reverse dependency |
| MT4 JSONL ingestion | PR #95 `src/ktrader/mt4_research.py` + `tests/test_mt4_research.py`, explicit `as_of`, metadata checks | Full corpus acceptance; header schema variations, malformed records, completeness/time semantics and performance |
| MT4 adapter CI | GitHub Actions CI #322 concluded **success** at earlier PR head | Re-run latest head after additions; CI alone does not certify full S1 |
| Existing Phase 11G research replay | `slice_datasets_asof()` and catalogue `ktrader.dataset_catalogue.v1` in existing K-Trader tooling | New MT4 provider must remain separate from Binance catalogue and prove integration independently |
| Seven Gerchik research pattern detectors | Research candidate implementation as documented; real 7-crypto study | Correctness of independently reviewed D1/W1 real formations for ACHC.us |
| Level strength rating v0.1 | 0..100 research components, no future evidence; 77 local tests recorded | Independent annotations, strength correctness and potential calibration |
| S1 owner rules | Final approved text dated 2026-10-05 | Actual full matching S1 event-engine code absent/NOT VERIFIED |
| ATR5 | Approved historical exclusion and bootstrap described in level-contract amendments | Verify an actual reusable, fully deterministic ATR5 v2 implementation and corner cases (repeated replacement, exhausted history) |
| Intrabar execution | Approved OHLC/OLHC scenarios and 30s BPU2 event in S1 specification | Dedicated bidirectional event scheduler/matched fixture tests not established |
| Risk/cost | Approved US stock 0.002P stop reference, 0.0004P luft, <=0.005 deposit loss budget | Broker Point, tick size, lot specifications, spread, commissions, stop slippage; cannot fabricate net P&L |
| Chronological research | Freeze and split artifacts in source | Ensure discovery vs validation partitions and never call tuned data independent final holdout |

## 4. S1 exact implementation acceptance checklist (no relaxation)

- Confirm D1/W1 extrema only, one level primary Gerchik type, review and at least one owner-approved strengthening feature. No raw-pivot-only legacy detector, no ATR levels, and no score>=60 shortcut.
- Confirm M5 approach trend agrees with D1/H1/M5: two causal confirmed swing highs and two swing lows, two closed bars left/right; mixed/unknown fails closed. Plateau tie policy recorded.
- Verify 3 close compression block and strictly farther equalizing close; equalization requires fresh valid entry pattern.
- Run ATR5 v2 on last completed D1 with replacement thresholds >=2x and <=1/3x; 60% movement reserve; last closed M5 only. Require previous 20 complete M5 for activity, BPU2 projected range >=2x average rejects.
- For ACHC.us: BPU1 exact touch, BPU2 adjacent same side within allowed luft with no penetration; activate limit 30 seconds before BPU2 close with only then-observable data. Respect session first-hour restriction and its conjunctive exception. Explicitly verify MT4 timestamp interpretation vs US exchange timezone and daylight savings.
- Technical stop behind protective structure by three actual broker Point; S_calc=0.002P and luft=0.0004P, full-risk cap, tick-side rounding. Missing Point/tick/minimum step -> BLOCK monetary calculation.
- Distinct immutable A: O-H-L-C and B: O-L-H-C paths with 0,1/3,2/3,1 nodes. Process entry then protective SL and 3R TP only from entry onward; stop gaps adverse price, no beneficial TP gap improvement; SL first for unresolved ambiguity; no future bar prices at T-30 seconds.
- Unfilled order cancellation when |last completed M5 close - level|>=2 full-risk-distance. Open end-of-series position censored, not an invented exit.
- Gross and net separate; unknown Bid/Ask/spread/commission/slippage means net UNKNOWN, not zero-cost proven profitability. Fee/spread counted once.
- Include determinism, no-lookahead, corrupt/missing data, time zone/DST/session gaps, same-bar order ambiguity and chronological split boundary tests before any real S1 performance report.

## 5. Release gates

G0 VERIFIED SOURCE READ: PASS.
G1 SINGLE-ASSET inventory and scope: PASS.
G2 JSONL read adapter: IMPLEMENTED IN DRAFT PR / NOT FULL-CORPUS ACCEPTED.
G3 D1/W1 levels and reviewed strength on selected symbol: PENDING.
G4 ATR5 v2/structure/M5 setup causal integration: PENDING.
G5 event execution OHLC and OLHC plus broker symbol/cost metadata: PENDING.
G6 deterministic unit/integration and S1 research backtest on ACHC.us: NOT RUN.
G7 independent validation/holdout: NOT RUN.
Production/trading/execution: prohibited and untouched.

**Do not claim S1 backtest results before G2–G6 pass.** Keep approved source and derivative artifacts isolated. This document records inspected architecture and missing integration, not successful backtest completion.
