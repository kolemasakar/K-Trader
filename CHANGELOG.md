# Changelog

## 2026-09-07 - Phase 10 Custom GPT product acceptance

- Completed configuration of the existing K_Trader GPT with `SYSTEM_K_TRADER_v1_2_COMPACT.md` and the production read-only K-Trader Action.
- Configured Action authentication as API key / Bearer using the existing production secret without storing the secret in repository files or acceptance evidence.
- Added public one-click Action schema endpoint `https://ktrader-api.duckdns.org/action-openapi.yaml` returning the packaged canonical `custom_gpt/openapi.yaml`.
- PR #24 exposed the canonical schema endpoint and packaged the schema in production; post-merge CI/Tests passed and Deploy Production #5 succeeded on SHA `322055f09346b309c9d477890715738036402393`.
- GPT Builder exposed a parser incompatibility with OpenAPI parameter `$ref`; PR #25 inlined Action parameters while preserving operation IDs and the read-only API contract.
- PR #25 post-merge CI run `34110324230` succeeded: pytest, Docker amd64 and Docker arm64 PASS; Tests run `34110324210` PASS.
- Deploy Production #6 run `34111173939` succeeded on SHA `470531500566b1dc7b6e5d7296caf57403aacaf4`; production container healthy and Phase 10 Action live acceptance PASS.
- GPT Builder recognized all eight required operations: `getHealth`, `getScannerStatus`, `listUniverse`, `getMarketSnapshot`, `getCandles`, `getAnalysis`, `listCandidates`, `listSignals`.
- All eight operations passed Builder Preview validation against production.
- Canonical-mode query preserved `NO TRADE` when no A/A+ signals were available and did not invent Entry/SL/TP or statistical probability.
- Provider ambiguity HTTP 409 remains covered by backend regression; the live 409 path was not reproducible in the current single-provider production state.
- Fail-closed fallback switched to `WATCHLIST ONLY` when canonical analysis/OHLCV was unavailable and did not fabricate class, Setup Score, Estimated Probability, Entry, SL, TP, ATR or VSA.
- Strict fallback verified direct official REST API priority Binance USD-M -> Bybit Linear, rejected stale/partially unavailable public responses, did not mix provider series, and did not use an aggregator.
- Privacy Policy URL `https://ktrader-api.duckdns.org/privacy` accepted in the Action and the existing link-access GPT was updated after Preview acceptance.
- Added `docs/PHASE_10_PRODUCT_ACCEPTANCE.md` as the final product-side closure evidence.
- Phase 10: COMPLETE for the read-only K-Trader v1 product boundary.

## 2026-08-23 - Phase 11G dataset catalogue foundation

- Added deterministic audit catalogue schema `ktrader.dataset_catalogue.v1` for fully linked research chains.
- Added exact artifact file/tree SHA-256 in addition to each artifact's semantic identity so byte/tree changes are detectable even when relationship metadata is unchanged.
- Added `ktrader.study_run_provenance.v1` binding the exact MTF bundle, cohort, symbol replay context, complete `RuntimeScannerConfig`, `ReplayStudyConfig` and replay-study file SHA-256.
- Upgraded canonical replay workflow with `run_replay_study.py --cohort` to emit cohort-linked provenance sidecars; standalone `--context` remains a legacy compatibility mode.
- Added replay-study artifact inspection for manifest/decision/outcome identity, count consistency, duplicate IDs and non-null probability rejection.
- Added immutable `ktrader.outcome_sample.v1` WIN/LOSS-only exports that require exact equality between replay-study embedded outcomes and `OutcomeRepository` rows.
- Added catalogue relationship validation for bundle/archive/cohort/context/study/provenance/outcome-sample identities and digests.
- Added artifact-root containment, relative-path, traversal and symlink guards.
- Added `scripts/export_outcome_sample.py` and `scripts/build_dataset_catalogue.py`.
- Preserved Trading Engine setup/scoring/RR/ATR/VSA/Trap behavior and kept `estimated_probability` null/N/A.
- PR #10 CI run `32657337221`: **163 tests PASS**, Python compile PASS, shell validation PASS, amd64 Docker/runtime PASS, arm64 QEMU/Buildx image/architecture/runtime PASS.
- PR #10 squash-merged as `96de78d503432122d98e1c9ad1f01299802862a8`.
- Phase 11G: VERIFIED repository-side; real catalogue population awaits provider-recorded production artifacts.

