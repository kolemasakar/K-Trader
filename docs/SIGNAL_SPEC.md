# Signal Specification v1.0

## Purpose

Define the canonical structured result consumed by the API and Custom GPT.

## Required fields

- provider_id
- exchange
- canonical_symbol
- provider_symbol
- market_type
- side: LONG | SHORT | NO_TRADE
- grade: A+ | A | B | C | null
- setup_score: 0..100 | null
- setup_type
- market_regime
- trend_context
- entry
- stop
- target
- rr
- atr5d
- atr_used_pct
- trap_state
- vsa_events
- level_refs
- reason_codes
- data_time
- last_closed_bar
- data_age_seconds
- freshness_status
- generated_at
- engine_version

## Optional fields

- position_size
- risk_amount
- estimated_probability

These remain null/N/A unless all prerequisites are confirmed.

## NO TRADE

For NO_TRADE or insufficient confirmed data:
- entry/stop/target may be null;
- grade/score may be null when analysis cannot be completed;
- reason_codes are mandatory;
- source/freshness metadata remain mandatory when data was queried.

## Signal eligibility

A LONG/SHORT tradable signal requires all hard filters to pass and grade A or A+.
