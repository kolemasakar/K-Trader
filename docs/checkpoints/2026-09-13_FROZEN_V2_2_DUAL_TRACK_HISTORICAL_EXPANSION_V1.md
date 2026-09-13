# K-Trader — Frozen v2.2 Dual-Track Checkpoint

Date: 2026-09-13
Status: ACCEPTED RESEARCH CHECKPOINT / PHASE 11G ACTIVE

## Scope

This checkpoint records the first accepted dual-track evidence state for frozen `candidate_rule_set_v2_2`:

- Track A: independent prospective accumulation remains active and unchanged.
- Track B: preregistered historical confirmatory expansion was added on a period strictly before the existing benchmark dataset.

No production deployment, strategy retuning, holdout opening, RR change, max-hold change, risk-gate change, symbol substitution or direction filter change occurred.

## Frozen identity

- strategy: `candidate_rule_set_v2_2`
- frozen harness SHA256: `b8471af989090375dec9e25daae184814674a776ab9b46b45e660e35b368be08`
- prospective boundary: `2026-09-11T20:00:00Z`
- holdout: `UNTOUCHED / NOT AUTHORIZED`
- production action: `false`

## Track B — Historical Expansion v1

The protocol was committed before strategy outcomes were inspected:

`docs/research/FROZEN_V2_2_HISTORICAL_EXPANSION_V1_PROTOCOL.md`

Protocol commit:

`7a3a51962030d1a5f591a41a1f200167cc47cc53`

Evaluator:

`research/strategy_benchmark_v1/historical_expansion_v2_2_v1.py`

Evaluator commit:

`a7ec89c5329db0b1a7a4aeaf08c871639916c8f6`

### Isolation

Hard external cutoff:

`2026-09-05T14:45:00Z`

Scored interval:

`2026-08-11T14:45:00Z -> 2026-09-05T14:44:59.999Z`

Per symbol:

- `2400` scored M15 bars = 25 days;
- earlier data used only as causal warm-up/context;
- existing development/validation/holdout dataset begins at approximately `2026-09-05T14:45:00Z`;
- no existing holdout outcome was evaluated.

### Data readiness

Provider: `binance_usdm`.

All frozen-panel symbols passed the preregistered M15/H1 readiness criteria:

- panel: `19/19`;
- every symbol: `3000` M15 bars;
- every symbol: `2000` H1 bars;
- every symbol: `1000` H4 bars;
- every symbol: `3000` M5 bars;
- official Binance USD-M funding exported for all 19 symbols.

Some newer instruments are age-limited only on the optional D1 depth (AKE, MET, PUMP, USELESS); this does not violate the preregistered M15/H1 primary-cohort criteria.

Dataset summary SHA256:

`1b25536c06489a8151c9de09989bbcf98c2c98e65c8d7be8ea17924a8be00b52`

Funding summary SHA256:

`924ac2dad419f13ef19bd3eaf2ec8def24bbf47c094e5138e6cd069dcaaf854b`

### Base result

Accepted report:

`/data/research/phase11g/historical_expansion_v1_20260905T144500Z/results_v1/report.json`

Report SHA256:

`2adf7f9ffeb9defd7ae57c42624abb6d797255e0c2284292e38949c0fbc7026c`

Base-trades SHA256:

`3446d1f9d1aedac059426dacee88ad37245edeb43013aa52e5c62221a9f26641`

Base economics:

- completed trades: `117`;
- censored open positions: `2`;
- wins / losses: `50 / 67`;
- win rate: `42.7350%`;
- Wilson 95% CI: `34.14% .. 51.79%`;
- expectancy: `+0.1863256189R` per completed trade;
- profit factor R: `1.347812099`;
- max drawdown in chronological trade stream: `19.09473870R`;
- average win: `+1.689557962R`;
- average loss: `-0.935489562R`;
- median hold: `19` M15 bars;
- exits: `55 STOP / 22 TARGET / 40 TIME_EXIT`;
- direction count: `98 LONG / 19 SHORT`;
- top-symbol trade share: `14.53%`;
- aggregate observed fee contribution: `4.13773R`;
- aggregate funding contribution: `0.10447R`.

### Stress result

Stress-trades SHA256:

`0c819605a07f2c8f5e68991d4e01ebe159df3c59e3253049b27d2254ac2c5224`

With frozen stress slippage (`5 bps` per execution side):

- completed trades: `118`;
- win rate: `42.3729%`;
- expectancy: `+0.1742143868R`;
- profit factor R: `1.326332898`;
- max drawdown: `20.88130304R`;
- stress expectancy delta vs base: `-0.0121112321R`.

Trade count differs by one under stress because the frozen harness applies adverse execution prices inside the executed-risk calculation; no rule was changed for the stress run.

### Diagnostic decomposition

Direction, base run:

