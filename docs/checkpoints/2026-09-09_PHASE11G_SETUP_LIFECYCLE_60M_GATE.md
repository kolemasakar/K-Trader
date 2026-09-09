# Phase 11G Setup Lifecycle 60m Gate

Date: 2026-09-09

Status: REPOSITORY + REPLAY VALIDATED / PRODUCTION DEPLOYMENT PENDING

## Decision

The canonical setup lifecycle is now explicit:

- setup interval: `5m`;
- `setup_max_age_bars = 12`;
- TTL: `60 minutes`;
- canonical confirmation time: the latest confirmed evidence bar that activates the selected setup;
- a setup remains valid when `setup_age <= 60 minutes`;
- a setup is hard-rejected with `SETUP_EXPIRED` when `setup_age > 60 minutes`;
- fresh candles do not refresh an already-confirmed setup;
- Trap/VSA local confirmation windows are unchanged;
- `RR >= 3`, stop geometry and structural-target geometry are unchanged.

Canonical specification: `docs/SETUP_SPEC.md` v1.1.

## Research basis

A read-only Setup Recency / Candidate Lifecycle audit showed that stale confirmed evidence was systematically reused during Window #4:

- RR-only decisions audited: `81`;
- setup-age minimum: `0m`;
- median: `545m` (`9h05m`);
- maximum: `1295m` (`21h35m`);
- older than 1h: `78/81`;
- older than 3h: `65/81`;
- older than 6h: `53/81`.

The implementation before this gate had evidence-local confirmation windows but no explicit setup expiry contract. The same-UTC-day geometry guard allowed completed setups to remain eligible for most of a UTC day. This was classified as a specification/lifecycle gap, not an arithmetic or structural-geometry defect.

## Expiry policy study

A read-only sensitivity study compared Trap-only, VSA-only, canonical-trigger and combined-any expiry semantics at 15m/30m/60m/120m.

The approved policy is `CANONICAL_TRIGGER` with TTL `60m` because it matches the setup-trigger semantics already used by canonical geometry and avoids independently expiring older evidence components when a newer confirmed component legitimately activates the setup.

For the reconstructed Window #4 population, the 60m canonical-trigger sensitivity funnel was:

```text
470 total TTL-surviving candidates
 -> 24 HTF aligned
 -> 5 primary-level strong
 -> 3 geometry-valid
 -> 3 ATR <= 80%
 -> 0 RR >= 3
```

RR-only survivors under that policy: `3`, all `NEARUSDT`.

No tested expiry policy created a valid `RR >= 3` trade.

## Implementation

PR #36: `Phase 11G: enforce 60m setup expiry`

Merged canonical main SHA:

`1dbc41d8521daab42b3edb7ef10d3ccfdb8b68bf`

Implemented changes:

- `docs/SETUP_SPEC.md` -> v1.1 lifecycle/expiry contract;
- `src/ktrader/runtime/models.py` -> `setup_max_age_bars: int = 12` with positive validation;
- `src/ktrader/runtime/analyzer.py` -> canonical live/replay analyzer passes `12 * 5 * 60` seconds;
- `src/ktrader/engine/service.py` -> `setup_is_expired()` and hard reject `SETUP_EXPIRED`;
- boundary semantics: exactly 60 minutes remains valid; strictly older is expired;
- future confirmation timestamps fail closed;
- `tests/test_setup_expiry.py` covers defaults, positive config, exact boundary and invalid/future contexts.

PR #36 validation:

- Tests workflow #67: PASS;
- CI workflow #138: PASS;
- CI `pytest`: PASS;
- CI Docker amd64: PASS;
- CI Docker arm64: PASS.

## Control Window #4 replay on merged main

The control replay used the merged-main implementation in a read-only shadow source against the currently available persistent Window #4 research inputs. Production source files were not mutated.

Job:

`job_d77dc7277002`

Result:

