# K-Trader — new-chat authoritative handoff (2026-09-28)

Status: research-only checkpoint. This file records the approved research direction and constraints, not completed implementation or production acceptance. Research branch: `research/dual-market-historical-levels-v0-1`; PR #88. Latest confirmed pre-handoff research commit: `752e4395196954bb3db6d62e871217f84b226588`. Read the branch head and the files below before any new work.

## Resume and source of truth
- `docs/CURRENT_STATE.md` — production/operational historical baseline; do not treat its older level rules as newly approved Gerchik research.
- `docs/research/GERCHIK_FIXED_LEVEL_CLASSIFICATION_CONTRACT_V0_1.md` — authoritative research classifier and ATR(5) decisions, including appended user approvals.
- `docs/research/archive/legacy_level_algorithms_20260928/README.md` — old research level algorithms archived and disabled. Never import/run them or treat previous exploratory counts as classifier results.
- Book: Alexander Gerchik, `Курс активного трейдера (Александр Герчик) (2).pdf`, especially ch. 2, ch. 9 and ATR section printed p. 101; user-supplied `1-1 Levels.pdf` and `02_ATR_and_range.pdf` if accessible in new chat.

## Approved level research contract
- Only K-Trader's **own internal historical data**; do not access the reserved external AI_Trading_System/Sentinel historical archive before model freeze and separate approval. Previously explored external archive is not pristine holdout.
- D1/W1 confirmed structural candle HIGH/LOW for candidate level price, never CLOSE. Ordinary unqualified D1 local pivots are not levels. Ordinary D1 bars may confirm existing levels. Preserve strict as-of causality.
- Seven Gerchik primary types: TREND_BREAK, HISTORICAL, MIRROR, LIMIT, PARANORMAL_BAR, CONSOLIDATION, GAP. Exactly ONE primary type per fixed level, assigned by formation event; later qualifying patterns = timestamped strengthening evidence, never duplicate primary levels. False breakout = strengthening evidence, not separate primary type. Floating levels remain unconfirmed. Do not invent numerical author scores.
- ATR deliberately not used for level creation/zone geometry/significance in the current simplified level classifier. This is a scope decision, not a claim that ATR is theoretically invalid for paranormal-bar identification. Non-ATR paranormal detector remains pending a defined baseline unless separately changed by the user.
- Volatility-transition no-trade/no-level-analysis gate was explicitly CANCELLED; do not reinstate it.

## Newly approved separate filtered D1 ATR(5) algorithm
The source book ATR chapter excludes unusually large bars with `range >= 2*ATR` and unusually small bars with `range <= ATR/3`. `range = High-Low`. Standard platform ATR is not interchangeable with this manual filtered mean. The project selects FIVE completed D1 bars (book describes 3–5); never include current unfinished bar.

User-approved bootstrap and filtering:
1. Start at the most recently **closed** D1 bar. Gather that bar and four immediately preceding completed D1 bars, in newest-to-oldest order. Compute preliminary arithmetic mean of their ranges.
2. Compare the newest bar against this five-bar preliminary mean. If abnormal (`>=2x` or `<=1/3x`), exclude it, move the starting bar back one completed bar, take the new consecutive five-bar window, recompute, and repeat until the starting bar is normal.
3. Then check the remaining four bars by the same abnormality criteria. Exclude abnormal ones, scan backward and replace with older normal completed bars until there are FIVE normal bars; recompute the final arithmetic mean of the five accepted ranges.
4. Log selected and rejected bar timestamps, range, comparison reference and reason. Strictly no future or unfinished bars.

**Not yet defined/tested:** the exact evolving reference ATR and convergence/replacement semantics when screening older bars. This detail is NOT supplied uniquely by the book or explicitly settled by the user. Write a deterministic proposal with worked numerical examples and tests before claiming implementation complete; do not silently invent it. Define insufficient-history and lookback bounds. The approved initial five-bar bootstrap itself IS resolved; do not reopen it unnecessarily.

## Implementation and evidence state
- Research contract/documentation updated through `752e439`; new filtered ATR(5) module and new seven-type classifier have NOT been verified as implemented by this checkpoint. Do not describe them as production-ready.
- Historical legacy raw-pivot/break-anchor counts are obsolete for Gerchik classification; no valid seven-type research result can be inferred from them.
- Proposed next sequence: finalize evolving-reference semantics; implement independent causal filtered ATR(5) module and fixtures; implement new Gerchik detector modules without importing archived prototypes; use K-Trader's internal D1/W1 history read-only for validation; record independent tests, human-reviewed examples and OOS results before any trading proposal.

## Operational safety
- **HP-OMEN is prohibited for ALL K-Trader uses**, including indirect K_AI/MT4 data, research, scripts, diagnostics, CI and backups. Do not touch it until explicit separate approval. Work only on independent K-Trader repo/server resources.
- No live trading, production deployment or application behavior changes authorized by this handoff. SentinelX host diagnostics only within existing constrained permissions.
- GitHub Actions quota previously exhausted through 2026-10-01; verify current status before treating unavailable CI as a software defect. Repository source updates do not prove CI passed.
- Preserve independent K-Trader source history and avoid any external archive contamination.

## New-chat prompt
```text
Віднови K-Trader із docs/operations/K_TRADER_NEW_CHAT_HANDOFF_2026-09-28_GERCHIK_ATR5.md у гілці research/dual-market-historical-levels-v0-1 (PR #88). Перевір актуальний branch HEAD, docs/CURRENT_STATE.md, docs/research/GERCHIK_FIXED_LEVEL_CLASSIFICATION_CONTRACT_V0_1.md та архів старих алгоритмів. Продовж дослідження нового семитипного класифікатора Герчика й окремого очищеного ATR(5). Не використовуй HP-OMEN, зовнішній AI_Trading_System/Sentinel архів, архівовані алгоритми чи продакшн. Спершу запропонуй детерміноване правило оновлення опорного ATR під час заміни решти чотирьох барів та перевір його на числових прикладах; далі реалізуй і протестуй у нових модулях.
```
