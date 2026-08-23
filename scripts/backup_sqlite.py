from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path

from ktrader.storage.sqlite import CandleRepository


def main() -> None:
    parser = argparse.ArgumentParser(description="Create and verify an online K-Trader SQLite backup")
    parser.add_argument("--database", required=True, type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    database = args.database.expanduser().resolve()
    if not database.is_file():
        raise SystemExit(f"database not found: {database}")
    output = args.output
    if output is None:
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        output = database.parent / "backups" / f"ktrader_{stamp}.db"

    repository = CandleRepository(database)
    try:
        target = repository.backup_to(output)
    finally:
        repository.close()

    verified = CandleRepository.verify_database(target)
    if not verified:
        raise SystemExit("backup verification failed")
    print(json.dumps({
        "database": str(database),
        "backup": str(target),
        "verified": True,
        "bytes": target.stat().st_size,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