- status: `succeeded`;
- exit code: `0`;
- duration: `386.38s`;
- logical cutoffs: `16`;
- selected snapshots: `16` / unique `16`;
- strict symbols: `47`;
- history/replay pass: `43`;
- history failures: `4`;
- analyzed cutoffs total: `645`;
- candidate decisions total: `8874`;
- `SETUP_EXPIRED`: `6563` decisions;
- tradable decisions with no hard reasons: `0`.

History failures were unchanged from the reconstructed V2 input set:

- `MARSCOINUSDT`: requested 300, collected 8;
- `PONSUSDT`: requested 300, collected 3;
- `牛来USDT`: requested 300, collected 10;
- `龙虾USDT`: requested 300, collected 182.

The script's legacy pre-expiry stage funnel remains:

```text
8874 -> 454 -> 166 -> 133 -> 81 -> 0
```

This funnel is intentionally not the lifecycle-filtered funnel because those legacy stage counters are evaluated before the new expiry reason is applied. The post-expiry operational result is represented by the exact RR-only population after all hard reasons:

- RR-only exact: `3`;
- RR-only unique geometry: `3`;
- all three: `NEARUSDT`;
- RR values: approximately `0.0851`, `0.1316`, `0.1316`;
- RR pass: `0`.

The diagnostic script printed `SETUP_EXPIRED` in its `unexpected_reasons` bucket only because that helper bucket represented reasons outside its older pre-TTL reason vocabulary. `SETUP_EXPIRED` is expected after PR #36 and is not an anomaly.

## Geometry conclusion remains unchanged

The preceding RR geometry audit traced all `81/81` pre-expiry RR-only decisions to real pre-mask `SetupGeometry` objects and found:

- `21` unique real geometries;
- all LONG;
- structural resistance targets, not synthetic 3R targets;
- observed RR range approximately `0.026` through `1.0`;
- no arithmetic RR defect;
- no evidence that the target-selection implementation should be loosened;
- low RR is explained by structural reward distance being small relative to stop risk.

Therefore:

- do not lower `RR >= 3`;
- do not synthesize a 3R target;
- do not alter stop/target geometry based on this gate.

## Provenance caveat

The original historical Window #4 checkpoint and the later reconstructed V2 input set are not byte-identical.

Historical checkpoint:

- strict symbols: `45`;
- MTF/history pass: `40`;
- analyzed cutoffs: `600`;
- candidate decisions: `7596`;
- final RR-only population: `142`.

Current reconstructed V2:

- strict symbols: `47`;
- history pass: `43`;
- analyzed cutoffs: `645`;
- candidate decisions: `8874`;
- pre-expiry RR-only population: `81`;
- post-expiry RR-only population: `3`.

Exact old Window #4 input artifacts are not persisted on the VM. A roughly one-day pause between research sessions is a plausible explanation for source/archive drift, but this is not proven. The historical checkpoint remains the canonical record of the old run; the V2 reconstruction is a separately labelled replay on the inputs available at reconstruction time.

## Gate closure

The Setup Lifecycle / Expiry research gate is closed at the repository/specification/replay level:

- lifecycle semantics explicit: PASS;
- TTL 60m approved: PASS;
- exact boundary tested: PASS;
- live/replay shared canonical path: PASS;
- CI amd64/arm64: PASS;
- Window #4 control replay: PASS;
- no RR/geometry relaxation: PASS;
- no synthetic tradable setup created: PASS.

Production still runs the previously deployed image `k-trader:7fa20c3d7f0d89ae628eb2bf21e4c50164eb3eab`; PR #36 has not yet been deployed to production. Production rollout is therefore an explicit subsequent operational task and is not silently implied by this research checkpoint.

## Next Phase 11G work

Next research sequence:

1. deploy the approved main baseline through the standard production workflow when rollout is authorized;
2. rerun corrected discovery for historical Windows #1-#4 under the explicit 60m setup lifecycle;
3. preserve actual per-run provenance and do not force new runs to reproduce superseded populations;
4. materialize a new chain only if a naturally useful deterministic setup survives every canonical hard gate;
5. keep `RR >= 3`, context freshness, structural target and probability rules unchanged.
