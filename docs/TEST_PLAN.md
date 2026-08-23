# Test Plan v2.6

## Test layers

1. Unit tests
- normalization/candle integrity
- gap/freshness/storage/live aggregation
- ATR/MA/volume metrics
- market structure/sessions/levels
- trap/VSA evidence
- setup discovery/geometry/scoring/risk

2. Provider contract tests
- equivalent normalized interface per adapter
- historical/live public market-data contract

3. Historical bootstrap tests
- closed depth, UTC alignment, gaps/staleness, atomic persistence

4. Live market-data tests
- provisional open bar isolation
- closed 5m persistence
- complete parent aggregation
- reconnect/stale/reconciliation/gap recovery

5. Market-structure tests
- swing/regime/strength/session/level lifecycle

6. Trap/VSA replay tests
- failed-break/return/confirmation
- causal incomplete Trap states before window expiry
- ND/NS/T/UT/BC/SC/SV raw detection
- HTF/location/confirmation hard filters

7. Trading Engine tests
- UTC-day range starts at 00:00 UTC
- setup discovery/evidence identity/strong-level/HTF gates
- Entry/Luft/SL/TP geometry and structural target
- RR/ATR-used hard gates
- deterministic scoring and A+/A/B/C
- hard-reject override
- optional RiskContext sizing
- best-decision ordering

8. API / Action tests
- health/readiness and GET-only routes
- exact Decimal/UTC serialization
- provider ambiguity -> HTTP 409
- candle provenance and tail behavior
- TradingDecision/candidate/signal filtering
- interval/grade validation
- rate limiting and stable OpenAPI operation IDs
- optional Bearer key protects `/v1/*`
- public `/health` and `/privacy`
- Action OpenAPI YAML parses and remains read-only
- exactly eight required Action operation IDs
- precise Action response schemas
- HTTPS server-origin renderer rejects unsafe origins

9. Runtime coordinator tests - Phase 8.5
- valid universe publishes explicit NO_SETUP/NO_TRADE analysis when no setup exists
- one-symbol failure is isolated and cycle becomes DEGRADED
- provider failure falls back without retaining old-provider snapshot state
- atomic cycle publication replaces prior provider state

10. Replay / regression hardening - Phase 11A
- chronological prefix replay only
- level BROKEN/MIRROR/INVALIDATED lifecycle
- Trap `BROKEN -> RETURNED -> CONFIRMED`
- Trap `BROKEN -> EXPIRED` only after full return window
- gap and cross-provider replay rejection
- historical Wilder ATR value unchanged by a future appended bar
- freshness exact boundary and post-boundary rejection
- deterministic canonical replay digest

11. Provider history / signal outcomes - Phase 11B
- `ktrader.history.v1` JSONL roundtrip
- canonical candle-content SHA-256 integrity verification
- tampered history dataset rejection
- closed/contiguous/single-provider history enforcement
- provider collector drops current open candle and keeps latest requested closed bars
- provider native page-capacity enforcement
- WIN and LOSS geometry-touch outcomes
- same-candle entry/exit ambiguity
- same-candle Stop+Target ambiguity after entry
- pending and explicit-horizon expiry states
- NO_TRADE excluded as `NOT_ELIGIBLE`
- cross-provider/gapped future outcome history rejected
- deterministic decision fingerprint
- SQLite outcome pending-to-resolved upsert
- binary sample query contains WIN/LOSS only

12. Deep provider history / MTF replay - Phase 11C
- Binance historical `endTime` and Bybit historical `end` cursor translation
- strict backward page-cursor progress
- page deduplication by candle open time
- exact requested closed-bar depth
- unsupported pagination and insufficient-depth fail-closed behavior
- cross-provider page identity rejection
- final merged-history gap rejection
- canonical `1d/4h/1h/15m/5m` bundle membership
- one provider/canonical symbol/provider symbol across the full bundle
- shared UTC `as_of` cutoff across all timeframes
- future candle beyond `as_of` rejection
- no-lookahead slicing to explicit replay cutoff
- per-series and bundle SHA-256 integrity
- bundle roundtrip and tamper detection

