# K-Trader: Gerchik fixed-level classification contract v0.1 (research only)

Sources: Alexander Gerchik, *Kurs aktivnogo treydera*, ch. 2 pp. 56-66 and ch. 9 pp. 207-213; user-supplied 12-page `1-1 Levels.pdf` pp. 2-11. This is a faithful classification specification, NOT a claim of completed automatic detectors or a trading-ready scoring engine.

## Strict source and causal constraints
- Generate candidate prices from **D1/W1 candle highs and lows** only; no close-derived level prices.
- Reject ordinary unqualified local D1 pivots. A confirmed structural event or one of the validated Gerchik patterns is required before admitting a level. Earlier break-anchor filter is only a BOS proxy, NOT full BOS/CHoCH.
- Require evidence known as-of classification time. A later confirmation cannot backdate tradable availability.
- Assign exactly ONE primary fixed-level type to each level, based on the pattern that established it. Any later overlapping pattern is recorded only as additional strengthening evidence, NOT a second primary type or a second independent level. Preserve evidence timestamps and provenance.
- A pending/floating ('radioactive') zone is NOT a confirmed fixed level; no trading claims.
- D1 subsequent bars may test contacts with existing levels even if they do not source new levels. D1 OHLC does not reveal intraday touch order.
- ATR remains DISABLED for level identification, zone geometry and level significance as an algorithm simplification explicitly chosen by the user. This is NOT a conceptual incompatibility: historical ATR can legitimately describe an abnormal candle for level identification, whereas estimating future movement potential is a distinct task. Do not confuse the two. For now, paranormal-bar detection must use a separately approved non-ATR rule (the book also describes >=2x average bar size), with its reference window documented; otherwise remain PENDING. In normal stable volatility ATR(5) is a useful near-proxy for typical bar size, but its use for level construction remains deliberately disabled.

## Fixed-level labels and confirmation evidence
1. TREND_BREAK: high/low at meaningful reversal and subsequent significant new swing high/low (perelou/perhigh). Distinguish genuine trend reversal from countertrend first technical pullback. Strongest base type in book, but must have several confirmations.
2. HISTORICAL: recurring same-price key structural points in visible history. Exact repetition at instrument tick precision; an unconfirmed candidate is weak/air, not a fixed level.
3. MIRROR: independently observed support-to-resistance or resistance-to-support role change at the same price, with confirmation.
4. LIMIT: >=3 consecutive hits at exactly the same tick-price without any penetration. If penetrated, demote to FLOATING/INVALID_LIMIT; later false breakout is separate evidence, not proof of unbroken limit.
5. PARANORMAL_BAR: two-end high/low candidates of a sufficiently anomalous bar; only confirmed with touches and false breakouts. Long wick and small body add evidence. Detector PENDING: user intentionally retains no-ATR implementation for simplicity, although ATR is conceptually admissible for level formation. The non-ATR >=2x average-bar-size variant requires an explicit averaging-window definition.
6. CONSOLIDATION: >=3 bars consolidating strictly on ONE side above/below a candidate level; require confirming touches/false breaks. Straddling price is FLOATING, not confirmed consolidation.
7. GAP: both boundaries of genuine open trading gap are candidate levels requiring confirmation; market-session awareness mandatory (crypto trades 24/7 and not every discontinuity is a real session gap).

## Significance and evidence (NO invented author numeric weights)
Book's base order ch. 9: trend break, mirror, historical, false breakout, limit, consolidation, paranormal bar, gap. The requested seven labels omit 'false breakout' as a separate type: store it as a cross-cutting evidence event instead. Book also states historical comparable to mirror, and a mirror can in particular circumstances exceed a trend-break level. Therefore base type ordering must NOT be treated as a fixed global score or override context.
- First practical selection criterion in ch. 9: level nearest the critical decision point; next: maximum confirmed touches; false breakout strengthens.
- Track touch count, near-miss count, false breakout count, significant new extreme after reversal, wick-to-body evidence, round-price proximity, D1/W1 timeframe provenance, exact tick-price identity, confirmation timestamps, source event IDs, and invalidation state.
- User excerpt mentions ~20% strengthening by round numbers, but no universal additive score formula; record as a qualitative factor, not numeric 20-point or 20% multiplicative scoring without calibration.
- Never infer intent/actual limit orders from OHLC alone: names are price-action patterns, not order-book proof.
- Preserve source disagreement: ch. 2 orders historical then mirror, while ch. 9 orders mirror then historical and explicitly calls their strength comparable. No arbitrary tie-break.

