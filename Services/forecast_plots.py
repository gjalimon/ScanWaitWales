"""Static Matplotlib v0.3 forecast plot generator with historical monthly seasonality.

Renders high-DPI PNG forecast cards into ``Static/Images/forecasts/``:
- Adults-only scope (``adult == 1``)
- Maps hospitals and active Health Boards directly from
  ``reference_datasets/selected_hospitals_services_coordinates.csv``
- Skips empty or all-zero/all-NaN series so no "No data" placeholder PNGs are saved
- Uses the full multi-year historical archive in ``forecasts_dataset/forecasts_dataset.csv``
  to extract calendar-month seasonal multipliers (``1..12``) for incoming referrals and
  clearance rates, deseasonalizes the trailing baseline, and projects 6 forward months
  with recurring monthly seasonality applied
- Background: ``#F1F5F0`` (ScanWait Wales off-white)
- Historical series: forest green (``#005C22``)
- Forecasted series & end dot: bright light green (``#3CA832``)
- Rolling window with leftmost start month-year tick
- Right half shaded into 3 projection horizons:
  ``1 mo forecast``, ``2–3 mo forecast``, and ``4–6 mo forecast``
- Supports: ``percentage_change``, ``total_waiting``, and ``incoming_referrals``
"""

from __future__ import annotations

import sys

sys.dont_write_bytecode = True

from pathlib import Path
import re
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from scan_config import SCAN_SERVICE_MAP

REF_CSV = (
    PROJECT_ROOT
    / "reference_datasets"
    / "selected_hospitals_services_coordinates.csv"
)
FORECASTS_CSV = PROJECT_ROOT / "forecasts_dataset" / "forecasts_dataset.csv"
OUTPUT_PLOTS_DIR = PROJECT_ROOT / "Static" / "Images" / "forecasts"

METRIC_LABELS = {
    "en": {
        "percentage_change": "Percentage change (%)",
        "total_waiting": "Total patients waiting",
        "incoming_referrals": "Incoming referrals",
        "band_1m": "1 mo\nforecast",
        "band_2_3m": "2–3 mo\nforecast",
        "band_4_6m": "4–6 mo\nforecast",
    },
    "cy": {
        "percentage_change": "Newid canrannol (%)",
        "total_waiting": "Cyfanswm cleifion yn aros",
        "incoming_referrals": "Atgyfeiriadau newydd",
        "band_1m": "Rhagolwg\n1 mis",
        "band_2_3m": "Rhagolwg\n2–3 mis",
        "band_4_6m": "Rhagolwg\n4–6 mis",
    },
}


def slugify(value: str) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9]+", "_", str(value).strip().lower()).strip("_")
    return cleaned or "all"


def load_reference_hospital_map() -> tuple[dict[str, str], list[str], set[tuple[str, str]]]:
    """Return ({hospital_name: health_board}, sorted_health_boards) from the reference CSV."""
    if not REF_CSV.exists():
        raise FileNotFoundError(f"Missing reference dataset at {REF_CSV}")

    ref_df = pd.read_csv(REF_CSV).dropna(subset=["Hospital Name", "Health board"])
    ref_df["Hospital Name"] = ref_df["Hospital Name"].astype(str).str.strip()
    ref_df["Health board"] = ref_df["Health board"].astype(str).str.strip()

    hosp_to_hb = ref_df.set_index("Hospital Name")["Health board"].to_dict()
    health_boards = sorted(ref_df["Health board"].unique().tolist())

    valid_pairs: set[tuple[str, str]] = set()
    for _, row in ref_df.iterrows():
        hosp = row["Hospital Name"]
        for scan_choice, source_cols in SCAN_SERVICE_MAP.items():
            for col in source_cols:
                if col in ref_df.columns and pd.to_numeric(row[col], errors="coerce") == 1:
                    valid_pairs.add((hosp, scan_choice))
                    break

    return hosp_to_hb, health_boards, valid_pairs

