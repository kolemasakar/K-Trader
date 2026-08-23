# Test Plan v1.9

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

8. API tests
- health/readiness and GET-only routes
- exact Decimal/UTC serialization
- provider ambiguity -> HTTP 409
- candle provenance and tail behavior
- TradingDecision/candidate/signal filtering
- interval/grade validation
- rate limiting and stable OpenAPI operation IDs

9. Runtime coordinator tests - Phase 8.5
- valid universe publishes explicit NO_SETUP/NO_TRADE analysis when no setup exists
- one-symbol failure is isolated and cycle becomes DEGRADED
- provider failure falls back without retaining old-provider snapshot state
- atomic cycle publication replaces prior provider state
- future repository integration coverage: real bootstrap/live/analyzer composition and clean shutdown

10. Integration tests
- provider -> validation -> storage -> indicators -> structure -> Trap/VSA -> Trading Engine -> runtime coordinator -> API
- source/freshness propagation
- fail-closed NO_TRADE behavior

11. Deployment and architecture tests
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
- MA alone cannot create directional market regime.
- Session cannot independently permit a trade.
- FLOATING/BROKEN/INVALIDATED levels cannot validate a primary setup.
- Primary tradable level must be STRONG.
- Trap requires break -> return -> confirmation.
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

## Current deterministic verification

- Phase 1 provider suite: 7 passed.
- Phase 2 isolated harness: 9 passed; compileall PASS.
- Phase 3 isolated harness: 10 passed; compileall PASS.
- Phase 4 isolated harness: 12 passed; compileall PASS.
- Phase 5 isolated harness: 12 passed; compile validation PASS.
- Phase 6 isolated harness: 14 passed; compile validation PASS.
- Phase 7 exact-module isolated harness: 17 passed; syntax compilation PASS.
- Phase 8 isolated API harness: 7 passed; FastAPI/OpenAPI generation and syntax validation PASS.
- Phase 8.5 orchestration code is included in the integrated repository-wide Phase 9 result.
- Phase 9 integrated repository-wide CI: **92 passed**, compile/Compose/Docker/runtime import PASS.
- Phase 9.1 CI run `32646869264`: **92 passed**, Python compile PASS, shell validation PASS, amd64 Docker/runtime PASS, ARM64 QEMU/Buildx image build/architecture/runtime import PASS.

Real provider/Oracle-host acceptance remains a separate Phase 9 live gate and cannot be claimed until OCI A1 capacity is available.

## Fixtures

Synthetic fixtures are allowed only inside tests and must be explicitly test data. Production/live outputs may never substitute synthetic data for missing exchange data.
