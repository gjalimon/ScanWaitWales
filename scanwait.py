"""Fast waiting-time lookup and gauge helpers reading from ``published_dataset/``.

Expects strictly ONE validated CSV file inside ``published_dataset/``, generated
by running ``python -B Services/data_loader.py``.
"""

from __future__ import annotations

from pathlib import Path
import sys

sys.dont_write_bytecode = True

import pandas as pd

from Services.waiting_math import calculate_needle_angle, classify_wait_time
from scan_config import (
    SCAN_SERVICE_MAP,
    get_hospital_choices,
    get_scan_choices,
    hospital_has_service,
)

PROJECT_ROOT = Path(__file__).resolve().parent
PUBLISHED_DIR = PROJECT_ROOT / "published_dataset"


def load_published_dataset() -> pd.DataFrame:
    """Load the single active CSV from ``published_dataset/``."""
    if not PUBLISHED_DIR.exists():
        raise FileNotFoundError(
            f"Published dataset folder does not exist: {PUBLISHED_DIR}"
        )

    csv_files = sorted(
        f for f in PUBLISHED_DIR.glob("*.csv") if f.is_file()
    )

    if len(csv_files) == 0:
        raise FileNotFoundError(
            f"No CSV file found in {PUBLISHED_DIR}. "
            "Run 'python -B Services/data_loader.py' first to generate the live dataset."
        )

    if len(csv_files) > 1:
        raise RuntimeError(
            f"Expected strictly 1 CSV file in {PUBLISHED_DIR}, found {len(csv_files)}: "
            f"{[f.name for f in csv_files]}. Archive older files before starting the app."
        )

    active_file = csv_files[0]
    df = pd.read_csv(active_file)
    df["adult"] = pd.to_numeric(df["adult"], errors="coerce").fillna(1).astype(int)
    print(f"  [OK] Loaded published dataset: {active_file.name} ({len(df):,} rows)")
    return df


print("=" * 55)
print("  Loading published ScanWait dataset...")
print("=" * 55)
CSV_FILE = load_published_dataset()
print()


def load_waiting_times(csv_data: pd.DataFrame) -> pd.DataFrame:
    """Return a clean copy of the pre-computed published dataset."""
    return csv_data.copy()


def get_wait_record(
    data: pd.DataFrame,
    scan_choice: str,
    hospital_choice: str,
    adult: int = 1,
) -> dict | None:
    """Return the pre-computed waiting-time & stock-and-flow record for a selection."""
    if scan_choice not in SCAN_SERVICE_MAP:
        return None
    if hospital_choice not in get_hospital_choices():
        return None
    if not hospital_has_service(hospital_choice, scan_choice):
        return None

    adult_flag = 1 if int(adult) == 1 else 0
    matched = data[
        (data["hospital_name"] == hospital_choice)
        & (data["scan_choice"] == scan_choice)
        & (data["adult"] == adult_flag)
    ]

    if matched.empty:
        return None

    row = matched.iloc[0]
    typical_wait = (
        None if pd.isna(row["typical_wait_weeks"]) else int(round(float(row["typical_wait_weeks"])))
    )
    predicted_wait = (
        None
        if pd.isna(row.get("predicted_wait_weeks"))
        else int(round(float(row["predicted_wait_weeks"])))
    )
    clearance_rate = (
        None
        if pd.isna(row.get("clearance_rate_pct"))
        else float(row["clearance_rate_pct"])
    )

    return {
        "typical_wait_weeks": typical_wait,
        "predicted_wait_weeks": predicted_wait,
        "wait_trend": str(row.get("wait_trend", "stable")),
        "clearance_rate_pct": clearance_rate,
        "colour_zone": str(row.get("colour_zone", classify_wait_time(typical_wait))),
        "needle_angle": float(row.get("needle_angle", calculate_needle_angle(typical_wait))),
        "latest_date": str(row.get("latest_date", "latest month")),
    }


def get_typical_wait_weeks(
    data: pd.DataFrame,
    scan_choice: str,
    hospital_choice: str,
    adult: int = 1,
) -> int | None:
    """Return typical wait in weeks for an approved (hospital, scan, age cohort)."""
    record = get_wait_record(data, scan_choice, hospital_choice, adult=adult)
    if record is None:
        return None
    return record["typical_wait_weeks"]


def get_scan() -> list[str]:
    return get_scan_choices()


def get_hospital() -> list[str]:
    return get_hospital_choices()


def get_max_date() -> str:
    if CSV_FILE.empty or "latest_date" not in CSV_FILE.columns:
        return "latest month"
    return str(CSV_FILE["latest_date"].dropna().iloc[0])
