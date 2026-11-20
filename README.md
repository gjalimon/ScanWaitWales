# ScanWait Wales

ScanWait Wales is a bilingual (English / Cymraeg) web application designed to help patients explore diagnostic imaging waiting times across selected NHS Wales hospitals. Built as an informational accessibility tool, it transforms publicly available StatsWales data into estimated waiting times, stock-and-flow queue projections, interactive visualisations, and nearby hospital travel comparisons—without storing any personal user data.

---

## Key Features & Methodology

* **Adult & Paediatric Cohort Support (`adult = 1` / `0`):** Users can select either **Adult (18+)** or **Child (under-18)** on the calculation page to view cohort-specific waiting times.
* **Cumulative Frequency Distribution (Median Band):** Calculates the exact 50% halfway point across weekly waiting bands and reports the conservative upper bound of that band (capped at `40` weeks for the `40 weeks and over` band).
* **Stock-and-Flow Queue Modelling:** Models weekly waiting bands as patient stocks and monthly transitions as cohort progression/exit flows to compute monthly queue clearance rates and projected next-month waiting times.
* **Ghost-Scanner Filtering:** Cross-checks all StatsWales records against the canonical reference table (`reference_datasets/selected_hospitals_services_coordinates.csv`) so waiting lists are only published for verified hospital-scanner combinations.
* **NHS Wales 8-Week Target Gauge:** Classifies waits into **Green** (`0–8` weeks, within target), **Orange** (`9–12` weeks), and **Red** (`13+` weeks).
* **Geospatial Nearest-Hospital Routing:** Resolves Welsh postcodes via [Postcodes.io](https://postcodes.io/), ranks eligible hospitals by Haversine straight-line distance, and queries the free public OSRM (OpenStreetMap Routing Machine) API for driving and walking durations (no API key required).
* **Interactive Visualisations:** Renders a Wales waiting-time heatmap, a hospital comparison stacked bar chart, and a multi-hospital historical time-series line graph using WCAG AA/AAA-compliant Plotly themes.
* **Bilingual Interface:** Full English (`en`) and Welsh (`cy`) support aligned with the Welsh Language Measure 2011 via `translations.py`.

---

## Repository Structure

```text
scanwait-wales/
├── reference_datasets/
│   └── selected_hospitals_services_coordinates.csv   # Canonical hospital, scanner & coordinate source
├── raw_datasets/
│   └── .gitkeep                                      # Raw StatsWales downloads: statswales_raw_[HHMMSS]_[DDMMYYYY].csv
├── published_dataset/
│   └── .gitkeep                                      # Strictly 1 active live CSV: [HHMMSS]_[DDMMYYYY].csv
├── archived_dataset/
│   └── .gitkeep                                      # Previous published_dataset files moved here automatically
├── visualisation_dataset/
│   └── .gitkeep                                      # Strictly 1 active viz CSV: visualisation_[HHMMSS]_[DDMMYYYY].csv
├── archived_viz_dataset/
│   └── .gitkeep                                      # Previous visualisation_dataset files moved here automatically
├── logs/
│   └── .gitkeep                                      # Timestamped script run logs: [HHMMSS]_[DDMMYYYY]_[script].txt
├── Services/
│   ├── __init__.py
│   ├── data_loader.py                                # Manual Step 1: Download raw -> validate -> publish live CSV
│   ├── viz_data_maker.py                             # Manual Step 2: Build merged historical + stock/flow viz CSV
│   ├── waiting_math.py                               # Median band & stock-and-flow cohort progression calculations
│   ├── distance_calc.py                              # Postcodes.io lookup, Haversine ranking & Google Routes API
│   ├── heatmap_viz.py                                # Hospital waiting-time & coordinate lookup for heatmap
│   ├── visualisations.py                             # Plotly stacked bar chart & time-series line graph builders
│   └── logger.py                                     # Execution logger writing [HHMMSS]_[DDMMYYYY]_[script].txt
├── Static/
│   ├── CSS/
│   │   ├── fonts/                                    # OpenDyslexic accessibility fonts
│   │   └── style.css                                 # Main application stylesheet
│   └── Images/                                       # Visualisation card icons
├── Templates/
│   ├── WelcomePage.HTML
│   ├── InputPage.HTML
│   ├── OutputPage.HTML
│   ├── VisualisationsPage.HTML
│   ├── HeatMapPage.HTML
│   ├── StackedBarChartPage.HTML
│   └── LineGraphPage.HTML
├── app.py                                            # Main Flask web application entry point
├── scan_config.py                                    # Canonical CSV loader & service display-name mappings
├── scanwait.py                                       # Fast published_dataset loader & record lookup helpers
├── translations.py                                   # Centralized English & Welsh UI dictionary
├── requirements.txt                                  # Python dependencies
└── .gitignore                                        # Excludes __pycache__, .env, raw/archived data & logs
```

---

## Setup & Installation

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

---

## Data Pipeline Workflow

All scripts disable `.pyc` bytecode generation (`sys.dont_write_bytecode = True`) and write an execution log to `logs/[HHMMSS]_[DDMMYYYY]_[script_name].txt`.

### Step 1: Generate the Live Application Dataset
Run `data_loader.py` manually whenever new monthly StatsWales data is released:
```bash
python -B Services/data_loader.py
```
1. Downloads the raw CSV from StatsWales and saves an immutable copy to `raw_datasets/statswales_raw_[HHMMSS]_[DDMMYYYY].csv`.
2. Filters hospitals and services against `reference_datasets/selected_hospitals_services_coordinates.csv`.
3. Computes current median wait times and stock-and-flow predictions for both **Adult (`adult=1`)** and **Child (`adult=0`)** cohorts.
4. Validates schema, binary flags, and scanner eligibility.
5. Archives any existing file in `published_dataset/` into `archived_dataset/` and writes `published_dataset/[HHMMSS]_[DDMMYYYY].csv`.

### Step 2: Generate the Visualisation Time-Series Dataset
Run `viz_data_maker.py` to update the historical dataset powering the stacked bar chart and line graph:
```bash
python -B Services/viz_data_maker.py
```
1. Reads the latest raw CSV in `raw_datasets/` and merges any historical snapshots from `archived_viz_dataset/`.
2. Archives the current file in `visualisation_dataset/` into `archived_viz_dataset/`.
3. Writes `visualisation_dataset/visualisation_[HHMMSS]_[DDMMYYYY].csv`.

### Step 2: Launch the Web Application
```bash
python -B app.py
```
Open `http://127.0.0.1:5000` in your browser. `app.py` loads the lightweight pre-computed CSV in `published_dataset/` on startup.

---

## Privacy, Ethics & Limitations

* **Zero User Data Storage:** Postcodes and scan selections are processed in memory only and are never saved to disk or a database.
* **No Clinical Priority Breakdown:** StatsWales aggregates urgent and routine referrals together; individual clinical urgency may result in shorter or longer waits than the median.
* **Infrastructure Verification:** Service availability relies on `reference_datasets/selected_hospitals_services_coordinates.csv` to filter out known reporting anomalies ("ghost scanners").

---

## License & Team

* **Web Application Content:** Open Government Licence v3.0
* **Source Code:** MIT License
* **Team (Cardiff University MSc Data Science & Analytics):** Eleri Hayman, Charlie Hastings, Faith Hamelin, Revée O'Neal-Allamby, Gerald Alimon
