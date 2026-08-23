# Scoring Specification v1.1

## Principle

K-Trader v1 exposes deterministic `Setup Score` 0..100.

`Setup Score` is a rule-based quality rating. It is not statistical win probability.

Hard rejects are evaluated independently from the numeric score and always override it.

## Canonical weights

Maximum total = 100.

- market regime: 20
- liquidity: 10
- session: 5
- confirmed trap: 15
- MTF primary level: 15
- HTF strength: 10
- confirmed VSA: 15
- ATR state: 5
- RR: 5

## Component rules

### Market regime

- candidate direction matches canonical MTF regime -> 20
- otherwise -> 0 and hard reject

### Liquidity

Using `liquidity_rank / universe_size`:

- top 20% -> 10
- top 50% -> 7
- remainder of valid universe -> 4
- invalid/non-positive liquidity context -> 0 and hard reject

### Session

Crypto remains 24/7. Session is context only.

- overlapping configured sessions -> 5
- one active configured session -> 3
- none -> 0

No session state can independently permit or reject a trade.

### Trap

- confirmed trap for same provider/symbol/direction/primary level -> 15
- otherwise -> 0

If a candidate declares trap evidence but that evidence is unconfirmed or mismatched, hard reject.

### MTF primary level

Diagnostic component:

- STRONG -> 15
- MODERATE -> 10
- WEAK -> 4

Tradable Phase 7 setup requires a STRONG active CONFIRMED/MIRROR primary level. Anything weaker is a hard reject regardless of points.

### HTF strength

Use the weaker evidence count of the HTF pair that establishes direction:

- `1d + 4h` when both establish direction;
- otherwise `4h + 1h` when both establish direction.

Classification:

- STRONG -> 10
- MODERATE -> 6
- WEAK -> 2

### VSA

- confirmed VSA for same provider/symbol/direction/primary level -> 15
- otherwise -> 0

If a candidate declares VSA evidence but it is not context-confirmed or identity-matched, hard reject.

### ATR

- ATR used <40% -> 5
- 40..80% inclusive -> 3
- >80% -> 0 and hard reject

### RR

- RR >=4 -> 5
- 3 <= RR <4 -> 3
- RR <3 -> 0 and hard reject

## Rating thresholds

- A+: 90..100
- A: 80..89
- B: 70..79
- C: 0..69

Only A+ and A may emit LONG/SHORT.

B/C always emit `NO_TRADE`.

## Hard reject handling

Canonical hard rejects include at minimum:

- stale data;
- invalid liquidity context;
- HTF context mismatch;
- primary level not active/confirmed;
- primary level not STRONG;
- no confirmed setup evidence;
- setup-type/evidence mismatch;
- trap/VSA identity mismatch;
- missing price tick;
- missing confirmation;
- invalid geometry;
- no confirmed structural target;
- ATR used >80%;
- RR <3;
- invalid explicit risk context;
- explicit account sizing below minimum quantity step.

For audit, engine retains `raw_score` before hard-reject override.

Canonical public `setup_score` is capped at 69 when any hard reject exists and grade is forced to C.

This prevents a rejected setup from appearing as A/A+ only because other components were strong.

## Future probability

`estimated_probability = N/A` until a statistically calibrated model is built from confirmed historical signals and outcomes.
