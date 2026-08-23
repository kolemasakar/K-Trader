# VSA Specification v1.1

## Scope

Phase 6 implements deterministic K-Trader VSA v1 heuristics over confirmed closed contiguous candles.

These rules are project-specific operational definitions, not a claim that VSA has one universally accepted mathematical specification.

A VSA event is evidence, not a trade signal.

## Supported events

- `ND` - No Demand
- `NS` - No Supply
- `T` - Test
- `UT` - Upthrust
- `BC` - Buying Climax
- `SC` - Selling Climax
- `SV` - Stopping Volume

## Baseline

Canonical baseline uses the previous 20 closed bars and excludes the current bar.

Derived values:

- `relative_volume = current_volume / average_previous_20_volume`
- `relative_spread = current_(high-low) / average_previous_20_(high-low)`
- `close_location = (close-low)/(high-low)`

If the current bar has zero spread, close location is normalized to 0.5.

## Canonical raw-pattern rules

### NS

- down bar;
- relative spread <= 0.8;
- relative volume <= 0.8;
- current volume lower than each of the previous two bars;
- close location >= 0.5.

Direction evidence: LONG.

### ND

- up bar;
- relative spread <= 0.8;
- relative volume <= 0.8;
- current volume lower than each of the previous two bars;
- close location <= 0.5.

Direction evidence: SHORT.

### T

- low below the lows of the previous two bars;
- close location >= 0.60;
- relative spread <= 1.0;
- relative volume <= 1.0.

Direction evidence: LONG.

### UT

- high above the highs of the previous two bars;
- close location <= 0.35;
- relative spread >= 1.2;
- relative volume >= 1.2.

Direction evidence: SHORT.

### BC

- close >= open;
- relative spread >= 1.5;
- relative volume >= 1.8;
- close location <= 0.75.

Direction evidence: SHORT.

### SC

- close <= open;
- relative spread >= 1.5;
- relative volume >= 1.8;
- close location >= 0.25.

Direction evidence: LONG.

### SV

- close <= open;
- relative volume >= 1.5;
- relative spread <= 1.0;
- close location >= 0.5.

Direction evidence: LONG.

One bar may satisfy more than one raw evidence rule. The engine preserves every matching raw event rather than silently choosing one label.

## Context hard rules

Raw VSA evidence can become `CONFIRMED` only when all required context exists.

### LONG context

Applicable raw types: `NS`, `T`, `SC`, `SV`.

Required:

- MTF regime = `BULLISH`;
- confirmed/mirror SUPPORT level near the event;
- event-to-level maximum distance <= `0.25 * ATR14` unless the candle overlaps the level zone;
- confirmation within the next 2 closed bars: close above the VSA event high.

### SHORT context

Applicable raw types: `ND`, `UT`, `BC`.

Required:

- MTF regime = `BEARISH`;
- confirmed/mirror RESISTANCE level near the event;
- event-to-level maximum distance <= `0.25 * ATR14` unless the candle overlaps the level zone;
- confirmation within the next 2 closed bars: close below the VSA event low.

## Context states

- `RAW`: pattern geometry only.
- `IGNORED`: wrong HTF context or no confirmed level location.
- `VALID_CONTEXT`: level/regime valid, confirmation not yet present.
- `CONFIRMED`: pattern + location + HTF context + next-bar confirmation are all valid.

`VALID_CONTEXT` is not a trade signal.

## Trap confluence

A confirmed trap may be attached as additional confluence only when it matches:

- provider;
- symbol;
- direction;
- the same reference level;
- and trap confirmation occurred no later than the VSA event.

Trap confluence is not mandatory for every VSA confirmation and does not by itself create a trade signal.

## Provider capabilities

Phase 6 canonical detection requires normalized OHLCV only.

Quote volume, trade count and taker-buy fields may be used by future versioned extensions but are not fabricated when unavailable and are not required by the v1 pattern detector.

## Output

Each `VSAEvent` records:

- type
- provider / symbol / timeframe
- bar index / timestamp
- LONG/SHORT evidence direction
- relative volume
- relative candle spread
- close location
- raw quality label
- context status
- confirmed flag
- reference level id
- trap-confluence flag
- reasons
- invalidation reason

## Phase boundary

Phase 6 does not assign Setup Score points or A/A+/B/C ratings. Phase 7 consumes confirmed/raw evidence and applies the scoring/rating policy.
