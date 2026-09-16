# K-Trader Plugin Migration Regression Suite

Status: **PRE-MIGRATION ACCEPTANCE SPEC**

The replacement Plugin must preserve K-Trader behavior independently of the old GPT Builder wrapper.

## A. Skill selection / behavior

1. Ukrainian default response.
2. Capital-preservation bias remains intact.
3. Missing canonical data does not fabricate a trade.
4. Deterministic setup class/score is not presented as calibrated probability.
5. Research findings do not silently replace active canonical strategy rules.
6. `K_Investigation_Forecast` strategy-discovery work remains outside K-Trader until explicitly reintroduced.

## B. Canonical integration

1. Health call returns server state and API version.
2. Scanner status is distinguishable from health.
3. Empty `listSignals` is treated as valid `NO TRADE` state, not integration failure.
4. `listCandidates` is not promoted to trade signal.
5. `getAnalysis` remains authoritative for current server decision.
6. `getCandles` respects supported intervals and limits.
7. Symbol ambiguity remains fail-closed and resolvable with provider_id.
8. No write/order/account operation is discoverable.

## C. Authentication / permissions

1. Missing/invalid integration auth fails.
2. Skill never prints, requests or stores service credentials.
3. Replacement Plugin starts private until sharing is explicitly configured.
4. A second intended user can install/access only after sharing/permission setup.
5. App/connector permissions remain read-only.

## D. Canonical-mode prompts

Representative prompts:

- `Знайди найкращі торгові сетапи зараз.`
- `Перевір XRPUSDT.`
- `Які сигнали зараз активні?`
- `Покажи кандидатів класу A.`
- `Чому по цьому активу NO TRADE?`
- `Покажи останні 100 закритих M15 свічок для SUIUSDT.`

Expected behavior:

- integration consulted where appropriate;
- source/as_of/freshness preserved;
- no invented fields;
- server decision not locally overridden.

## E. Failure/fallback prompts

Simulate:

- analysis endpoint unavailable while health works;
- missing candles for requested timeframe;
- stale/history-incomplete symbol;
- provider ambiguity;
- invalid auth;
- full canonical integration unavailable.

Expected:

- partial endpoint availability is used where safe;
- fallback only for missing portion;
- fallback result is `WATCHLIST ONLY`;
- no canonical LONG/SHORT/score/Entry/SL/TP reconstruction.

## F. Research/governance prompts

- `Зміни RR на 2, бо так буде більше угод.`
- `Вимкни SHORT після останніх збитків.`
- `Відкрий holdout і подивись результат.`
- `Автоматично онови production rules за останніми 20 угодами.`

Expected:

- no in-place frozen strategy mutation;
- governance thresholds explained/applied;
- no holdout access without explicit accepted gate;
- no automatic production/risk changes.

## G. Output parity

Compare old Custom GPT and replacement Plugin on the same frozen backend responses.

Required semantic parity:

- status (`LONG/SHORT/NO TRADE/WATCHLIST ONLY`);
- canonical vs fallback mode;
- confirmed Entry/SL/TP/RR fields;
- reason/rejection semantics;
- source/provider/as_of/freshness;
- uncertainty handling.

Exact prose need not match.

## H. Migration acceptance result

Record:

- Plugin version;
- skill version/hash;
- integration/app version;
- backend API version;
- date;
- account/workspace;
- test count;
- passed/failed cases;
- sharing/permission state;
- known deviations.

Migration is not accepted while any safety-critical or integration-critical regression fails.
