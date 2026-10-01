from __future__ import annotations

import argparse
import asyncio
import os
import stat
from pathlib import Path


async def _pipe(reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
    try:
        while True:
            chunk = await reader.read(65536)
            if not chunk:
                break
            writer.write(chunk)
            await writer.drain()
    except (ConnectionError, asyncio.CancelledError):
        pass
    finally:
        try:
            writer.write_eof()
        except (AttributeError, OSError):
            pass


async def _handle_client(
    reader: asyncio.StreamReader,
    writer: asyncio.StreamWriter,
    *,
    target_host: str,
    target_port: int,
) -> None:
    try:
        upstream_reader, upstream_writer = await asyncio.open_connection(
            target_host,
            target_port,
        )
    except OSError:
        writer.close()
        await writer.wait_closed()
        return

    try:
        await asyncio.gather(
            _pipe(reader, upstream_writer),
            _pipe(upstream_reader, writer),
        )
    finally:
        upstream_writer.close()
        writer.close()
        await asyncio.gather(
            upstream_writer.wait_closed(),
            writer.wait_closed(),
            return_exceptions=True,
        )


def _prepare_socket_path(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists() and not path.is_symlink():
        return
    mode = path.lstat().st_mode
    if not stat.S_ISSOCK(mode):
        raise RuntimeError(f"refusing to replace non-socket path: {path}")
    path.unlink()


async def _serve(socket_path: Path, target_host: str, target_port: int) -> None:
    _prepare_socket_path(socket_path)
    server = await asyncio.start_unix_server(
        lambda reader, writer: _handle_client(
            reader,
            writer,
            target_host=target_host,
            target_port=target_port,
        ),
        path=str(socket_path),
    )
    os.chmod(socket_path, 0o600)
    try:
        async with server:
            await server.serve_forever()
    finally:
        try:
            if socket_path.exists() and stat.S_ISSOCK(socket_path.lstat().st_mode):
                socket_path.unlink()
        except OSError:
            pass


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Relay a private Unix socket to the host-local K_AI delivery tunnel."
    )
    parser.add_argument("--socket", required=True)
    parser.add_argument("--target-host", default="127.0.0.1")
    parser.add_argument("--target-port", type=int, default=18765)
    args = parser.parse_args()
    if args.target_host != "127.0.0.1":
        raise SystemExit("target-host must remain 127.0.0.1")
    if not 1 <= args.target_port <= 65535:
        raise SystemExit("invalid target port")
    asyncio.run(_serve(Path(args.socket), args.target_host, args.target_port))


if __name__ == "__main__":
    main()
