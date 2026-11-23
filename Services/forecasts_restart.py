"""Backup and initial seed generator for ScanWait Wales forecasts.

Step-by-step workflow when run manually (``python -B forecasts_restart.py``):
1. Ensures ``forecasts_restart_datasets/`` exists and prevents ``__pycache__``
   bytecode files from being written to disk.
2. Reads ALL raw dataset files (``.csv``, ``.xlsx``, ``.xls``) placed inside
   ``forecasts_restart_datasets/`` (which is ignored in ``.gitignore``).
3. Processes and combines all raw records into an initial forecasts table.
4. Writes ``forecasts_restart_[timestamp]_[datestamp].csv`` directly inside
   ``forecasts_restart_datasets/`` with NO archiving and NO deleting of any
   files in ``forecasts_restart_datasets/``.
5. Writes a timestamped log file ``forecasts_restart_log_[timestamp]_[datestamp].txt``
   inside ``forecasts_restart_datasets/``.
"""

from __future__ import annotations

import sys

# Prevent Python from writing .pyc bytecode files or __pycache__ folders
sys.dont_write_bytecode = True

from datetime import datetime
from pathlib import Path
import re
import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RESTART_DIR = PROJECT_ROOT / "forecasts_restart_datasets"


def _parse_week_lower(label: object) -> float:
    """Extract lower week bound from a StatsWales waiting-time label."""
    text = str(label).strip().lower()
    if text in {"total waiting", "over 8 weeks", "up to 8 weeks", "nan", ""}:
        return np.nan
    if text == "forty weeks and over":
        return 40.0
    nums = re.findall(r"\d+", text)
    return float(int(nums[0])) if nums else np.nan


def _median_band_upper(week_totals: dict[int, float]) -> float | None:
    """Compute conservative median waiting-time band upper bound."""
    total = sum(v for v in week_totals.values() if v > 0)
    if total <= 0:
        return None
    half = total / 2.0
    running = 0.0
    for wk in sorted(week_totals):
        running += week_totals[wk]
        if running >= half:
            return 40.0 if wk >= 40 else float(wk + 1)
    return None


def _load_single_raw_file(file_path: Path, log_lines: list[str]) -> pd.DataFrame:
    """Load a single raw StatsWales CSV or Excel file and normalise rows."""
    suffix = file_path.suffix.lower()
    if suffix == ".csv":
        raw = pd.read_csv(file_path)
    elif suffix in {".xlsx", ".xls"}:
        raw = pd.read_excel(file_path)
    else:
        log_lines.append(f"[SKIP] Unsupported file extension for {file_path.name}")
        return pd.DataFrame()

    # Handle StatsWales CSVs that may have leading/trailing metadata or standard headers
    required_cols = {"Date", "Service", "Local health board or site", "Weeks waiting", "Data values"}
    if not required_cols.issubset(raw.columns):
        log_lines.append(
            f"[SKIP] {file_path.name} missing expected StatsWales columns; found {list(raw.columns)[:8]}"
        )
        return pd.DataFrame()

    df = raw.copy()
    df["date_ref"] = pd.to_datetime(df["Date"], format="%B %Y", errors="coerce")
    df = df.dropna(subset=["date_ref"])
    df["week_num"] = df["Weeks waiting"].apply(_parse_week_lower)
    df = df.dropna(subset=["week_num"])
    df["week_num"] = df["week_num"].astype(int)
    df["Data values"] = pd.to_numeric(df["Data values"], errors="coerce").fillna(0.0)

    age_col = df.get("Age group", pd.Series(["18 years of age and over"] * len(df), index=df.index))
    df["adult"] = (
        age_col.astype(str).str.lower().str.contains("under 18|child|0-17")
    ).map({True: 0, False: 1})

    records: list[dict] = []
    group_cols = ["date_ref", "Date", "Local health board or site", "Service", "adult"]
    for (dt_ref, dt_str, hosp, svc, adult_flag), grp in df.groupby(group_cols, sort=True):
        wk_map = grp.groupby("week_num")["Data values"].sum().to_dict()
        med_wait = _median_band_upper(wk_map)
        if med_wait is None:
            continue
        records.append(
            {
                "date_key": dt_ref.strftime("%Y-%m"),
                "date_label": str(dt_str),
                "hospital_name": str(hosp).strip(),
                "scan_choice": str(svc).strip(),
                "adult": int(adult_flag),
                "current_wait_weeks": med_wait,
                "predicted_wait_weeks": med_wait,
                "wait_trend": "stable",
                "source_file": file_path.name,
            }
        )

    out = pd.DataFrame(records)
    log_lines.append(
        f"[READ] Processed {file_path.name} -> {len(out):,} aggregated rows."
    )
    return out


