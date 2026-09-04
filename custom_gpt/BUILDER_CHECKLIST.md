# K-Trader Builder Checklist v1.2

Status: TWO-STAGE rollout.

## Stage A — immediate GPT behavior update

This stage may be applied before a real HTTPS K-Trader backend exists.

1. Open the existing K_Trader GPT editor.
2. Replace the current Builder Instructions with `custom_gpt/SYSTEM_K_TRADER_v1_2_COMPACT.md`. The full `SYSTEM_K_TRADER_v1_2.md` remains the canonical long-form policy; the compact file is the Builder-safe operational baseline under the 8000-character product limit.
3. Set the GPT description to a non-probabilistic description. Recommended text:

   `Професійний трейдер-аналітик. Відбір і ранжування торгових можливостей за підтвердженими ринковими даними та правилами K-Trader; без виконання угод.`

   Do not use claims such as `сценарії ≥60%` or any other probability threshold until `estimated_probability` is statistically calibrated and explicitly enabled.
4. Keep the production Action disabled/unconfigured while `custom_gpt/openapi.yaml` still points to `https://api.k-trader.invalid`.
5. In Preview verify fallback behavior:
   - a broad request such as "find the best crypto setups for the next 4 hours" returns `WATCHLIST ONLY` when canonical data is unavailable but public discovery data is sufficient;
   - direct exchange public market endpoints (Binance/Bybit/OKX/KuCoin where available) are preferred over aggregators such as CoinGecko;
   - aggregator data is clearly labelled aggregated and not exchange-native;
   - shortlist language is neutral, e.g. `За результатами preliminary screening відібрано...`, not subjective `я б звузив ринок`;
   - the GPT does not fabricate Grade, Score, probability, Entry, SL, TP, ATR, VSA/Trap or A/A+ status in fallback mode.
6. Verify insufficient public discovery data produces an explicit insufficient-data response rather than invented candidates.

## Stage B — canonical Action activation after real HTTPS live acceptance

1. Confirm target host passes `scripts/phase10_action_acceptance.py` with `data_ready=true`.
2. Generate a high-entropy `KTRADER_ACTION_API_KEY`; store it only in the GitHub `production` Environment secret and in the GPT Action authentication configuration.
3. Render `custom_gpt/openapi.yaml` with the real HTTPS origin using `scripts/render_custom_gpt_openapi.py`.
4. Open the existing K_Trader GPT editor and create/update its Action.
5. Authentication: API key -> Bearer; use the same secret as `KTRADER_ACTION_API_KEY`.
6. Paste/import the rendered OpenAPI schema.
7. Verify exactly these operations are detected: getHealth, getScannerStatus, listUniverse, getMarketSnapshot, getCandles, getAnalysis, listCandidates, listSignals.
8. Privacy Policy URL: `https://REAL_HOST/privacy` if the publishing mode requires it.
9. In Preview test readiness, signals, candidates, one-symbol analysis, provider ambiguity and NO_TRADE preservation.
10. Verify automatic mode switching: `data_ready=true` uses canonical Action results; Action unavailable/not-ready uses only `WATCHLIST ONLY` fallback.
11. Verify the GPT does not use Apps simultaneously with Actions and select a model/mode that supports Actions.
12. Do not publish broadly until source/freshness/NO_TRADE and fallback-separation behavior pass acceptance.
