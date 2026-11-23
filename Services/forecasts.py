"""Adult-only incremental forecast dataset generator with historical monthly seasonality.

Step-by-step workflow when run manually (``python -B Services/forecasts.py``):
1. Ensures ``forecasts_dataset/`` and ``logs/`` exist and disables ``__pycache__``
   bytecode files (``sys.dont_write_bytecode = True``).
2. Loads ``reference_datasets/selected_hospitals_services_coordinates.csv`` to map
   every approved hospital to its Health Board and enforce verified scanners.
3. Loads an existing ``forecasts_dataset/forecasts_dataset.csv`` as a historical
   archive (filtering strictly to ``adult == 1`` and verified scanners).
4. Reads the latest raw StatsWales CSV in ``raw_datasets/`` (or falls back to the
   latest ``visualisation_dataset/visualisation_*.csv``) and computes monthly
   adult-only (``18 years of age and over``) queue stocks and flows.
5. Merges historical archive + new rows, deduplicates on
   ``(date_key, hospital_name, scan_choice)``, then computes calendar-month
   seasonal indices across all historical years for each (hospital, scan) series:
   - ``inflow_seasonal_index``
   - ``clearance_seasonal_index``
   - ``wait_seasonal_index``
   and updates ``predicted_wait_weeks`` and ``wait_trend`` using the next
   calendar month's seasonal factor.
6. Overwrites ``forecasts_dataset/forecasts_dataset.csv`` and logs to
   ``logs/forecasts_log.txt``.
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
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scan_config import SCAN_SERVICE_MAP, SERVICE_DISPLAY_NAMES

REF_CSV = (
    PROJECT_ROOT
    / "reference_datasets"
    / "selected_hospitals_services_coordinates.csv"
)
FORECASTS_DIR = PROJECT_ROOT / "forecasts_dataset"
FORECASTS_CSV = FORECASTS_DIR / "forecasts_dataset.csv"
LOGS_DIR = PROJECT_ROOT / "logs"
FORECASTS_LOG = LOGS_DIR / "forecasts_log.txt"

RAW_DIR = PROJECT_ROOT / "raw_datasets"
VIZ_DIR = PROJECT_ROOT / "visualisation_dataset"

HEALTH_BOARD_FULL_NAMES = {
    "Aneurin Bevan": "Aneurin Bevan University Health Board",
    "Betsi Cadwaladr": "Betsi Cadwaladr University Health Board",
    "Cardiff and Vale": "Cardiff and Vale University Health Board",
    "Cwm Taf Morgannwg": "Cwm Taf Morgannwg University Health Board",
    "Hywel Dda": "Hywel Dda University Health Board",
    "Powys": "Powys Teaching Health Board",
    "Swansea Bay": "Swansea Bay University Health Board",
}


def append_log(message: str) -> None:
    """Append a timestamped message to ``logs/forecasts_log.txt`` and print it."""
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{stamp}] {message}"
    print(line)
    with FORECASTS_LOG.open("a", encoding="utf-8") as fh:
        fh.write(line + "\n")


def _load_reference_maps() -> tuple[dict[str, str], set[tuple[str, str]]]:
    """Return (hospital -> full Health Board name, valid (hospital, service) pairs)."""
    ref = pd.read_csv(REF_CSV)
    hb_map: dict[str, str] = {}
    valid_pairs: set[tuple[str, str]] = set()

    for _, row in ref.iterrows():
        hosp = str(row["Hospital Name"]).strip()
        short_hb = str(row.get("Health board", "")).strip()
        hb_map[hosp] = HEALTH_BOARD_FULL_NAMES.get(short_hb, short_hb)

        for display_name, raw_cols in SCAN_SERVICE_MAP.items():
            has_scanner = False
            for col in raw_cols:
                if col in ref.columns and pd.to_numeric(row[col], errors="coerce") == 1:
                    has_scanner = True
                    valid_pairs.add((hosp, col))
            if has_scanner:
                valid_pairs.add((hosp, display_name))

    return hb_map, valid_pairs


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


def _find_latest_input_csv() -> tuple[str, Path]:
    """Prefer the latest raw StatsWales CSV in raw_datasets/, else visualisation_*.csv."""
    if RAW_DIR.exists():
        raw_files = sorted(
            (p for p in RAW_DIR.glob("*.csv") if p.is_file()),
            key=lambda p: p.stat().st_mtime,
        )
        if raw_files:
            return "raw", raw_files[-1]

    if VIZ_DIR.exists():
        viz_files = sorted(
            (p for p in VIZ_DIR.glob("visualisation_*.csv") if p.is_file()),
            key=lambda p: p.stat().st_mtime,
        )
        if viz_files:
            return "viz", viz_files[-1]

    raise FileNotFoundError(
        "No input CSV found in raw_datasets/ or visualisation_dataset/. "
        "Run 'python -B Services/data_loader.py' first."
    )


def _build_from_raw_csv(
    source_path: Path,
    hb_map: dict[str, str],
    valid_pairs: set[tuple[str, str]],
) -> pd.DataFrame:
    """Parse a raw StatsWales CSV into adult-only stock-and-flow monthly rows."""
    raw = pd.read_csv(source_path)
    run_ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if "Age group" in raw.columns:
        raw = raw[
            raw["Age group"].astype(str).str.strip().str.lower()
            == "18 years of age and over"
        ].copy()

    raw["date_ref"] = pd.to_datetime(raw["Date"], format="%B %Y", errors="coerce")
    raw = raw.dropna(subset=["date_ref"])
    raw["week_num"] = raw["Weeks waiting"].apply(_parse_week_lower)
    raw = raw.dropna(subset=["week_num"])
    raw["week_num"] = raw["week_num"].astype(int)
    raw["Data values"] = pd.to_numeric(raw["Data values"], errors="coerce").fillna(0.0)

    raw["Hospital"] = raw["Local health board or site"].astype(str).str.strip()
    raw["Service_Raw"] = raw["Service"].astype(str).str.strip()
    raw["Service_Display"] = raw["Service_Raw"].map(SERVICE_DISPLAY_NAMES).fillna(
        raw["Service_Raw"]
    )

    keep_mask = [
        (h in hb_map) and ((h, sr) in valid_pairs or (h, sd) in valid_pairs)
        for h, sr, sd in zip(raw["Hospital"], raw["Service_Raw"], raw["Service_Display"])
    ]
    raw = raw[keep_mask].copy()

    records: list[dict] = []
    for (hosp, scan_disp), grp in raw.groupby(["Hospital", "Service_Display"], sort=True):
        monthly_rows = []
        for (dt_ref, dt_str), m_grp in grp.groupby(["date_ref", "Date"], sort=True):
            wk_map = m_grp.groupby("week_num")["Data values"].sum().to_dict()
            total_wait = float(sum(v for v in wk_map.values() if v > 0))
            new_under_4w = float(sum(v for wk, v in wk_map.items() if wk < 4 and v > 0))
            med_wait = _median_band_upper(wk_map)
            monthly_rows.append(
                {
                    "date_ref": dt_ref,
                    "date_key": dt_ref.strftime("%Y-%m"),
                    "date_label": str(dt_str),
                    "total_waiting": total_wait,
                    "new_under_4w": new_under_4w,
                    "current_wait_weeks": med_wait,
                }
            )

        m_df = pd.DataFrame(monthly_rows).sort_values("date_ref").reset_index(drop=True)
        for i, r in m_df.iterrows():
            curr_total = float(r["total_waiting"])
            if i == 0:
                inflow = round(float(r["new_under_4w"]), 1)
                clear_pct = 50.0
            else:
                prev_total = float(m_df.loc[i - 1, "total_waiting"])
                retained = max(0.0, curr_total - float(r["new_under_4w"]))
                outflow = max(0.0, prev_total - retained)
                inflow = round(max(0.0, curr_total - prev_total + outflow), 1)
                clear_pct = (
                    round(float(np.clip((outflow / prev_total) * 100.0, 0.0, 100.0)), 2)
                    if prev_total > 0
                    else 50.0
                )

            curr_w = r["current_wait_weeks"]
            records.append(
                {
                    "date_key": r["date_key"],
                    "date_label": r["date_label"],
                    "health_board": hb_map[hosp],
                    "hospital_name": hosp,
                    "scan_choice": scan_disp,
                    "adult": 1,
                    "total_waiting": round(curr_total, 1),
                    "incoming_referrals": inflow,
                    "clearance_rate_pct": clear_pct,
                    "current_wait_weeks": curr_w,
                    "predicted_wait_weeks": curr_w,
                    "wait_trend": "stable",
                    "source_file": source_path.name,
                    "updated_at": run_ts,
                }
            )

    return pd.DataFrame(records)


def _build_from_viz_csv(
    source_path: Path,
    hb_map: dict[str, str],
    valid_pairs: set[tuple[str, str]],
) -> pd.DataFrame:
    """Fallback builder from visualisation_*.csv filtered strictly to adult == 1 and valid scanners."""
    df = pd.read_csv(source_path)
    run_ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if "adult" in df.columns:
        df = df[pd.to_numeric(df["adult"], errors="coerce").fillna(1).astype(int) == 1].copy()

    df["date_ref"] = pd.to_datetime(
        df.get("Date_YYYY_MM", df["Date"]), errors="coerce"
    )
    df = df.dropna(subset=["date_ref"]).sort_values(
        ["Hospital", "Service_Display", "date_ref"]
    )

    records: list[dict] = []
    for (hosp, scan_disp), grp in df.groupby(["Hospital", "Service_Display"], sort=True):
        hosp_clean = str(hosp).strip()
        scan_clean = str(scan_disp).strip()
        if hosp_clean not in hb_map:
            continue
        if (hosp_clean, scan_clean) not in valid_pairs:
            continue

        grp = grp.sort_values("date_ref").reset_index(drop=True)
        for i, r in grp.iterrows():
            curr_total = float(pd.to_numeric(r.get("Total_Waiting", 0), errors="coerce") or 0.0)
            clear_pct = float(pd.to_numeric(r.get("Clearance_Rate_Pct", 50.0), errors="coerce") or 50.0)
            if i == 0:
                inflow = round(curr_total * (clear_pct / 100.0), 1)
            else:
                prev_total = float(
                    pd.to_numeric(grp.loc[i - 1, "Total_Waiting"], errors="coerce") or 0.0
                )
                outflow = prev_total * (clear_pct / 100.0)
                inflow = round(max(0.0, curr_total - prev_total + outflow), 1)

            curr_w = pd.to_numeric(r.get("Estimated_Median_Waiting_Weeks"), errors="coerce")
            pred_w = pd.to_numeric(r.get("Predicted_Wait_Weeks"), errors="coerce")
            if pd.isna(pred_w):
                pred_w = curr_w

            records.append(
                {
                    "date_key": r["date_ref"].strftime("%Y-%m"),
                    "date_label": str(r["Date"]),
                    "health_board": hb_map[hosp_clean],
                    "hospital_name": hosp_clean,
                    "scan_choice": scan_clean,
                    "adult": 1,
                    "total_waiting": round(curr_total, 1),
                    "incoming_referrals": inflow,
                    "clearance_rate_pct": round(clear_pct, 2),
                    "current_wait_weeks": None if pd.isna(curr_w) else float(curr_w),
                    "predicted_wait_weeks": None if pd.isna(pred_w) else round(float(pred_w), 2),
                    "wait_trend": str(r.get("Wait_Trend", "stable")).lower(),
                    "source_file": source_path.name,
                    "updated_at": run_ts,
                }
            )

    return pd.DataFrame(records)


def _apply_historical_monthly_seasonality(df: pd.DataFrame) -> pd.DataFrame:
    """Compute calendar-month seasonal indices across all historical years and update predictions."""
    if df.empty:
        return df

    df = df.copy()
    df["_dt"] = pd.to_datetime(df["date_key"] + "-01", errors="coerce")
    df["_cal_month"] = df["_dt"].dt.month

    enriched_groups: list[pd.DataFrame] = []

    for (_, _), grp in df.groupby(["hospital_name", "scan_choice"], sort=False):
        g = grp.sort_values("date_key").reset_index(drop=True)

        # Centered 12-month moving baseline to isolate recurring calendar-month seasonality
        inflow_base = g["incoming_referrals"].rolling(12, center=True, min_periods=1).mean()
        clear_base = g["clearance_rate_pct"].rolling(12, center=True, min_periods=1).mean()
        wait_series = pd.to_numeric(g["current_wait_weeks"], errors="coerce")
        wait_base = wait_series.rolling(12, center=True, min_periods=1).mean()

        inflow_ratio = np.where(inflow_base > 0, g["incoming_referrals"] / inflow_base, 1.0)
        clear_ratio = np.where(clear_base > 0, g["clearance_rate_pct"] / clear_base, 1.0)
        wait_ratio = np.where((wait_base > 0) & wait_series.notna(), wait_series / wait_base, 1.0)

        g["_in_r"] = inflow_ratio
        g["_cl_r"] = clear_ratio
        g["_wt_r"] = wait_ratio

        raw_in, raw_cl, raw_wt, counts = {}, {}, {}, {}
        for m in range(1, 13):
            sub_m = g[g["_cal_month"] == m]
            n = len(sub_m)
            counts[m] = n
            raw_in[m] = float(sub_m["_in_r"].mean()) if n > 0 else 1.0
            raw_cl[m] = float(sub_m["_cl_r"].mean()) if n > 0 else 1.0
            raw_wt[m] = float(sub_m["_wt_r"].mean()) if n > 0 else 1.0

        obs = [m for m, n in counts.items() if n > 0]
        if obs:
            mean_in = float(np.mean([raw_in[m] for m in obs])) or 1.0
            mean_cl = float(np.mean([raw_cl[m] for m in obs])) or 1.0
            mean_wt = float(np.mean([raw_wt[m] for m in obs])) or 1.0
            for m in obs:
                raw_in[m] /= mean_in
                raw_cl[m] /= mean_cl
                raw_wt[m] /= mean_wt

        # Shrinkage damping w = n / (n + 1) so sparse years shrink smoothly toward 1.0
        idx_in, idx_cl, idx_wt = {}, {}, {}
        for m in range(1, 13):
            w = counts[m] / (counts[m] + 1.0)
            idx_in[m] = round(float(np.clip(1.0 + w * (raw_in[m] - 1.0), 0.65, 1.40)), 4)
            idx_cl[m] = round(float(np.clip(1.0 + w * (raw_cl[m] - 1.0), 0.70, 1.35)), 4)
            idx_wt[m] = round(float(np.clip(1.0 + w * (raw_wt[m] - 1.0), 0.70, 1.35)), 4)

        g["inflow_seasonal_index"] = g["_cal_month"].map(idx_in).fillna(1.0)
        g["clearance_seasonal_index"] = g["_cal_month"].map(idx_cl).fillna(1.0)
        g["wait_seasonal_index"] = g["_cal_month"].map(idx_wt).fillna(1.0)

        # Compute seasonally-adjusted next-month predicted_wait_weeks and wait_trend
        pred_waits = []
        trends = []
        for i, r in g.iterrows():
            curr_w = wait_series.iloc[i]
            if pd.isna(curr_w):
                pred_waits.append(np.nan)
                trends.append("stable")
                continue

            curr_m = int(r["_cal_month"])
            next_m = 1 if curr_m == 12 else curr_m + 1
            curr_s = idx_wt.get(curr_m, 1.0)
            next_s = idx_wt.get(next_m, 1.0)

            # Deseasonalized current wait + deseasonalized drift, re-seasonalized to next month
            deseas_curr = float(curr_w) / curr_s if curr_s > 0 else float(curr_w)
            if i > 0 and pd.notna(wait_series.iloc[i - 1]):
                prev_m = int(g.loc[i - 1, "_cal_month"])
                prev_s = idx_wt.get(prev_m, 1.0)
                deseas_prev = (
                    float(wait_series.iloc[i - 1]) / prev_s
                    if prev_s > 0
                    else float(wait_series.iloc[i - 1])
                )
                deseas_drift = deseas_curr - deseas_prev
            else:
                deseas_drift = 0.0

            pred_w = round(max(1.0, (deseas_curr + 0.5 * deseas_drift) * next_s), 2)
            pred_waits.append(pred_w)

            if pred_w > float(curr_w) + 0.15:
                trends.append("rising")
            elif pred_w < float(curr_w) - 0.15:
                trends.append("falling")
            else:
                trends.append("stable")

        g["predicted_wait_weeks"] = pred_waits
        g["wait_trend"] = trends
        g = g.drop(columns=["_dt", "_cal_month", "_in_r", "_cl_r", "_wt_r"])
        enriched_groups.append(g)

    return pd.concat(enriched_groups, ignore_index=True)


def run_forecasts() -> Path:
    """Load existing adult-only archive, merge new stock-and-flow rows, apply seasonality, and overwrite CSV."""
    FORECASTS_DIR.mkdir(parents=True, exist_ok=True)
    LOGS_DIR.mkdir(parents=True, exist_ok=True)

    append_log("=" * 60)
    append_log("Starting Services/forecasts.py (ADULTS ONLY + HISTORICAL MONTHLY SEASONALITY)")

    hb_map, valid_pairs = _load_reference_maps()

    if FORECASTS_CSV.exists():
        archive_df = pd.read_csv(FORECASTS_CSV)
        if "adult" in archive_df.columns:
            archive_df = archive_df[
                pd.to_numeric(archive_df["adult"], errors="coerce").fillna(1).astype(int) == 1
            ].copy()
        archive_df["hospital_name"] = archive_df["hospital_name"].astype(str).str.strip()
        archive_df["scan_choice"] = archive_df["scan_choice"].astype(str).str.strip()
        archive_df = archive_df[
            [
                (h, s) in valid_pairs
                for h, s in zip(archive_df["hospital_name"], archive_df["scan_choice"])
            ]
        ].copy()
        if "health_board" not in archive_df.columns and "hospital_name" in archive_df.columns:
            archive_df["health_board"] = archive_df["hospital_name"].map(hb_map)
        append_log(
            f"Loaded existing adult archive from {FORECASTS_CSV.name} "
            f"({len(archive_df):,} verified rows)."
        )
    else:
        archive_df = pd.DataFrame()
        append_log(f"No existing {FORECASTS_CSV.name} found; starting fresh adult archive.")

    mode, source_path = _find_latest_input_csv()
    append_log(f"Reading latest {mode} input dataset: {source_path.name}")

    if mode == "raw":
        new_df = _build_from_raw_csv(source_path, hb_map, valid_pairs)
    else:
        new_df = _build_from_viz_csv(source_path, hb_map, valid_pairs)

    append_log(f"Computed {len(new_df):,} adult-only rows from {source_path.name}.")

    key_cols = ["date_key", "hospital_name", "scan_choice"]
    if not archive_df.empty:
        combined_df = pd.concat([archive_df, new_df], ignore_index=True)
        before_count = len(combined_df)
        combined_df = combined_df.drop_duplicates(subset=key_cols, keep="last")
        append_log(
            f"Merged archive + new rows ({before_count:,} -> {len(combined_df):,} after deduplication)."
        )
    else:
        combined_df = new_df.drop_duplicates(subset=key_cols, keep="last")

    combined_df = _apply_historical_monthly_seasonality(combined_df)
    append_log("Applied historical calendar-month seasonality indices across full archive.")

    combined_df = combined_df.sort_values(
        ["date_key", "health_board", "hospital_name", "scan_choice"]
    ).reset_index(drop=True)

    combined_df.to_csv(FORECASTS_CSV, index=False)
    append_log(
        f"Overwrote {FORECASTS_CSV} ({len(combined_df):,} adult-only rows, "
        f"{FORECASTS_CSV.stat().st_size / 1024:.1f} KB)."
    )
    append_log("Completed Services/forecasts.py successfully.")
    return FORECASTS_CSV


if __name__ == "__main__":
    run_forecasts()