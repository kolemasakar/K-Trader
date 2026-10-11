# S1–S6 restoration matrix — 2026-10-04
Status: PRIMARY OWNER-APPROVED IDENTITIES RECOVERED / CURRENT EXECUTABLE PORT NOT FROZEN.

This records independently observed sources, not a newly approved mapping. The draft catalogue at research HEAD fe5ec24 and the 2026-09-25 historical plan use different IDs. Neither a historical implementation nor an assistant draft can establish the owner's intended current strategy identities by itself.

| ID | Historical plan 2026-09-25 | Active draft catalogue 2026-10-02 | Current restoration status |
|---|---|---|---|
| S1 | Prior D1/W1 rejection | First approach/rejection | Family agrees; exact trigger, stop, confirmation pending |
| S2 | Breakout continuation | Breakout + retest | ID conflict |
| S3 | Breakout + retest | False breakout + return | ID conflict; owner's SL beyond level remains binding |
| S4 | One-bar false breakout | Range boundary reaction | ID conflict |
| S5 | Multi-bar false breakout, 2–5 closed bars | Trend continuation pullback | ID conflict |
| S6 | Trend/range control family | Historical H1 breakout reference | Source code recovered; current level integration not compliant |

Historical plan pinned at 73a24b32dc2000686a5ceafcb3cd2a955d050163:
`docs/research/PHASE11G_HISTORY_FIRST_LEVEL_STRATEGY_PLAN_20260925.md`.
Active catalogue pinned at fe5ec24fc1fcbe44e06ebfd13fdf71ad646a3906:
`docs/research/GERCHIK_RESEARCH_STRATEGY_CATALOG_DRAFT_V0_1.md`.

## Independently recovered server evidence
Read only the existing K-Trader-owned cohort; no K_AI/MT4 access.
Root: /data/research/phase11g/historical_recovery_v1/approved_seven_year_20260925.
Source byte hashes are recorded in `GERCHIK_STRATEGY_SOURCE_HASHES_2026-10-04.json`.

- strategy_approval_v1.json: USER_APPROVED, dated 2026-09-25, all S1–S6, S3 stop behind broken level. Its historical ±0.15 ATR14 buffer and >=2R rule are implementation-era records, not a replacement for latest ATR5 v2 / 1R then 3R decisions.
- backtests_approved_six_v1/exploratory_summary.json: EXPLORATORY_IN_SAMPLE_ONLY; initial S1–S5 simplified and explicitly require user-reviewed formal specifications. Next H1 open; 12-bar horizon; 0.12% roundtrip cost proxy; no funding. This summary is not an executable specification or realistic cost validation.
- s6_reproducible_offline_v1/s6_offline_reproduce.py: H1 close beyond previous 20 highs/lows, EMA50 (alpha 2/51), level proximity <= H1 mean TR14, next H1 open, stop beyond 6-bar extreme plus 0.15 H1 mean TR14, 12-bar signal embargo. Historical sensitivity evaluated 1/2/3R and 6/12/24/48-hour holding windows.
- Old S6 uses ATR14-based pivot grouping, zone width and level strength. Those upstream algorithms are superseded and must not be imported into the current no-ATR Gerchik level engine.
- Old S6 labels its late segment previously_inspected_holdout. Never rebrand it untouched. No late-segment outcomes were recomputed in this audit.

## Binding current constraints
D1/W1 High/Low-based confirmed levels and equal-significance symmetric zones; no ATR in formation, geometry or strength. M5/M15 entry-model precision is distinct from contextual tolerance. Canonical iterative ATR5 v2, experimental v3 separate. S3 technical SL beyond level. Study 1R first, then 3R; no mandatory 2R stage.

## Minimum missing information
A single authoritative executable mapping for S1–S6 with precise triggers and confirmations. Freeze percentage-price/time anchor, instrument tick rounding, entry-model precision, SL buffer and horizons explicitly. Forex point definition only blocks Forex implementation; crypto data inventory proceeds independently. Real historical costs/funding and a demonstrably uninspected independent control dataset remain separate requirements.

## Primary owner approval recovered after the first inventory
Personal Context retrieval returned the original assistant specification at 2026-09-25T17:54:51Z and owner's approval at 2026-09-25T18:01:55Z in «16 PH-11». These retrieved primary interaction excerpts resolve the strategy ID dispute; the conflicting active draft is corrected. Retrieval is an excerpted context record, not a downloaded full conversation export.

| ID | Restored owner-approved family | Historical specification excerpt |
|---|---|---|
| S1 | Відбій від рівня | Touch plus confirmation; SL beyond reaction extreme plus 0.15 ATR; target 2R or nearer opposite level |
| S2 | Пробій із продовженням | Close beyond level >=0.15 ATR plus confirmation; SL beyond level with 0.15 ATR buffer |
| S3 | Пробій і повторне тестування | Return to level within 6 candles and resumed movement; owner changes SL to beyond level |
| S4 | Одинарний хибний пробій | One candle penetrates >=0.15 ATR and closes back into prior range; SL beyond false-break extreme |
| S5 | Багатобарний хибний пробій | 2–4 consecutive candles beyond level then return; allow structures up to 6 candles; SL beyond furthest structure extreme |
| S6 | Трендовий вихід із діапазону | Break past prior 20 completed candle highs/lows in EMA50 direction; SL local extreme or 1.5 ATR; trailing sensitivity separate |

Historical common profile: H1 signals, additional M15/M30/H4; ATR14; daily/weekly prior completed period extrema; 0.15 ATR tolerance; 2R; <=12-hour H1 holding. Later binding decisions supersede old ATR-based level geometry and the mandatory 2R target. Preserve historical identity and trigger provenance; do not quietly convert every 0.15 ATR14 coefficient to 0.15 daily ATR5, as scale/timeframe differ.

Remaining formalization: precise confirmation predicates for S1–S3, tick and entry-tolerance semantics, S5 2–4 baseline versus up-to-6 variant, S6 local-stop/trailing branch rules; reconcile H1 research profile with separately approved M5/M15 intraday execution model. Mandatory current upstream: confirmed Gerchik D1/W1 ledger, not all prior daily highs/lows or archived pivot clusters. Keep numerical migration proposed explicitly and frozen before outcome testing.
