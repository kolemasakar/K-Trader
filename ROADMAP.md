# K-Trader Roadmap v1.15

Status: APPROVED baseline; Phase 9 production and Phase 10 Custom GPT product integration are complete; repository-side implementation is verified through Phase 11G, two canonical production chains are catalogued, and corrected historical discovery is active at the RR-geometry gate as of 2026-09-08.

## Phase 0 - Foundation

Status: COMPLETE.

- read-only, exchange-agnostic v1 architecture;
- canonical data, analysis, scoring, API, deployment and security contracts;
- Setup Score is deterministic and is not statistical probability.

## Phase 1 - Exchange-Agnostic Market Data Foundation

Status: IMPLEMENTATION COMPLETE / TARGET-HOST LIVE ACCEPTANCE VERIFIED.

- provider contract/capabilities;
- Binance USD-M + Bybit Linear public adapters;
- normalized instruments/tickers/candles and provider-native symbols;
- price/liquidity universe;
- provider fallback without series mixing.

## Phase 2 - Market Data Core

Status: IMPLEMENTATION COMPLETE / TARGET-HOST LIVE ACCEPTANCE VERIFIED.

- REST MTF bootstrap `1d/4h/1h/15m/5m`;
- SQLite WAL / Decimal persistence;
- UTC/gap/freshness validation;
- atomic MTF persistence.

## Phase 3 - Live Market Data

Status: IMPLEMENTATION COMPLETE / TARGET-HOST LIVE ACCEPTANCE VERIFIED.

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

Status: COMPLETE / TARGET-HOST PRODUCTION DEPLOYMENT AND LIVE ACCEPTANCE VERIFIED.

Completed and verified:

- GitHub-hosted repository-wide CI;
- compile + pytest + Compose + Docker gates;
- hardened production Docker image;
- manual-only `main` deployment workflow for repository-scoped self-hosted runner;
- immutable `/opt/k-trader/releases/<sha>` deployment model and rollback;
- optional Caddy HTTPS profile;
- Ubuntu/Docker provisioning automation;
- checksum-verified GitHub runner registration;
- target-host REST/WebSocket/scanner acceptance utilities;
- Oracle ARM64 host provisioned and production runner registered;
- runtime UID/GID aligned with host production identity for writable persistent SQLite data;
- live Binance USD-M REST/WebSocket acceptance passed;
- scanner `data_ready=true` and MTF API publication passed;
- production container reached Docker `healthy` state and release was promoted.

Production evidence on 2026-09-04:

- PR #17 CI: **170 tests PASS**, amd64 Docker PASS, arm64 Docker PASS;
- production workflow run `33920829993`: SUCCESS;
- deployed SHA `9ed572349ed0195e518f128894a1f187419dbcc1`;
- runtime build identity `uid:gid 1002:1002`;
- Phase 9 provider acceptance: Binance USD-M REST `5m,15m,1h,4h,1d` + WebSocket `5m` PASS;
- scanner acceptance: `DEGRADED` with usable data, `data_ready=true`, 13 symbols ready / 7 failed during the final deployment cycle;
- MTF API acceptance passed for all five canonical intervals;
- final local `/health`: `status=ok`, `mode=read_only`, `data_ready=true`;
- application remains bound to `127.0.0.1:8000`.

Earlier repository CI evidence includes run `32636825758` (92 tests) and production-prep run `32637233264`.

## Phase 9.1 - Oracle ARM64 / Multi-arch

Status: VERIFIED / PRODUCTION HOST ACTIVE.

Primary production target:

- Oracle Cloud Always Free;
- Germany Central (Frankfurt);
- Ubuntu 24.04 Minimal aarch64;
- `VM.Standard.A1.Flex`;
- active production allocation: 1 OCPU / 6 GB RAM;
- Linux ARM64 self-hosted runner label `k-trader-prod-arm64`.

Repository adaptation:

- architecture-aware runner installer with pinned official checksums;
- amd64 and arm64 Ubuntu provisioning;
- separate amd64/arm64 Docker CI gates;
- QEMU/Buildx ARM64 image build, architecture assertion and production ASGI import;
- amd64 compatibility retained.

