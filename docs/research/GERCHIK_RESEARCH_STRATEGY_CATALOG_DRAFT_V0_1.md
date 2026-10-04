# K-Trader restored S1–S6 research catalogue
Updated: 2026-10-04. Status: OWNER-APPROVED FAMILY IDENTITIES RESTORED / CURRENT EXECUTABLE SPEC NOT FROZEN.

Primary interaction: «16 PH-11», assistant specification 2026-09-25T17:54:51Z; owner approval 2026-09-25T18:01:55Z. The earlier assistant draft on this branch incorrectly reassigned S2–S5; this version corrects that error using retrieved original approval context. See [restoration matrix and source differences](GERCHIK_S1_S6_RESTORATION_MATRIX_2026-10-04.md).

| ID | Approved family | Prerequisites | Stop |
|---|---|---|---|
| S1 | Відбій від рівня | Known level, touch, reaction confirmation | Beyond reaction extreme; buffer formalization remains explicit |
| S2 | Пробій із продовженням | Known level, qualifying close beyond it, continuation confirmation | Beyond broken level |
| S3 | Пробій і повторне тестування | Known level, breakout, retest within 6 candles, movement resumes | **Beyond level — owner's correction** |
| S4 | Одинарний хибний пробій | Single-bar penetration and close back to original side | Beyond false-break extreme |
| S5 | Багатобарний хибний пробій | 2–4 closed bars beyond level then return; up-to-6 structure is a separate declared variant | Beyond furthest structure extreme |
| S6 | Трендовий вихід із діапазону | Previous 20 completed candles breakout in EMA50 direction | Historical alternatives: local extreme or 1.5 ATR; exact current branch not yet frozen |

## Historical parameters, preserved as provenance
Original H1 research profile, M15/M30/H4 context, <=12h horizon; ATR14 with 0.15 ATR tolerance; 2R targets or structural alternatives, depending on strategy. These describe the original research versions. Do not reactivate ATR-derived levels, 2R minimum admission or archived lookahead/level proxies under this label.
Old server S6 code also adds H1 TR14 proximity and a 6-bar-extreme stop. Those details are recovered implemented behavior, not proof that every deviation from the primary original specification was owner-approved.

## Current binding shared pipeline
- Admit only confirmed causal D1/W1 Gerchik level events; prices derive from High/Low, no ATR in level creation, geometry or strength. Record when each level actually became available.
- Symmetric equally significant contextual zones; percentage-price/time anchor, tick rounding and Forex point semantics remain explicit required inputs. Separate M5/M15 intraday entry-model precision from higher-TF context.
- Approved ATR5 v2: current-five arithmetic mean, inclusive >=2x / <=1/3 anomaly tests, replace one, recompute and recheck all five, newest-abnormal-first engineering order. v3 is a separately labelled experiment.
- Missing ATR is a recorded data condition; no reinstated blanket transitional-volatility prohibition.
- Evaluate owner's research targets **1R first, then 3R**. S3 technical SL beyond level. No mandatory 2R stage.
- Freeze precise triggers, costs, causal execution, ambiguity/censoring, horizons and data splits before outcomes. Old already-inspected holdout cannot be renamed independent.
- Run analysis, then Level Strength v2 and independent reserved control. K-Trader does not place orders; K_AI owns execution.

The confirmed family identities are restored. Full numeric/boolean strategy migration to the current level/ATR engine is still incomplete; no six-strategy profitability claim follows. [Prepared backtest protocol](GERCHIK_BACKTEST_PROTOCOL_V0_1_2026-10-04.md).


## Executable pattern candidates (2026-10-04)
All six LONG/SHORT pattern kernels are now implemented with explicit tick-based parameters and declared engineering confirmation alternatives: [executable candidate specification](GERCHIK_EXECUTABLE_PATTERN_CANDIDATES_V0_1_2026-10-04.md). They preserve restored IDs and S3 stop-beyond-level, reject future/gapped input, and hand candidate setups to the separate execution simulator. This is not a frozen numeric migration or automatic confirmed-level engine. The candidate protocol retains per-strategy unresolved decisions; no market outcomes were computed. 60 combined synthetic tests passed.
