# Signal Specification v1.1

## Purpose

Define the canonical structured Trading Engine result consumed later by the API and Custom GPT.

## Required fields

- provider_id
- exchange
- canonical_symbol
- provider_symbol
- market_type
- side: LONG | SHORT | NO_TRADE
- grade: A+ | A | B | C
- setup_score: 0..100
- raw_score: 0..100
- setup_type
- market_regime
- trend_context
- liquidity_rank
- liquidity_score
- sessions
- session_overlap
- strength
- primary_level_id
- primary_level_strength
- trap_state
- vsa_events
- entry
- luft
- stop
- target
- rr
- atr5d
- atr_used_pct
- atr_state
- position_size
- risk_amount
- risk_percent
- reason_codes
- data_time
- last_closed_bar
- data_age_seconds
- freshness_status
- generated_at
- engine_version

## Probability

`estimated_probability` remains N/A/null in v1.

Setup Score must never be presented as statistical probability.

## Tradable output

LONG/SHORT requires:

- all hard filters pass;
- final grade A or A+;
- structural Entry/SL/TP geometry is complete.

## NO_TRADE

For NO_TRADE:

- Entry/Luft/SL/TP are null in public decision output;
- reason_codes are mandatory;
- RR/ATR diagnostics may remain available if they were validly calculated before rejection;
- source/freshness metadata remain mandatory.

B/C always result in NO_TRADE.

Any hard reject forces final grade C and public setup_score <=69. `raw_score` remains available for audit/ranking diagnostics only.

## Position size

Position size/risk fields are null unless explicit confirmed account/risk/instrument quantity-value inputs are supplied.

No account state is inferred from public exchange market data.
