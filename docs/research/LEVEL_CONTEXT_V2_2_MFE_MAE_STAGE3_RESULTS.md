# Level Context v2.2 + MFE/MAE Stage 3 — Results

Date: 2026-09-11
Status: DIAGNOSTIC COMPLETE / NO STRATEGY CHANGE / HOLDOUT UNTOUCHED

## Boundary

Frozen `candidate_rule_set_v2_2` was not modified. Production, risk, SL, TP, RR, max-hold and deployment semantics remain unchanged. Holdout remains unopened.

## Artifacts

- traversal report: `/data/research/phase11g/strategy_benchmark_v1/combined_rules/level_context_v2_2_traversal/report.json`
- SHA256: `96c47133cf10d1da8418a5f899faba9ea1902f153d5f067ceeebfec741b1a6b1`

- MFE/MAE Stage 3 report: `/data/research/phase11g/strategy_benchmark_v1/combined_rules/mfe_mae_v2_2_stage3/report.json`
- SHA256: `7dbda865505635e923376ae5370b1b657f4196bc7fe5b85e1d98b649cc75e4e1`

## 1. Broken-level traversal lifecycle

The cleanest structural discriminator is not raw zone-crossing count and not wrong-side closes. It is whether the broken H1 level was revisited at all before entry.

### No revisit episode

Development:
- n=9;
- WR 66.67%;
- expectancy `+0.588R`;
- PF_R `2.641`.

Validation:
- n=2;
- WR 100%;
- expectancy `+2.949R`.

Combined non-holdout:
- n=11;
- WR 72.73%;
- expectancy `+1.017R`;
- PF_R `4.471`.

### One revisit episode

Development:
- n=7;
- expectancy `-0.221R`.

Validation:
- n=5;
- expectancy `-0.259R`.

Combined non-holdout:
- n=13;
- expectancy `-0.219R`.

### Two or more revisit episodes

Development and validation are negative, but combined non-holdout becomes mildly positive because later-period observations differ. Therefore the relationship is not monotonic enough to promote a numeric revisit-count threshold.

### Interpretation

The most promising concept is **clean break continuation with no broken-level revisit before entry**. This is more precise than the previous `mirror/retest` label and is directionally consistent across development and validation, but validation has only two clean cases.

Keep as a prospective feature/hypothesis only. Do not promote to a hard gate.

Zone crossings and wrong-side closes were not stable discriminators. Do not prioritize them for promotion.

## 2. MFE/MAE Stage 3 — early progress

A strong descriptive separation appears in the first four M15 bars after entry.

### TARGET trades, non-holdout (n=8)

- median MFE after 1 bar: `0.645R`;
- after 2 bars: `1.093R`;
- after 4 bars: `1.940R`;
- after 8 bars: `2.128R`;
- reached +0.5R by 4 bars: `8/8`;
- reached +1R by 4 bars: `7/8`.

Validation TARGET trades also show +0.5R by 4 bars in `3/3` and +1R by 4 bars in `3/3`.

### STOP trades, non-holdout (n=18)

- median MFE after 1 bar: `0.168R`;
- after 2 bars: `0.278R`;
- after 4 bars: `0.300R`;
- after 8 bars: `0.355R`;
- reached +0.5R by 4 bars: `4/18`;
- reached +1R by 4 bars: `1/18`.

Validation STOP trades reached +0.5R by 4 bars in `0/6`.

### TIME_EXIT trades, non-holdout (n=11)

- median MFE after 4 bars: `0.373R`;
- after 8 bars: `0.654R`;
- +0.5R by 4 bars: `4/11`;
- +1R by 4 bars: `3/11`;
- median peak MFE occurs about `19` bars before exit;
- median peak-to-terminal giveback: `0.719R`.

This confirms that TIME_EXIT trades are a distinct middle population: slower than TARGET winners, but often ultimately profitable.

## 3. Interpretation

The Stage 3 result supports two separate future hypotheses:

1. **pre-entry structural quality:** clean break / no broken-level revisit before entry;
2. **post-entry progress state:** high-quality 3R winners usually demonstrate meaningful favorable excursion during the first four M15 bars.

These must not be merged into an optimized rule using the already inspected validation sample.

In particular, `+0.5R by 4 bars` is NOT approved as an exit rule. Applying it mechanically could discard slower but profitable TIME_EXIT trades. Any early-progress management rule must be a new preregistered version evaluated on fresh prospective/OOS data.

## 4. Next research direction

Without altering v2.2:

- add `clean_break_no_revisit` and traversal fields to future shadow/prospective feature capture;
- add early MFE checkpoints (1/2/4/8 M15 bars) to future outcome capture;
- keep current 8h max-hold unchanged;
- accumulate fresh resolved setup families before considering a new candidate;
- treat existing validation as already inspected and unavailable for further tuning claims.

## Promotion status

Unchanged:
- v2.2 promotion gate: FAILED;
- holdout: UNOPENED;
- production: unchanged / read-only.
