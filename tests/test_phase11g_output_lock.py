from __future__ import annotations

from pathlib import Path
import subprocess
import sys
import time

import pytest

from ktrader.replay.output_lock import OutputLockError, exclusive_output_lock, output_lock_path


def test_output_lock_rejects_second_process_and_releases_after_termination(tmp_path: Path) -> None:
    output = tmp_path / "shard.json"
    ready = tmp_path / "ready"
    code = """
from pathlib import Path
import sys
import time
from ktrader.replay.output_lock import exclusive_output_lock

output = Path(sys.argv[1])
ready = Path(sys.argv[2])
with exclusive_output_lock(output):
    ready.write_text("ready", encoding="utf-8")
    time.sleep(30)
"""
    process = subprocess.Popen([sys.executable, "-c", code, str(output), str(ready)])
    try:
        deadline = time.monotonic() + 5
        while time.monotonic() < deadline and not ready.exists():
            if process.poll() is not None:
                break
            time.sleep(0.02)

        assert ready.exists(), "lock-holder subprocess did not acquire the output lock"
        assert process.poll() is None

        with pytest.raises(OutputLockError, match="output is already locked"):
            with exclusive_output_lock(output):
                pass
    finally:
        if process.poll() is None:
            process.terminate()
        process.wait(timeout=5)

    with exclusive_output_lock(output) as lock_path:
        assert lock_path == output_lock_path(output)
        assert lock_path.exists()

    assert output_lock_path(output).exists()