def _get_reference_health_boards() -> list[str]:
    _, health_boards, _ = load_reference_hospital_map()
    return health_boards
   
# Exported dynamically from the reference CSV for compatibility with Services/visualisations.py
WELSH_HEALTH_BOARDS = _get_reference_health_boards()


def load_forecasts_df() -> pd.DataFrame:
    """Load forecasts_dataset.csv (adult == 1) strictly filtered to approved hospital-scanner pairs."""
    if not FORECASTS_CSV.exists():
        raise FileNotFoundError(
            f"Missing {FORECASTS_CSV}. Run 'python -B Services/forecasts.py' first."
        )
    df = pd.read_csv(FORECASTS_CSV)
    if "adult" in df.columns:
        df = df[pd.to_numeric(df["adult"], errors="coerce").fillna(1).astype(int) == 1].copy()

    hosp_to_hb, _, valid_pairs = load_reference_hospital_map()
    df["hospital_name"] = df["hospital_name"].astype(str).str.strip()
    df["scan_choice"] = df["scan_choice"].astype(str).str.strip()

    # Keep only rows where the hospital actually offers that scanner (value == 1 in reference CSV)
    is_valid_scanner = [
        (h, s) in valid_pairs for h, s in zip(df["hospital_name"], df["scan_choice"])
    ]
    df = df[is_valid_scanner].copy()

    df["health_board"] = df["hospital_name"].map(hosp_to_hb)
    df = df.dropna(subset=["health_board"]).copy()
    return df

def _short_month_year(date_key: str) -> str:
    try:
        dt = pd.to_datetime(f"{date_key}-01")
        return dt.strftime("%b %Y")
    except Exception:
        return str(date_key)


def _add_months(date_key: str, months: int) -> str:
    dt = pd.to_datetime(f"{date_key}-01") + pd.DateOffset(months=months)
    return dt.strftime("%Y-%m")


def compute_monthly_seasonality(full_grouped: pd.DataFrame) -> dict[int, dict[str, float]]:
    """Estimate calendar-month (1..12) seasonal multipliers from all available historical years."""
    g = full_grouped.copy().sort_values("date_key").reset_index(drop=True)
    g["cal_month"] = pd.to_datetime(g["date_key"] + "-01", errors="coerce").dt.month

    inflow_base = g["incoming_referrals"].rolling(12, center=True, min_periods=1).mean()
    clear_base = g["clearance_rate_pct"].rolling(12, center=True, min_periods=1).mean()

    g["inflow_ratio"] = np.where(
        inflow_base > 0, g["incoming_referrals"] / inflow_base, 1.0
    )
    g["clear_ratio"] = np.where(
        clear_base > 0, g["clearance_rate_pct"] / clear_base, 1.0
    )

    raw_inflow: dict[int, float] = {}
    raw_clear: dict[int, float] = {}
    counts: dict[int, int] = {}

    for m in range(1, 13):
        sub_m = g[g["cal_month"] == m]
        n = len(sub_m)
        counts[m] = n
        if n > 0:
            raw_inflow[m] = float(sub_m["inflow_ratio"].mean())
            raw_clear[m] = float(sub_m["clear_ratio"].mean())
        else:
            raw_inflow[m] = 1.0
            raw_clear[m] = 1.0

    obs_months = [m for m, n in counts.items() if n > 0]
    if obs_months:
        mean_in = float(np.mean([raw_inflow[m] for m in obs_months])) or 1.0
        mean_cl = float(np.mean([raw_clear[m] for m in obs_months])) or 1.0
        for m in obs_months:
            raw_inflow[m] /= mean_in
            raw_clear[m] /= mean_cl

    seasonality: dict[int, dict[str, float]] = {}
    for m in range(1, 13):
        w = counts[m] / (counts[m] + 1.0)
        adj_in = float(np.clip(1.0 + w * (raw_inflow[m] - 1.0), 0.65, 1.40))
        adj_cl = float(np.clip(1.0 + w * (raw_clear[m] - 1.0), 0.70, 1.35))
        seasonality[m] = {
            "inflow_factor": round(adj_in, 4),
            "clearance_factor": round(adj_cl, 4),
            "sample_count": counts[m],
        }
    return seasonality


