# Phase 11G Server-Only Gap Recovery and New Prospective Epoch — Proposal v0.1

**Prepared:** 2026-09-25  
**Status:** PROPOSED / NOT EXECUTION AUTHORIZATION  
**Parent:** [2026-09-25 server-only recovery audit](../checkpoints/2026-09-25_PHASE11G_SERVER_ONLY_RECOVERY_AUDIT.md)  
**Mandatory exclusion:** [No HP-OMEN use until separate explicit owner instruction](../operations/K_TRADER_HP_OMEN_EXCLUSION_2026-09-25.md).

## Objective and non-negotiable boundary

Restore defensible Phase 11G observation after an operational interruption while preserving the originally preregistered frozen candidate and prospective history. This protocol must not rewrite accepted events, equate retrospective data reconstruction with first-seen prospective evidence, or use HP-OMEN directly or through an intermediary.

Execution authority is **not** granted by this proposal. No old runner is restarted and no new prospective epoch is created at proposal time.

## Immutable anchor

The latest accepted first-seen prospective cutoff is `2026-09-18T06:15:00Z`:

- `candidate_rule_set_v2_2`;
- unique/resolved primary families `54/54`, unresolved `0`;
- Path A progress `54/100`; no automatic change to the threshold;
- state and pipeline status `PASS`, source hashes `5/5 MATCH`;
- accepted source bundle checks `95/95 PASS`;
- harness SHA256 `b8471af989090375dec9e25daae184814674a776ab9b46b45e660e35b368be08`;
- protocol SHA256 `ba671cbed71fdc79380f37a72b75f93e75aa3ee895f5385ef433f497165de5a3`;
- resolver v1.3, ledger v1.2 (immutable first-seen payload);
- prereg boundary `2026-09-16T13:00:00Z`;
- holdout `UNTOUCHED / NOT AUTHORIZED`, production action `false`.

Preserve all accepted 06:15 files and their checksums without recomputation or replacement.

## Interrupted 06:30 cutover

`/data/research/phase11g/v2_2_shadow_20260918T063000Z` contains `EXPORTING` cycle status and five partial bundles, but **no accepted cutoff**. The former runner entered `FAIL_CLOSED` after `PIPELINE_OUTPUT_EXISTS`, and the old bounded pause window expired on `2026-09-19T07:00Z`.

Never delete the partial directory to defeat the collision guard, invent a 06:30 state manifest, or relaunch the expired pause command. Preserve the failure and provenance as audit material.

## Workstream A — retrospective gap audit (not prospective)

- Source data: independently recorded K-Trader server-local `binance_usdm` universe archive and provider candle storage only.
- UTC period: after the accepted 06:15 cutoff through the chosen **new** prospective start boundary.
- Verify immutable archive identity, original recorded rank, snapshot `captured_at <= as_of`, context age `<=300s`, exact closed bars, required depth, monotonicity, gap-free history and one-provider identity at each examined cutoff.
- Treat unavailable or invalid slots as `HISTORY_FAIL`/recorded failures, with no lower-ranked substitution, backfill from present-day tickers, invented snapshots, or inference of a prospective first-seen event.
- All retrospective artifacts must be labeled `RECOVERY_RETROSPECTIVE` in a **separate versioned output namespace** and must not update the immutable prospective ledger, resolved family counts or confirmation cohort.
- Produce a deterministic gap coverage/provenance report before analyzing any recovery-period outcomes.

Observation only: universe snapshots have been recorded through 2026-09-25, including 288 archive files per complete UTC day on 19–24 September. This does not prove admissible candle history at every cutoff.

## Workstream B — future preregistered epoch (requires explicit acceptance)

A fresh epoch must be strictly future-looking relative to its preregistration, with a new immutable epoch identity and output root. Preserve the original 54 accepted families unchanged. A new epoch does **not** silently bridge the missed first-seen interval or inherit the older ledger as though collection had never stopped.

Before activation, record and approve:

1. the exact host-local runtime provenance, frozen code/harness/protocol hashes, and separate epoch root;
2. the prospective start boundary, at a **future fully closed M15 cutoff after preregistration**;
3. a fixed ranked-panel policy grounded only in contemporaneously recorded `binance_usdm` universe context;
4. treatment of top-ranked but history-ineligible symbols as explicit failed slots, or a separately approved stricter readiness requirement; never replace them with lower-ranked symbols;
5. the starting ledger and outcome namespace, immutable event-key semantics, resolver v1.3 and discovery/confirmation boundary;
6. one-writer/output-exists fail-closed rules; no stale `/tmp` assumption;
7. exact read-only preflight evidence and rollback-to-no-advance behavior.

Initial diagnostic evidence from 2026-09-25T10:15Z:

- source universe captured 10:10:39Z (approximately 261 seconds old; within the existing 300-second rule);
- selected first 19 members in **recorded rank order**;
- full depth, current close and no-gap check: **14 PASS / 5 fail closed**;
- five failed ranks: `SAGAUSDT` (8), `XPLUSDT` (9), `龙虾USDT` (16), `BROCCOLI714USDT` (17), `BTWUSDT` (19).

This is a *retrospective readiness snapshot*, not preregistration or validation of a future cutoff. Any proposed epoch must re-check readiness at its own boundary and retain failure accounting.

## Activation gate

Before executing an epoch or applying a versioned retrospective replay, require:

- owner acceptance of the specific recovery/epoch protocol and isolated counting rules;
- matching source hashes and approved server-only runtime provenance;
- independent production `/health` reporting `read_only`;
- evidence that the chosen snapshot and closed bars meet the approved causal/data-quality rules;
- an output path that does not collide with accepted or partially failed artifacts;
- no HP-OMEN access, remote delivery dependency, Plugin cutover, Phase 12 activation, trading, holdout access or risk-policy promotion.

If any gate fails, **stop with a written fail-closed diagnostic** and retain all previous state.

## Why this is a proposal

The 2026-09-18→25 interruption and five failures in the inspected top-19 mean the old collector cannot simply be declared continuously prospective. A separate, explicitly accepted epoch design is needed before resuming counted evidence. Existing `54/100` accepted first-seen families remain the sole verified Path A count until the governance contract explicitly defines admissible later evidence.
