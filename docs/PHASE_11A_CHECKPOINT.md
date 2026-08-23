# Phase 11A Checkpoint - Replay / Regression Hardening

Date: 2026-08-23

Status: VERIFIED.

## Scope

- deterministic chronological replay harness;
- level lifecycle regression;
- Trap lifecycle causality;
- gap/cross-provider fail-closed replay validation;
- ATR no-future-lookahead regression;
- freshness boundary regression;
- deterministic replay digest for future snapshot fixtures.

## Important hardening fix

Trap detection no longer marks a fresh break as `EXPIRED` before the configured return window has elapsed. The causal states are now:

`NONE -> BROKEN -> RETURNED -> CONFIRMED`

or, when the full return window expires without return:

`BROKEN -> EXPIRED`.

Only `confirmed=True` Trap events remain eligible for setup discovery, so this lifecycle correction does not weaken entry gates.

During the first PR gate, the new replay test exposed a harness defect: the harness selected the last newly-created break event rather than following the original break cycle. Production Trap logic was not weakened; the harness was corrected to track the first event in that replay cycle.

## Verification evidence

Initial PR CI run `32647770969`:

- compile: PASS;
- shell validation: PASS;
- **105 passed / 1 replay-harness test failed**.

Corrected PR CI run `32647828382`:

- Python compile: PASS;
- shell validation: PASS;
- repository-wide pytest: **106 passed, 1 dependency deprecation warning**;
- linux/amd64 Docker/runtime gate: PASS;
- linux/arm64 QEMU/Buildx image/architecture/runtime gate: PASS.

PR #4 was squash-merged to `main` as:

`a1c578524bbc41afa575b3f4fb6446642a48453d`

This phase currently uses deterministic synthetic historical-style replay fixtures. Provider-recorded real-history regression datasets and signal-outcome calibration remain later hardening work and do not change the replay contract.
