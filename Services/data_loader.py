"""Manual data loader & publisher for ScanWait Wales.

Workflow when run manually (``python -B Services/data_loader.py``):
1. Downloads the latest raw CSV dataset from the StatsWales API and saves it to
   ``raw_datasets/statswales_raw_[HHMMSS]_[DDMMYYYY].csv`` (preserving all raw downloads).
2. Reads ``reference_datasets/selected_hospitals_services_coordinates.csv`` to verify
   which hospitals and diagnostic scanners exist (eliminating ghost scanners).
3. Computes median waiting times and stock-and-flow predictions for both
   Adult (18+, ``adult=1``) and Child (under-18, ``adult=0``) cohorts.
4. Validates schema, data types, and row integrity.
5. Archives any existing file in ``published_dataset/`` into ``archived_dataset/``
   so ``published_dataset/`` strictly holds ONE current file.
6. Writes the slimmed, fast-loading output CSV:
   ``published_dataset/[HHMMSS]_[DDMMYYYY].csv``
"""
from datetime import datetime
import io
from pathlib import Path
import shutil
import sys

sys.dont_write_bytecode = True

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import pandas as pd
import requests

from Services.logger import setup_script_logger
from Services.waiting_math import (
    AGE_GROUP_MAP,
    calculate_needle_angle,
    classify_wait_time,
    compute_stock_and_flow_metrics,
    compute_wait_percentiles,
    get_week_number,
    median_band_from_week_totals,
)
from scan_config import (
    SCAN_SERVICE_MAP,
    get_hospital_choices,
    get_scan_choices,
    hospital_has_service,
)

# StatsWales "Diagnostic Services: pathway waiting times" dataset ID
DATASET_ID = "3c2720e6-95ae-4eeb-9e88-ed74bb40c6b9"
DOWNLOAD_URL = f"https://api.stats.gov.wales/v1/{DATASET_ID}/download/csv"

RAW_DIR = PROJECT_ROOT / "raw_datasets"
PUBLISHED_DIR = PROJECT_ROOT / "published_dataset"
ARCHIVED_DIR = PROJECT_ROOT / "archived_dataset"

REQUIRED_PUBLISHED_COLUMNS = [
    "hospital_name",
    "scan_choice",
    "adult",
    "latest_date",
    "typical_wait_weeks",
    "wait_weeks_25pct",
    "wait_weeks_75pct",
    "predicted_wait_weeks",
    "wait_trend",
    "clearance_rate_pct",
    "colour_zone",
    "needle_angle",
]


def _ensure_directories() -> None:
    for folder in (RAW_DIR, PUBLISHED_DIR, ARCHIVED_DIR):
        folder.mkdir(parents=True, exist_ok=True)


def _download_raw_csv(timestamp_str: str) -> tuple[pd.DataFrame, Path]:
    """Download fresh CSV from StatsWales and save to raw_datasets/."""
    print(f"[DOWNLOAD] Fetching StatsWales dataset from {DOWNLOAD_URL} ...")
    response = requests.get(DOWNLOAD_URL, timeout=90)
    response.raise_for_status()

    raw_filename = f"statswales_raw_{timestamp_str}.csv"
    raw_path = RAW_DIR / raw_filename
    raw_path.write_text(response.text, encoding="utf-8")
    print(f"[RAW SAVED] {raw_path} ({raw_path.stat().st_size / (1024 * 1024):.2f} MB)")

    df = pd.read_csv(io.StringIO(response.text))
    print(f"[LOADED] Raw dataset contains {len(df):,} rows and {len(df.columns)} columns.")
    return df, raw_path