13. Full-engine historical replay / outcome studies - Phase 11D
- live `EngineSymbolAnalyzer` and historical replay share `analyze_candle_snapshot()`
- replay context JSON roundtrip with confirmed instrument and timestamped liquidity points
- replay-context provider/symbol/provider-symbol identity enforcement
- historical liquidity rank/universe-size validation
- context point selected only when timestamp <= replay cutoff
- missing/stale liquidity context causes cutoff skip, never fabricated rank
- chronological MTF slicing before shared engine invocation
- unchanged setup geometry deduplicated by stable signal key
- exact decision fingerprint remains time-specific audit identity
- only unique tradable setups are evaluated for outcomes
- NO_TRADE decisions do not produce calibration outcomes
- Phase 11B future-candle evaluator/persistence integration
- explicit optional study horizon
- replay study JSONL artifact always keeps `estimated_probability=null`
- deterministic study identity inputs

14. Historical universe / study cohorts - Phase 11E
- `ktrader.universe_snapshot.v1` preserves provider-native instrument/ticker inputs, liquidity score, rank and live-compatible universe size
- snapshot ranks are contiguous and reproducible from captured ticker inputs
- cross-provider instruments/tickers are rejected
- ticker timestamps after snapshot capture time are rejected
- `ktrader.universe_archive.v1` requires one provider, one UniverseConfig and strictly chronological snapshots
- per-snapshot and archive SHA-256 tampering is detected
- append preserves prior snapshots and archive identity
- cohort time window selects only actually captured snapshots
- requested symbols absent from captured universe are rejected
- per-symbol ReplayStudyContext is generated only from captured membership observations
- context points use snapshot timestamps and captured score/rank/universe size
- changed analysis-critical instrument metadata inside one cohort is rejected
- cohort/context digest mismatch and unsafe context paths are rejected
- current ticker data is never accepted as a retroactive historical rank substitute

15. Operations hardening / continuous research capture - Phase 11F
- live universe service retains the exact normalized instrument/ticker inputs from the selected provider request cycle
- research capture reuses those exact source inputs and does not issue a second provider fetch
- default 300-second capture cadence suppresses premature duplicate captures
- each capture is written as an immutable digest-verified one-snapshot universe archive
- online SQLite backup uses the native backup API while the source repository remains open
- backup must pass `PRAGMA integrity_check` before atomic publication
- corrupt/non-SQLite files fail backup verification
- backup retention keeps only the configured newest files
- a generated backup can be opened as a fresh repository with persisted candle state intact
- disk guard rejects operation before provider access when configured free-space requirements are not met
- disk-guard failure clears current publishable scanner state and sets `data_ready=false`
- stale scanner timestamp degrades `/health` without changing the public response shape
- fresh scanner timestamp returns normal health when all other readiness gates pass
- Docker healthcheck requires `/health` JSON `status=ok`
- Docker log configuration is bounded by max-size/max-file rotation

16. Dataset catalogue / study provenance - Phase 11G
- `ktrader.study_run_provenance.v1` roundtrip and digest validation
- complete `RuntimeScannerConfig` participates in provenance hashing
- replay/study configuration changes produce different provenance identities
- replay-study inspector rejects non-null estimated probability
- replay-study decision IDs are unique and decision/outcome identity/counts are internally consistent
- `ktrader.outcome_sample.v1` accepts only WIN/LOSS outcomes
- immutable outcome sample carries source study ID and exact replay-study file SHA-256
- repository outcome must exactly match the replay-study embedded binary outcome before sample export
- `ktrader.dataset_catalogue.v1` entry links bundle/archive/cohort/study/provenance/sample with one provider and symbol
- cohort archive SHA must equal the supplied universe archive SHA
- replay-study bundle SHA must equal the supplied MTF bundle SHA
- provenance context SHA must equal the exact cohort symbol context SHA
- registered artifact exact content SHA changes are detected
- directory tree SHA is deterministic and symlink/path traversal escapes are rejected
- catalogue entry and catalogue SHA roundtrip is deterministic
- duplicate replay-study registration is rejected
- full catalogue load can re-open and rebuild all referenced artifact relationships

17. Integration tests
- provider -> validation -> storage -> indicators -> structure -> Trap/VSA -> Trading Engine -> runtime coordinator -> API
- provider-recorded MTF bundle + timestamped liquidity context -> shared analysis engine -> TradingDecision -> outcome evaluator -> OutcomeRepository
- provider instruments/tickers -> captured universe archive -> study cohort -> ReplayStudyContext -> Phase 11D replay
- selected live universe request -> immutable research capture + scanner analysis without a second provider fetch
- MTF bundle + universe archive/cohort + full scanner/study configuration -> replay study/provenance -> immutable outcome sample -> verified dataset catalogue
- source/freshness propagation
- fail-closed NO_TRADE behavior

