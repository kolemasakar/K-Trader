from __future__ import annotations

from typing import Any

import httpx

from ktrader.providers.base import ProviderError


class PublicHttpClient:
    def __init__(
        self,
        *,
        base_url: str,
        timeout_seconds: float = 10.0,
        client: httpx.AsyncClient | None = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self._owns_client = client is None
        self.client = client or httpx.AsyncClient(
            timeout=timeout_seconds,
            headers={"User-Agent": "K-Trader/0.1 read-only-market-data"},
        )

    async def get_json(self, path: str, params: dict[str, Any] | None = None) -> Any:
        url = path if path.startswith("http") else f"{self.base_url}/{path.lstrip('/')}"
        try:
            response = await self.client.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except (httpx.HTTPError, ValueError) as exc:
            raise ProviderError(f"Public market-data request failed: {exc}") from exc

    async def close(self) -> None:
        if self._owns_client:
            await self.client.aclose()
