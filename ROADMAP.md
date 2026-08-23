# K-Trader Roadmap v1.9

Status: APPROVED baseline; repository-side implementation verified through Phase 10 preparation and Phase 11E historical universe/liquidity capture and reproducible study cohorts, 2026-08-23.

## Phase 0 - Foundation

Status: COMPLETE.

- read-only, exchange-agnostic v1 architecture;
- canonical data, analysis, scoring, API, deployment and security contracts;
- Setup Score is deterministic and is not statistical probability.

## Phase 1 - Exchange-Agnostic Market Data Foundation

Status: IMPLEMENTATION COMPLETE / TARGET-HOST LIVE ACCEPTANCE PENDING.

- provider contract/capabilities;
- Binance USD-M + Bybit Linear public adapters;
- normalized instruments/tickers/candles and provider-native symbols;
- price/liquidity universe;
- provider fallback without series mixing.

## Phase 2 - Market Data Core

Status: IMPLEMENTATION COMPLETE / TARGET-HOST LIVE ACCEPTANCE PENDING.

- REST MTF bootstrap `1d/4h/1h/15m/5m`;
- SQLite WAL / Decimal persistence;
- UTC/gap/freshness validation;
- atomic MTF persistence.

## Phase 3 - Live Market Data

Status: IMPLEMENTATION COMPLETE / TARGET-HOST LIVE ACCEPTANCE PENDING.

- Binance/Bybit public WebSocket;
- live 5m base state;
- local 15m/1h/4h/1d aggregation;
- reconnect/stale/reconciliation/gap recovery.

## Phase 4 - Indicators

Status: IMPLEMENTATION COMPLETE.

- Wilder ATR14 / canonical ATR5D;
- SMA/EMA MA50/200;
- volume/VSA spread metrics;
- generic ATR-used metric.

## Phase 5 - Market Structure

Status: IMPLEMENTATION COMPLETE.

- swings/regime/strength;
- DST-aware sessions;
- MTF levels and lifecycle;
- consolidation.

## Phase 6 - Trap + VSA

Status: IMPLEMENTATION COMPLETE.

- liquidity-sweep/trap engine;
- ND/NS/T/UT/BC/SC/SV;
- HTF/location/confirmation hard rules.

## Phase 7 - Setup / Rating Engine

Status: IMPLEMENTATION COMPLETE.

- approved evaluation flow and evidence gates;
- Entry/Luft/SL/structural TP;
- RR >=3 and ATR-used hard gates;
- deterministic Setup Score and A+/A/B/C;
- explicit optional RiskContext;
- LONG/SHORT/NO_TRADE TradingDecision.

## Phase 8 - Read-only K-Trader API

Status: IMPLEMENTATION COMPLETE.

- FastAPI read-only health/status/universe/market/candles/analysis/candidates/signals;
- Decimal-as-string and UTC serialization;
- provider ambiguity fail-closed behavior;
- API rate limiting;
- Custom GPT OpenAPI/Action guide.

## Phase 8.5 - Runtime Scanner Coordinator

Status: IMPLEMENTATION COMPLETE / REPOSITORY-WIDE CI VERIFIED.

- provider priority/fallback refresh per scanner cycle;
- liquidity-ranked universe and configurable top-N analysis shortlist;
- bounded MTF bootstrap/analysis concurrency;
- retained live WebSocket task unless provider/shortlist changes;
- MTF readiness/freshness gate before analysis;
- indicators -> structure -> Trap/VSA -> Trading Engine orchestration;
- per-symbol failure isolation;
- valid/fresh no-setup -> explicit NO_TRADE;
- stale/incomplete input -> no fabricated decision;
- atomic `ApiReadModel` publication;
- production ASGI lifespan entrypoint and clean shutdown.

Historical Phase 9 baseline including Phase 8.5: **92 tests passed**.

## Phase 9 - Docker / CI-CD / live deployment

Status: REPOSITORY-SIDE COMPLETE / TARGET-HOST DEPLOYMENT AND LIVE ACCEPTANCE PENDING.