def run_forecasts_restart() -> tuple[Path, Path]:
    """Read ALL raw files in forecasts_restart_datasets/ and output a timestamped CSV + log."""
    RESTART_DIR.mkdir(parents=True, exist_ok=True)

    now = datetime.now()
    # Format: [timestamp]_[datestamp] -> HHMMSS_DDMMYYYY
    ts_ds = now.strftime("%H%M%S_%d%m%Y")
    output_csv = RESTART_DIR / f"forecasts_restart_{ts_ds}.csv"
    output_log = RESTART_DIR / f"forecasts_restart_log_{ts_ds}.txt"

    log_lines: list[str] = [
        "=" * 65,
        "Script: forecasts_restart.py (Initial Seed / Backup Generator)",
        f"Started: {now.strftime('%Y-%m-%d %H:%M:%S')}",
        f"Input/Output Folder: {RESTART_DIR} (no archiving, no deleting)",
        "=" * 65,
    ]

    # Collect all raw files in forecasts_restart_datasets/, excluding previous outputs/logs
    candidates = [
        p
        for p in sorted(RESTART_DIR.iterdir())
        if p.is_file()
        and p.name != ".gitkeep"
        and not p.name.startswith("forecasts_restart_")
        and p.suffix.lower() in {".csv", ".xlsx", ".xls"}
    ]

    log_lines.append(f"Found {len(candidates)} raw dataset file(s) in {RESTART_DIR.name}/.")

    frames: list[pd.DataFrame] = []
    for raw_file in candidates:
        parsed = _load_single_raw_file(raw_file, log_lines)
        if not parsed.empty:
            frames.append(parsed)

    if frames:
        combined = pd.concat(frames, ignore_index=True)
        combined = combined.sort_values(
            ["date_key", "hospital_name", "scan_choice", "adult", "source_file"]
        ).reset_index(drop=True)

        # Compute sequential forecast/trend per (hospital_name, scan_choice, adult)
        enriched_parts: list[pd.DataFrame] = []
        for (_, _, _), grp in combined.groupby(
            ["hospital_name", "scan_choice", "adult"], sort=False
        ):
            grp = grp.sort_values("date_key").reset_index(drop=True)
            waits = grp["current_wait_weeks"].tolist()
            preds: list[float] = []
            trends: list[str] = []
            for idx, w in enumerate(waits):
                if idx == 0:
                    p = w
                else:
                    drift = w - waits[idx - 1]
                    p = max(1.0, round(w + 0.5 * drift, 2))
                preds.append(p)
                if p > w:
                    trends.append("rising")
                elif p < w:
                    trends.append("falling")
                else:
                    trends.append("stable")
            grp["predicted_wait_weeks"] = preds
            grp["wait_trend"] = trends
            enriched_parts.append(grp)

        final_df = pd.concat(enriched_parts, ignore_index=True).sort_values(
            ["date_key", "hospital_name", "scan_choice", "adult"]
        ).reset_index(drop=True)
    else:
        log_lines.append(
            "[WARNING] No valid raw StatsWales files found; writing empty schema template CSV."
        )
        final_df = pd.DataFrame(
            columns=[
                "date_key",
                "date_label",
                "hospital_name",
                "scan_choice",
                "adult",
                "current_wait_weeks",
                "predicted_wait_weeks",
                "wait_trend",
                "source_file",
            ]
        )

    final_df.to_csv(output_csv, index=False)
    log_lines.append(
        f"[OUTPUT CSV] Wrote {output_csv.name} ({len(final_df):,} rows, "
        f"{output_csv.stat().st_size / 1024:.1f} KB)."
    )
    log_lines.append(f"Finished: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    log_lines.append("=" * 65)

    output_log.write_text("\n".join(log_lines) + "\n", encoding="utf-8")
    for line in log_lines:
        print(line)

    return output_csv, output_log


if __name__ == "__main__":
    run_forecasts_restart()