18. Deployment and architecture tests
- container build/start
- persistence across restart
- scanner coordinator + API health
- repository-wide CI/CD smoke
- target-host REST/bootstrap/WebSocket acceptance
- target-host persistence/backup/restart acceptance
- target-host research capture and watchdog acceptance
- linux/amd64 production image build/import
- linux/arm64 production image build/import under QEMU/Buildx in CI
- image architecture assertion before ARM64 runtime import
- packaged target-host acceptance utility on both image architectures
- production runner architecture label must match the approved Oracle ARM64 host

## Mandatory acceptance cases

- Cross-provider OHLCV mixing is rejected.
- Stale/gapped/open data cannot masquerade as confirmed analysis input.
- Failed MTF bootstrap writes no partial snapshot.
- ATR5D cannot replace/duplicate rejected D1 bars.
- Historical ATR output at bar N must not change when future bar N+1 is appended.
- MA alone cannot create directional market regime.
- Session cannot independently permit a trade.
- FLOATING/BROKEN/INVALIDATED levels cannot validate a primary setup.
- Primary tradable level must be STRONG.
- Trap requires break -> return -> confirmation.
- A Trap break cannot become `EXPIRED` before its configured return window elapses.
- Context-free/unconfirmed VSA cannot validate a setup.
- Evidence identity mismatch is rejected.
- Daily ATR-used context must begin at 00:00 UTC.
- No structural target -> NO_TRADE; synthetic 3R target is prohibited.
- RR <3 is rejected.
- ATR used >80% is rejected.
- Hard reject cannot retain A/A+ public grade/score.
- B/C never emits tradable LONG/SHORT.
- Missing account/risk inputs produce position size/risk N/A.
- API cannot expose write/trading operations.
- Ambiguous multi-provider symbol cannot be silently resolved.
- API must not recalculate/override TradingDecision fields.
- Autonomous runtime must not publish analysis before data readiness.
- Valid/fresh symbol with no setup must return explicit NO_SETUP/NO_TRADE rather than a fabricated setup.
- Total provider/runtime failure must clear current publishable market/decision state.
- Provider fallback must atomically replace the prior provider snapshot.
- ARM64 CI image must report architecture `arm64` and import the same production ASGI app as amd64.
- Runner registration must reject unsupported host architectures and checksum-verify the architecture-specific archive.
- Production Action key must not be committed; configured `/v1/*` auth must reject missing/invalid Bearer credentials.
- Canonical Action OpenAPI must remain GET-only and retain the `.invalid` server placeholder until real HTTPS is accepted.
- Provider-history datasets must be closed, contiguous and single-provider with a verified content digest.
- Historical outcome bars must start after the decision's last closed bar.
- Outcome evaluation must never guess OHLC intrabar ordering.
- `NO_TRADE`, `AMBIGUOUS`, pending and expired outcomes must not enter the WIN/LOSS binary sample set.
- Phase 11B/11C/11D/11E/11F/11G must not populate `estimated_probability` or reinterpret Setup Score as probability.
- Deep historical collection must never splice another provider to fill a missing page.
- Deep historical collection must fail if the exact requested closed-bar depth cannot be produced.
- Historical page cursors must make strict backward progress.
- An MTF replay bundle must contain exactly `1d/4h/1h/15m/5m` for one provider and one symbol identity.
- Any candle closing after the bundle `as_of` cutoff must be rejected.
- Replay slicing must exclude all bars not closed by the selected cutoff.
- Bundle/series digest mismatches must be detected on load.
- Historical full-engine replay must use the same canonical snapshot analyzer as live runtime.
- Historical liquidity score/rank/universe size must come from a timestamped replay-context observation, never a guessed default.
- A replay context observation with timestamp after the cutoff must never be used.
- A stale or missing replay context observation must skip the cutoff fail-closed.
- Repeated unchanged setup geometry must not be counted as independent signals on every 5m cutoff.
- Exact decision fingerprint and stable signal key must remain separate concepts: audit identity vs setup-study identity.
- Historical universe ranks may be used only from snapshots actually captured at that time; current tickers cannot backfill old ranks.
- A universe archive must never mix provider IDs or UniverseConfig values.
- A study cohort must derive its context points only from archive snapshots inside the selected window.
- Continuous research capture must reuse the exact selected live universe source inputs rather than re-fetching a second ticker snapshot.
- Low disk must fail the scan closed before provider/bootstrap writes and must not leave stale data publishable as current.
- A SQLite backup is valid only after integrity verification and atomic publication.
- Backup verification must reject corrupt database artifacts.
- Runtime health must degrade when the scanner exceeds its configured maximum scan age.
- Container health must depend on semantic `status=ok`, not HTTP reachability alone.
- A catalogue entry must never connect a cohort to a different universe archive or a replay study to a different MTF bundle.
- Study provenance must bind the exact cohort symbol context and complete scanner/study configuration.
- Registered artifact paths must stay within one explicit artifact root and must not escape through traversal or symlinks.
- A changed registered artifact must fail catalogue verification rather than silently replacing prior evidence.
- Immutable outcome samples may contain only study-linked WIN/LOSS rows that exactly match `OutcomeRepository`.
- The dataset catalogue and outcome sample must never calculate win probability.

