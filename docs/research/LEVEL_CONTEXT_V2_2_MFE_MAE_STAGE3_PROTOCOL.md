# Level Context v2.2 + MFE/MAE Stage 3 — Diagnostic Protocol

Date: 2026-09-11
Status: PREREGISTERED DIAGNOSTIC / NO STRATEGY CHANGE / HOLDOUT UNTOUCHED

## Boundary

Frozen `candidate_rule_set_v2_2` remains unchanged. This stage only measures behavior on the already generated development, validation and combined non-holdout trade paths.

No output from this stage may retroactively authorize v2.2 promotion or holdout access.

## A. Broken-level traversal lifecycle

Stage 2 showed that the binary `strict_mirror_retest_present` label is associated with weaker outcomes but does not behave like a simple failed mirror. Stage 3 therefore removes the semantic assumption and measures traversal directly.

For the most recent strict confirmed-level break already identified causally by Level Context v2.1, record from the break bar through the decision bar:

- `revisit_episode_count`: number of distinct H1 bar episodes whose ranges intersect the broken-level zone;
- `first_revisit_delay_bars`;
- `last_revisit_age_bars`;
- `zone_crossing_count`: number of changes between closes clearly above and clearly below the level zone, ignoring closes inside the zone;
- `breakout_side_close_fraction`: fraction of post-break closed H1 bars that close on the breakout side of the raw level;
- `wrong_side_close_count`: closes beyond the opposite side of the level tolerance;
- `any_wrong_side_close`;
- `entry_distance_to_broken_level_R`.

The level zone remains the already frozen Level Context v2 tolerance (`0.25 * H1 ATR14` at decision time). No new eligibility threshold is introduced.

Predeclared descriptive buckets:

- revisit episodes: `0`, `1`, `>=2`;
- zone crossings: `0`, `1`, `>=2`;
- wrong-side close: `False/True`.

Purpose: distinguish clean continuation after a break from repeated traversal/chop without labeling either as a hard gate.

## B. MFE/MAE Stage 3 time profile

Use only actual v2.2 trade paths. Preserve the Stage 1 rule: full high/low information from the exit-event bar is not inspected; only the known terminal execution event is used.

For each trade record:

- peak MFE and its bar index;
- bars from peak MFE to exit;
- favorable excursion available within the first `1`, `2`, `4`, and `8` M15 bars;
- whether +0.5R and +1R were reached within those early windows;
- directional close-R at `4`, `8`, and `12` bars before exit when available;
- terminal change from each of those checkpoints to executed exit;
- peak-to-terminal giveback in R;
- gross terminal R after adding explicit fee/funding R back to net realized R.

This stage is descriptive. It does not define an early-failure exit, break-even rule, trailing stop, or profit-protection threshold.

## Interpretation policy

- Development may suggest a future hypothesis.
- Validation is not reused as a tuning surface.
- Any trade-management rule must be a separately preregistered strategy version and validated on fresh prospective/OOS data.
- Small subgroups remain descriptive regardless of apparent performance.

## Expected outputs

- `combined_rules/level_context_v2_2_traversal/report.json`
- `combined_rules/mfe_mae_v2_2_stage3/report.json`

Both must state `diagnostic_only=true` and `holdout_opened=false`.