- LONG: `98` trades, `45` wins / `53` losses, expectancy `+0.3260307549R`;
- SHORT: `19` trades, `5` wins / `14` losses, expectancy `-0.5342587667R`.

Fixed five-day diagnostic blocks over the 25-day primary window:

- block 1: `n=13`, expectancy `-0.1037534793R`;
- block 2: `n=27`, expectancy `+0.3799418812R`;
- block 3: `n=45`, expectancy `-0.0192083237R`;
- block 4: `n=7`, expectancy `+0.1412282325R`;
- block 5: `n=25`, expectancy `+0.5106495518R`.

This decomposition is diagnostic only. It does not create a LONG-only rule or any other in-place v2.2 modification.

Selected per-symbol base expectancy with meaningful sample sizes:

- USELESSUSDT: `n=17`, `+0.5510R`;
- ENAUSDT: `n=14`, `+0.1491R`;
- PUMPUSDT: `n=13`, `+0.2975R`;
- 1000PEPEUSDT: `n=11`, `+0.1232R`;
- ETHFIUSDT: `n=11`, `-0.0821R`;
- AKEUSDT: `n=9`, `+0.3332R`;
- ARBUSDT: `n=8`, `+0.2308R`;
- RAYSOLUSDT: `n=7`, `-0.6419R`;
- XRPUSDT: `n=7`, `+0.5818R`.

DOTUSDT, NEARUSDT and WLDUSDT produced zero completed trades in the fixed primary window; they remain part of the frozen cohort and were not substituted.

## Track A — Latest prospective state

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
- one known invalid infrastructure snapshot remains rejected;
- holdout: unopened.

Hashes:

- bundle set: `70df3ba7a614f7e254a0e3bcba545c30e43cc161ba238b8aabbf51cee6a91f9a`;
- bundle export summary: `10204b8dab8a0cf8c0550c55409adfa8e81307f3e65159ab543ad8d447c69089`;
- shadow summary: `0b8c88dc9973c4ad803f72e6021b8c41a32b1501d5dbae2e7a8a7ef8470ba1f0`;
- event file: `25063e48eaa1a9667fea4674a6194f1f6d593a77e7b3173c46b999c2af4e5ff1`;
- ledger event set: `c506a23a1fc32b49f718263318c9cba2288d01d2bc928632cf98a97379ace5b1`;
- outcome report: `4b068d4326c494c11a37270bacf217d90f528d4f8236c893f134c7e1f353e002`;
- family outcome set: `b5708948c98f9fdacd59551749e9368cf1f2afdac23de1aa4c41ae8d36c60ae2`;
- observation outcome set: `200b76ab25bb9194ba8e121f5f9d4d422a99107e6034a481b38d66d7cfae5ddc`;
- Level Context observation: `a687cf20b552d7eb6a0f855572becb2fecd1b198af71b081609d295666c2c532`.

Prospective family state:

- unique families: `11`;
- resolved primary families: `9`;
- unresolved primary families: `2`;
- resolved wins / losses: `1 / 8`;
- resolved win rate: `11.11%`;
- resolved expectancy: `-0.8807054663R`;
- evidence status: `OBSERVATION_ONLY_LT_30_RESOLVED_FAMILIES`.

The newly observed independent family is:

- `5f7acb47...` — `VTHOUSDT LONG`, primary entry `2026-09-13T08:00:00Z`.

The earlier unresolved family remains:

- `e363704d...` — `VTHOUSDT LONG`, primary entry `2026-09-13T06:30:00Z`.

Level Context remains diagnostic only across 11 families:

- clean-break/no-revisit: `4`;
- frozen-v2.2 vs richer open-space disagreements: `2`;
- richer obstacle inside `3R`: `5`;
- richer obstacle inside `1R`: `4`.

## Interpretation

The historical confirmatory block is materially more positive than the current very small prospective resolved cohort. This is not a contradiction that can yet be resolved statistically: the prospective cohort contains only nine resolved independent families and remains far below the preregistered threshold.

Therefore:

- historical and prospective evidence streams remain separate;
- historical trades are not added to prospective family counts;
- no in-place retuning is authorized;
- no LONG-only filter is authorized;
- the observed SHORT weakness is a hypothesis for a future version only;
- the existing benchmark holdout remains untouched.

## Next work order

1. Continue exact frozen-v2.2 prospective accumulation and causal resolution toward `>=30` resolved primary families.
2. Preserve Historical Expansion v1 as the fixed primary 25-day confirmatory block.
3. Add separately preregistered longer historical robustness blocks (90d / 180d / 1y where symbol age allows) without redefining the primary result.
4. Analyze regime and direction stability as diagnostics only.
5. Prepare the 2026-09-14 pre-pause baseline; manual host actions, if required, are to be provided at 07:00 Europe/Kyiv.
