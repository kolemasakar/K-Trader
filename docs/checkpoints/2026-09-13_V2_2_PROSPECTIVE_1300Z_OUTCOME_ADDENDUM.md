# K-Trader — 13:00Z Prospective Outcome Addendum

Date: 2026-09-13
Status: ACCEPTED

This addendum supersedes any earlier repository text that still describes the 13:00Z outcome resolver as pending.

Canonical accepted state at `2026-09-13T13:00:00Z`:

- capture: `VALID_SHADOW_CAPTURE`
- panel: `19/19`
- eligible observations: `17`
- unique prospective families: `12`
- resolved primary families: `12`
- unresolved primary families: `0`
- resolved wins / losses: `1 / 11`
- win rate: `8.333333333333333%`
- expectancy: `-0.9007780994315739R`
- evidence status: `OBSERVATION_ONLY_LT_30_RESOLVED_FAMILIES`
- holdout opened: `false`
- production action: `false`

Funding was required only for newly resolved VTHOUSDT observations and was captured from the official Binance USD-M funding endpoint.

Accepted artifact hashes:

- funding summary: `a86f971d935a6fa73aba60279def60f73561dd74d54d78b41e605755f0c7a272`
- promoted cache: `c0ba653fc0bc12f1b4253619f0fe7b5e56949d54b24fca13e6fec6387add2284`
- observation artifact: `3e292b44d9ad2641e4e47c96c96492533167a260c7628e04ba9e228e7e6386fb`
- family artifact: `28a417ec91457291e88bedda53fc0a3e5ab21d1cc419312baa878555e5b63b17`
- summary artifact: `a4ea3745ac3b325c6c6aace8d6427a0c159c3810bac49674cfca883d25333c3d`

Frozen v2.2 remains unchanged. No holdout access or production action occurred. The next hard prospective milestone remains `>=30` unique resolved primary families.
