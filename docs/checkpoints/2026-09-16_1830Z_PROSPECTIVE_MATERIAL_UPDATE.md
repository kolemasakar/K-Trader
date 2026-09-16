# K-Trader checkpoint — 2026-09-16 18:30Z prospective material update

Status: ACCEPTED

## Scope

This checkpoint records the causal continuation after Sentinel Remote recovery and the first material prospective-state change after the accepted 16:30Z checkpoint.

Research branch: `research-strategy-benchmark-v1`

Frozen strategy: `candidate_rule_set_v2_2`

Frozen harness SHA256: `b8471af989090375dec9e25daae184814674a776ab9b46b45e660e35b368be08`

Protocol SHA256: `ba671cbed71fdc79380f37a72b75f93e75aa3ee895f5385ef433f497165de5a3`

Prereg boundary: `2026-09-16T13:00:00Z`

Holdout: `UNTOUCHED / NOT AUTHORIZED`

Production action: `false`

## Recovery continuity

Sentinel Remote incident was closed as recovered in its own repository and K-Trader resumed from:

- `RESUME_FROM=2026-09-16T17:15:00Z`
- `PRIOR_OUTCOMES=20260916T170000Z`

Causal pipeline v2 continuation completed through cutoffs:

- `17:15Z` PASS
- `17:30Z` PASS
- `17:45Z` PASS
- `18:00Z` PASS
- `18:15Z` PASS — material state change
- `18:30Z` PASS — material state stable

All cycles used resolver v1.3, canonical pipeline v2, frozen v2.2, unchanged prereg boundary, holdout false and production false.

## Production invariant

Latest verified production state during recovery continuation:

- host `k-trader-prod-vnic`
- deployed SHA `81b79b281a4cc330b7c11058d202e0d74fb6d70e`
- health `ok`
- mode `read_only`
- `data_ready=true`
- provider `binance_usdm`
- scanner `DEGRADED` remains the known fail-closed/history-readiness condition

No production deploy, restart, trading action, holdout opening, frozen-rule change or Phase 12 activation occurred.

## Accepted 18:30Z state

Run root:

`/data/research/phase11g/v2_2_shadow_20260916T183000Z`

Outcomes root:

`/data/research/phase11g/strategy_benchmark_v1/combined_rules/prospective_v2_2_outcomes_offline_v1_3/20260916T183000Z`

State manifest:

`/data/research/phase11g/strategy_benchmark_v1/combined_rules/current_state_manifests/20260916T183000Z.json`

State manifest SHA256:

`3eab4fa5d94808176db63bdcb5c2d266d01ffe041847612e2c5e0f6ef53b0341`

State:

- status `PASS`
- eligible observations `61`
- unique primary families `47`
- resolved primary families `47`
- unresolved primary families `0`
- current open families `0`
- wins/losses `13/34`
- win rate `27.659574%`
- expectancy `-0.5989123384630131R`
- evidence tier `DIAGNOSTIC_30_49_RESOLVED_FAMILIES`
- confirmation families `3`
- confirmation resolved `3`
- confirmation unresolved `0`

Phase 11G Path A remains incomplete: `47/100` resolved primary families, shortfall `53`.

## Material resolutions at 18:15Z

The four previously unresolved primary families all resolved by STOP:

- TRUMPUSDT SHORT `12:30Z` -> STOP, `-1.0660070957569756R` — discovery context
- ADAUSDT SHORT `13:15Z` -> STOP, `-1.0833591484214327R` — confirmation
- DOGEUSDT SHORT `13:15Z` -> STOP, `-1.075440314509089R` — confirmation
- ADAUSDT SHORT `15:00Z` -> STOP, `-1.1028235346941972R` — confirmation

This moved confirmation evidence from `3 families / 0 resolved` to `3 families / 3 resolved`.

The confirmation sample remains too small to authorize retuning or frozen-rule changes.

## 18:30Z capture and provenance

Capture:

- cycle status `VALID_SHADOW_CAPTURE`
- panel `19/19`
- eligible setups `49`
- event count `296`
- signal bars evaluated `6574`
- bundle export summary SHA256 `1313f96ff9ea9dacb19c9590ad44fea01c250bb650ea2bad70f65179e33f662c`
- event file SHA256 `6466ae36bb637adaf5329709c31e996fce706e3e720c043d7fa4229c8714c322`
- shadow summary SHA256 `e7efecddb39da4cbc578154ef9b770e2aaa89fdc9adf41b1f1fefd4e5a6dbd8a`

Funding:

- symbols `19`
- summary SHA256 `59b18c8d33c190b6a968f1c9ae767c05bc1097c00197f5371d0ccd2e3cdd50b2`

Resolver:

- outcomes summary SHA256 `672dffd2c05793f194b3b3a7c38a90d52326000073f92c38b3a4e6a7e6591b64`
- prior terminal reuse `61`
- current-path revalidated `51`
- source-window expired `10`
- max prior entry delta `0.0`
- max prior stop delta `5.68053737089267e-09`

Diagnostics:

- descriptive SHA256 `69ac3ff4142be71f86c9db537206cc6e876cfd034c644391d643641867ad5cc8`
- statistical SHA256 `a4446e873c89d03d5a8f2cf98d0ee65135d4fdcc4b1d38be0b01fde1f8c7527d`

Evidence:

- evidence report SHA256 `e1f6db64913dbff977dc2f93792fcad815ebf319a6d0f298ee66100f551e9a2b`
- discovery families `44`
- confirmation families `3`
- confirmation resolved `3`
- chronology/governance invariants PASS

Portfolio risk:

- report SHA256 `5fae672e7bc9301ed4ff2713a66586214938e8fe99b7160c98208e6b624eb98a`
- current open families `0`
- observed max concurrent all `8`
- observed max concurrent SHORT `8`
- largest correlated cohort `4`

Pipeline execute manifest SHA256:

`564d2a6118b956b260e73b56972a2b876015df94d4a8b8ef4dc8c2bba4734724`

State-manifest source hashes independently verified `5/5`, mismatches `0`.

## Governance decision

No strategy decision is authorized by this checkpoint.

- frozen v2.2 remains unchanged
- no RR/max-hold/filter/side/risk-gate retune
- holdout remains closed
- Phase 12 remains inactive
- production remains read-only
- broad strategy discovery remains delegated to `K_Investigation_Forecast`

## Resume point

Next causal cycle must use:

`PRIOR_OUTCOMES=/data/research/phase11g/strategy_benchmark_v1/combined_rules/prospective_v2_2_outcomes_offline_v1_3/20260916T183000Z`

Continue only at a fully closed M15 cutoff via canonical pipeline v2.
