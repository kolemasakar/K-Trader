from __future__ import annotations

import asyncio
import json
from collections.abc import AsyncIterator, Iterable
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from websockets.asyncio.client import connect


@dataclass(frozen=True, slots=True)
class JsonWsMessage:
    payload: Any
    received_at: datetime
    connection_id: int


async def json_websocket_session(
    url: str,
    *,
    subscribe_payloads: Iterable[object] = (),
    heartbeat_payload: object | None = None,
    heartbeat_interval_seconds: float | None = None,
    connection_id: int = 0,
) -> AsyncIterator[JsonWsMessage]:
    async with connect(
        url,
        ping_interval=20,
        ping_timeout=20,
        close_timeout=10,
        max_queue=4096,
    ) as ws:
        for payload in subscribe_payloads:
            await ws.send(json.dumps(payload, separators=(",", ":")))
        heartbeat_task = None
        if heartbeat_payload is not None and heartbeat_interval_seconds is not None:
            heartbeat_task = asyncio.create_task(
                _heartbeat(ws, heartbeat_payload, heartbeat_interval_seconds)
            )
        try:
            async for raw in ws:
                if isinstance(raw, bytes):
                    raw = raw.decode("utf-8")
                payload = json.loads(raw)
                yield JsonWsMessage(
                    payload=payload,
                    received_at=datetime.now(timezone.utc),
                    connection_id=connection_id,
                )
        finally:
            if heartbeat_task is not None:
                heartbeat_task.cancel()
                try:
                    await heartbeat_task
                except asyncio.CancelledError:
                    pass


async def _heartbeat(ws, payload: object, interval_seconds: float) -> None:
    while True:
        await asyncio.sleep(interval_seconds)
        await ws.send(json.dumps(payload, separators=(",", ":")))
