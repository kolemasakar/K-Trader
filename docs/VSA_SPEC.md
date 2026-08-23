# VSA Specification v1.0

## Supported events

- ND: No Demand
- NS: No Supply
- T: Test
- UT: Upthrust
- BC: Buying Climax
- SC: Selling Climax
- SV: Stopping Volume

## Core rule

A VSA event is evidence, not a trade signal.

## Long context

Potentially valid only when VSA supports bullish context, e.g. NS/T/SC near confirmed support with HTF context and confirmation.

## Short context

Potentially valid only when VSA supports bearish context, e.g. ND/UT/BC near confirmed resistance with HTF context and confirmation.

## Ignore rule

A pattern in the middle of an unqualified range or without valid location/context/confirmation is ignored.

## Inputs

VSA may use:
- spread/range
- body and close location
- relative volume
- quote volume where available
- trade count where available
- taker-buy ratios where available
- prior bar sequence
- confirmed level proximity
- trap state
- trend/market regime

Provider capability differences must be explicit. The engine SHALL NOT fabricate unavailable order-flow fields.

## Output

Each event records:
- type
- symbol/provider
- timeframe
- bar timestamp
- confidence/quality score
- location context
- confirmation state
- reasons
- invalidation reason when ignored
