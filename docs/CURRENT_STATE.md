# K-Trader Current State

Updated: 2026-09-13 dual-track frozen-v2.2 evidence through prospective cutoff `2026-09-13T08:30:00Z`  
Research checkpoint: `docs/checkpoints/2026-09-13_FROZEN_V2_2_DUAL_TRACK_HISTORICAL_EXPANSION_V1.md`  
Bootstrap: `docs/handoffs/BOOTSTRAP_PACKAGE_2026-09-13_K_TRADER_POST_PAUSE_RESUME.md`

## Production

Accepted/deployed application SHA:

`81b79b281a4cc330b7c11058d202e0d74fb6d70e`

Latest runtime state:

- container `k-trader-ktrader-1`;
- image `k-trader:81b79b281a4cc330b7c11058d202e0d74fb6d70e`;
- `running / healthy`;
- API `status=ok`, `mode=read_only`, `data_ready=true`;
- provider `binance_usdm`;
- scanner `DEGRADED` remains the known fail-closed/history-readiness state;
- host system state `running`;
- no reboot-required marker;
- no production deploy/restart was performed during current research work.

## Research isolation

Research branch:

`research-strategy-benchmark-v1`

Frozen candidate:

`candidate_rule_set_v2_2`

Frozen harness SHA256:

`b8471af989090375dec9e25daae184814674a776ab9b46b45e660e35b368be08`

Prospective boundary:

`2026-09-11T20:00:00Z`

Holdout:

`UNTOUCHED / NOT AUTHORIZED`

No frozen rule, RR, 8h max-hold, risk gate, symbol/direction filter or holdout authorization changed.

## Dual-track evidence plan

Current research now runs two strictly separated evidence streams.

### Track A — prospective evidence

Independent future observations continue under exact frozen v2.2 semantics. This stream alone counts toward the preregistered prospective family thresholds.

### Track B — historical confirmatory expansion

A separate historical block is evaluated before the existing benchmark dataset. It supplements confidence and regime diagnostics but is never numerically merged with prospective family counts.

Protocol:

`docs/research/FROZEN_V2_2_HISTORICAL_EXPANSION_V1_PROTOCOL.md`

Protocol commit:

`7a3a51962030d1a5f591a41a1f200167cc47cc53`

Evaluator:

`research/strategy_benchmark_v1/historical_expansion_v2_2_v1.py`

Evaluator commit:

`a7ec89c5329db0b1a7a4aeaf08c871639916c8f6`

## Track B — Historical Expansion v1 result

Hard external cutoff:

`2026-09-05T14:45:00Z`

Primary scored window:

`2026-08-11T14:45:00Z -> 2026-09-05T14:44:59.999Z`

Coverage:

- frozen panel `19/19`;
- `2400` scored M15 bars per symbol = 25 days;
- all 19 symbols have at least `3000` M15 and `2000` H1 bars in the exported dataset;
- official Binance USD-M funding exported for all 19;
- no symbol substitution;
- existing benchmark holdout not evaluated.

Accepted report:

`/data/research/phase11g/historical_expansion_v1_20260905T144500Z/results_v1/report.json`

Report SHA256:

`2adf7f9ffeb9defd7ae57c42624abb6d797255e0c2284292e38949c0fbc7026c`

Data hashes:

- dataset summary: `1b25536c06489a8151c9de09989bbcf98c2c98e65c8d7be8ea17924a8be00b52`;
- funding summary: `924ac2dad419f13ef19bd3eaf2ec8def24bbf47c094e5138e6cd069dcaaf854b`;
- base trades: `3446d1f9d1aedac059426dacee88ad37245edeb43013aa52e5c62221a9f26641`;
- stress trades: `0c819605a07f2c8f5e68991d4e01ebe159df3c59e3253049b27d2254ac2c5224`.

Base historical result:

- completed trades: `117`;
- censored open positions: `2`;
- wins/losses: `50 / 67`;
- win rate: `42.7350%`;
- expectancy: `+0.1863256189R`;
- profit factor R: `1.347812099`;
- max drawdown: `19.09473870R`;
- exits: `55 STOP / 22 TARGET / 40 TIME_EXIT`;
- directions: `98 LONG / 19 SHORT`;
- top-symbol trade share: `14.53%`.

Stress result at frozen `5 bps` execution slippage per side:

- completed trades: `118`;
- win rate: `42.3729%`;
- expectancy: `+0.1742143868R`;
- profit factor R: `1.326332898`;
- max drawdown: `20.88130304R`;
- expectancy delta vs base: `-0.0121112321R`.

Direction diagnostic, base:

- LONG: `98` trades, expectancy `+0.3260307549R`;
- SHORT: `19` trades, expectancy `-0.5342587667R`.

This direction split is a hypothesis signal only. It does not authorize an in-place LONG-only filter or any v2.2 retuning.

Five equal 5-day diagnostic blocks produced expectancy values:

`-0.1038R, +0.3799R, -0.0192R, +0.1412R, +0.5106R`.

Historical Expansion v1 therefore supports a positive aggregate historical edge over this fixed 25-day block, but also shows material direction/regime heterogeneity and a large chronological trade-stream drawdown. It remains confirmatory historical evidence, not prospective evidence.

