"""Plotly charts powered by visualisation_dataset/visualisation_[timestamp].csv."""

from __future__ import annotations

from pathlib import Path
import sys

sys.dont_write_bytecode = True

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scan_config import SERVICE_DISPLAY_NAMES, SERVICE_DISPLAY_ORDER

REF_CSV = PROJECT_ROOT / "reference_datasets" / "selected_hospitals_services_coordinates.csv"

from Services.forecast_plots import (
    WELSH_HEALTH_BOARDS,
    compute_series_payload,
    load_forecasts_df,
    render_forecast_plot,
    slugify,
)

VIZ_DIR = PROJECT_ROOT / "visualisation_dataset"
FORECASTS_CSV = PROJECT_ROOT / "forecasts_dataset" / "forecasts_dataset.csv"

# ============================================================
# Custom theme creation (WCAG AA/AAA contrast compliant)
# ============================================================
my_theme = go.layout.Template(
    layout=go.Layout(
        font=dict(family="Verdana", size=19, color="#003816"),
        title=dict(font=dict(family="Verdana", size=24, color="#005C22")),
        xaxis=dict(
            title_font=dict(family="Verdana", size=19, color="#003816"),
            tickfont=dict(size=12, color="#003816"),
            showgrid=False,
        ),
        yaxis=dict(
            title_font=dict(family="Verdana", size=19, color="#003816"),
            tickfont=dict(size=12, color="#003816"),
            gridcolor="#003816",
        ),
        legend=dict(font=dict(size=12)),
        plot_bgcolor="#F1F5F0",
        paper_bgcolor="#F1F5F0",
        colorway=[
            "#005C22",
            "#A70626",
            "#E55F10",
            "#36313F",
            "#A32E78",
            "#353F1C",
            "#14857D",
            "#1C3497",
        ],
    )
)
pio.templates["my_theme"] = my_theme

DISPLAY_TO_SERVICE = {
    display: service
    for service, display in SERVICE_DISPLAY_NAMES.items()
}


def _load_latest_viz_df() -> pd.DataFrame:
    """Load the active visualisation_[timestamp].csv from visualisation_dataset/."""
    viz_files = sorted(
        (f for f in VIZ_DIR.glob("visualisation_*.csv") if f.is_file()),
        key=lambda p: p.stat().st_mtime,
    )
    if not viz_files:
        raise FileNotFoundError(
            f"No visualisation_*.csv file found in {VIZ_DIR}. "
            "Run 'python -B Services/viz_data_maker.py' first."
        )
    return pd.read_csv(viz_files[-1])

# ------ Forecasts viz data loader -------- #

def get_forecast_filter_options() -> dict:
    """Return cascading dropdown options derived from adult-only forecasts_dataset.csv."""
    df = load_forecasts_df()
    scan_types = sorted(df["scan_choice"].dropna().unique().tolist())
    hospitals = sorted(df["hospital_name"].dropna().unique().tolist())
    health_boards = [hb for hb in WELSH_HEALTH_BOARDS if hb in set(df["health_board"].dropna())]
    return {
        "scan_types": scan_types,
        "hospitals": hospitals,
        "health_boards": health_boards,
    }


