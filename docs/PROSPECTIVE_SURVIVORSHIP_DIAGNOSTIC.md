# Phase 11G Prospective Survivorship Diagnostic

Status: RESEARCH DIAGNOSTIC ONLY

This diagnostic complements the canonical prospective-control report. It does not replace the canonical record funnel, does not change any trading gate, and does not alter report hashes or production behavior.

## Motivation

The canonical prospective-control funnel counts decision records at every logical cutoff. That is correct for causal replay accounting, but repeated M5 observations of the same structural level can create highly autocorrelated record counts.

For research interpretation, a count such as `27 RR>=3 records` must not automatically be read as `27 independent setups`.

The survivorship diagnostic therefore reports two views side by side:

- record-level funnel — the same sequential gate semantics used by prospective control;
- distinct-primary-level funnel — unique `(canonical_symbol, primary_level_id)` keys surviving each gate.

The second view is an effective-sample/dependency diagnostic only. It is not a signal identity, not an outcome identity, and not a trading rule.

## Sequential gates

The diagnostic mirrors the canonical funnel in the same order:

1. HTF aligned;
2. STRONG + confirmed primary level;
3. valid structural geometry;
4. ATR-used <= 80%;
5. FAST TTL not expired;
6. structural RR >= 3;
7. Grade A/A+;
8. tradable LONG/SHORT.

No threshold is changed.

## Identity definition

A distinct structural level is keyed only by:

```text
(canonical_symbol, primary_level_id)
```

Records with no `primary_level_id` remain visible in the record funnel and are counted separately under `records_without_primary_level`; they are not silently assigned a synthetic identity.

This is deliberately narrower than a hypothetical "unique setup" identity. Different entries or confirmations can occur around the same primary level. The diagnostic therefore uses the explicit term `unique_primary_level`, not `unique_setup`.

## Source validation

The analyzer accepts one or more complete canonical prospective-control shards and requires all sources to share:

- provider;
- scanner configuration SHA;
- cutoff interval;
- analysis limit;
- maximum context age.

Overlapping cutoff timestamps are rejected so the same causal observation cannot be counted twice.

Different non-overlapping windows may use different universe archives and MTF bundle SHAs.

## Output

The output schema is:

```text
ktrader.prospective_survivorship.v1
```

Key fields include:

- `record_funnel`;
- `unique_primary_level_funnel`;
- `records_without_primary_level`;
- `records_by_symbol`;
- `late_stage_repeated_levels`;
- source shard hashes and source windows;
- `analysis_sha256`.

`late_stage_repeated_levels` exposes repeated structural levels for geometry/ATR/TTL/RR/grade/tradable stages so autocorrelation is visible rather than hidden.

## CLI

Example:

```bash
python scripts/analyze_prospective_survivorship.py \
  --shard /data/research/phase11g/window_a/shards/shard_0.json \
  --shard /data/research/phase11g/window_a/shards/shard_1.json \
  --shard /data/research/phase11g/window_b/shards/shard_0.json \
  --output /data/research/phase11g/survivorship.json
```

The output path uses the same single-writer sidecar locking model as the prospective-control CLI.

## Interpretation rule

Use record counts to audit causal system behavior. Use distinct-primary-level counts to judge how much structurally independent evidence exists.

Neither count is a profitability estimate. Neither may be used to fabricate probability, outcome samples, or synthetic signals.

Any future proposal to change RR, ATR, TTL, HTF, level-strength, scoring, or structural-target rules must be supported by separate research and explicit approval.