def compute_series_payload(
    df: pd.DataFrame,
    title: str,
    subtitle: str = "",
    metric: str = "percentage_change",
) -> dict:
    """Aggregate full historical monthly rows, extract seasonality, and project 6 forward months."""
    metric = (
        metric
        if metric in {"percentage_change", "total_waiting", "incoming_referrals"}
        else "percentage_change"
    )
    empty_payload = {
        "has_data": False,
        "title": title,
        "subtitle": subtitle,
        "metric": metric,
        "hist_keys": [],
        "hist_vals": [],
        "proj_keys": [],
        "proj_vals": [],
        "latest_wait": None,
        "predicted_wait": None,
        "trend": "stable",
        "latest_total_waiting": 0,
        "latest_incoming_referrals": 0,
        "pct_change_1m": 0.0,
        "seasonality_applied": True,
    }

    if df.empty:
        return empty_payload

    # Skip slices where waiting stock is 0 across all months and wait weeks are all NaN
    has_positive_stock = (
        pd.to_numeric(df["total_waiting"], errors="coerce").fillna(0).gt(0).any()
    )
    has_valid_wait = (
        pd.to_numeric(df["current_wait_weeks"], errors="coerce").notna().any()
    )
    if not has_positive_stock and not has_valid_wait:
        return empty_payload

    full_grouped = (
        df.groupby("date_key", as_index=False)
        .agg(
            total_waiting=("total_waiting", "sum"),
            incoming_referrals=("incoming_referrals", "sum"),
            clearance_rate_pct=("clearance_rate_pct", "mean"),
            current_wait_weeks=("current_wait_weeks", "median"),
            predicted_wait_weeks=("predicted_wait_weeks", "median"),
        )
        .sort_values("date_key")
        .reset_index(drop=True)
    )

    seasonality = compute_monthly_seasonality(full_grouped)

    grouped = full_grouped.tail(6).reset_index(drop=True)
    hist_keys = grouped["date_key"].tolist()
    last_key = hist_keys[-1]

    recent_tail = grouped.tail(3).copy()
    recent_months = pd.to_datetime(recent_tail["date_key"] + "-01").dt.month.tolist()

    deseas_inflows = [
        float(val) / seasonality[m]["inflow_factor"]
        for val, m in zip(recent_tail["incoming_referrals"], recent_months)
    ]
    deseas_clear_rates = [
        (float(val) / 100.0) / seasonality[m]["clearance_factor"]
        for val, m in zip(recent_tail["clearance_rate_pct"], recent_months)
    ]

    base_inflow = float(np.mean(deseas_inflows))
    base_clear_rate = float(np.clip(np.mean(deseas_clear_rates), 0.05, 0.95))

    curr_stock = float(grouped["total_waiting"].iloc[-1])
    proj_keys = [_add_months(last_key, step) for step in range(1, 7)]
    proj_stocks: list[float] = []
    proj_inflows: list[float] = []

    s = curr_stock
    for f_key in proj_keys:
        f_month = int(pd.to_datetime(f"{f_key}-01").month)
        s_in_factor = seasonality[f_month]["inflow_factor"]
        s_cl_factor = seasonality[f_month]["clearance_factor"]

        step_inflow = max(0.0, base_inflow * s_in_factor)
        step_clear_rate = float(np.clip(base_clear_rate * s_cl_factor, 0.05, 0.95))

        outflow = s * step_clear_rate
        s = max(0.0, s + step_inflow - outflow)

        proj_stocks.append(round(s, 1))
        proj_inflows.append(round(step_inflow, 1))

    if metric == "total_waiting":
        hist_vals = [round(float(v), 1) for v in grouped["total_waiting"]]
        proj_vals = proj_stocks
    elif metric == "incoming_referrals":
        hist_vals = [round(float(v), 1) for v in grouped["incoming_referrals"]]
        proj_vals = proj_inflows
    else:
        base = float(grouped["total_waiting"].mean())
        if base <= 0:
            hist_vals = [0.0 for _ in grouped["total_waiting"]]
            proj_vals = [0.0 for _ in proj_stocks]
        else:
            hist_vals = [
                round(((float(v) - base) / base) * 100.0, 1)
                for v in grouped["total_waiting"]
            ]
            proj_vals = [
                round(((float(v) - base) / base) * 100.0, 1) for v in proj_stocks
            ]

    latest_wait = grouped["current_wait_weeks"].iloc[-1]
    pred_wait = grouped["predicted_wait_weeks"].iloc[-1]
    if pd.notna(latest_wait) and pd.notna(pred_wait):
        if float(pred_wait) > float(latest_wait):
            trend = "rising"
        elif float(pred_wait) < float(latest_wait):
            trend = "falling"
        else:
            trend = "stable"
    else:
        trend = "stable"

    pct_1m = (
        round(((proj_stocks[0] - curr_stock) / curr_stock) * 100.0, 1)
        if curr_stock > 0
        else 0.0
    )

    return {
        "has_data": True,
        "title": title,
        "subtitle": subtitle,
        "metric": metric,
        "hist_keys": hist_keys,
        "hist_vals": hist_vals,
        "proj_keys": proj_keys,
        "proj_vals": proj_vals,
        "latest_wait": None if pd.isna(latest_wait) else round(float(latest_wait), 1),
        "predicted_wait": None if pd.isna(pred_wait) else round(float(pred_wait), 1),
        "trend": trend,
        "latest_total_waiting": int(round(curr_stock)),
        "latest_incoming_referrals": int(round(float(grouped["incoming_referrals"].iloc[-1]))),
        "pct_change_1m": pct_1m,
        "seasonality_applied": True,
        "seasonal_factors": seasonality,
    }