def get_forecast_view_data(
    category: str = "",
    selection: str = "",
    metric: str = "percentage_change",
    lang: str = "en",
) -> dict:
    """Build adult-only v0.3 forecast cards for the default view or cascading filter view."""
    df = load_forecasts_df()
    cards: list[dict] = []
    is_default = not category or not selection

    def _append_if_valid(sub_df: pd.DataFrame, card_title: str, stem: str) -> None:
        if sub_df.empty:
            return
        payload = compute_series_payload(sub_df, title=card_title, metric=metric)
        if not payload.get("has_data"):
            return
        img_rel = render_forecast_plot(
            payload,
            lang=lang,
            filename_stem=stem,
            force_rebuild=False,
        )
        if img_rel:
            payload["image_rel"] = img_rel
            cards.append(payload)

    if is_default:
        # Default landing view: 1 plot card per Health Board across all scan types
        for hb in WELSH_HEALTH_BOARDS:
            sub = df[df["health_board"] == hb]
            payload = compute_series_payload(sub, title=hb, metric=metric)
            img_rel = render_forecast_plot(
                payload,
                lang=lang,
                filename_stem=f"hb_{slugify(hb)}",
                force_rebuild=False,
            )
            payload["image_rel"] = img_rel
            cards.append(payload)

    elif category == "scan_type":
        # Scan Type -> Health Board: HB total first, then each hospital in that HB offering the scan
        scan_choice, _, health_board = selection.partition("||")
        hb_sub = df[(df["scan_choice"] == scan_choice) & (df["health_board"] == health_board)]
        total_payload = compute_series_payload(
            hb_sub,
            title=f"{health_board} — {scan_choice} (Total)",
            metric=metric,
        )
        total_payload["image_rel"] = render_forecast_plot(
            total_payload,
            lang=lang,
            filename_stem=f"scan_hb_{slugify(scan_choice)}_{slugify(health_board)}",
            force_rebuild=False,
        )
        cards.append(total_payload)

        for hosp in sorted(hb_sub["hospital_name"].dropna().unique()):
            hosp_sub = hb_sub[hb_sub["hospital_name"] == hosp]
            p = compute_series_payload(hosp_sub, title=f"{hosp} — {scan_choice}", metric=metric)
            p["image_rel"] = render_forecast_plot(
                p,
                lang=lang,
                filename_stem=f"scan_hosp_{slugify(scan_choice)}_{slugify(hosp)}",
                force_rebuild=False,
            )
            cards.append(p)

    elif category == "hospital":
        # Hospital -> Site: all approved scan type forecasts at that hospital site
        hosp_sub = df[df["hospital_name"] == selection]
        for scan in sorted(hosp_sub["scan_choice"].dropna().unique()):
            scan_sub = hosp_sub[hosp_sub["scan_choice"] == scan]
            p = compute_series_payload(scan_sub, title=f"{selection} — {scan}", metric=metric)
            p["image_rel"] = render_forecast_plot(
                p,
                lang=lang,
                filename_stem=f"hosp_scan_{slugify(selection)}_{slugify(scan)}",
                force_rebuild=False,
            )
            cards.append(p)

    elif category == "health_board":
        # Health Board -> Scan Type: one card per Health Board for that selected scan type
        scan_sub = df[df["scan_choice"] == selection]
        for hb in WELSH_HEALTH_BOARDS:
            hb_sub = scan_sub[scan_sub["health_board"] == hb]
            p = compute_series_payload(hb_sub, title=f"{hb} — {selection}", metric=metric)
            p["image_rel"] = render_forecast_plot(
                p,
                lang=lang,
                filename_stem=f"hb_scan_{slugify(hb)}_{slugify(selection)}",
                force_rebuild=False,
            )
            cards.append(p)

    return {
        "is_default": is_default,
        "category": category,
        "selection": selection,
        "metric": metric,
        "cards": cards,
    }

  # ============================================================
# Build fig 1: stacked bar graph for latest wait times across hospitals
# ============================================================
def get_fig1(translations, adult: int = 1):
    df = _load_latest_viz_df()
    df = df[df["adult"] == int(adult)].copy()

    latest_ym = df["Date_YYYY_MM"].max()
    latest_df = df[df["Date_YYYY_MM"] == latest_ym].copy()

    pivoted = (
        latest_df.pivot_table(
            index="Hospital",
            columns="Service_Display",
            values="Estimated_Median_Waiting_Weeks",
            aggfunc="first",
        )
        .fillna(0)
        .reset_index()
    )

    available_scans = [
        col for col in SERVICE_DISPLAY_ORDER if col in pivoted.columns
    ]

    fig_1 = px.bar(
        pivoted,
        x="Hospital",
        y=available_scans,
        barmode="group",
        template="my_theme",
    )

    raw_title = translations["chart_title_summary"]
    words = raw_title.split()
    mid = len(words) // 2
    wrapped_title = " ".join(words[:mid]) + "<br>" + " ".join(words[mid:])

    fig_1.update_layout(
        height=850,
        font=dict(size=16),
        xaxis_title="<b>" + translations["chart_xaxis_hospital"] + "</b>",
        yaxis_title="<b>" + translations["chart_yaxis_weeks"] + "</b>",
        title=dict(
            text="<b>" + wrapped_title + "</b>",
            x=0.5,
            xanchor="center",
            font=dict(size=18),
        ),
        legend=dict(
            orientation="v",
            yanchor="top",
            y=-0.90,
            xanchor="center",
            x=0.5,
            title_text="",
            itemsizing="constant",
            itemwidth=50,
            tracegroupgap=16,
            entrywidth=0.33,
            entrywidthmode="fraction",
        ),
        margin=dict(t=95, b=380, l=75, r=25),
    )
    fig_1.update_traces(
        marker_line_color="#F1F5F0",
        marker_line_width=1,
        hovertemplate="<b>%{x}</b><br>"
        + translations["chart_hover_scan"]
        + ": %{fullData.name}<br>"
        + translations["chart_hover_wait"]
        + ": %{y} "
        + translations["chart_weeks"]
        + "<extra></extra>",
    )
    return fig_1


