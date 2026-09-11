# Checkpoint — First Frozen v2.2 Prospective Shadow Capture

Date: 2026-09-11
Status: PROSPECTIVE SHADOW CAPTURE PASS / ZERO EVENTS / HOLDOUT UNTOUCHED / NO PRODUCTION ACTION

## Purpose

Begin fresh post-freeze evidence capture for the exact frozen `candidate_rule_set_v2_2` while attaching research-only Level Context / traversal features.

The shadow runner does not send orders and does not alter production behavior.

## Freeze boundary

Frozen executable v2.2 was committed before the prospective interval.

First fully prospective M15 signal-bar boundary:

`2026-09-11T20:00:00Z`

Frozen harness SHA256 verified during capture:

`b8471af989090375dec9e25daae184814674a776ab9b46b45e660e35b368be08`

Benchmark protocol SHA256:

`ba671cbed71fdc79380f37a72b75f93e75aa3ee895f5385ef433f497165de5a3`

## Provider-recorded bundle set

Provider: `binance_usdm`.

As-of:

`2026-09-11T20:30:00Z`

Fixed preregistered panel: `19/19` symbols exported successfully; no substitutions and no missing symbols.

Per symbol:
- M15: 400 bars;
- H1: 300 bars;
- H4: 80 bars;
- D1: 20 bars;
- M5: 20 bars.

Bundle-set semantic provenance hash:

`a6e5fbedf8468e0c3e9def8e95e1a36f646c3656ec2e573da2bc1fcd98a97ecf`

The shadow summary stores the individual bundle SHA256 for every panel symbol.

## Causal evaluation coverage

The bundle contains two closed M15 bars whose opens are at/after the prospective boundary (`20:00` and `20:15` UTC), but the frozen candidate enters only at the next M15 open.

Therefore only the `20:00` signal bar is fully entry-evaluable within the 20:30 closed-candle bundle. The `20:15` signal bar is intentionally deferred until a subsequent closed M15 bar makes its next-open entry causally available.

Evaluated signal bars:

- 1 per symbol;
- 19 total symbol-bar evaluations;
- earliest evaluated signal-bar open: `2026-09-11T20:00:00Z`;
- latest evaluated signal-bar open: `2026-09-11T20:00:00Z`.

## Result

- frozen-v2.2 signal events reaching entry evaluation: `0`;
- eligible shadow setups: `0`;
- unique eligible setup families: `0`;
- clean-break/no-revisit eligible setups: `0`;
- holdout opened: `false`;
- production action: `false`.

This is a valid zero-event prospective observation and must not be converted into synthetic samples.

## Artifacts

Bundle root:

`/data/research/phase11g/v2_2_shadow_20260911T203000Z/bundles`

Hardened shadow output:

`/data/research/phase11g/v2_2_shadow_20260911T203000Z/shadow_v1_1`

Summary SHA256:

`0cd0d836a5bb7780fc12f8044a20bc845a15822116c70ca3c323345b2421319d`

Empty events file SHA256:

`e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`

## Provenance hardening

The first raw zero-event run exposed a logging deficiency: with no events, the summary did not prove which bundles had been evaluated.

The shadow logger was hardened without changing trading semantics. Summary schema `v1_1` now records:

- every per-symbol bundle hash and as-of timestamp;
- bundle-set hash;
- exact frozen harness hash;
- protocol hash;
- evaluated signal-bar count per symbol and total;
- earliest/latest evaluated signal-bar open times.

Research code commit:

`ca0dd53a57bdc31f0418916f14bcdeb963b460fc`

The original raw run remains preserved separately; the hardened run was written to `shadow_v1_1`.

## State

Unchanged:

- v2.2 remains frozen;
- pre-holdout promotion gate remains FAILED;
- holdout remains unopened;
- production remains read-only and unchanged;
- no research threshold was promoted.

## Next evidence step

Repeat the same frozen prospective capture on a later provider-recorded bundle set. Resolve outcomes only after enough future closed bars exist for a given eligible setup. Do not tune v2.2 from interim observations.
