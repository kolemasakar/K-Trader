# Independent retrospective label gate — 2026-10-04

Status: IMPLEMENTED / 21 REAL CASES AWAIT INDEPENDENT REVIEW.

## Executed

Verified current research HEAD561d387d and CI37206146061 SUCCESS. Read-only metadata discovery did not establish historical tick metadata: bounded filename scan (depth5, stopped at2000directory budget; not exhaustive) and production SQLite schema (mode=ro) showing only candles/bootstrap_runs/sqlite_sequence. No metadata was fabricated from decimal places or current contract settings; no production mutation or external order endpoint used.

`gerchik_independent_labels_v0_1.py` now validates review data against the exact semantic SHA256 of the prepared real panel packet. Template: `GERCHIK_REVIEW_INPUT_TEMPLATE_2026-10-04.json`. CLI output on actual packet with no fabricated reviews: `GERCHIK_INDEPENDENT_LABEL_READINESS_2026-10-04.json`, PENDING,21missing cases,0tradable levels.

## Contract

- A review must name an independent reviewer and a different proposer. This checks declarations, not personal identity/authentication. Never substitute the same model's self-review for an independently supplied human label.
- Review date cannot precede the displayed data cutoff or exceed evaluated_at. Packet hash must match the exact data displayed; stale labels fail.
- Positive decision LEVELS needs labelled levels; negative NO_LEVELS needs an empty level list. Both require rationale.
- Historical tick metadata needs positive tick size, source provenance and effective from/until bounds covering all displayed D1/W1 bars. Current tick metadata without historical coverage does not pass. Price decimal formatting is not tick-size evidence.
- Every panel OHLC price must be an exact multiple of the declared tick. Each labelled price must equal its referenced source D1/W1 High/Low. Exactly one primary type per same-TF price identity; duplicate records fail. Reviewed pattern witnesses must be unique, reference displayed closed bars and include the source bar; a pattern rationale is mandatory.
- Semantic correctness of TREND_BREAK/HISTORICAL/etc is the independent reviewer's responsibility. Mechanical checks do not establish all seven formations automatically or prove structural significance.
- No model score/rating/outcome fields in the review; no backdated tradable_known_at. Retrospective reference labels are exclusively for classifier agreement evaluation. They do not create formation approvals, strengthen causal research ledgers, establish historical trading availability or turn the inspected year into an untouched holdout.

## Usage

`python scripts/research/gerchik_independent_labels_v0_1.py --packet docs/research/GERCHIK_BLIND_REVIEW_PANELS_2026-10-04.json --input docs/research/GERCHIK_REVIEW_INPUT_TEMPLATE_2026-10-04.json`

Read-only JSON stdout; exit1for pending completeness, exit0for complete reference declarations. Optional --evaluated-at-ms fixes evaluation time for reproducibility. Input metadata keyed by symbol; reviews list contains one review per case. Template placeholders are guidance, not submitted reviews; supplied reviews must reference the packet hash and real reviewer declarations. The source packet's embedded review placeholders remain unchanged.

## Evidence and remaining gate

8new test methods plus77existing cases:85local Python3.12 tests passed. Coverage includes self-review rejection, historical metadata coverage, wrong extrema, duplicate type assignments, unknown/future witnesses, score leakage, no backdating, missing reviews, retrospective negative cases and exact packet version binding. CLI was run on the real21panel packet, returned PENDING and did not mutate either input. New change CI checked after publication.

Remaining: source effective historical instrument metadata and independent21case labels. Full seven-step scientific acceptance and real-level scoring remain pending. This is completion of the ingestion/checking workflow, not completion of the independent review itself. FREE_ONLY/no HP-OMEN/no K_AI access remain binding; research PR94 stays unmerged, no production deployment authorized or performed.