## Current deterministic verification

- Phase 1 provider suite: 7 passed.
- Phase 2 isolated harness: 9 passed; compileall PASS.
- Phase 3 isolated harness: 10 passed; compileall PASS.
- Phase 4 isolated harness: 12 passed; compileall PASS.
- Phase 5 isolated harness: 12 passed; compile validation PASS.
- Phase 6 isolated harness: 14 passed; compile validation PASS.
- Phase 7 exact-module isolated harness: 17 passed; syntax compilation PASS.
- Phase 8 isolated API harness: 7 passed; FastAPI/OpenAPI generation and syntax validation PASS.
- Phase 9 integrated baseline: **92 passed**, compile/Compose/Docker/runtime PASS.
- Phase 9.1 CI run `32646869264`: **92 passed**, amd64/arm64 Docker/runtime PASS.
- Phase 10 preparation + Phase 11A final CI run `32647828382`: **106 passed**, Python compile PASS, shell validation PASS, amd64 Docker/runtime PASS, arm64 QEMU/Buildx image/architecture/runtime PASS.
- Phase 11B CI run `32650220382`: **121 passed**, Python compile PASS, shell validation PASS, amd64 Docker/runtime PASS, arm64 QEMU/Buildx image/architecture/runtime PASS.
- Phase 11C CI run `32652044967`: **134 passed**, Python compile PASS, shell validation PASS, amd64 Docker/runtime PASS, arm64 QEMU/Buildx image/architecture/runtime PASS.
- Phase 11D final CI run `32653087172`: **140 passed**, Python compile PASS, shell validation PASS, amd64 Docker/runtime PASS, arm64 QEMU/Buildx image/architecture/runtime PASS.
- Phase 11E CI run `32654162474`: **147 passed**, Python compile PASS, shell validation PASS, amd64 Docker/runtime PASS, arm64 QEMU/Buildx image/architecture/runtime PASS.
- Phase 11F CI run `32656033224`: **155 passed**, Python compile PASS, shell validation PASS, Docker Compose PASS, amd64 Docker/runtime PASS, arm64 QEMU/Buildx image/architecture/runtime PASS.
- Phase 11G CI run `32657337221`: **163 passed**, Python compile PASS, shell validation PASS, amd64 Docker/runtime PASS, arm64 QEMU/Buildx image/architecture/runtime PASS.

The initial Phase 11D PR gate `32653028353` had 135 passed / 5 failed because one newly added synthetic fixture violated existing OHLC validation (`low > open`). Only the fixture was corrected; production validation was not weakened.

Real provider/Oracle-host acceptance remains a separate Phase 9 live gate. Phase 10 live Action acceptance remains blocked until a real HTTPS endpoint exists. Phase 11F repository-side restart/backup/watchdog logic is verified, while real host restart and persistent-volume evidence remains part of the live gate. Phase 11G catalogue logic is repository-verified; real catalogue population requires provider-recorded production artifacts.

## Fixtures

Synthetic fixtures are allowed only inside tests and must be explicitly test data. Production/live outputs may never substitute synthetic data for missing exchange data.

Provider-recorded historical fixtures must preserve provider/symbol/timeframe provenance and the `ktrader.history.v1` content digest. Long real-provider MTF bundles are operator-generated artifacts; normal PR CI uses deterministic mocked provider pages and must not fabricate live exchange captures when network collection is unavailable.

Historical liquidity/universe context must likewise be captured as explicit timestamped study input. A synthetic context may be used only in tests and may never be presented as recorded exchange history.

Catalogue test artifacts may be synthetic only inside tests. A production catalogue entry must reference the original provider-recorded artifacts, exact configuration provenance and verified outcome sample without substituting synthetic evidence.
