# K-Trader Trading Horizon Profiles

Updated: 2026-09-09

Status: FAST CANONICAL / INTRADAY M15 UNIVERSAL TTL UNRESOLVED / MEDIUM H1 8-12H TIME-SPLIT VALIDATED / NON-FAST NOT PRODUCTION-ACTIVE

## Purpose

Setup TTL is not a universal wall-clock constant. It is part of the setup timeframe and trading-horizon contract.

The invariant lifecycle rule is:

- `setup_age = evaluation_time - canonical_confirmation_time`;
- `setup_age <= profile TTL` remains eligible;
- `setup_age > profile TTL` is hard-rejected as `SETUP_EXPIRED`.

TTL controls how long a confirmed setup remains eligible for entry. It is not the same as the eventual holding duration of an opened position.

## FAST profile — canonical current runtime

Intended horizon: fast trades, approximately up to 4 hours.

- setup/evidence interval: `5m`;
- `setup_max_age_bars = 12`;
- TTL: `60 minutes`;
- exact 60-minute boundary remains valid;
- strictly older than 60 minutes -> `SETUP_EXPIRED`.

This is the existing Setup Spec v1.1 production contract. No RR, ATR, stop, target, context-freshness or probability rule changes are introduced by naming it FAST.

## INTRADAY profile — research state

Intended horizon: same-day trading where an M5 trigger scale is too local.

Initial setup/evidence interval selected for research: `15m`.

Why M15 first:

- `15m` is already part of the canonical MTF history contract;
- it changes the trigger/evidence scale without expanding provider/history/storage contracts;
- `30m` is not currently part of the canonical MTF bundle/history plan and is therefore deferred until evidence shows that M15 is insufficient.

Lifecycle sensitivity band tested:

- 60m = 4 bars;
- 120m = 8 bars;
- 240m = 16 bars;
- 360m = 24 bars;
- 480m = 32 bars.

The first sample suggested a provisional `4–6 hours` band (`16–24 x M15 bars`). A later eight-symbol time-separated validation did not reproduce that band as a universal M15 lifecycle rule: 4h retained 37.0% of geometry, 6h 45.4%, and 8h 58.4%. Evidence-type and primary-level-timeframe stratification did not yield a stable replacement rule across time samples. Therefore no single M15 production TTL is currently approved. Geometry-survival share alone is not used to optimize TTL; additional time-separated evidence plus naturally tradable setups and real outcomes are required.

## MEDIUM profile — research state

Intended horizon: multi-session / medium-duration analysis where M5/M15 trigger persistence is too local.

Initial setup/evidence interval selected for research: `1h`.

Lifecycle sensitivity band tested:

- 60m = 1 bar;
- 120m = 2 bars;
- 240m = 4 bars;
- 480m = 8 bars;
- 720m = 12 bars;
- 1440m = 24 bars.

The provisional `8–12 hours` band (`8–12 x H1 bars`) is now time-split validated as a lifecycle design band. Exact first-study geometry survival was 66.7% at 8h and 88.9% at 12h; a later eight-symbol time-split sample produced 55.9% at 8h and 84.7% at 12h. This remains research-only: both samples produced zero tradable signals, so the band is not a profitability optimum and is not a production default.

## Shared invariants

All profiles preserve the existing hard contracts unless separately approved:

- `RR >= 3`;
- structural stop;
- nearest valid structural target;
- no synthetic 3R target;
- canonical ATR-used rule;
- provider/context provenance and freshness rules;
- deterministic replay/live analyzer path;
- no fabricated probability;
- no profile may be selected merely to manufacture more signals.

The UTC-day range used by ATR-used remains derived from canonical `5m` candles even when setup/evidence is evaluated on `15m` or `1h`. Setup timeframe changes must not silently change the ATR-used day-range definition.

## Activation policy

- FAST remains the only production-active profile until a separate rollout is approved.
- INTRADAY and MEDIUM are research profiles only.
- A profile may become production-active only after repository CI, replay provenance, target-host acceptance and explicit owner approval.
- Profile TTL must be stored and reported as both `setup_interval` and `setup_max_age_bars`; derived wall-clock TTL must be computed from the interval rather than hard-coded to five minutes.

## Latest validation checkpoint

`docs/checkpoints/2026-09-09_PHASE11G_HORIZON_TIMESPLIT_VALIDATION.md` records the exact first-study reconstruction, the new eight-symbol time-separated panel, M15 stratification, and H1 cross-sample validation.
