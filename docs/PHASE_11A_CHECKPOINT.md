# Phase 11A Checkpoint - Replay / Regression Hardening

Date: 2026-08-23

Status: IMPLEMENTED / PR CI VERIFICATION PENDING.

Scope:

- deterministic chronological replay harness;
- level lifecycle regression;
- Trap lifecycle causality;
- gap/cross-provider fail-closed replay validation;
- ATR no-future-lookahead regression;
- freshness boundary regression;
- deterministic replay digest for future snapshot fixtures.

Important hardening fix:

Trap detection no longer marks a fresh break as `EXPIRED` before the configured return window has elapsed. The causal states are now:

`NONE -> BROKEN -> RETURNED -> CONFIRMED`

or, when the full return window expires without return:

`BROKEN -> EXPIRED`.

Only `confirmed=True` Trap events remain eligible for setup discovery, so this lifecycle correction does not weaken entry gates.

This phase uses deterministic synthetic historical-style replay fixtures. Provider-recorded real-history regression datasets can be added later without changing the replay contract.
