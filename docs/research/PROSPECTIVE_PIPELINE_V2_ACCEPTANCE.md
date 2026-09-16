# Prospective Research Pipeline v2 Acceptance

Status: **ACCEPTED FOR FUTURE FROZEN-v2.2 PROSPECTIVE CYCLES**

Accepted on: 2026-09-16

Canonical runner:

`research/strategy_benchmark_v1/run_prospective_research_pipeline_v2.py`

## Purpose

Pipeline v2 is the fail-closed orchestration wrapper for future prospective frozen-v2.2 cycles. It does not change strategy logic, risk rules, holdout state or production behavior.

## Eight stages

1. capture;
2. funding snapshot;
3. resolver v1.3;
4. post-30 descriptive diagnostics;
5. statistical diagnostics;
6. prereg/discovery evidence tracker;
7. portfolio-risk diagnostic;
8. machine-readable state manifest.

A failed stage blocks every later stage.

## Safety properties

- plan-only by default;
- execution requires explicit `--execute`;
- resolver pinned to v1.3;
- prereg boundary explicit and recorded;
- output collisions fail closed;
- prior accepted outcomes required;
- required runtime dependencies preflighted;
- holdout remains false;
- production action remains false;
- each run produces a pipeline manifest.

## Acceptance evidence

Clean temporary checkout of `research-strategy-benchmark-v1`:

- pipeline v2 tests: `2/2 PASS`;
- pipeline v1 regression tests: `6/6 PASS`;
- full current research test directory after portfolio-simulation tests were added: `10/10 PASS`.

Runtime plan preflight inside the production research container:

- as-of used for plan acceptance: `2026-09-16T16:45:00Z`;
- required runtime files: `13`;
- planned stages: `8/8`;
- mode: `PLAN_ONLY`;
- status: `PLAN_ONLY`;
- holdout opened: `false`;
- production action: `false`;
- plan manifest SHA256: `4b69ddf71296179ae0ec038ee8c9c20afca552deaa68f98f7bcb29a66fb049e6`.

## Transition rule

Pipeline v2 is canonical for the **next fresh prospective cutoff**.

The accepted `16:30Z` cycle was already in progress before v2 acceptance, so its remaining stages were completed manually with the same canonical component scripts. It must not be rerun solely to manufacture a v2 execution manifest.

Pipeline v1 remains preserved for audit/history but is no longer the preferred orchestration entry point.

## Non-effects

This acceptance does not:

- change frozen `candidate_rule_set_v2_2`;
- authorize holdout access;
- authorize production trading;
- select portfolio-risk caps;
- activate Phase 12;
- reopen broad adaptive strategy discovery delegated to `K_Investigation_Forecast`.
