# K-Trader Roadmap v1.11

Status: APPROVED baseline; repository-side implementation verified through Phase 10 preparation and Phase 11G dataset catalogue foundation, 2026-08-23.

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
- real persistence/backup/restart validation;
- continuous research-capture validation;
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
- `ktrader.universe_archive.v1` chronological same-provider/same-config archive with archive SHA-256;
- `ktrader.study_cohort.v1` explicit time-window/symbol selection;
- automatic per-symbol `ktrader.replay_context.v1` generation from actually captured snapshots;
- provider/config mixing, future ticker timestamps, missing symbols, changed analysis-critical instrument metadata, unsafe paths and digest mismatches are rejected;
- current ticker data is never used to fabricate historical ranks retroactively;
- operator utilities: `capture_universe_snapshot.py`, `build_study_cohort.py`.

Verification: PR #8 CI `32654162474` SUCCESS; repository-wide pytest **147 passed**, compile/shell PASS, linux/amd64 Docker/runtime PASS, linux/arm64 QEMU/Buildx image/architecture/runtime PASS; squash merge `3c2a21644442e1d621ca8402e9c1c97bedb0fe80`.

Historical universe archives must accumulate prospectively because current public ticker endpoints do not provide trustworthy historical universe/rank snapshots retroactively.

### Phase 11F - Operations Hardening / Continuous Research Capture

Status: VERIFIED.

- selected live provider cycle retains the exact normalized instrument/ticker source inputs for research persistence without a second provider fetch;
- automatic provider-coherent universe capture, default every 300 seconds;
- immutable per-capture one-snapshot archive files under the persistent research tree;
- pre-cycle disk-space guard with hard fail-closed behavior and stale publishable-state clearing;
- online SQLite backup through native backup API;
- mandatory `PRAGMA integrity_check` before atomic backup publication;
- configurable backup interval/retention and standalone backup utility;
- restore regression by opening a generated backup as a fresh repository;
- scanner-age watchdog integrated into health evaluation without changing response schema;
- Docker healthcheck requires health JSON `status=ok`;
- bounded K-Trader/Caddy json-file log rotation;
- production environment configuration for research capture, backup, disk guard and watchdog.

Verification: PR #9 CI `32656033224` SUCCESS; repository-wide pytest **155 passed**, compile/shell/Compose PASS, linux/amd64 Docker/runtime PASS, linux/arm64 QEMU/Buildx image/architecture/runtime PASS; squash merge `ae3620f7ce4bb6b857098ba470a5f2ddbfe374d5`.

### Phase 11G - Dataset Catalogue Foundation

Status: VERIFIED.

- `ktrader.dataset_catalogue.v1` deterministic research audit catalogue;
- one entry links one coherent provider/symbol chain: MTF bundle -> universe archive -> study cohort -> replay study -> study provenance -> optional outcome sample;
- every reference stores artifact schema, semantic identity and exact file/tree content SHA-256;
- deterministic catalogue-entry and catalogue SHA-256 identities;
- catalogue verification re-opens source artifacts and rebuilds relationships instead of trusting stored hashes alone;
- artifact-root containment plus absolute-path, traversal and symlink guards;
- `ktrader.study_run_provenance.v1` records exact bundle/cohort/context, full `RuntimeScannerConfig`, `ReplayStudyConfig` and replay-study file hashes;
- canonical `run_replay_study.py --cohort` mode emits cohort-linked provenance;
- replay-study inspection validates decision/outcome identity/counts and rejects non-null `estimated_probability`;
- `ktrader.outcome_sample.v1` is an immutable WIN/LOSS-only study sample that must exactly match both the replay-study artifact and `OutcomeRepository`;
- utilities: `export_outcome_sample.py`, `build_dataset_catalogue.py`.

Verification: PR #10 CI `32657337221` SUCCESS; repository-wide pytest **163 passed**, compile/shell PASS, linux/amd64 Docker/runtime PASS, linux/arm64 QEMU/Buildx image/architecture/runtime PASS; squash merge `96de78d503432122d98e1c9ad1f01299802862a8`.

### Remaining Phase 11 work

- populate the catalogue with real provider-recorded MTF/universe/cohort/study/outcome artifacts after continuous production capture begins;
- optionally automate catalogue registration after scheduled study jobs exist;
- target-host restart/recovery, backup, disk guard and watchdog acceptance;
- extended runtime failure/stale-data validation if live evidence exposes gaps;
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