# ============================================================
# Build fig 2: time-series line graph of wait times across hospitals
# ============================================================
def get_fig2(scan_display_name, translations, adult: int = 1):
    df = _load_latest_viz_df()
    df = df[df["adult"] == int(adult)].copy()

    df_2 = df[df["Service_Display"] == scan_display_name].sort_values("Date_YYYY_MM")

    fig_2 = px.line(
        df_2,
        x="Date",
        y="Estimated_Median_Waiting_Weeks",
        color="Hospital",
        template="my_theme",
    )
    fig_2.update_layout(
        height=1250,
        xaxis_title="<b>" + translations["chart_xaxis_date"] + "</b>",
        yaxis_title="<b>" + translations["chart_yaxis_waittime"] + "</b>",
        title=dict(
            text="<b>"
            + scan_display_name
            + "</b> "
            + translations["chart_line_title_prefix"],
            font=dict(size=16),
        ),
        legend=dict(
            orientation="v",
            yanchor="top",
            y=-0.28,               # Gap below "Date" (more negative = more space below chart)
            xanchor="center",
            x=0.5,
            title_text="",
            font=dict(size=16),    # Larger hospital text
            itemsizing="constant",
            itemwidth=45,          # Space/width for each colored line swatch (min 30)
            tracegroupgap=6,      # Vertical spacing (in px) between wrapped rows
            entrywidth=0.33,       # Optional: aligns items into neat columns (e.g. 4 per row)
            entrywidthmode="fraction",
        ),
        margin=dict(t=70, b=620, l=75, r=25),  # b=300 controls bottom padding below the legend
    )
    fig_2.update_traces(
        marker_line_color="#F1F5F0",
        marker_line_width=1,
        hovertemplate="<b>%{fullData.name}</b><br>"
        + translations["chart_xaxis_date"]
        + ": %{x}<br>"
        + translations["chart_hover_wait"]
        + ": %{y} "
        + translations["chart_weeks"]
        + "<extra></extra>",
    )
    return fig_2


# ============================================================
# Build fig 3: individual Financial Times-style forecast line graphs per hospital (adults only)
# ============================================================