Completed and CI-verified:

- GitHub-hosted repository-wide CI;
- compile + pytest + Compose + Docker gates;
- hardened production Docker image;
- manual-only `main` deployment workflow for repository-scoped self-hosted runner;
- immutable `/opt/k-trader/releases/<sha>` deployment model and rollback;
- optional Caddy HTTPS profile;
- Ubuntu/Docker provisioning automation;
- checksum-verified GitHub runner registration;
- target-host REST/WebSocket/scanner acceptance utilities.

CI evidence includes run `32636825758` (92 tests) and production-prep run `32637233264`.

## Phase 9.1 - Oracle ARM64 / Multi-arch

Status: VERIFIED.

Primary production target:

- Oracle Cloud Always Free;
- Germany Central (Frankfurt);
- Ubuntu 24.04 Minimal aarch64;
- `VM.Standard.A1.Flex`, target 2 OCPU / 12 GB RAM;
- Linux ARM64 self-hosted runner label `k-trader-prod-arm64`.

Repository adaptation:

- architecture-aware runner installer with pinned official checksums;
- amd64 and arm64 Ubuntu provisioning;
- separate amd64/arm64 Docker CI gates;
- QEMU/Buildx ARM64 image build, architecture assertion and production ASGI import;
- amd64 compatibility retained.

Verification: PR #3 CI `32646869264`, **92 tests PASS**, amd64/arm64 Docker/runtime PASS; squash merge `8e7ef38311e8c92398eb7cf530c92ff773e2a9a1`.

External Oracle status on 2026-08-23:

- A1 unavailable in Frankfurt AD-1, AD-2 and AD-3;
- reduced 1 OCPU / 6 GB A1 request also unavailable;
- no paid shape approved as workaround;
- retry A1 when capacity becomes available.

Potential fallback, not implemented: home Windows PC + Tailscale Funnel. Cloudflare Workers + Durable Objects are not part of K-Trader v1.

### Phase 9 live exit

Pending on external infrastructure/capacity:

- create/provision Oracle A1 host;
- register `k-trader-prod-arm64` runner;
- production deploy;
- target-host REST/WS/runtime acceptance;
- persistence across real restart;
- DNS/TLS and public HTTPS.

## Phase 10 - Custom GPT Update

Status: REPOSITORY-SIDE PREPARATION VERIFIED / LIVE ACTIVATION PENDING HTTPS.

- exact read-only OpenAPI schemas for eight Action operations;
- Bearer API-key authentication and production secret wiring;
- public health/privacy endpoints;
- OpenAPI origin renderer/validator;
- live Action acceptance utility;
- Builder checklist and privacy-policy baseline.

Verification: PR #4 CI `32647828382`, **106 tests PASS**, amd64/arm64 PASS; squash merge `a1c578524bbc41afa575b3f4fb6446642a48453d`.

Activation awaits a real HTTPS endpoint after Phase 9 live deployment.

## Phase 11 - Hardening

### Phase 11A - Replay / Regression

Status: VERIFIED.

- deterministic chronological replay harness;
- causal level/Trap lifecycle;
- gap/cross-provider fail-closed replay validation;
- ATR no-future-lookahead and freshness regressions;
- deterministic replay digest.

Verified in PR #4 final CI as part of the **106-test PASS** baseline.

### Phase 11B - Provider History / Signal Outcomes

Status: VERIFIED.

- `ktrader.history.v1` provider-history JSONL contract;
- content SHA-256 integrity and coherent closed/contiguous/single-provider validation;
- provider-native Binance/Bybit history export;
- conservative future-candle outcome tracking;
- explicit OHLC intrabar ambiguity;
- deterministic decision fingerprint;
- separate SQLite outcome persistence/upsert;
- WIN/LOSS-only extraction for later calibration research;
- no Probability.

Verification: PR #5 CI `32650220382`, **121 tests PASS**, amd64/arm64 PASS; squash merge `0b201a5112dca057e3071ef878d8acc6653ab994`.

### Phase 11C - Deep History / MTF Replay Bundles