Verification: PR #3 CI `32646869264`, **92 tests PASS**, amd64/arm64 Docker/runtime PASS; squash merge `8e7ef38311e8c92398eb7cf530c92ff773e2a9a1`.

Historical note: on 2026-08-23 A1 capacity was unavailable in Frankfurt AD-1, AD-2 and AD-3, including a reduced 1 OCPU / 6 GB request. Capacity later became available and `k-trader-prod` was provisioned successfully.

### Phase 9 live exit

Exit criteria completed on 2026-09-04:

- Oracle A1 host created and provisioned;
- `k-trader-prod-arm64` runner registered as a system service under `ktrader`;
- production deployment from approved `main` completed;
- target-host REST/WS/runtime acceptance passed;
- persistent SQLite database, WAL, backups and research directories created under `/opt/k-trader/data`;
- runtime identity and data-directory ownership verified as `1002:1002`;
- Docker health verified `healthy`.

Public DNS/TLS was intentionally deferred from the Phase 9 localhost gate and completed in Phase 10.

## Phase 10 - Custom GPT Update

Status: COMPLETE / PRODUCT ACCEPTANCE VERIFIED 2026-09-07.

Repository-side preparation:

- exact read-only OpenAPI schemas for eight Action operations;
- Bearer API-key authentication and production secret wiring;
- public health/privacy endpoints;
- OpenAPI origin renderer/validator;
- live Action acceptance utility;
- Builder checklist and privacy-policy baseline.

Preparation verification: PR #4 CI `32647828382`, **106 tests PASS**, amd64/arm64 PASS; squash merge `a1c578524bbc41afa575b3f4fb6446642a48453d`.

Production activation completed on 2026-09-05:

- public DNS: `ktrader-api.duckdns.org -> 92.5.56.198`;
- OCI stateful ingress TCP 80/443 enabled;
- host iptables allows 80/443 before terminal reject and is persisted with `netfilter-persistent`;
- GitHub Environment variable `KTRADER_DOMAIN=ktrader-api.duckdns.org` configured;
- high-entropy `KTRADER_ACTION_API_KEY` configured only as a GitHub `production` Environment secret;
- PR #19 fixed authenticated Phase 9 local `/v1/*` acceptance after Action auth activation;
- Caddy persistent storage contract corrected to `root:root 0700` for `caddy_data` and `caddy_config` under the capability-dropped root profile;
- Let's Encrypt HTTP-01 validation and certificate issuance succeeded;
- direct public HTTPS `/health` returned `status=ok`, `data_ready=true`, `action_auth_enabled=true`;
- final `Deploy Production #4` run `33945690930` re-run succeeded;
- accepted production SHA: `7c60a77b9773774373ea4a3f095c5ab2ee7767e2`;
- provider REST/WS acceptance PASS;
- scanner `DEGRADED`, `data_ready=true`, 17 ready / 3 failed in the accepted cycle;
- MTF API PASS;
- `PASS Phase 10 Action live acceptance`;
- canonical `custom_gpt/openapi.yaml` points to `https://ktrader-api.duckdns.org`.

Product-side completion on 2026-09-07:

- PR #24 exposed public one-click schema import at `https://ktrader-api.duckdns.org/action-openapi.yaml` and packaged the canonical schema in the production image;
- PR #25 replaced GPT Builder-incompatible parameter `$ref` usage with inline parameter definitions while preserving the read-only API contract and operation IDs;
- post-merge PR #25 CI run `34110324230`: pytest PASS, Docker amd64 PASS, Docker arm64 PASS; Tests run `34110324210` PASS;
- final Deploy Production #6 run `34111173939` succeeded on SHA `470531500566b1dc7b6e5d7296caf57403aacaf4`;
- production container healthy and Phase 10 Action live acceptance PASS;
- existing K_Trader GPT uses `SYSTEM_K_TRADER_v1_2_COMPACT.md`;
- Action authentication configured as API key / Bearer with the existing production secret;
- Privacy Policy URL configured as `https://ktrader-api.duckdns.org/privacy`;
- GPT Builder recognized all eight required operations;
- all eight operations passed production Preview tests;
- `NO TRADE` preservation, Setup Score/non-probability semantics and canonical mode passed;
- provider ambiguity HTTP 409 remains regression-covered; live 409 was not reproduced in the current single-provider live state;
- fail-closed `WATCHLIST ONLY` fallback passed when canonical analysis/OHLCV was unavailable;
- strict direct-source fallback checked Binance USD-M then Bybit Linear REST APIs, rejected stale/partial responses, avoided provider-series mixing and did not fabricate trading fields;
- current link-access distribution was updated successfully after Preview acceptance.