def render_forecast_plot(
    payload: dict,
    lang: str = "en",
    filename_stem: str = "forecast_card",
    force_rebuild: bool = False,
) -> str | None:
    """Render a v0.3 static PNG plot card, or return None if there is no valid data."""
    if not payload.get("has_data") or not payload.get("hist_keys"):
        return None

    OUTPUT_PLOTS_DIR.mkdir(parents=True, exist_ok=True)
    lang_key = "cy" if lang == "cy" else "en"
    labels = METRIC_LABELS[lang_key]
    metric = payload["metric"]

    out_name = f"{filename_stem}_{metric}_{lang_key}.png"
    out_path = OUTPUT_PLOTS_DIR / out_name
    if out_path.exists() and not force_rebuild:
        return f"Images/forecasts/{out_name}"

    fig, ax = plt.subplots(figsize=(7.6, 4.3), dpi=160)
    fig.patch.set_facecolor("#F1F5F0")
    ax.set_facecolor("#F1F5F0")

    hist_keys = payload["hist_keys"]
    hist_vals = payload["hist_vals"]
    proj_keys = payload["proj_keys"]
    proj_vals = payload["proj_vals"]

    n_hist = len(hist_keys)
    n_proj = len(proj_keys)
    x_hist = np.arange(n_hist, dtype=float)
    x_proj = np.arange(n_hist, n_hist + n_proj, dtype=float)

    all_vals = hist_vals + proj_vals
    y_min = min(all_vals)
    y_max = max(all_vals)
    pad = max(1.0, (y_max - y_min) * 0.22)
    if metric == "percentage_change":
        y_low = min(y_min - pad, -5.0)
        y_high = max(y_max + pad, 5.0)
    else:
        y_low = max(0.0, y_min - pad)
        y_high = y_max + pad
    ax.set_ylim(y_low, y_high)

    split_x = n_hist - 0.5
    end_x = n_hist + n_proj - 0.5
    ax.set_xlim(-0.3, end_x)

    band_specs = [
        (split_x, split_x + 1.0, "#DCE8DC", labels["band_1m"]),
        (split_x + 1.0, split_x + 3.0, "#C5DBC6", labels["band_2_3m"]),
        (split_x + 3.0, end_x, "#ADCEAF", labels["band_4_6m"]),
    ]
    for x0, x1, color, band_text in band_specs:
        ax.axvspan(x0, x1, color=color, alpha=0.65, zorder=0)
        ax.text(
            (x0 + x1) / 2.0,
            y_high - (y_high - y_low) * 0.04,
            band_text,
            ha="center",
            va="top",
            fontsize=8.5,
            fontweight="bold",
            color="#003816",
            zorder=4,
        )

    ax.axvline(split_x, color="#003816", linestyle=":", linewidth=1.2, alpha=0.75, zorder=2)
    if metric == "percentage_change":
        ax.axhline(0.0, color="#6B7C6E", linestyle="--", linewidth=0.9, alpha=0.6, zorder=1)

    ax.plot(
        x_hist,
        hist_vals,
        color="#005C22",
        linewidth=2.6,
        marker="o",
        markersize=5.5,
        zorder=5,
    )

    conn_x = np.concatenate(([x_hist[-1]], x_proj))
    conn_y = [hist_vals[-1]] + proj_vals
    ax.plot(
        conn_x,
        conn_y,
        color="#3CA832",
        linewidth=2.6,
        linestyle="-",
        marker="o",
        markersize=4.5,
        zorder=6,
    )
    ax.scatter(
        [x_proj[-1]],
        [proj_vals[-1]],
        color="#3CA832",
        edgecolors="#003816",
        linewidths=1.2,
        s=62,
        zorder=7,
    )

    tick_positions = [x_hist[0], x_hist[-1], x_proj[2], x_proj[-1]]
    tick_labels = [
        _short_month_year(hist_keys[0]),
        _short_month_year(hist_keys[-1]),
        _short_month_year(proj_keys[2]),
        _short_month_year(proj_keys[-1]),
    ]
    ax.set_xticks(tick_positions)
    ax.set_xticklabels(tick_labels, fontsize=9, fontweight="bold", color="#003816")
    ax.tick_params(axis="y", labelsize=9, colors="#003816")

    ax.set_ylabel(labels[metric], fontsize=9.5, fontweight="bold", color="#003816")
    ax.set_title(
        payload["title"],
        loc="left",
        fontsize=12,
        fontweight="bold",
        color="#003816",
        pad=12,
    )

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color("#003816")
    ax.spines["bottom"].set_color("#003816")
    ax.grid(axis="y", linestyle="-", linewidth=0.5, color="#B7C7B9", alpha=0.6)

    fig.tight_layout()
    fig.savefig(out_path, facecolor="#F1F5F0", dpi=160)
    plt.close(fig)
    return f"Images/forecasts/{out_name}"


def pre_render_all_default_cards(force_rebuild: bool = True) -> list[str]:
    """Pre-render default Health Board v0.3 cards using the reference dataset."""
    df = load_forecasts_df()
    _, health_boards, _ = load_reference_hospital_map()

    rendered: list[str] = []
    for hb in health_boards:
        sub = df[df["health_board"] == hb]
        if sub.empty:
            continue
        for metric in ("percentage_change", "total_waiting", "incoming_referrals"):
            payload = compute_series_payload(sub, title=hb, metric=metric)
            if not payload.get("has_data"):
                continue
            for lang in ("en", "cy"):
                rel = render_forecast_plot(
                    payload,
                    lang=lang,
                    filename_stem=f"hb_{slugify(hb)}",
                    force_rebuild=force_rebuild,
                )
                if rel:
                    rendered.append(rel)
    return rendered


if __name__ == "__main__":
    files = pre_render_all_default_cards(force_rebuild=True)
    print(f"Pre-rendered {len(files)} adult-only seasonal v0.3 forecast PNG cards in {OUTPUT_PLOTS_DIR}")