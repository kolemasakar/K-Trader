from __future__ import annotations

from contextlib import contextmanager
import errno
import os
from pathlib import Path
from typing import Iterator, TextIO


class OutputLockError(RuntimeError):
    """Raised when another process already owns the requested output lock."""


def output_lock_path(output: str | Path) -> Path:
    target = Path(output)
    return Path(f"{target}.lock")


@contextmanager
def exclusive_output_lock(output: str | Path) -> Iterator[Path]:
    """Acquire a process-scoped, non-blocking advisory lock for one output path.

    The sidecar lock file is intentionally persistent.  The operating-system
    lock, not file existence, determines ownership, so an interrupted process
    releases the lock automatically without creating stale-lock cleanup risk.
    """

    target = Path(output)
    lock_path = output_lock_path(target)
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    handle = lock_path.open("a+", encoding="utf-8")
    locked = False
    try:
        _lock(handle, lock_path)
        locked = True
        handle.seek(0)
        handle.truncate()
        handle.write(f"pid={os.getpid()}\n")
        handle.write(f"output={target}\n")
        handle.flush()
        yield lock_path
    finally:
        if locked:
            _unlock(handle)
        handle.close()


def _lock(handle: TextIO, lock_path: Path) -> None:
    if os.name == "nt":
        import msvcrt

        handle.seek(0, os.SEEK_END)
        if handle.tell() == 0:
            handle.write("\0")
            handle.flush()
        handle.seek(0)
        try:
            msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
        except OSError as exc:
            raise OutputLockError(f"output is already locked: {lock_path}") from exc
        return

    import fcntl

    try:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError as exc:
        if exc.errno in (errno.EACCES, errno.EAGAIN):
            raise OutputLockError(f"output is already locked: {lock_path}") from exc
        raise


def _unlock(handle: TextIO) -> None:
    if os.name == "nt":
        import msvcrt

        handle.seek(0)
        msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
        return

    import fcntl

    fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