## 2026-08-23 - Phase 11F operations hardening / continuous research capture

- Retained exact normalized instrument/ticker source inputs from the selected live universe request cycle so research capture does not issue a second temporally different provider fetch.
- Added periodic provider-coherent universe capture with a default 300-second interval.
- Stored every automatic research capture as an immutable one-snapshot digest-verified `ktrader.universe_archive.v1` artifact under the persistent provider/date tree.
- Added pre-cycle disk-space safety guard with hard fail-closed behavior and current publishable-state clearing when storage is below the configured threshold.
- Added online SQLite backups using `sqlite3.Connection.backup()`, mandatory `PRAGMA integrity_check`, atomic publication and configurable retention.
- Added `scripts/backup_sqlite.py` and recovery regression proving generated backups can be reopened as fresh repositories with persisted candle state intact.
- Added scanner-age watchdog semantics to `/health` without changing the existing public response shape.
- Hardened Docker healthcheck to require semantic `/health` JSON `status=ok` rather than HTTP reachability alone.
- Added bounded json-file log rotation for the K-Trader and Caddy containers.
- Added production environment controls for research capture, backups, disk guard and watchdog.
- Preserved Trading Engine setup/scoring/RR/ATR/VSA/Trap behavior and kept `estimated_probability` null/N/A.
- PR #9 CI run `32656033224`: **155 tests PASS**, Python compile PASS, shell validation PASS, Compose PASS, amd64 Docker/runtime PASS, arm64 QEMU/Buildx image/architecture/runtime PASS.
- PR #9 squash-merged as `ae3620f7ce4bb6b857098ba470a5f2ddbfe374d5`.
- Phase 11F: VERIFIED repository-side; real persistent-volume restart/backup/watchdog acceptance remains part of the target-host live gate.

## 2026-08-23 - Phase 11E historical universe / liquidity capture and study cohorts

- Added versioned `ktrader.universe_snapshot.v1` provider-native timestamped universe snapshots.
- Preserved raw normalized ticker inputs required to reproduce liquidity score, rank and live-compatible universe size.
- Added strict provider/timestamp/config validation and per-snapshot SHA-256 integrity.
- Added versioned `ktrader.universe_archive.v1` for chronological same-provider/same-config snapshot archives with archive-level SHA-256.
- Added versioned `ktrader.study_cohort.v1` with explicit time-window and optional symbol selection.
- Added automatic per-symbol `ktrader.replay_context.v1` generation using only actually captured historical membership observations.
- Explicitly prohibited reconstructing old liquidity ranks from current ticker data; historical universe context must be captured prospectively.
- Added operator utilities `scripts/capture_universe_snapshot.py` and `scripts/build_study_cohort.py`.
- Preserved Setup Score as non-probabilistic and kept `estimated_probability` null/N/A.
- PR #8 CI run `32654162474`: **147 tests PASS**, Python compile PASS, shell validation PASS, amd64 Docker/runtime PASS, arm64 QEMU/Buildx image/architecture/runtime PASS.
- PR #8 squash-merged as `3c2a21644442e1d621ca8402e9c1c97bedb0fe80`.
- Phase 11E: VERIFIED.

## 2026-08-23 - Phase 11D full-engine historical replay / outcome studies

