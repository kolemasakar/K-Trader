# Phase 7 Checkpoint

Date: 2026-08-23

Status: IMPLEMENTATION COMPLETE.

## Implemented

- provider-independent Phase 7 Trading Engine package;
- setup candidate discovery from confirmed Trap/VSA evidence;
- setup types `TRAP_VSA_CONFIRMATION`, `VSA_LEVEL_CONFIRMATION`, `TRAP_LEVEL_CONFIRMATION`;
- evidence identity and setup-type consistency gates;
- STRONG confirmed/mirror primary-level hard gate;
- directional HTF regime hard gate;
- canonical luft `max(1 tick, 0.02 * ATR14)`;
- confirmation-trigger Entry geometry;
- structural trap/level Stop geometry;
- nearest confirmed/mirror opposing structural Target;
- synthetic 3R target prohibition;
- RR hard gate >=3;
- canonical ATR-used origin from current UTC-day directional extreme to proposed Entry;
- full-day context requires closed 5m bars from exactly 00:00 UTC;
- deterministic score weights totaling 100;
- A+/A/B/C thresholds;
- hard-reject public score cap and forced C grade;
- optional position sizing only from explicit RiskContext;
- final `TradingDecision` with LONG/SHORT/NO_TRADE and reason codes;
- best-decision selector prioritizing tradable setup, then score/RR.

## Canonical score

Weights:

- regime 20
- liquidity 10
- session 5
- trap 15
- MTF level 15
- strength 10
- VSA 15
- ATR 5
- RR 5

Grades:

- A+ >=90
- A >=80
- B >=70
- C <70

Only A+/A without hard rejects are tradable.

## Hard rejects

Phase 7 covers at minimum:

- stale data;
- invalid liquidity context;
- HTF mismatch;
- primary level not active/confirmed/STRONG;
- missing or mismatched setup evidence;
- missing tick/confirmation/geometry;
- missing structural target;
- ATR used >80%;
- RR <3;
- invalid explicit risk context;
- explicit position size below quantity step.

## Deterministic verification

Exact Phase 7 module logic was executed in an isolated dependency harness:

- 17/17 checks PASS;
- syntax compilation PASS for Phase 7 modules and repository test file.

Covered cases include:

- complete UTC-day range context;
- partial-day rejection;
- all three setup types;
- structural target geometry;
- no-target rejection;
- ATR-used origin;
- A+ full confluence;
- stale-data cap;
- strong-level gate;
- evidence identity mismatch;
- ATR >80 rejection;
- RR <3 rejection;
- explicit/absent position-risk context;
- final LONG emission;
- best-decision selection.

A repository test file `tests/test_trading_engine.py` with 17 deterministic tests is committed.

Repository-wide pytest/CI is still a Phase 9 gate and is not claimed as executed here.

## Remaining infrastructure acceptance

Phases 1-3 still require target-VPS live REST/bootstrap/WebSocket acceptance after deployment.
