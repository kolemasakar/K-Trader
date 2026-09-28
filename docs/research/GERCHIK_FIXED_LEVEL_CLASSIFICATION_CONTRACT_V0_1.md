# K-Trader: Gerchik fixed-level classification contract v0.1 (research only)

Sources: Alexander Gerchik, *Kurs aktivnogo treydera*, ch. 2 pp. 56-66 and ch. 9 pp. 207-213; user-supplied 12-page `1-1 Levels.pdf` pp. 2-11. This is a faithful classification specification, NOT a claim of completed automatic detectors or a trading-ready scoring engine.

## Strict source and causal constraints
- Generate candidate prices from **D1/W1 candle highs and lows** only; no close-derived level prices.
- Reject ordinary unqualified local D1 pivots. A confirmed structural event or one of the validated Gerchik patterns is required before admitting a level. Earlier break-anchor filter is only a BOS proxy, NOT full BOS/CHoCH.
- Require evidence known as-of classification time. A later confirmation cannot backdate tradable availability.
- Classify the **same level with multiple labels** when independently supported; do not duplicate its event merely because labels overlap.
- A pending/floating ('radioactive') zone is NOT a confirmed fixed level; no trading claims.
- D1 subsequent bars may test contacts with existing levels even if they do not source new levels. D1 OHLC does not reveal intraday touch order.
- No ATR for K-Trader level creation, zone geometry, clustering, anomaly detection, or ranking under existing project policy. The book's ch. 9 paranormal-bar criterion of >2 ATR conflicts with that policy: keep this detector BLOCKED pending explicit policy decision; the separate ch. 2 wording of >=2x average bar size is recorded as an alternative **not silently substituted** for the ch. 9 ATR rule.

## Fixed-level labels and confirmation evidence
1. TREND_BREAK: high/low at meaningful reversal and subsequent significant new swing high/low (perelou/perhigh). Distinguish genuine trend reversal from countertrend first technical pullback. Strongest base type in book, but must have several confirmations.
2. HISTORICAL: recurring same-price key structural points in visible history. Exact repetition at instrument tick precision; an unconfirmed candidate is weak/air, not a fixed level.
3. MIRROR: independently observed support-to-resistance or resistance-to-support role change at the same price, with confirmation.
4. LIMIT: >=3 consecutive hits at exactly the same tick-price without any penetration. If penetrated, demote to FLOATING/INVALID_LIMIT; later false breakout is separate evidence, not proof of unbroken limit.
5. PARANORMAL_BAR: two-end high/low candidates of a sufficiently anomalous bar; only confirmed with touches and false breakouts. Long wick and small body add evidence. Detector currently BLOCKED because book's >2 ATR variant conflicts with K-Trader no-ATR level rule; ch. 2 >=2x average bar size variant requires explicit approval of definition/window.
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
G3: settle paranormal bar ATR conflict with user before implementing detector.
G4: blinded human-labelled D1/W1 examples and independent review, then run full internal-history reanalysis. Previous 1,260 zones and 1,157 first contacts are **break-anchor-only** exploratory results and must not be represented as Gerchik-classified results.
G5: out-of-sample validation before using any significance signal in trading.