- Refactored live `EngineSymbolAnalyzer` to call a shared pure `analyze_candle_snapshot()` path.
- Reused that exact snapshot path for historical replay so replay cannot silently diverge from live ATR/structure/Trap/VSA/geometry/scoring logic.
- Added versioned `ktrader.replay_context.v1` for confirmed timestamped historical liquidity score, liquidity rank and universe size.
- Added fail-closed replay-context freshness and identity rules; missing/stale context is skipped rather than approximated.
- Added deterministic `ktrader.replay_study.v1` study artifacts and study IDs.
- Kept exact time-specific `decision_fingerprint()` for audit and added separate stable setup-geometry keys to deduplicate unchanged signals across consecutive 5m cutoffs.
- Connected unique tradable replay signals to the conservative Phase 11B future-candle outcome evaluator and optional SQLite `OutcomeRepository`.
- Added explicit optional outcome horizon in setup-timeframe bars; no universal holding period was introduced.
- Added operator utility `scripts/run_replay_study.py`.
- Preserved Trading Engine scoring weights, RR/ATR-used gates and `estimated_probability=null`.
- Initial PR #7 CI run `32653028353`: compile/shell PASS, 135 tests PASS / 5 FAIL because one newly added synthetic OHLC fixture had `low > open`; fixed the fixture only, without weakening production validation.
- Final PR #7 CI run `32653087172`: **140 tests PASS**, Python compile PASS, shell validation PASS, amd64 Docker/runtime PASS, arm64 QEMU/Buildx image/architecture/runtime PASS.
- PR #7 squash-merged as `cb2869bc9d5f56496368920e8b7e43faf9ba3bbd`.
- Phase 11D: VERIFIED.

## 2026-08-23 - Phase 11C deep history / MTF replay bundles

- Added optional provider historical-page contract with explicit UTC end cursor.
- Added Binance USD-M backward kline pagination through `endTime` and Bybit Linear pagination through `end`.
- Added exact-depth multi-page closed-history collection with page deduplication and strict backward cursor progress.
- Added fail-closed handling for unsupported paging, insufficient depth, gaps and provider identity mismatch.
- Added deterministic `ktrader.mtf_bundle.v1` bundles for canonical `1d/4h/1h/15m/5m` history under one provider/symbol and one UTC `as_of` cutoff.
- Added per-timeframe history SHA-256 digests and bundle-level SHA-256 integrity verification.
- Added no-lookahead MTF slicing and bundle roundtrip/tamper validation.
- Added deep single-timeframe export and `scripts/export_mtf_history.py` using public market-data endpoints only.
- Preserved Trading Engine scoring/RR/ATR rules and kept `estimated_probability` null/N/A.
- PR #6 CI run `32652044967`: **134 tests PASS**, Python compile PASS, shell validation PASS, amd64 Docker/runtime PASS, arm64 QEMU/Buildx image/architecture/runtime PASS.
- PR #6 squash-merged as `0b7fd93246d4d5e6213ab0bf4ab63ee52b5fc007`.
- Phase 11C: VERIFIED.
- Long real provider-recorded MTF bundles remain operator-generated artifacts; deterministic PR CI does not fabricate live exchange captures.

## 2026-08-23 - Phase 11B provider history / signal outcomes

- Added versioned `ktrader.history.v1` JSONL datasets for provider-recorded closed candles.
- Added canonical candle-content SHA-256 integrity verification and manifest identity/range validation.
- Added public provider-history export through the existing Binance USD-M and Bybit Linear adapters without introducing exchange credentials.
- Kept current capture depth within one provider-native REST page; deep multi-page pagination is deferred without changing the dataset contract.
- Added conservative no-lookahead outcome evaluation for canonical `TradingDecision` geometry.
- Added explicit `AMBIGUOUS` handling when OHLC cannot determine entry/SL/TP intrabar ordering; no optimistic/pessimistic ordering assumption is made.
- Added `PENDING_ENTRY`, `OPEN`, `WIN`, `LOSS`, `AMBIGUOUS`, `EXPIRED_NO_ENTRY`, `EXPIRED_OPEN` and `NOT_ELIGIBLE` outcome states.
- Added deterministic TradingDecision fingerprints and separate SQLite outcome persistence/upsert.
- Added WIN/LOSS-only sample extraction for future calibration work without calculating probability.
- Preserved Setup Score as a deterministic rule score; `estimated_probability` remains null/N/A.
- PR #5 CI run `32650220382`: **121 tests PASS**, Python compile PASS, shell validation PASS, amd64 Docker/runtime PASS, arm64 QEMU/Buildx image/architecture/runtime PASS.
- PR #5 squash-merged as `0b201a5112dca057e3071ef878d8acc6653ab994`.
- Phase 11B: VERIFIED.

## 2026-08-23 - Phase 10 preparation + Phase 11A replay/regression hardening

