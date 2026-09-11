# Checkpoint — Level Context v2.2 + MFE/MAE Stage 3

Date: 2026-09-11
Branch: `research-strategy-benchmark-v1`
Status: RESEARCH CHECKPOINT / HOLDOUT UNTOUCHED / NO PRODUCTION CHANGE

## Frozen candidate

`candidate_rule_set_v2_2` remains frozen.

Unchanged preholdout metrics:
- development: 23 trades, WR 47.83%, expectancy +0.1003R, PF_R 1.1818;
- validation: 10 trades, WR 30.00%, expectancy +0.2507R, PF_R 1.3941;
- non-holdout: 37 trades, WR 45.95%, expectancy +0.2888R, PF_R 1.5592;
- stress: expectancy +0.2741R, PF_R 1.5235.

Promotion gate remains FAILED. Holdout remains unauthorized/unopened.

## Completed diagnostics

### Level Context v2.1
- strict confirmed-level break remained universal and is not a useful binary discriminator;
- H1 open-space remains a strong development/non-holdout hypothesis but validation is too small;
- binary broken-level revisit showed a negative association that is not explained simply by later invalidation.

### Level Context v2.2 traversal
- clean break with zero revisit episodes is the clearest structural hypothesis;
- non-holdout zero-revisit: n=11, WR 72.73%, expectancy +1.017R, PF_R 4.471;
- one revisit: n=13, expectancy -0.219R;
- validation zero-revisit is only n=2 and therefore not sufficient for promotion;
- crossing count and wrong-side closes are not stable enough to prioritize as gates.

Traversal report SHA256:
`96c47133cf10d1da8418a5f899faba9ea1902f153d5f067ceeebfec741b1a6b1`

### MFE/MAE Stage 2
- 13/18 non-holdout STOP trades never reached +0.5R;
- TARGET median time-to-3R = 13.5 M15 bars;
- TIME_EXIT = 11, positive = 9, median giveback = 0.719R.

Stage 2 report SHA256:
`36f09c7bb8b99198729eddbb9f1ffb45c889897a925f687921135f72977a5bb3`

### MFE/MAE Stage 3
Non-holdout TARGET n=8:
- median MFE after 1/2/4/8 bars = 0.645R / 1.093R / 1.940R / 2.128R;
- +0.5R by 4 bars = 8/8;
- +1R by 4 bars = 7/8.

Non-holdout STOP n=18:
- median MFE after 1/2/4/8 bars = 0.168R / 0.278R / 0.300R / 0.355R;
- +0.5R by 4 bars = 4/18;
- +1R by 4 bars = 1/18.

TIME_EXIT remains a slower middle population; do not introduce a 4-bar hard exit from the current evidence.

Stage 3 report SHA256:
`7dbda865505635e923376ae5370b1b657f4196bc7fe5b85e1d98b649cc75e4e1`

## Methodological decision

Existing validation has now been inspected repeatedly for diagnostics and must not be represented as fresh independent evidence for any new rule derived from these studies.

Any candidate based on:
- clean-break/no-revisit;
- early favorable progress;
- MFE profit protection;

must be a new version and rely on fresh prospective/OOS evidence for validation.

## Production state

No production changes made. Existing deployed read-only runtime remains separate from this research branch.

## Next research action

Build prospective/shadow feature capture for:
- clean-break/revisit lifecycle fields;
- early MFE checkpoints at 1/2/4/8 M15 bars;
- MFE peak age and giveback;
- unique setup-family identity and exact strategy/data hashes.

Do not change frozen v2.2 execution while collecting these observations.
