# K-Trader Phase 10 Builder Checklist

Status: PREPARED; execute only after real HTTPS live acceptance.

1. Confirm target host passes `scripts/phase10_action_acceptance.py` with `data_ready=true`.
2. Generate a high-entropy `KTRADER_ACTION_API_KEY`; store it only in the GitHub `production` Environment secret and in the GPT Action authentication configuration.
3. Render `custom_gpt/openapi.yaml` with the real HTTPS origin using `scripts/render_custom_gpt_openapi.py`.
4. Open the existing K_Trader GPT editor and create/update its Action.
5. Authentication: API key -> Bearer; use the same secret as `KTRADER_ACTION_API_KEY`.
6. Paste/import the rendered OpenAPI schema.
7. Verify exactly these operations are detected: getHealth, getScannerStatus, listUniverse, getMarketSnapshot, getCandles, getAnalysis, listCandidates, listSignals.
8. Privacy Policy URL: `https://REAL_HOST/privacy` if the publishing mode requires it.
9. In Preview test readiness, signals, candidates, one-symbol analysis, provider ambiguity, and NO_TRADE preservation.
10. Verify the GPT does not use Apps simultaneously with Actions and select a model/mode that supports Actions.
11. Do not publish broadly until source/freshness/NO_TRADE behavior passes the Phase 10 acceptance checklist.

No Builder change is required while the server still uses the `.invalid` placeholder.