## Implementation gates
G1: exact tick-size and exchange/session metadata; confirm BOS/CHoCH and meaningful swing/pullback semantics.
G2: causal historical, mirror, limit, consolidation, gap pattern detectors and provenance tests.
G3: implement paranormal bar using a documented, separately approved non-ATR average-bar baseline; keep ATR disabled for level construction by user choice.
G4: blinded human-labelled D1/W1 examples and independent review, then run full internal-history reanalysis. Previous 1,260 zones and 1,157 first contacts are **break-anchor-only** exploratory results and must not be represented as Gerchik-classified results.
G5: out-of-sample validation before using any significance signal in trading.

## Supersession (2026-09-28)
The user supersedes all previous research level-selection and contact-analysis algorithms. Previous raw-pivot, break-anchor-only, close-based, gradient and first-contact prototypes are ARCHIVED / NON-AUTHORITATIVE; their counts must not enter new classification or significance decisions. New classifier contract: ONE primary Gerchik type per level, additional overlapping patterns only as strengthening features. Do not reactivate archived algorithms without new explicit authorization. Source/ATR nuance above is binding.

## Clarification: classification and strengthening
A level has ONE primary type determined by its formation event. Later qualifying events from other Gerchik categories do not relabel it as multiple independent primary types; they are additional **strengthening features** with provenance, not new level identities. Do not double-count touches or source extrema shared by strengthening patterns.

## Volatility-transition rule withdrawn
By user instruction, the proposed no-trade/no-analysis exclusion during changing volatility is CANCELLED and must not be implemented as a gate. No ATR(5) transition threshold is needed. Existing choice to avoid ATR in level creation remains unchanged. This cancellation does not assert that any volatility regime is inherently safe to trade.

## APPROVED: Gerchik manually filtered daily ATR(5) (2026-09-28)
User explicitly approves the source-described **separate ATR calculation** (not the previously cancelled volatility-transition trading exclusion). On D1 use 5 **completed normal bars** from previous trading sessions, excluding the current incomplete day. For each, range = High - Low. Exclude abnormal bars with range >= 2 x the applicable reference ATR or <= 1/3 x that ATR; replace each excluded candidate with the nearest earlier eligible completed normal session bar until five eligible bars are collected; arithmetic mean of five ranges is the manually filtered ATR(5). No abnormal bars enter the final average. Do not substitute platform default ATR, which does not exclude abnormal bars. A 3–5 session choice is described in the source; project selection is 5.

**Open implementation detail, not claimed to be specified by the book:** determining the initial reference ATR before exclusion is circular. Implementer must explicitly define and separately validate a causal bootstrap/reference procedure (e.g., an earlier completed baseline), a deterministic historical lookback limit and insufficient-history outcome. Do not silently treat a proposed bootstrap as Gerchik's own formula, and do not run production on an undefined bootstrap. Exact thresholds >=2 and <=1/3 are sourced from the book's ATR chapter; other informal training material sometimes states different bounds and must not override this approved source.

**Scope separation:** approval authorizes a dedicated manually filtered ATR(5) module and the abnormal-bar exclusion within its calculation. The existing simplified Gerchik **level creation** path still does NOT consume ATR unless separately approved; a bar excluded from the ATR average is not automatically excluded from structural level formation. The earlier volatility-transition no-trade/no-analysis gate remains CANCELLED. All superseded level research algorithms remain ARCHIVED and disabled. This approval does not authorize live trading or production changes.

## User-defined initial ATR sampling order (2026-09-28)
The initial ATR(5) reference must be constructed in **reverse chronological order from completed D1 bars**: first inspect the most recently closed bar (offset 0), then the immediately preceding closed bar (offset 1), then offset 2, and so on backward. The current incomplete bar is excluded. Continue scanning backward when a bar is excluded until five eligible completed bars have been selected. Calculate the arithmetic mean of selected High-Low ranges, as approved.

**Implementation caution:** the user specified sampling order, not the mathematical rule for judging the very first bar as abnormal when no pre-existing reference is available. Do not invent a self-referential threshold or claim the book resolves this initialization. Mark initial abnormality reference as a separately testable implementation detail before running the filtered historical calculation. No ATR for level construction; previous level algorithms stay archived; cancelled volatility-transition gate stays cancelled.