def _build_published_table(raw_df: pd.DataFrame) -> pd.DataFrame:
    """Filter valid scanners, compute Adult & Child waits + stock-and-flow trends."""
    approved_hospitals = set(get_hospital_choices())
    all_scan_choices = get_scan_choices()

    # Keep only approved hospital sites (removes ghost/unapproved sites immediately)
    df = raw_df[raw_df["Local health board or site"].isin(approved_hospitals)].copy()
    df["Date_reference"] = pd.to_datetime(df["Date"], format="%B %Y", errors="coerce")
    df = df.dropna(subset=["Date_reference"])

    if df.empty:
        raise ValueError("Filtered dataset is empty after matching approved hospitals.")

    latest_date_ref = df["Date_reference"].max()
    latest_date_label = str(
        df.loc[df["Date_reference"] == latest_date_ref, "Date"].iloc[0]
    )
    print(f"[INFO] Latest reporting month in dataset: {latest_date_label}")

    df["week_num"] = df["Weeks waiting"].apply(get_week_number)
    df = df.dropna(subset=["week_num"])
    df["week_num"] = df["week_num"].astype(int)
    df["Data values"] = pd.to_numeric(df["Data values"], errors="coerce").fillna(0.0)

    records: list[dict] = []

    for hospital in sorted(approved_hospitals):
        hosp_df = df[df["Local health board or site"] == hospital]

        for scan_choice in all_scan_choices:
            # Verify against selected_hospitals_services_coordinates.csv
            if not hospital_has_service(hospital, scan_choice):
                continue

            source_services = SCAN_SERVICE_MAP[scan_choice]
            scan_df = hosp_df[hosp_df["Service"].isin(source_services)]

            for adult_flag, age_label in AGE_GROUP_MAP.items():
                age_df = scan_df[scan_df["Age group"] == age_label]

                # Build chronological monthly series for stock-and-flow modelling
                monthly_series: list[dict] = []
                for (date_ref, date_str), grp in age_df.groupby(
                    ["Date_reference", "Date"], sort=True
                ):
                    week_totals = (
                        grp.groupby("week_num")["Data values"].sum().to_dict()
                    )
                    total_waiting = float(sum(week_totals.values()))
                    wait_25pct, typical_wait, wait_75pct = compute_wait_percentiles(
                        week_totals
                    )
                    monthly_series.append(
                        {
                            "date_ref": date_ref,
                            "date_str": str(date_str),
                            "week_totals": week_totals,
                            "total_waiting": total_waiting,
                            "typical_wait_weeks": typical_wait,
                            "wait_weeks_25pct": wait_25pct,
                            "wait_weeks_75pct": wait_75pct,
                        }
                    )

                enriched = compute_stock_and_flow_metrics(monthly_series)
                latest_entries = [
                    item for item in enriched if item["date_ref"] == latest_date_ref
                ]

                if latest_entries:
                    latest_item = latest_entries[0]
                    typical_wait = latest_item["typical_wait_weeks"]
                    wait_25pct = latest_item["wait_weeks_25pct"]
                    wait_75pct = latest_item["wait_weeks_75pct"]
                    predicted_wait = latest_item["predicted_wait_weeks"]
                    wait_trend = latest_item["wait_trend"]
                    clearance_rate = latest_item["clearance_rate_pct"]
                else:
                    typical_wait = None
                    wait_25pct = None
                    wait_75pct = None
                    predicted_wait = None
                    wait_trend = "stable"
                    clearance_rate = None

                records.append(
                    {
                        "hospital_name": hospital,
                        "scan_choice": scan_choice,
                        "adult": int(adult_flag),
                        "latest_date": latest_date_label,
                        "typical_wait_weeks": typical_wait,
                        "wait_weeks_25pct": wait_25pct,
                        "wait_weeks_75pct": wait_75pct,
                        "predicted_wait_weeks": predicted_wait,
                        "wait_trend": wait_trend,
                        "clearance_rate_pct": clearance_rate,
                        "colour_zone": classify_wait_time(typical_wait),
                        "needle_angle": calculate_needle_angle(typical_wait),
                    }
                )

    published_df = pd.DataFrame(records, columns=REQUIRED_PUBLISHED_COLUMNS)
    return published_df


def _validate_published_df(df: pd.DataFrame) -> None:
    """Run strict validation checks before publishing."""
    if df.empty:
        raise ValueError("Validation failed: published DataFrame is empty.")

    missing_cols = set(REQUIRED_PUBLISHED_COLUMNS) - set(df.columns)
    if missing_cols:
        raise ValueError(f"Validation failed: missing columns {missing_cols}")

    if not set(df["adult"].unique()).issubset({0, 1}):
        raise ValueError("Validation failed: 'adult' column must only contain 0 or 1.")

    if not set(df["colour_zone"].unique()).issubset({"green", "orange", "red"}):
        raise ValueError("Validation failed: invalid 'colour_zone' values detected.")

    # Confirm no unapproved hospital/service pair exists
    for _, row in df.iterrows():
        if not hospital_has_service(row["hospital_name"], row["scan_choice"]):
            raise ValueError(
                f"Ghost scanner leak detected: {row['scan_choice']} at {row['hospital_name']}"
            )

    print(
        f"[VALIDATED] {len(df):,} rows passed schema, cohort (adult 0/1), and scanner checks."
    )


def _archive_existing_published() -> None:
    """Move any existing file(s) in published_dataset/ to archived_dataset/."""
    for item in PUBLISHED_DIR.iterdir():
        if item.name == ".gitkeep":
            continue
        dest = ARCHIVED_DIR / item.name
        if dest.exists():
            stem = dest.stem
            suffix = dest.suffix
            dest = ARCHIVED_DIR / f"{stem}_archived_{datetime.now().strftime('%H%M%S')}{suffix}"
        shutil.move(str(item), str(dest))
        print(f"[ARCHIVED] Moved old published file -> {dest}")


def run_data_loader() -> Path:
    """Execute the full manual data loading, validation, archiving, and publishing run."""
    setup_script_logger("data_loader")
    _ensure_directories()

    timestamp_str = datetime.now().strftime("%H%M%S_%d%m%Y")
    raw_df, _ = _download_raw_csv(timestamp_str)

    published_df = _build_published_table(raw_df)
    _validate_published_df(published_df)

    _archive_existing_published()

    output_path = PUBLISHED_DIR / f"{timestamp_str}.csv"
    published_df.to_csv(output_path, index=False)
    print(
        f"[PUBLISHED] Created {output_path} "
        f"({output_path.stat().st_size / 1024:.1f} KB, {len(published_df)} rows)"
    )
    return output_path


if __name__ == "__main__":
    run_data_loader()