Detailed evidence:

- backend activation: `docs/PHASE_10_CHECKPOINT.md`;
- product acceptance: `docs/PHASE_10_PRODUCT_ACCEPTANCE.md`.

Phase 10 has no remaining product-side work for the read-only v1 boundary. Future broader GPT Store/public distribution must re-check then-current publishing/privacy requirements. Order execution, exchange-account access and statistical win probability remain outside Phase 10.

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

### Phase 11G - Dataset Catalogue Foundation and Discovery

Status: VERIFIED FOUNDATION / ACTIVE CORRECTED DATASET DISCOVERY.

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

Foundation verification: PR #10 CI `32657337221` SUCCESS; repository-wide pytest **163 passed**, compile/shell PASS, linux/amd64 Docker/runtime PASS, linux/arm64 QEMU/Buildx image/architecture/runtime PASS; squash merge `96de78d503432122d98e1c9ad1f01299802862a8`.

Current production/research checkpoint:

- canonical catalogue contains 2 verified chains: SUIUSDT and XRPUSDT;
- catalogue SHA: `057ff750966d2bc5043fffd7fdc37583dd0133480452c131b51f84109d2fb4b6`;
- strict context policy remains `max_context_age_seconds=300` with newest snapshot at/before cutoff;
- PR #32 aligned research capture cadence to UTC slots;
- PR #33 fixed the side/regime contract (`LONG -> BULLISH`, `SHORT -> BEARISH`) and aligned D1 fallback semantics;
- PR #33 main SHA `7fa20c3d7f0d89ae628eb2bf21e4c50164eb3eab` passed post-merge Tests/CI and Deploy Production #9 `34177978988`;
- corrected Window #4 replay produced 7596 candidate decisions: 7161 HTF-rejected and 435 HTF-aligned;
- conditional audit reproduced all 435 aligned candidates as `LONG -> BULLISH`;
- sequential downstream funnel: `435 -> 202 -> 168 -> 142 -> 0` at HTF -> primary-level strength -> geometry -> ATR -> RR;
- all 142 final survivors were blocked only by `RR_BELOW_3`;
- no threshold/freshness/catalogue/probability rule was relaxed;
- no new chain was materialized during discovery.

Canonical current checkpoint: `docs/checkpoints/2026-09-08_PHASE11G_CORRECTED_REPLAY_RR_GEOMETRY_GATE.md`.

### Remaining Phase 11 work

Immediate Phase 11G gate:

- run a read-only RR-geometry audit of the 142 RR-only Window #4 candidates;
- inspect entry, stop, structural target, risk/reward distances, target level identity/type/timeframe and RR distribution;
- deduplicate unchanged setup geometry across neighboring cutoffs before interpreting the RR distribution;
- do not lower `RR >= 3` merely to manufacture signals.

After geometry is understood:

- rerun corrected historical discovery for Windows #1–#4;
- materialize only naturally useful deterministic chains;
- register future catalogue entries only after full artifact verification;
- export immutable WIN/LOSS samples only when real binary outcomes exist;
- continue provider-recorded production accumulation and target-host operational evidence;
- consider statistical calibration only under a separately approved methodology with sufficient sample size and time-separated out-of-sample validation.

## Phase 12 - Multi-provider expansion

Status: FUTURE / NOT ACTIVE.

- add OKX/KuCoin/other public adapters through the same provider contract;
- keep Trading Engine provider-independent.

## Deferred beyond v1

- exchange credentials/account reads;
- order execution/automatic trading;
- PostgreSQL/TimescaleDB/Redis/Kafka/Kubernetes unless measured load justifies them;
- statistical win probability until calibrated from confirmed outcomes with an approved out-of-sample methodology;
- full order-book storage.
