# 2026-09-11 — Candidate v2.2 Pre-Holdout Checkpoint

Status: RESEARCH ONLY / HOLDOUT UNTOUCHED / NO PRODUCTION CHANGE

## Frozen candidate

Candidate: `candidate_rule_set_v2_2`

Preregistered spec commit:
- `a2ff9f796cfbe3144135db55efc6c48a63deb2be`

Executable harness commit:
- `9abb05d88912293cee3c254dd427a7127ce5bcc7`

Runtime harness SHA256:
- `b8471af989090375dec9e25daae184814674a776ab9b46b45e660e35b368be08`

The candidate inherits v2.1 and adds one hard gate only:

`OPEN_SPACE OR next_confirmed_H1_level_R >= 3.0`

The H1 structural level detector uses causal 2-left/2-right pivots, pivot confirmation only after `k+2` closes, level clustering tolerance `0.20 * ATR14_H1`, and minimum two pivot touches per confirmed level.

## Important discovery-vs-executable nuance

The development-only discovery subset on already-resolved v2.1 trades selected 20/55 trades and showed:
- WR 55.0%
- expectancy +0.3175R
- PF_R 1.6632

The actual executable v2.2 development backtest produced 23 trades, not 20, because rejecting an earlier v2.1 trade frees position/episode capacity for later signals that were not present in the fixed v2.1 trade subset.

This path-dependence is expected and confirms that candidate evaluation must use the full executable backtest rather than only filtering an old trade list.

## Frozen executable results

### Development
- completed trades: 23
- WR: 47.83%
- expectancy_R: +0.1003R
- PF_R: 1.1818
- max DD: 4.5068R
- LONG/SHORT: 23 / 0

Exit reasons:
- STOP: 12, avg -1.0578R
- TARGET: 3, avg +2.9541R
- TIME_EXIT: 8, avg +0.7673R

### Validation
- completed trades: 10
- WR: 30.0%
- expectancy_R: +0.2507R
- PF_R: 1.3941
- max DD: 3.2375R
- LONG/SHORT: 8 / 2

Exit reasons:
- STOP: 6, avg -1.0531R
- TARGET: 3, avg +2.9557R
- TIME_EXIT: 1, -0.0416R

### Non-holdout
- completed trades: 37
- WR: 45.95%
- expectancy_R: +0.2888R
- PF_R: 1.5592
- max DD: 3.4383R
- LONG/SHORT: 34 / 3
- top symbol share: 16.22%

Exit reasons:
- STOP: 18, avg -1.0562R
- TARGET: 8, avg +2.9560R
- TIME_EXIT: 11, avg +0.5498R; 9/11 positive

### Stress slippage
- completed trades: 37
- WR: 43.24%
- expectancy_R: +0.2741R
- PF_R: 1.5235

## Artifacts

Pre-holdout report:
- `/data/research/phase11g/strategy_benchmark_v1/combined_rules/v2_2_preholdout_report.json`
- SHA256 `577debe6e6a8a4f1954ffd5b27e872ce971d2de2074783a0abe2e69e79747f8a`

Machine-readable candidate:
- `/data/research/phase11g/strategy_benchmark_v1/combined_rules/candidate_rule_set_v2_2.json`
- SHA256 `85e96f699e54d08a4795d50034fc40b2f69aea535ecf4b22b56ddfbb9417179b`

## Promotion gate

FAIL.

Reasons:
- `NON_HOLDOUT_SAMPLE_LT_100`
- `VALIDATION_SAMPLE_LT_30`
- `NON_HOLDOUT_WIN_RATE_LT_50`
- `VALIDATION_WIN_RATE_LT_50`

Therefore:
- `holdout_authorized = false`
- production approval = false
- no live rule change

## Diagnostics — not new rules

1. Economics improved versus v2.1 in the combined non-holdout sample, especially PF_R and expectancy_R, but the sample is only 37 resolved trades and validation is only 10 trades.
2. The 50% WR operating target is not met.
3. The selected trade set is highly LONG-concentrated (34/37 non-holdout). This must be treated as regime/selection concentration, not as proof that LONG should be preferred.
4. 35/37 non-holdout trades are tagged `OPEN_SPACE`; only two qualified via a confirmed H1 obstacle at >=3R. The current detector therefore behaves mostly as an open-space/new-extreme selector.
5. The 8h time exit is not currently shown to be harmful: 9/11 non-holdout time exits were positive, average +0.5498R. No max-hold change is justified from this sample.
6. Floating-zone, mirror-anchor, VSA, ATR-used and other legacy-derived features remain diagnostic/research-only.

## Evidence discipline

Current v2.2 non-holdout sample is in the `30–49 unique-family` diagnostic band. It is not sufficient for another hard-rule promotion.

Do not tune v2.2 against the same validation data. Any next version must be separately preregistered and require fresh OOS/prospective evidence.

## Recommended next step

Run v2.2 prospectively in research/shadow mode and accumulate new unique resolved setup families with full causal feature logging, including both eligible and rejected-near-miss cases.

Priority fields:
- structural-space pass/fail and nearest level distance in R;
- open-space vs bounded-space;
- side and market regime;
- H4/D1 alignment as features only;
- ATR-used / clean ATR5D as features only;
- VSA features as features only;
- MFE/MAE;
- time-to-target/time-to-stop/time-exit;
- realized R and costs.

No holdout opening and no production mutation until the promotion gate is satisfied.