- Added deterministic replay harness for chronological Trap/level lifecycle regression.
- Corrected Trap causality so a fresh break remains `BROKEN` while the configured return window is still open; `EXPIRED` is emitted only after that full window elapses without return.
- Preserved the setup gate: only `confirmed=True` Trap evidence can produce setup candidates.
- Added replay regression for gaps, provider identity, ATR future-lookahead resistance, freshness boundary and deterministic digesting.
- Added optional Bearer API-key enforcement for production `/v1/*` endpoints while keeping `/health` and `/privacy` public.
- Added `KTRADER_ACTION_API_KEY` production secret wiring; no key is committed to the repository.
- Replaced generic Action response bodies with precise read-only OpenAPI schemas for all eight operations.
- Added OpenAPI render/validation utility and live Phase 10 Action acceptance utility.
- Added Builder checklist and privacy-policy baseline.
- Initial PR #4 gate `32647770969`: compile/shell PASS, 105 tests PASS and 1 new replay-harness test failed; harness event selection was corrected without weakening production rules.
- Final PR #4 gate `32647828382`: **106 tests PASS**, compile/shell PASS, amd64 Docker/runtime PASS, arm64 QEMU/Buildx build/architecture/runtime PASS.
- PR #4 squash-merged as `a1c578524bbc41afa575b3f4fb6446642a48453d`.
- Phase 10 repository-side preparation: VERIFIED; live Action activation still requires real HTTPS after Phase 9 deployment.
- Phase 11A: VERIFIED.

## 2026-08-23 - Phase 9.1 Oracle ARM64 / multi-arch

- Selected Oracle Cloud Always Free Ampere A1 in Germany Central (Frankfurt) as the primary K-Trader production hosting path.
- Added Linux ARM64 production runner target `k-trader-prod-arm64` while retaining amd64 fallback compatibility.
- Generalized GitHub Actions Runner registration to auto-detect linux-x64 vs linux-arm64 and verify architecture-specific official SHA-256 checksums.
- Updated Ubuntu provisioning to support both `arm64` and `amd64` Docker repositories.
- Split Docker CI into amd64 and ARM64 gates.
- Added QEMU/Buildx ARM64 image build, architecture assertion, production ASGI import, and packaged acceptance-utility verification.
- Added Oracle A1 provisioning documentation and hosting decision record.
- Recorded Oracle capacity status: `VM.Standard.A1.Flex` unavailable in Frankfurt AD-1/AD-2/AD-3 on 2026-08-23, including reduced 1 OCPU / 6 GB attempts.
- No paid Oracle shape approved as a capacity workaround.
- Retained home Windows PC + Tailscale Funnel as a potential fallback only; no implementation approved.
- Cloudflare Workers + Durable Objects deferred from K-Trader v1 and retained only as a future-project architecture idea.
- Verification: PR #3 CI run `32646869264` SUCCESS; **92 tests passed**, shell validation PASS, amd64 Docker/runtime PASS, ARM64 QEMU/Buildx image build/architecture/runtime PASS.
- PR #3 squash-merged as `8e7ef38311e8c92398eb7cf530c92ff773e2a9a1`.

## 2026-08-23 - Phase 9 CI / Docker / production preparation

- Added GitHub-hosted repository-wide CI and separated it from the production self-hosted runner.
- Real integrated CI initially found two invalid synthetic fixtures; fixed fixtures without weakening production candle validation.
- Real Docker import found a FastAPI lifecycle compatibility regression; migrated runtime startup/shutdown to ASGI lifespan.
- CI run `32636825758`: **92 tests passed**, compile PASS, Compose PASS, Docker build PASS, production runtime import PASS.
- Added hardened non-root Dockerfile and read-only Compose runtime with loopback-only application bind.
- Added optional Caddy HTTPS profile.
- Added manual-only `main` production deploy workflow.
- Added immutable commit-SHA releases and rollback when process/live acceptance fails.
- Added target-VPS REST acceptance for 5m/15m/1h/4h/1d and public 5m WebSocket acceptance.
- Added scanner `data_ready` and MTF API acceptance gate.
- Added Ubuntu/Docker and runner registration scripts.
- Final production-prep CI run `32637233264`: pytest/compile/Compose/Docker/runtime/acceptance-packaging PASS.
- Phase 9 remains open only for external VPS provisioning, live acceptance, persistence/restart and HTTPS verification.

## 2026-08-23 - Phase 8.5 runtime scanner coordinator

