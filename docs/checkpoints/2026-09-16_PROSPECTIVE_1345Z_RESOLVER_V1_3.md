# 2026-09-16 — Prospective 13:45Z / Resolver v1.3 Acceptance

Status: **ACCEPTED CURRENT CHECKPOINT**

## Production invariants

- deployed application SHA unchanged: `81b79b281a4cc330b7c11058d202e0d74fb6d70e`;
- mode remains `read_only`;
- holdout remains closed/unopened;
- no production deploy/restart/action;
- frozen candidate remains `candidate_rule_set_v2_2`;
- frozen harness SHA remains `b8471af989090375dec9e25daae184814674a776ab9b46b45e660e35b368be08`;
- protocol SHA remains `ba671cbed71fdc79380f37a72b75f93e75aa3ee895f5385ef433f497165de5a3`.

## 13:30Z capture

The first controlled post-prereg capture at `2026-09-16T13:30:00Z` was valid after staging dependencies were completed.

- panel: `19/19`;
- current capture eligible setups: `48`;
- event count: `299`;
- ledger eligible observations: `60`;
- ledger unique families: `46`;
- bundle set SHA256: `6f69588ab1a7c4251b35e1700fc15c40342f7065a7ee3a6dc67a4cbcf4ac27c4`;
- shadow summary SHA256: `9630f64a062b3174e10e92e1b76542e347fcf0ea0c8962c19dbd6b111675cb71`;
- funding records: `1859` across `19` symbols;
- funding summary SHA256: `2e285f0eff034f6eaa1d34d23d5ea078c69438ed9bfbdec2057d553019f7e58f`.

Relative to 12:00Z, unique families increased `43 -> 46`.

Three new families appeared:

- TRUMPUSDT SHORT, entry `12:30Z` — discovery/context only because it is before prereg boundary;
- ADAUSDT SHORT, entry `13:15Z` — post-prereg confirmation sample;
- DOGEUSDT SHORT, entry `13:15Z` — post-prereg confirmation sample.

Confirmation sample therefore starts with `2` families, both unresolved at this checkpoint series.

For preregistered H1 (`SHORT && h1_ema_sep_atr < 0.9033277894201235`):

- ADAUSDT `h1_ema_sep_atr = 1.723638807428305` -> REST;
- DOGEUSDT `h1_ema_sep_atr = 1.614385470865619` -> REST.

Neither has a rich next obstacle inside 1R/3R (`level_v2_h1_next_level_R = null`).

## Pipeline hardening discovered during 13:30Z

Two early execute attempts failed closed before producing accepted outcomes:

1. missing capture companion staging;
2. missing level-context dependency staging.

After full research-module dependency staging, capture/funding/resolver passed, but post-30 diagnostics exposed an orchestration bug: resolver v1.2 was invoked without explicit `--output-root`, causing its inherited v1.1 default output directory to be used.

The misplaced output was marked:

`INVALID_ORCHESTRATION_OUTPUT_DO_NOT_USE.json`

Canonical 13:30Z v1.2 outcome was then recomputed deterministically with explicit v1.2 output root:

- `46` families;
- `39` resolved;
- `7` unresolved;
- wins/losses `9/30`;
- expectancy `-0.6482720085510278R`.

No strategy metric changed.

## Runner fixes

`run_prospective_research_pipeline_v1.py` was hardened to:

- preflight the five top-level scripts plus five capture runtime dependencies;
- fail before execution when any runtime file is missing;
- use an explicit versioned resolver output root;
- reject existing run/outcome roots in execute mode;
- record outcomes root and resolver version in the manifest.

Regression suite after hardening: **6/6 PASS**.

## Why resolver v1.3 was introduced

At the next closed cutoff `2026-09-16T13:45:00Z`, the hardened v1.2 pipeline reached resolver and correctly failed closed on:

`VTHOUSDT stop_abs_delta = 3.561768196352899e-9`

This exceeded v1.2 absolute guard `3e-9`.

Audit across all 50 prior resolved observations showed:

- entry max delta exactly `0.0`;
- largest stop drifts concentrated in low-priced VTHOUSDT;
- maximum stop drift / accepted risk distance = `4.9105198702635914e-05` (~0.0049% of risk).

A fixed absolute stop tolerance is therefore not scale-neutral.

## Resolver v1.3

Accepted v1.3 rules:

- stable identity unchanged;
- prior accepted entry must match exactly;
- stop sanity guard allows existing `3e-9`/`1e-12` close or at most `1e-4` of accepted initial risk distance;
- revalidation uses accepted prior entry/stop;
- accepted terminal/economic fields remain immutable;
- larger drift fails closed.

Canonical v1.3 output at `13:45Z`:

`/data/research/phase11g/strategy_benchmark_v1/combined_rules/prospective_v2_2_outcomes_offline_v1_3/20260916T134500Z`

State:

- eligible observations `60`;
- unique families `46`;
- resolved primary families `39`;
- unresolved primary families `7`;
- wins/losses `9/30`;
- win rate `23.0769230769%`;
- expectancy `-0.6482720085510278R`;
- prior reused `50`;
- current-path revalidated `44`;
- aged-out preserved `6`;
- prior entry max delta `0.0`;
- prior stop max delta `3.561768196352899e-9`;
- parity against 50 prior resolved observations: **0 terminal/economic mismatches**;
- holdout `false`;
- production action `false`.

Summary SHA256:

`9ecd26069c514fcafd1ce73fc06d5e05eb5aeffba549a99ef9487e18b9fc21af`

Post-30 descriptive SHA256:

`f1b2566593a0a0d2878b1db9c0b2e1894643fcfddea2c8a3d15536dbba1c745e`

Post-30 statistical SHA256:

`fd56096c5a5b37de3e64e5f49a364256d5ffbf3c6c2c7ae93ec9a163c55ab0b5`

Resolved diagnostic conclusions remain unchanged.

## Open primary families at 13:45Z

- SUIUSDT SHORT, entry `08:00Z`: `23/32` bars, pre-prereg;
- XRPUSDT SHORT, entry `08:00Z`: `23/32`, pre-prereg;
- ADAUSDT SHORT, entry `08:15Z`: `22/32`, pre-prereg;
- DOGEUSDT SHORT, entry `08:15Z`: `22/32`, pre-prereg;
- TRUMPUSDT SHORT, entry `12:30Z`: `5/32`, pre-prereg discovery/context;
- ADAUSDT SHORT, entry `13:15Z`: `2/32`, post-prereg confirmation;
- DOGEUSDT SHORT, entry `13:15Z`: `2/32`, post-prereg confirmation.

## Current governance

- evidence tier remains `DIAGNOSTIC_30_49_RESOLVED_FAMILIES`;
- prereg confirmation boundary remains `entry_time >= 2026-09-16T13:00:00Z`;
- confirmation sample: `2` families / `0` resolved;
- no frozen-v2.2 retune is authorized;
- no holdout access;
- no Phase 12 activation.

## Next work order

1. use resolver v1.3 for all future prospective continuation;
2. use the hardened fail-closed runner with full dependency preflight;
3. continue collecting/resolving all primary families causally;
4. keep pre-prereg families out of H1-H4 confirmation counts;
5. track post-prereg confirmation families separately;
6. leave frozen v2.2, holdout, production and disk-retention timer unchanged.
