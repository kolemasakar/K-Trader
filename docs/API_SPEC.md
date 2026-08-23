# API Specification v1.0

## Role

Expose scanner state to K_Trader Custom GPT through a read-only HTTPS API. The API is an integration layer; the scanner must function without OpenAI.

## v1 endpoints

- `GET /health`
- `GET /v1/scanner/status`
- `GET /v1/universe`
- `GET /v1/market/{symbol}`
- `GET /v1/candles/{symbol}`
- `GET /v1/analysis/{symbol}`
- `GET /v1/candidates`
- `GET /v1/signals`

## Rules

- No POST/PUT/PATCH/DELETE trading endpoints in v1.
- No exchange account endpoints in v1.
- Responses carry provider/source and freshness metadata.
- Symbols must resolve unambiguously to provider + canonical instrument.
- Invalid/stale data returns explicit status/reason; it is not silently substituted.
- Rate limiting is required for public deployment.

## Custom GPT Action

`custom_gpt/openapi.yaml` will be generated from/kept consistent with the API contract during Phase 8.

Initial Action authentication may be `None` because the API exposes read-only non-account market analysis. HTTPS remains mandatory.

If the GPT is distributed publicly, deployment documentation must include any OpenAI publication requirements applicable at that time, including privacy-policy requirements for external Actions.
