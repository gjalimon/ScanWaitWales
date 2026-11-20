"""Shared execution logger for ScanWait Wales scripts.

Creates a timestamped log file in ``logs/`` with the naming pattern:
    [HHMMSS]_[DDMMYYYY]_[script_name].txt

Mirrors stdout/stderr to the log file so every manual or scheduled run
leaves a complete audit trail.
"""

from __future__ import annotations

import atexit
from datetime import datetime
from pathlib import Path
import sys
from typing import TextIO

sys.dont_write_bytecode = True

PROJECT_ROOT = Path(__file__).resolve().parent.parent
LOGS_DIR = PROJECT_ROOT / "logs"


class _TeeStream:
    """Write output simultaneously to the original stream and a log file."""

    def __init__(self, primary: TextIO, log_file: TextIO) -> None:
        self._primary = primary
        self._log_file = log_file

    def write(self, data: str) -> int:
        written = self._primary.write(data)
        self._log_file.write(data)
        self._log_file.flush()
        return written

    def flush(self) -> None:
        self._primary.flush()
        self._log_file.flush()

    def isatty(self) -> bool:
        return getattr(self._primary, "isatty", lambda: False)()


_INITIALISED_SCRIPTS: set[str] = set()


def setup_script_logger(script_name: str) -> Path:
    """Create a timestamped log file for ``script_name`` and mirror console output."""
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    clean_name = Path(script_name).stem
    timestamp = datetime.now().strftime("%H%M%S_%d%m%Y")
    log_path = LOGS_DIR / f"{timestamp}_{clean_name}.txt"

    if clean_name in _INITIALISED_SCRIPTS:
        return log_path

    log_file = log_path.open("a", encoding="utf-8")
    header = (
        f"{'=' * 65}\n"
        f"Script: {clean_name}.py\n"
        f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        f"Log file: {log_path.name}\n"
        f"{'=' * 65}\n"
    )
    log_file.write(header)
    log_file.flush()

    orig_stdout = sys.stdout
    orig_stderr = sys.stderr
    sys.stdout = _TeeStream(orig_stdout, log_file)
    sys.stderr = _TeeStream(orig_stderr, log_file)

    def _close_log() -> None:
        try:
            log_file.write(
                f"\n{'=' * 65}\n"
                f"Finished: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                f"{'=' * 65}\n"
            )
            log_file.flush()
            sys.stdout = orig_stdout
            sys.stderr = orig_stderr
            log_file.close()
        except Exception:
            pass

    atexit.register(_close_log)
    _INITIALISED_SCRIPTS.add(clean_name)
    return log_path
