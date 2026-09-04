# K-Trader Custom GPT Action Guide v1.2

## Role

The Action is a read-only bridge from K_Trader Custom GPT to the K-Trader scanner API. It cannot place, modify or cancel orders.

K_Trader has two data modes:

- **Canonical mode** — Action/backend available and data-ready; TradingDecision comes only from K-Trader scanner outputs.
- **Discovery fallback** — Action/backend unavailable or not data-ready; Web Search/public market data may be used only for a preliminary `WATCHLIST ONLY` result.

## Authentication

Production uses a server-side Bearer API key.

- Server secret: environment/GitHub Environment secret `KTRADER_ACTION_API_KEY`.
- GPT editor: Authentication -> API key -> Bearer.
- The secret is never committed to the repository.
- `/health` and `/privacy` remain public; `/v1/*` is protected when the server secret is configured.

## Preferred operations

For "find the best setups now":

1. `getHealth` or `getScannerStatus` when readiness is unknown.
2. If `data_ready=true`, use `listSignals` for current A/A+ LONG/SHORT signals.
3. Use `listCandidates` when the user asks why assets were rejected, wants a wider shortlist, or when no A/A+ signals exist.

For one symbol:

1. `getAnalysis` for the canonical TradingDecision.
2. `getMarketSnapshot` for latest normalized ticker/liquidity metadata.
3. `getCandles` only when confirmed raw bars are needed, such as a VSA sequence.

## Automatic fallback behavior

If the Action is unreachable, authentication fails, `data_ready=false`, or required canonical OHLCV/VSA data is stale/insufficient:

- do not fabricate a canonical signal;
- do not convert Web Search into A/A+, LONG/SHORT, Setup Score, Entry/SL/TP, ATR or VSA confirmation;
- if enough public market data exists, perform a preliminary market-discovery pass and return `WATCHLIST ONLY`;
- include actual sources, timestamps/freshness where available, and only confirmed discovery metrics such as price, turnover/volume, range, funding/open interest when supported;
- state clearly: `Not validated by Trading Engine. Entry/SL/TP/Grade/Score: N/A`;
- if even discovery data is insufficient, return an explicit insufficient-data result rather than inventing candidates.

When the Action becomes available again and `data_ready=true`, automatically return to canonical mode. The discovery fallback never overrides canonical K-Trader scanner output.

## Provider ambiguity

If an operation returns HTTP 409, repeat it with explicit `provider_id`. Never silently substitute another provider.

## Data rules

- Action API data has priority over Web Search for current OHLCV/VSA analysis.
- Never mix candle series from different providers.
- Respect freshness/data timestamps.
- Stale/insufficient canonical data cannot be promoted to a trade.
- Web Search/public data may support discovery but not canonical TradingDecision fields.
- Decimal market values are strings to preserve exact exchange precision.
- Setup Score is not statistical probability.
- `estimated_probability` remains null until calibrated historical evidence exists.
- Preserve canonical TradingDecision Entry/SL/TP/RR/ATR/grade; do not recalculate them in GPT.

## Deployment rendering

Canonical `custom_gpt/openapi.yaml` intentionally contains `https://api.k-trader.invalid`.

After the real HTTPS origin exists:

```sh
python scripts/render_custom_gpt_openapi.py \
  --server https://REAL_HOST \
  --output /tmp/k-trader-openapi.yaml
```

Then run:

```sh
python scripts/phase10_action_acceptance.py \
  --base-url https://REAL_HOST
```

Use the rendered schema in the existing K_Trader GPT editor. Do not commit a production API key.

## Builder instruction

Use `custom_gpt/SYSTEM_K_TRADER_v1_2.md` as the current GPT instruction baseline. It preserves fail-closed canonical trading logic while adding the non-trading discovery fallback.

## Current OpenAI product constraints to verify at activation

The Action uses the GPT editor's external API Action feature with an OpenAPI schema and API-key authentication. An existing GPT can be edited subject to account/workspace permissions. GPTs use Apps or Actions, not both simultaneously. Public/shared GPT distribution with Actions requires a valid Privacy Policy URL. Re-check these product rules immediately before activation because they can change.