## Track A — latest prospective evidence

Latest accepted safe closed-M15 cutoff:

`2026-09-13T08:30:00Z`

Run root:

`/data/research/phase11g/v2_2_shadow_20260913T083000Z`

Capture:

- cycle: `VALID_SHADOW_CAPTURE`;
- provider: `binance_usdm`;
- panel: `19/19`;
- signal bars evaluated: `2755`;
- deduplicated events: `110`;
- eligible observations: `15`;
- unique eligible families: `11`;
- valid snapshots: `11`;
- discovered snapshots: `12`;
- one previously known invalid infrastructure snapshot remains rejected;
- holdout: unopened.

Latest hashes:

- bundle set: `70df3ba7a614f7e254a0e3bcba545c30e43cc161ba238b8aabbf51cee6a91f9a`;
- bundle export summary: `10204b8dab8a0cf8c0550c55409adfa8e81307f3e65159ab543ad8d447c69089`;
- shadow summary: `0b8c88dc9973c4ad803f72e6021b8c41a32b1501d5dbae2e7a8a7ef8470ba1f0`;
- event file: `25063e48eaa1a9667fea4674a6194f1f6d593a77e7b3173c46b999c2af4e5ff1`;
- ledger event set: `c506a23a1fc32b49f718263318c9cba2288d01d2bc928632cf98a97379ace5b1`;
- outcome report: `4b068d4326c494c11a37270bacf217d90f528d4f8236c893f134c7e1f353e002`;
- family outcome set: `b5708948c98f9fdacd59551749e9368cf1f2afdac23de1aa4c41ae8d36c60ae2`;
- observation outcome set: `200b76ab25bb9194ba8e121f5f9d4d422a99107e6034a481b38d66d7cfae5ddc`;
- Level Context observation: `a687cf20b552d7eb6a0f855572becb2fecd1b198af71b081609d295666c2c532`.

## Prospective family outcomes

Primary evidence unit remains unique resolved `setup_family_id`.

Current state:

- unique families: `11`;
- resolved primary families: `9`;
- unresolved primary families: `2`;
- resolved wins/losses: `1 / 8`;
- resolved WR: `11.11%`;
- resolved expectancy: `-0.8807054663R`;
- evidence status: `OBSERVATION_ONLY_LT_30_RESOLVED_FAMILIES`.

Unresolved primary families:

- `e363704d...` — `VTHOUSDT LONG`, primary entry `2026-09-13T06:30:00Z`;
- `5f7acb47...` — `VTHOUSDT LONG`, primary entry `2026-09-13T08:00:00Z`.

Current prospective sample remains too small to override the preregistered governance or explain the historical/prospective difference statistically.

## Observation-only diagnostics

Level Context v2 across 11 primary families:

- clean-break/no-revisit: `4`;
- frozen-v2.2 vs richer open-space disagreements: `2`;
- richer obstacle inside `3R`: `5`;
- richer obstacle inside `1R`: `4`.

All diagnostic features remain non-gating.

## Family evidence governance

- `<30` resolved primary families: observation only;
- `30–49`: diagnostics;
- `50–99`: hypotheses/ablation proposals only;
- `>=100`: versioned recalibration proposal may be considered, still requiring fresh OOS/prospective evidence and explicit promotion.

Next prospective hard milestone:

`>=30 unique resolved prospective frozen-v2.2 setup families`.

Historical trades do not count toward this threshold.

## Host / pre-pause preparation

Planned technical/data-collection pause:

`2026-09-14 10:00 Europe/Kyiv -> 2026-09-15 10:00 Europe/Kyiv`.

Current host preparation state:

- `/data` free space approximately `37G`;
- Phase 11G research footprint approximately `294M` before the new historical bundle growth;
- `apt-daily.timer` enabled/active;
- `apt-daily-upgrade.timer` enabled/active;
- observed next `apt-daily-upgrade` schedule was approximately `2026-09-14 09:01 Europe/Kyiv`;
- SentinelX `sudo systemctl` requires a password, so host timer freeze is expected to require a manual owner action unless permissions change.

Per user instruction, exact manual actions are to be supplied at `2026-09-14 07:00 Europe/Kyiv`. No automatic reminder/task is configured.

## Repository/governance

Canonical `main`:

`4919fea4397d34898ddc7d4215ea898e6caea815`

Research ancestry remains synchronized without history rewrite:

- canonical `main` is an ancestor of research;
- no rebase;
- no force update.

Production remains deployed on `81b79...`; research and documentation commits do not require redeployment.

## Next work order

1. Continue exact frozen-v2.2 prospective accumulation and deterministic family resolution.
2. Keep Historical Expansion v1 immutable as the primary 25-day historical confirmatory block.
3. Preregister and add longer historical robustness windows separately (90d / 180d / 1y where instrument age supports them), without redefining the primary result.
4. Continue direction/regime/Level Context/VSA/execution diagnostics only as hypotheses, not gates.
5. Prepare the 2026-09-14 pre-pause baseline and manual host freeze instructions at 07:00 Europe/Kyiv.
6. Create a new strategy version only through preregistration when evidence supports it.

Phase 11G remains **ACTIVE**.

Phase 12 remains **FUTURE / NOT ACTIVE**.
