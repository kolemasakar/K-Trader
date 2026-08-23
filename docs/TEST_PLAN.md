# Test Plan v2.2

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

13. Integration tests
- provider -> validation -> storage -> indicators -> structure -> Trap/VSA -> Trading Engine -> runtime coordinator -> API
- source/freshness propagation
- fail-closed NO_TRADE behavior

14. Deployment and architecture tests
- container build/start
- persistence across restart
- scanner coordinator + API health
- repository-wide CI/CD smoke
- target-host REST/bootstrap/WebSocket acceptance
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
- Phase 11B/11C must not populate `estimated_probability` or reinterpret Setup Score as probability.
- Deep historical collection must never splice another provider to fill a missing page.
- Deep historical collection must fail if the exact requested closed-bar depth cannot be produced.
- Historical page cursors must make strict backward progress.
- An MTF replay bundle must contain exactly `1d/4h/1h/15m/5m` for one provider and one symbol identity.
- Any candle closing after the bundle `as_of` cutoff must be rejected.
- Replay slicing must exclude all bars not closed by the selected cutoff.
- Bundle/series digest mismatches must be detected on load.

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

Real provider/Oracle-host acceptance remains a separate Phase 9 live gate. Phase 10 live Action acceptance remains blocked until a real HTTPS endpoint exists.

## Fixtures

Synthetic fixtures are allowed only inside tests and must be explicitly test data. Production/live outputs may never substitute synthetic data for missing exchange data.

Provider-recorded historical fixtures must preserve provider/symbol/timeframe provenance and the `ktrader.history.v1` content digest. Long real-provider MTF bundles are operator-generated artifacts; normal PR CI uses deterministic mocked provider pages and must not fabricate live exchange captures when network collection is unavailable.
