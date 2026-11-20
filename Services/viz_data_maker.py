"""Build unified historical & stock-and-flow visualisation dataset.

Workflow when run manually (``python -B Services/viz_data_maker.py``):
1. Reads the latest raw StatsWales CSV from ``raw_datasets/``.
2. Filters against ``reference_datasets/selected_hospitals_services_coordinates.csv``
   so ghost scanners never appear in charts.
3. Computes monthly historical waiting times, total queue sizes, and stock-and-flow
   metrics for both Adult (``adult=1``) and Child (``adult=0``) cohorts.
4. Merges historical records from any existing file in ``visualisation_dataset/`` or
   ``archived_viz_dataset/`` so multi-year time series remain intact even if StatsWales
   trims older months.
5. Archives the current file in ``visualisation_dataset/`` to ``archived_viz_dataset/``
   and writes ``visualisation_dataset/visualisation_[HHMMSS]_[DDMMYYYY].csv``.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
import shutil
import sys

sys.dont_write_bytecode = True

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import pandas as pd

from Services.logger import setup_script_logger
from Services.waiting_math import (
    AGE_GROUP_MAP,
    compute_stock_and_flow_metrics,
    get_week_number,
    median_band_from_week_totals,
)
from scan_config import (
    SCAN_SERVICE_MAP,
    get_hospital_choices,
    get_scan_choices,
    hospital_has_service,
)

RAW_DIR = PROJECT_ROOT / "raw_datasets"
VIZ_DIR = PROJECT_ROOT / "visualisation_dataset"
ARCHIVED_VIZ_DIR = PROJECT_ROOT / "archived_viz_dataset"

VIZ_COLUMNS = [
    "Date",
    "Date_YYYY_MM",
    "Hospital",
    "Service_Display",
    "adult",
    "Estimated_Median_Waiting_Weeks",
    "Predicted_Wait_Weeks",
    "Wait_Trend",
    "Total_Waiting",
    "Clearance_Rate_Pct",
]


def _ensure_directories() -> None:
    for folder in (RAW_DIR, VIZ_DIR, ARCHIVED_VIZ_DIR):
        folder.mkdir(parents=True, exist_ok=True)


def _get_latest_raw_file() -> Path:
    raw_files = sorted(
        (f for f in RAW_DIR.glob("*.csv") if f.is_file()),
        key=lambda p: p.stat().st_mtime,
    )
    if not raw_files:
        raise FileNotFoundError(
            f"No raw CSV files found in {RAW_DIR}. Run Services/data_loader.py first."
        )
    return raw_files[-1]


def _load_archived_history() -> pd.DataFrame:
    """Collect historical rows from existing visualisation files so history is preserved."""
    frames: list[pd.DataFrame] = []
    for folder in (ARCHIVED_VIZ_DIR, VIZ_DIR):
        for csv_file in sorted(folder.glob("visualisation_*.csv")):
            try:
                hist_df = pd.read_csv(csv_file)
                if set(VIZ_COLUMNS).issubset(hist_df.columns):
                    frames.append(hist_df[VIZ_COLUMNS])
            except Exception as exc:
                print(f"[WARNING] Skipping unreadable archive {csv_file.name}: {exc}")

    if not frames:
        return pd.DataFrame(columns=VIZ_COLUMNS)

    combined = pd.concat(frames, ignore_index=True)
    combined = combined.drop_duplicates(
        subset=["Date_YYYY_MM", "Hospital", "Service_Display", "adult"],
        keep="last",
    )
    return combined


def _build_viz_dataframe(raw_df: pd.DataFrame) -> pd.DataFrame:
    approved_hospitals = set(get_hospital_choices())
    all_scan_choices = get_scan_choices()

    df = raw_df[raw_df["Local health board or site"].isin(approved_hospitals)].copy()
    df["Date_reference"] = pd.to_datetime(df["Date"], format="%B %Y", errors="coerce")
    df = df.dropna(subset=["Date_reference"])

    df["week_num"] = df["Weeks waiting"].apply(get_week_number)
    df = df.dropna(subset=["week_num"])
    df["week_num"] = df["week_num"].astype(int)
    df["Data values"] = pd.to_numeric(df["Data values"], errors="coerce").fillna(0.0)

    records: list[dict] = []

    for hospital in sorted(approved_hospitals):
        hosp_df = df[df["Local health board or site"] == hospital]

        for scan_choice in all_scan_choices:
            if not hospital_has_service(hospital, scan_choice):
                continue

            source_services = SCAN_SERVICE_MAP[scan_choice]
            scan_df = hosp_df[hosp_df["Service"].isin(source_services)]

            for adult_flag, age_label in AGE_GROUP_MAP.items():
                age_df = scan_df[scan_df["Age group"] == age_label]
                monthly_series: list[dict] = []

                for (date_ref, date_str), grp in age_df.groupby(
                    ["Date_reference", "Date"], sort=True
                ):
                    week_totals = (
                        grp.groupby("week_num")["Data values"].sum().to_dict()
                    )
                    total_waiting = float(sum(week_totals.values()))
                    typical_wait = median_band_from_week_totals(week_totals)
                    monthly_series.append(
                        {
                            "date_ref": date_ref,
                            "date_str": str(date_str),
                            "week_totals": week_totals,
                            "total_waiting": total_waiting,
                            "typical_wait_weeks": typical_wait,
                        }
                    )

                enriched = compute_stock_and_flow_metrics(monthly_series)
                for item in enriched:
                    records.append(
                        {
                            "Date": item["date_str"],
                            "Date_YYYY_MM": item["date_ref"].strftime("%Y-%m"),
                            "Hospital": hospital,
                            "Service_Display": scan_choice,
                            "adult": int(adult_flag),
                            "Estimated_Median_Waiting_Weeks": item["typical_wait_weeks"],
                            "Predicted_Wait_Weeks": item["predicted_wait_weeks"],
                            "Wait_Trend": item["wait_trend"],
                            "Total_Waiting": item["total_waiting"],
                            "Clearance_Rate_Pct": item["clearance_rate_pct"],
                        }
                    )

    fresh_df = pd.DataFrame(records, columns=VIZ_COLUMNS)
    archived_df = _load_archived_history()

    if not archived_df.empty:
        merged = pd.concat([archived_df, fresh_df], ignore_index=True)
        merged = merged.drop_duplicates(
            subset=["Date_YYYY_MM", "Hospital", "Service_Display", "adult"],
            keep="last",
        )
    else:
        merged = fresh_df

    merged = merged.sort_values(
        by=["Date_YYYY_MM", "Hospital", "Service_Display", "adult"]
    ).reset_index(drop=True)
    return merged


def _archive_existing_viz() -> None:
    """Move any existing file(s) in visualisation_dataset/ to archived_viz_dataset/."""
    for item in VIZ_DIR.iterdir():
        if item.name == ".gitkeep":
            continue
        dest = ARCHIVED_VIZ_DIR / item.name
        if dest.exists():
            dest = ARCHIVED_VIZ_DIR / f"{dest.stem}_archived_{datetime.now().strftime('%H%M%S')}{dest.suffix}"
        shutil.move(str(item), str(dest))
        print(f"[ARCHIVED VIZ] Moved old visualisation file -> {dest}")


def run_viz_data_maker() -> Path:
    setup_script_logger("viz_data_maker")
    _ensure_directories()

    latest_raw = _get_latest_raw_file()
    print(f"[SOURCE] Reading latest raw dataset: {latest_raw.name}")
    raw_df = pd.read_csv(latest_raw)

    viz_df = _build_viz_dataframe(raw_df)
    if viz_df.empty:
        raise ValueError("Visualisation dataset generation produced 0 rows.")

    _archive_existing_viz()

    timestamp_str = datetime.now().strftime("%H%M%S_%d%m%Y")
    output_path = VIZ_DIR / f"visualisation_{timestamp_str}.csv"
    viz_df.to_csv(output_path, index=False)
    print(
        f"[PUBLISHED VIZ] Created {output_path} "
        f"({output_path.stat().st_size / 1024:.1f} KB, {len(viz_df):,} rows)"
    )
    return output_path


if __name__ == "__main__":
    run_viz_data_maker()