Status: VERIFIED.

- Binance `endTime` and Bybit `end` backward pagination;
- exact-depth multi-page closed-history collection;
- page deduplication and strict cursor progress;
- fail-closed gaps/insufficient depth/provider mismatch;
- deterministic `ktrader.mtf_bundle.v1` for `1d/4h/1h/15m/5m`;
- one provider/symbol and one UTC `as_of` cutoff;
- per-timeframe and bundle SHA-256;
- no-lookahead MTF slicing;
- deep single-timeframe and MTF export utilities.

Verification: PR #6 CI `32652044967`, **134 tests PASS**, amd64/arm64 PASS; squash merge `0b7fd93246d4d5e6213ab0bf4ab63ee52b5fc007`.

### Phase 11D - Full-engine Historical Replay / Outcome Studies

Status: VERIFIED.

- live and historical paths share `analyze_candle_snapshot()`;
- chronological MTF replay with explicit `as_of` cutoffs;
- `ktrader.replay_context.v1` timestamped liquidity score/rank/universe size;
- missing/stale historical context skips cutoff fail-closed;
- deterministic `ktrader.replay_study.v1` artifact;
- exact decision fingerprints retained for audit;
- stable setup-geometry key deduplicates unchanged signals;
- unique tradable setups feed Phase 11B outcome evaluation/persistence;
- explicit optional outcome horizon;
- no Probability.

Verification: first PR #7 gate `32653028353` found only one invalid new synthetic OHLC fixture; production validation was not weakened. Final CI `32653087172`: **140 tests PASS**, amd64/arm64 PASS; squash merge `cb2869bc9d5f56496368920e8b7e43faf9ba3bbd`.

### Phase 11E - Historical Universe / Liquidity Capture + Study Cohorts

Status: VERIFIED.

- `ktrader.universe_snapshot.v1` provider-native timestamped ranked universe snapshots;
- raw ticker inputs required to reproduce liquidity score/rank are preserved;
- rank and universe size are generated with the same `UniverseConfig`/`build_universe()` rules as live scanning;
- snapshot provider identity, timestamp and SHA-256 integrity are fail-closed;
- `ktrader.universe_archive.v1` append-only chronological same-provider/same-config archive with archive SHA-256;
- `ktrader.study_cohort.v1` explicit time-window/symbol selection;
- automatic per-symbol `ktrader.replay_context.v1` generation from actually captured snapshots;
- provider/config mixing, future ticker timestamps, missing symbols, changed analysis-critical instrument metadata, unsafe paths and digest mismatches are rejected;
- current ticker data is never used to fabricate historical ranks retroactively;
- operator utilities: `capture_universe_snapshot.py`, `build_study_cohort.py`.

Verification: PR #8 CI `32654162474` SUCCESS; repository-wide pytest **147 passed**, compile/shell PASS, linux/amd64 Docker/runtime PASS, linux/arm64 QEMU/Buildx image/architecture/runtime PASS; squash merge `3c2a21644442e1d621ca8402e9c1c97bedb0fe80`.

Historical universe archives must accumulate prospectively because current public ticker endpoints do not provide trustworthy historical universe/rank snapshots retroactively.

### Remaining Phase 11 work

- integrate periodic universe-snapshot persistence into the continuously running production runtime;
- catalogue canonical real-provider MTF bundles + matching universe archives/cohorts + replay-study digests;
- operations hardening: SQLite backup/recovery, disk/log guards, metrics/watchdog and restart/recovery validation;
- extended runtime failure/stale-data validation;
- later approved statistical calibration methodology with time-separated out-of-sample validation.

## Phase 12 - Multi-provider expansion

- add OKX/KuCoin/other public adapters through the same provider contract;
- keep Trading Engine provider-independent.

## Deferred beyond v1

- exchange credentials/account reads;
- order execution/automatic trading;
- PostgreSQL/TimescaleDB/Redis/Kafka/Kubernetes unless measured load justifies them;
- statistical win probability until calibrated from confirmed outcomes with an approved out-of-sample methodology;
- full order-book storage.
