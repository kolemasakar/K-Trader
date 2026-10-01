#!/usr/bin/env python3
"""Bounded, Landlock-constrained research child; never mutates the source archive.

This launcher is designed to run as the existing unprivileged ktrader user.
It is not a container, network, or full process-tree cgroup isolation boundary.
"""
from __future__ import annotations

import argparse
import ctypes
import errno
import json
import os
from pathlib import Path
import resource
import signal
import subprocess
import sys

DEFAULT_ARCHIVE = Path("/data/research/phase11g/historical_expansion_v1_20260905T144500Z")
# Landlock's arm64 and x86_64 system call IDs; supported Linux kernels only.
_CREATE_RULESET = 444
_ADD_RULE = 445
_RESTRICT_SELF = 446
_PR_SET_NO_NEW_PRIVS = 38
_PATH_BENEATH = 1
_WRITE_RIGHTS = sum(1 << bit for bit in (1, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14))


class Ruleset(ctypes.Structure):
    _fields_ = [("handled_access_fs", ctypes.c_uint64)]


class PathBeneath(ctypes.Structure):
    _fields_ = [("allowed_access", ctypes.c_uint64), ("parent_fd", ctypes.c_int32)]


def _checked(value: int, operation: str) -> int:
    if value < 0:
        code = ctypes.get_errno()
        raise OSError(code, f"{operation}: {os.strerror(code)}")
    return value


def _apply_landlock(write_directory: Path) -> None:
    if sys.platform != "linux":
        raise RuntimeError("Linux Landlock is required: fail closed")
    libc = ctypes.CDLL(None, use_errno=True)
    ruleset = _checked(
        libc.syscall(_CREATE_RULESET, ctypes.byref(Ruleset(_WRITE_RIGHTS)),
                     ctypes.sizeof(Ruleset), 0),
        "landlock_create_ruleset",
    )
    try:
        # Allow writing only to the explicitly separate results directory and
        # /tmp (needed by libraries). No rule permits writes to source data.
        for directory in dict.fromkeys((write_directory, Path("/tmp"))):
            parent = os.open(directory, os.O_PATH | os.O_CLOEXEC)
            try:
                _checked(
                    libc.syscall(_ADD_RULE, ruleset, _PATH_BENEATH,
                                 ctypes.byref(PathBeneath(_WRITE_RIGHTS, parent)), 0),
                    "landlock_add_rule",
                )
            finally:
                os.close(parent)
        _checked(libc.prctl(_PR_SET_NO_NEW_PRIVS, 1, 0, 0, 0), "no_new_privs")
        _checked(libc.syscall(_RESTRICT_SELF, ruleset, 0), "landlock_restrict_self")
    finally:
        os.close(ruleset)


def validate_paths(archive: Path, results: Path) -> tuple[Path, Path]:
    archive = archive.resolve(strict=True)
    results = results.resolve(strict=True)
    if not archive.is_dir() or not results.is_dir():
        raise ValueError("archive and results must be existing directories")
    if archive == results or archive in results.parents or results in archive.parents:
        raise ValueError("archive and results must not overlap")
    if results == Path("/tmp") or Path("/tmp") in archive.parents:
        raise ValueError("reserve /tmp for scratch, not canonical archive or results")
    if not (archive / "dataset_summary.json").is_file():
        raise ValueError("dataset_summary.json is missing; wrong archive")
    if not os.access(archive, os.R_OK | os.X_OK):
        raise PermissionError("research user cannot read archive")
    if not os.access(results, os.W_OK | os.X_OK):
        raise PermissionError("research user cannot write results")
    if os.geteuid() == 0:
        raise PermissionError("launch as unprivileged ktrader, not root")
    return archive, results


def run(archive: Path, results: Path, command: list[str], *,
        memory_mib: int, cpu_seconds: int, max_file_mib: int,
        wall_seconds: int) -> int:
    archive, results = validate_paths(archive, results)
    if not command:
        raise ValueError("a command is required")
    if min(memory_mib, cpu_seconds, max_file_mib, wall_seconds) < 1:
        raise ValueError("positive resource limits required")

    def limit_child() -> None:
        os.setsid()
        resource.setrlimit(resource.RLIMIT_AS, (memory_mib << 20, memory_mib << 20))
        resource.setrlimit(resource.RLIMIT_CPU, (cpu_seconds, cpu_seconds))
        resource.setrlimit(resource.RLIMIT_FSIZE, (max_file_mib << 20, max_file_mib << 20))
        _apply_landlock(results)

    environment = dict(os.environ)
    environment["KTRADER_RESEARCH_ARCHIVE"] = str(archive)
    environment["KTRADER_RESEARCH_RESULTS"] = str(results)
    process = subprocess.Popen(command, preexec_fn=limit_child, env=environment,
                               cwd=str(results), close_fds=True)
    try:
        return process.wait(timeout=wall_seconds)
    except subprocess.TimeoutExpired:
        os.killpg(process.pid, signal.SIGKILL)
        process.wait()
        return 124


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", type=Path, default=DEFAULT_ARCHIVE)
    parser.add_argument("--results", required=True, type=Path)
    parser.add_argument("--memory-mib", type=int, default=512)
    parser.add_argument("--cpu-seconds", type=int, default=30)
    parser.add_argument("--max-file-mib", type=int, default=32)
    parser.add_argument("--wall-seconds", type=int, default=60)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("command", nargs=argparse.REMAINDER)
    args = parser.parse_args(argv)
    command = args.command[1:] if args.command[:1] == ["--"] else args.command
    if args.self_test:
        # Attempt O_WRONLY only; do NOT write even if protection fails.
        script = (
            "import json,os,pathlib,errno;"
            "p=pathlib.Path(os.environ['KTRADER_RESEARCH_ARCHIVE']);"
            "s=json.loads((p/'dataset_summary.json').read_text());"
            "f=p/'dataset_summary.json';"
            "blocked=False;"
            "\\ntry: fd=os.open(f,os.O_WRONLY);os.close(fd)"
            "\\nexcept OSError as e: blocked=e.errno in (errno.EPERM,errno.EACCES)"
            "\\nprint(json.dumps({'source_read':True,'source_write_denied':blocked,"
            "'panel_size':s.get('panel_size')}));"
            "\\nsys.exit(0 if blocked else 2)"
        ).replace("\\n", "\n")
        script = "import sys\n" + script
        command = [sys.executable, "-c", script]
    try:
        return run(args.archive, args.results, command, memory_mib=args.memory_mib,
                   cpu_seconds=args.cpu_seconds, max_file_mib=args.max_file_mib,
                   wall_seconds=args.wall_seconds)
    except (OSError, ValueError, RuntimeError) as exc:
        print(f"RESEARCH_LAUNCH_DENIED: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
