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

VIZ_DIR = PROJECT_ROOT / "visualisation_dataset"

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
    fig_1.update_layout(
        height=750,
        xaxis_title="<b>" + translations["chart_xaxis_hospital"] + "</b>",
        yaxis_title="<b>" + translations["chart_yaxis_weeks"] + "</b>",
        title="<b>" + translations["chart_title_summary"] + "</b>",
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.5,
            xanchor="center",
            x=0.5,
            title=dict(
                text=translations["chart_legend_scan_type"],
                font=dict(size=26),
            ),
            font=dict(size=24),        # Enlarges the button text & clickable area
            itemsizing="constant",     # Keeps swatch icons large regardless of bar width
            itemwidth=50,              # Widens the colored swatch box (default is 30)
            tracegroupgap=16,          # Adds vertical breathing room between rows
        ),
        margin=dict(b=380),            # Reserves space at the bottom for the larger rows
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
        height=850,
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
            orientation="h",
            yanchor="top",
            y=-0.35,               # Gap below "Date" (more negative = more space below chart)
            xanchor="center",
            x=0.5,
            title_text="",
            font=dict(size=16),    # Larger hospital text
            itemsizing="constant",
            itemwidth=45,          # Space/width for each colored line swatch (min 30)
            tracegroupgap=14,      # Vertical spacing (in px) between wrapped rows
            entrywidth=0.33,       # Optional: aligns items into neat columns (e.g. 4 per row)
            entrywidthmode="fraction",
        ),
        margin=dict(t=70, b=350, l=50, r=20),  # b=300 controls bottom padding below the legend
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