def get_fig3(scan_display_name: str, translations: dict, adult: int = 1) -> list[dict]:
    """Build one individual forecast line graph per hospital for ``scan_display_name`` (adult=1).

    Returns a list of dicts containing ``hospital``, ``current_wait``, ``predicted_wait``,
    ``trend``, and ``fig`` (a Plotly ``go.Figure`` styled in an FT-inspired small-multiples look).
    """
    # Strictly enforce adult-only (adult = 1) across the entire forecasts section
    _ = adult
    df = _load_adult_forecasts_df()
    if df.empty:
        return []

    service_source = DISPLAY_TO_SERVICE.get(scan_display_name, scan_display_name)
    sub = df[
        (df["scan_choice"] == scan_display_name)
        | (df["scan_choice"] == service_source)
    ].copy()

    if sub.empty:
        return []

    sub["current_wait_weeks"] = pd.to_numeric(
        sub["current_wait_weeks"], errors="coerce"
    )
    sub["predicted_wait_weeks"] = pd.to_numeric(
        sub["predicted_wait_weeks"], errors="coerce"
    )
    sub["date_key"] = sub["date_key"].astype(str)
    sub["date_label"] = sub["date_label"].astype(str)

    # Keep a rolling 12-month window per hospital so FT-style small multiples stay crisp and readable
    recent_keys = sorted(sub["date_key"].dropna().unique())[-12:]
    sub = sub[sub["date_key"].isin(recent_keys)].sort_values(["hospital_name", "date_key"])

    palette = my_theme.layout.colorway or [
        "#005C22",
        "#A70626",
        "#E55F10",
        "#36313F",
        "#A32E78",
        "#353F1C",
        "#14857D",
        "#1C3497",
    ]

    weeks_label = translations.get("chart_weeks", "weeks")
    hist_label = translations.get("forecast_hist_label", "Observed")
    pred_label = translations.get("forecast_pred_label", "Forecast")
    target_label = translations.get("forecast_target_label", "8-wk target")

    hospital_charts: list[dict] = []

    for idx, (hospital, h_df) in enumerate(sub.groupby("hospital_name", sort=True)):
        h_df = h_df.sort_values("date_key").reset_index(drop=True)
        line_color = palette[idx % len(palette)]

        x_labels = h_df["date_label"].tolist()
        hist_vals = h_df["current_wait_weeks"].tolist()
        pred_vals = h_df["predicted_wait_weeks"].tolist()

        latest_row = h_df.iloc[-1]
        latest_curr = (
            None if pd.isna(latest_row["current_wait_weeks"]) else float(latest_row["current_wait_weeks"])
        )
        latest_pred = (
            None
            if pd.isna(latest_row["predicted_wait_weeks"])
            else float(latest_row["predicted_wait_weeks"])
        )
        trend_str = str(latest_row.get("wait_trend", "stable") or "stable").lower()

        # Forecast accent colour: crimson for rising waits, deep green for falling/stable
        forecast_color = "#A70626" if trend_str == "rising" else "#005C22"

        fig = go.Figure()

        # Subtle FT-style 8-week NHS Wales diagnostic target reference line
        fig.add_hline(
            y=8,
            line_dash="dot",
            line_color="#5A6B5E",
            line_width=1.2,
            annotation_text=target_label,
            annotation_position="top left",
            annotation_font=dict(size=10, color="#5A6B5E"),
        )

        # Historical observed series
        fig.add_trace(
            go.Scatter(
                x=x_labels,
                y=hist_vals,
                mode="lines+markers",
                name=hist_label,
                line=dict(color=line_color, width=2.5),
                marker=dict(size=6, color=line_color),
                hovertemplate=(
                    f"<b>{hospital}</b> ({hist_label})<br>"
                    "%{x}: <b>%{y}</b> " + weeks_label + "<extra></extra>"
                ),
            )
        )

        # Predicted series (dashed FT-style forecast line + diamond markers)
        if any(pd.notna(v) for v in pred_vals):
            fig.add_trace(
                go.Scatter(
                    x=x_labels,
                    y=pred_vals,
                    mode="lines+markers",
                    name=pred_label,
                    line=dict(color=forecast_color, width=2.5, dash="dash"),
                    marker=dict(symbol="diamond", size=7, color=forecast_color),
                    hovertemplate=(
                        f"<b>{hospital}</b> ({pred_label})<br>"
                        "%{x}: <b>%{y}</b> " + weeks_label + "<extra></extra>"
                    ),
                )
            )

        y_candidates = [v for v in (hist_vals + pred_vals) if v is not None and not pd.isna(v)]
        y_max = max([12.0] + [float(v) * 1.15 for v in y_candidates])

        fig.update_layout(
            template="my_theme",
            height=300,
            showlegend=(idx == 0),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="left",
                x=0,
                font=dict(size=11),
            ),
            paper_bgcolor="#FFF9F5",  # Subtle FT-inspired warm editorial card surface
            plot_bgcolor="#FFF9F5",
            title=dict(
                text=f"<b>{hospital}</b>",
                x=0.02,
                xanchor="left",
                font=dict(size=15, color="#003816"),
            ),
            xaxis=dict(
                showgrid=False,
                tickfont=dict(size=10, color="#003816"),
                title_text="",
            ),
            yaxis=dict(
                range=[0, y_max],
                gridcolor="#DCE3DC",
                tickfont=dict(size=10, color="#003816"),
                title=dict(
                    text=translations.get("chart_yaxis_weeks", "Weeks"),
                    font=dict(size=11, color="#003816"),
                ),
            ),
            margin=dict(t=46, b=36, l=46, r=14),
        )

        hospital_charts.append(
            {
                "hospital": hospital,
                "current_wait": latest_curr,
                "predicted_wait": latest_pred,
                "trend": trend_str,
                "fig": fig,
            }
        )

    return hospital_charts