- Added autonomous `ScannerCoordinator` composing provider selection, universe, data readiness, indicators, market structure, Trap/VSA, Trading Engine and API publication.
- Added configurable top-N analysis shortlist, scan interval and bounded bootstrap concurrency.
- Integrated the existing Phase 2 MTF bootstrap and Phase 3 live WebSocket service.
- Retain live subscription across cycles unless provider or shortlist changes.
- Added per-symbol failure isolation and DEGRADED runtime state.
- Added explicit `NO_SETUP` -> `NO_TRADE` sentinel for fully valid/fresh symbols with no confirmed setup.
- Stale/incomplete symbols produce no fabricated TradingDecision.
- Added atomic `ApiReadModel.publish_cycle()` and full runtime-data clearing on total failure/provider loss.
- Extended candle-series provenance to `provider|aggregate|mixed`.
- Extended runtime status with cycle/readiness/live-stream metrics.
- Added production entrypoint `ktrader.runtime.app:app` and clean shutdown boundaries.
- Phase 8.5 code is now included in the Phase 9 repository-wide **92-test PASS** baseline.

## 2026-08-23 - Phase 8 read-only API

- Added FastAPI read-only application boundary.
- Added thread-safe `ApiReadModel` for scanner-published runtime state.
- Added health/status/universe/market/candles/analysis/candidates/signals endpoints.
- Added exact Decimal-as-string and UTC ISO-8601 timestamps.
- Added provider ambiguity detection with HTTP 409; no silent provider substitution.
- Added candle source provenance and A/A+ LONG/SHORT-only signal filtering.
- Added application-level fixed-window rate limiter.
- Added Custom GPT OpenAPI schema and Action guide.
- Verification: isolated Phase 8 API harness 7/7 PASS.

## 2026-08-23 - Phase 7 setup / rating engine

- Added provider-independent Trading Engine package and canonical setup discovery/geometry/scoring.
- Added evidence/STRONG-level/HTF/RR/ATR hard gates.
- Added structural Entry/Stop/Target and prohibited synthetic 3R targets.
- Added 100-point Setup Score, A+/A/B/C and hard-reject override.
- Added optional explicit RiskContext sizing.
- Verification: exact Phase 7 module logic 17/17 isolated checks PASS.

## 2026-08-23 - Phase 6 trap + VSA

- Added trap engine and VSA ND/NS/T/UT/BC/SC/SV with HTF/location/confirmation rules.
- Verification: isolated Phase 6 harness 14 tests passed.

## 2026-08-23 - Phase 5 market structure

- Added swings, MTF regime/strength, DST-aware sessions, levels/lifecycle and consolidation.
- Verification: isolated Phase 5 harness 12 tests passed.

## 2026-08-23 - Phase 4 indicators

- Added Wilder ATR14, canonical ATR5D, SMA/EMA MA50/200 and relative volume/spread metrics.
- Verification: isolated Phase 4 harness 12 tests passed.

## 2026-08-23 - Phase 3 live market data

- Added Binance USD-M and Bybit Linear public WebSocket streaming, local MTF aggregation, reconnect and REST reconciliation/gap recovery.
- Verification: isolated Phase 3 harness 10 tests passed.
- Target-VPS continuous REST/WS acceptance remains pending.

## 2026-08-23 - Phase 2 market-data core

- Added UTC validation, missing-bar/freshness rules, fail-closed MTF bootstrap and SQLite WAL persistence.
- Verification: isolated Phase 2 harness 9 tests passed.
- Target-VPS live bootstrap acceptance remains pending.

## 2026-08-23 - Phase 1 market-data foundation

- Added exchange-agnostic MarketDataProvider contract, Binance USD-M + Bybit Linear public REST adapters, universe/liquidity filtering and fallback.
- Verification: 7 tests passed.
- Target-VPS provider acceptance remains pending.

## 2026-08-23 - Phase 0 foundation

- Approved K-Trader Roadmap v1.0 and read-only exchange-agnostic architecture.
- Approved SYSTEM K_Trader v1.1.
- Replaced uncalibrated Probability with Setup Score for v1.
- Defined canonical data, ATR, VSA, levels, trap, scoring, signal, API, deployment, test and security contracts.
