"""Shared waiting-time & stock-and-flow calculation helpers.

Used by both ``Services/data_loader.py`` (for the fast published app dataset)
and ``Services/viz_data_maker.py`` (for the historical visualisation dataset).
"""

from __future__ import annotations

import re
import sys

sys.dont_write_bytecode = True

import numpy as np
import pandas as pd

AGE_GROUP_MAP: dict[int, str] = {
    1: "18 years of age and over",
    0: "Under 18 years of age",
}

WEEKS_PER_MONTH = 4.33


def get_week_number(week_label: object) -> float:
    """Return the lower week integer from a StatsWales waiting-time band label."""
    label = str(week_label).strip().lower()
    if label in {"total waiting", "over 8 weeks", "up to 8 weeks"}:
        return np.nan
    if label == "forty weeks and over":
        return 40.0
    numbers = re.findall(r"\d+", label)
    if not numbers:
        return np.nan
    return float(int(numbers[0]))


def classify_wait_time(weeks: float | int | None) -> str:
    """Classify a wait time (in weeks) into green, orange, or red."""
    if weeks is None or pd.isna(weeks):
        return "green"
    if weeks <= 8:
        return "green"
    if weeks <= 12:
        return "orange"
    return "red"


def calculate_needle_angle(weeks: float | int | None, max_weeks: int = 15) -> float:
    """Map a wait time to a speedometer needle angle in [-90, 90] degrees."""
    if weeks is None or pd.isna(weeks):
        return -90.0
    fraction = float(weeks) / max_weeks
    angle = (fraction * 180.0) - 90.0
    return round(max(-90.0, min(90.0, angle)), 2)


def median_band_from_week_totals(week_totals: dict[int, float]) -> int | None:
    """Compute conservative median waiting-time band upper bound from week stocks."""
    if not week_totals:
        return None
    total_waiting = sum(week_totals.values())
    if total_waiting <= 0:
        return None

    halfway_point = total_waiting / 2.0
    running_total = 0.0
    for week in sorted(week_totals):
        running_total += week_totals[week]
        if running_total >= halfway_point:
            if week >= 40:
                return 40
            return int(week) + 1
    return None


def compute_stock_and_flow_metrics(
    monthly_series: list[dict],
) -> list[dict]:
    """Enrich a chronologically ordered monthly series for one (hospital, scan, adult)
    with stock-and-flow clearance rates and next-month wait predictions.

    Each item in ``monthly_series`` must contain:
      - ``date_str``: e.g. "July 2026"
      - ``date_ref``: pd.Timestamp
      - ``week_totals``: dict[int, float] mapping week band -> patient stock
      - ``typical_wait_weeks``: int | None
      - ``total_waiting``: float
    """
    if not monthly_series:
        return []

    monthly_series = sorted(monthly_series, key=lambda x: x["date_ref"])
    retention_history: dict[int, list[float]] = {}

    for idx, entry in enumerate(monthly_series):
        curr_stocks: dict[int, float] = entry["week_totals"]
        curr_total = float(entry["total_waiting"])
        curr_wait = entry["typical_wait_weeks"]

        if idx == 0:
            entry["net_queue_change"] = 0.0
            entry["clearance_rate_pct"] = None
            entry["predicted_wait_weeks"] = curr_wait
            entry["wait_trend"] = "stable"
            continue

        prev_entry = monthly_series[idx - 1]
        prev_stocks: dict[int, float] = prev_entry["week_totals"]
        prev_total = float(prev_entry["total_waiting"])
        prev_wait = prev_entry["typical_wait_weeks"]

        # New arrivals in the latest month are patients currently in bands 0..3 weeks
        inflow_new = sum(v for w, v in curr_stocks.items() if w < 4)
        # Stock balance identity: S_t = S_{t-1} + Inflow_t - Outflow_t
        outflow = max(0.0, prev_total + inflow_new - curr_total)
        clearance_rate = (
            round((outflow / prev_total) * 100.0, 1) if prev_total > 0 else None
        )

        # Cohort progression ratios r_w = S_t(w) / S_{t-1}(w - 4)
        for w in range(4, 41):
            prev_cohort = prev_stocks.get(w - 4, 0.0)
            curr_cohort = curr_stocks.get(w, 0.0)
            if prev_cohort > 0:
                ratio = min(1.0, max(0.0, curr_cohort / prev_cohort))
                retention_history.setdefault(w, []).append(ratio)

        # Predict next month's wait time
        predicted_wait = curr_wait
        if curr_wait is not None:
            if curr_total >= 30 and retention_history:
                # Option A: Project next month's week stocks using 3-month rolling retention
                projected_stocks: dict[int, float] = {}
                # Assume similar new monthly inflow for bands 0..3
                for w in range(0, 4):
                    if w in curr_stocks:
                        projected_stocks[w] = curr_stocks[w]
                for w in range(4, 41):
                    source_stock = curr_stocks.get(w - 4, 0.0)
                    if source_stock > 0:
                        hist = retention_history.get(w, [0.75])
                        avg_r = float(np.mean(hist[-3:]))
                        projected_stocks[w] = projected_stocks.get(w, 0.0) + (
                            source_stock * avg_r
                        )
                proj_median = median_band_from_week_totals(projected_stocks)
                if proj_median is not None:
                    predicted_wait = proj_median
            else:
                # Option B: Sparse-cohort fallback using recent drift
                if prev_wait is not None:
                    drift = curr_wait - prev_wait
                    predicted_wait = max(1, int(round(curr_wait + (0.5 * drift))))

        # Determine directional trend
        if curr_wait is None or predicted_wait is None:
            trend = "stable"
        elif predicted_wait > curr_wait:
            trend = "rising"
        elif predicted_wait < curr_wait:
            trend = "falling"
        else:
            trend = "stable"

        entry["net_queue_change"] = round(curr_total - prev_total, 1)
        entry["clearance_rate_pct"] = clearance_rate
        entry["predicted_wait_weeks"] = predicted_wait
        entry["wait_trend"] = trend

    return monthly_series
