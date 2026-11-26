# ============================================================
# Imports
# ============================================================
"""Flask application entry point for ScanWait Wales."""

import sys

import markdown

sys.dont_write_bytecode = True

from pathlib import Path
from flask import Flask, abort, render_template, request

from Services.logger import setup_script_logger

setup_script_logger("app")

from translations import get_translations

from scan_config import (
    SERVICE_DISPLAY_NAMES,
    SERVICE_DISPLAY_ORDER,
    get_hospital_choices,
    get_scan_choices,
    hospital_has_service,
)
from Services.distance_calc import (
    PostcodeServiceUnavailable,
    get_hospitals_offering_scan,
    get_nearest_hospitals,
    get_welsh_hospital_name,
)
from scanwait import (
    CSV_FILE,
    get_max_date,
    get_wait_record,
    load_waiting_times,
)

from Services.visualisations import (
    DISPLAY_TO_SERVICE,
    get_fig1,
    get_fig2,
    get_forecast_filter_options,
    get_forecast_view_data,
)

from Services.heatmap_viz import build_waiting_time_map, load_hospital_coordinates

BASE_DIR = Path(__file__).resolve().parent
app = Flask(
    __name__,
    template_folder=str(BASE_DIR / "Templates"),
    static_folder=str(BASE_DIR / "Static"),
)
data = load_waiting_times(CSV_FILE)


def _parse_adult_flag(raw_value: str | None) -> int:
    """Normalise age-group parameter to 1 (Adult 18+) or 0 (Child under-18)."""
    if str(raw_value or "").strip() == "0":
        return 0
    return 1


# ============================================================
# Translations helpers
# ============================================================
SERVICE_TRANSLATION_KEYS = {
    "CT": "scan_type_CT",
    "CT [Cardiac only]": "scan_type_Cardiac_CT",
    "MRI": "scan_type_MRI",
    "MRI [Cardiac only]": "scan_type_Cardiac_MRI",
    "Ultrasound [Not pregnancy related]": "scan_type_Ultrasound",
    "Nuclear Medicine": "scan_type_Nuclear_Medicine",
    "Nuclear Medicine [Cardiac / Myocardial Perfusion]": "scan_type_Nuclear_Medicine_Cardiac",
    "Fluoroscopy": "scan_type_Fluoroscopy",
    "Diagnostic Angiography": "scan_type_Diagnostic_Angiography",
}


def _get_translated_services(translations):
    """Return a list of (value, display_text) tuples for the scan dropdown."""
    english_services = get_scan_choices()
    services_with_translations = []
    for service in english_services:
        trans_key = SERVICE_TRANSLATION_KEYS.get(service)
        if trans_key and trans_key in translations:
            display_text = translations[trans_key]
        else:
            display_text = service
        services_with_translations.append((service, display_text))
    return services_with_translations


HEALTH_BOARD_TRANSLATION_KEYS = {
    "Aneurin Bevan University Health Board": "health_board_Aneurin_Bevan",
    "Betsi Cadwaladr University Health Board": "health_board_Betsi_Cadwaladr",
    "Cardiff and Vale University Health Board": "health_board_Cardiff_and_Vale",
    "Cwm Taf Morgannwg University Health Board": "health_board_Cwm_Taf_Morgannwg",
    "Hywel Dda University Health Board": "health_board_Hywel_Dda",
    "Swansea Bay University Health Board": "health_board_Swansea_Bay",
}


def _translate_health_board(english_name, translations):
    """Look up the translated health board name, fall back to English."""
    if not english_name:
        return english_name
    trans_key = HEALTH_BOARD_TRANSLATION_KEYS.get(english_name)
    if trans_key and trans_key in translations:
        return translations[trans_key]
    return english_name


# ============================================================
# Home page
# ============================================================
@app.route("/")
def home():
    lang = request.args.get("lang", "en")
    translations = get_translations(lang)

    txt_filename = "home_cy.txt" if lang == "cy" else "home_en.txt"
    txt_path = BASE_DIR / "content" / txt_filename
    raw_txt = txt_path.read_text(encoding="utf-8")

    home_content_html = markdown.markdown(raw_txt)

    return render_template(
        "WelcomePage.HTML",
        translations=translations,
        lang=lang,
        home_content_html=home_content_html,
    )

# ============================================================
# Calculation page (input)
# ============================================================
@app.route("/input")
def input_page():
    """Show the scan, age-group, and hospital search page."""
    lang = request.args.get("lang", "en")
    translations = get_translations(lang)

    selected_service = request.args.get("service", "")
    postcode = request.args.get("postcode", "")
    adult = _parse_adult_flag(request.args.get("adult", "1"))

    locations = []
    result_mode = None
    health_board = None

    show_all = request.args.get("show_all", "")
    if show_all == "true" and selected_service in get_scan_choices():
        try:
            result = get_hospitals_offering_scan(selected_service)
            for h in result["hospitals"]:
                if lang == "cy":
                    h["display_name"] = h.get(
                        "Hospital Name (Welsh)", h["Hospital Name"]
                    )
                else:
                    h["display_name"] = h["Hospital Name"]
            locations = result["hospitals"]
            result_mode = "all"
        except ValueError:
            pass

    return render_template(
        "InputPage.HTML",
        translations=translations,
        lang=lang,
        services=_get_translated_services(translations),
        locations=locations,
        selected_service=selected_service,
        postcode=postcode,
        adult=adult,
        result_mode=result_mode,
        health_board=health_board,
    )


@app.route("/choose-hospital-search", methods=["POST"])
def choose_hospital_search():
    """Return a filtered hospital list on the input page."""
    lang = request.form.get("lang", "").strip() or "en"
    translations = get_translations(lang)

    scan_choice = request.form.get("service", "").strip()
    postcode = request.form.get("postcode", "").strip()
    search_method = request.form.get("search_method", "").strip()
    adult = _parse_adult_flag(request.form.get("adult", "1"))

    if scan_choice not in get_scan_choices():
        abort(400, description="Please select a valid scan.")

    def _add_display_name(hospital_dict):
        if lang == "cy":
            hospital_dict["display_name"] = hospital_dict.get(
                "Hospital Name (Welsh)", hospital_dict["Hospital Name"]
            )
        else:
            hospital_dict["display_name"] = hospital_dict["Hospital Name"]
        return hospital_dict

    if search_method == "nearest":
        if not postcode:
            abort(400, description="Please enter a postcode.")

        try:
            result = get_nearest_hospitals(
                postcode=postcode,
                scan_choice=scan_choice,
                limit=3,
            )
        except PostcodeServiceUnavailable as error:
            abort(503, description=str(error))
        except ValueError as error:
            abort(400, description=str(error))

        return render_template(
            "InputPage.HTML",
            translations=translations,
            lang=lang,
            services=_get_translated_services(translations),
            locations=[_add_display_name(h) for h in result["hospitals"]],
            selected_service=scan_choice,
            postcode=result["postcode"],
            adult=adult,
            result_mode="nearest",
            health_board=_translate_health_board(
                result["health_board"], translations
            ),
        )

    if search_method == "all":
        try:
            result = get_hospitals_offering_scan(scan_choice)
        except ValueError as error:
            abort(400, description=str(error))

        return render_template(
            "InputPage.HTML",
            translations=translations,
            lang=lang,
            services=_get_translated_services(translations),
            locations=[_add_display_name(h) for h in result["hospitals"]],
            selected_service=scan_choice,
            postcode=postcode,
            adult=adult,
            result_mode="all",
            health_board=None,
        )

    abort(400, description="Please choose Nearest or All hospitals.")


# ============================================================
# Output page
# ============================================================
@app.route("/calculate", methods=["GET", "POST"])
def run_calculation():
    """Look up pre-computed waiting time & stock-and-flow projection."""
    lang = request.form.get("lang") or request.args.get("lang", "").strip() or "en"
    translations = get_translations(lang)

    scan_choice = request.form.get("service") or request.args.get("service", "").strip()
    postcode = (
        request.form.get("postcode") or request.args.get("postcode", "")
    ).strip().upper()
    hospital_choice = (
        request.form.get("location") or request.args.get("location", "")
    ).strip()
    adult = _parse_adult_flag(
        request.form.get("adult") or request.args.get("adult", "1")
    )

    other_hospitals = []
    if postcode:
        try:
            result = get_nearest_hospitals(
                postcode=postcode,
                scan_choice=scan_choice,
                limit=3,
            )
        except PostcodeServiceUnavailable as error:
            abort(503, description=str(error))
        except ValueError as error:
            abort(400, description=str(error))

        other_hospitals = [
            hospital
            for hospital in result["hospitals"]
            if hospital["Hospital Name"] != hospital_choice
        ]
        # Attach current waiting time to each nearby alternative hospital
        for alt_hospital in other_hospitals:
            alt_record = get_wait_record(
                data,
                scan_choice,
                alt_hospital["Hospital Name"],
                adult=adult,
            )
            alt_hospital["typical_wait"] = (
                alt_record["typical_wait_weeks"] if alt_record is not None else None
            )
            
    driving_distance = request.form.get("driving_distance")
    driving_duration = request.form.get("driving_duration")
    walking_distance = request.form.get("walking_distance")
    walking_duration = request.form.get("walking_duration")

    if not scan_choice:
        abort(400, description="A service must be selected.")
    if scan_choice not in get_scan_choices():
        abort(400, description="The selected service is not in the approved list.")
    if not hospital_choice:
        abort(404, description="Please select a valid hospital from the list.")

    record = get_wait_record(
        data,
        scan_choice,
        hospital_choice,
        adult=adult,
    )

    if record is not None:
        typical_wait = record["typical_wait_weeks"]
        wait_weeks_25pct = record.get("wait_weeks_25pct")
        wait_weeks_75pct = record.get("wait_weeks_75pct")
        predicted_wait = record["predicted_wait_weeks"]
        wait_trend = record["wait_trend"]
        colour_zone = record["colour_zone"]
        needle_angle = record["needle_angle"]
        latest_date_en = record["latest_date"]
    else:
        typical_wait = None
        wait_weeks_25pct = None
        wait_weeks_75pct = None
        predicted_wait = None
        wait_trend = "stable"
        colour_zone = "green"
        needle_angle = -90.0
        latest_date_en = get_max_date()

    if " " in latest_date_en:
        month_en, year = latest_date_en.split(" ", 1)
        month_key = f"month_{month_en}"
        latest_date = f"{translations.get(month_key, month_en)} {year}"
    else:
        latest_date = latest_date_en

    if lang == "cy":
        hospital_display_name = get_welsh_hospital_name(hospital_choice)
    else:
        hospital_display_name = hospital_choice

    return render_template(
        "OutputPage.HTML",
        translations=translations,
        lang=lang,
        adult=adult,
        typical_wait=typical_wait,
        wait_weeks_25pct=wait_weeks_25pct,
        wait_weeks_75pct=wait_weeks_75pct,
        predicted_wait=predicted_wait,
        wait_trend=wait_trend,
        scan_choice=scan_choice,
        hospital_choice=hospital_choice,
        hospital_display_name=hospital_display_name,
        postcode=postcode,
        latest_date=latest_date,
        colour_zone=colour_zone,
        needle_angle=needle_angle,
        driving_distance=driving_distance,
        driving_duration=driving_duration,
        walking_distance=walking_distance,
        walking_duration=walking_duration,
        other_hospitals=other_hospitals,
    )


# ============================================================
# Visualisations pages
# ============================================================

@app.route("/visualisations")
def visualisations_page():
    lang = request.args.get("lang", "en")
    translations = get_translations(lang)
    return render_template(
        "VisualisationsPage.HTML",
        translations=translations,
        lang=lang,
    )


COORDINATES_FILE = (
    Path(__file__).resolve().parent
    / "reference_datasets"
    / "selected_hospitals_services_coordinates.csv"
)


@app.route("/visualisations/heatmap")
def heatmap_page():
    hospital_coordinates = load_hospital_coordinates(COORDINATES_FILE)
    lang = request.args.get("lang", "en")
    adult = _parse_adult_flag(request.args.get("adult", "1"))
    translations = get_translations(lang)

    all_services = get_scan_choices()
    scan_name_translations = {}
    for service in all_services:
        trans_key = SERVICE_TRANSLATION_KEYS.get(service)
        if trans_key and trans_key in translations:
            scan_name_translations[service] = translations[trans_key]
        else:
            scan_name_translations[service] = service

    waiting_time_map = build_waiting_time_map(data, adult=adult)

    return render_template(
        "HeatMapPage.HTML",
        translations=translations,
        lang=lang,
        waiting_time_map=waiting_time_map,
        hospital_coordinates=hospital_coordinates,
        scan_name_translations=scan_name_translations,
    )


@app.route("/visualisations/stacked-chart")
def stacked_chart_page():
    lang = request.args.get("lang", "en")
    adult = _parse_adult_flag(request.args.get("adult", "1"))
    translations = get_translations(lang)

    fig1 = get_fig1(translations, adult=adult)
    graph1_html = fig1.to_html(full_html=False)

    return render_template(
        "StackedBarChartPage.HTML",
        lang=lang,
        translations=translations,
        graph1=graph1_html,
    )


@app.route("/visualisations/line-graph")
def line_graph_page():
    lang = request.args.get("lang", "en")
    adult = _parse_adult_flag(request.args.get("adult", "1"))
    translations = get_translations(lang)

    translated_services = _get_translated_services(translations)
    selected_service = request.args.get("service")
    all_services = get_scan_choices()

    if not selected_service or selected_service not in all_services:
        selected_service = all_services[0]

    fig2 = get_fig2(selected_service, translations, adult=adult)
    graph2_html = fig2.to_html(full_html=False)

    return render_template(
        "LineGraphPage.HTML",
        lang=lang,
        translations=translations,
        services=translated_services,
        scan_type=selected_service,
        graph2=graph2_html,
    )

@app.route("/visualisations/forecast")
def forecast_page():
    """Render static adult-only (adult = 1) v0.3 forecast cards."""
    lang = request.args.get("lang", "en")
    translations = get_translations(lang)

    category = request.args.get("category", "").strip()
    selection = request.args.get("selection", "").strip()
    metric = request.args.get("metric", "percentage_change").strip()

    valid_metrics = {"percentage_change", "total_waiting", "incoming_referrals"}
    if metric not in valid_metrics:
        metric = "percentage_change"

    if category not in {"scan_type", "hospital", "health_board"}:
        category = ""
        selection = ""

    filter_options = get_forecast_filter_options()
    view_data = get_forecast_view_data(
        category=category,
        selection=selection,
        metric=metric,
        lang=lang,
    )

    # Translate scan display labels and Welsh hospital names for dropdown menus
    scan_display_lookup = dict(_get_translated_services(translations))
    scan_choices = [
        {
            "value": scan_val,
            "label": scan_display_lookup.get(scan_val, scan_val),
        }
        for scan_val in filter_options["scan_types"]
    ]
    hospital_choices = [
        {
            "value": hosp_name,
            "label": get_welsh_hospital_name(hosp_name) if lang == "cy" else hosp_name,
        }
        for hosp_name in filter_options["hospitals"]
    ]
    health_board_choices = [
        {
            "value": hb_name,
            "label": _translate_health_board(hb_name, translations),
        }
        for hb_name in filter_options["health_boards"]
    ]

    #Filter out empty result Cards

    valid_cards = [
        card
        for card in view_data["cards"]
        if any(isinstance(v, str) and v.endswith(".png") for v in card.values())
    ]

    return render_template(
        "Forecasts.HTML",
        lang=lang,
        translations=translations,
        category=view_data["category"],
        selection=view_data["selection"],
        metric=view_data["metric"],
        is_default=view_data["is_default"],
        cards=valid_cards,
        scan_choices=scan_choices,
        hospital_choices=hospital_choices,
        health_board_choices=health_board_choices,
    )

    return render_template(
        "Forecasts.HTML",
        lang=lang,
        translations=translations,
        category=view_data["category"],
        selection=view_data["selection"],
        metric=view_data["metric"],
        is_default=view_data["is_default"],
        cards=view_data["cards"],
        scan_choices=scan_choices,
        hospital_choices=hospital_choices,
        health_board_choices=health_board_choices,
    )

# ============================================================
# Information page
# ============================================================
@app.route("/information")
def information_page():
    lang = request.args.get("lang", "en")
    translations = get_translations(lang)
    return render_template(
        "InformationPage.HTML",
        translations=translations,
        lang=lang,
    )


# ============================================================
# Data Quality Page
# ============================================================

@app.route("/data-quality")
def data_quality_page():
    lang = request.args.get("lang", "en")
    translations = get_translations(lang)

    md_filename = "data_quality_cy.md" if lang == "cy" else "data_quality_en.md"
    md_path = BASE_DIR / "content" / md_filename
    raw_md = md_path.read_text(encoding="utf-8")

    content_html = markdown.markdown(
        raw_md,
        extensions=["tables", "fenced_code", "sane_lists"],
    )

    return render_template(
        "Data_Quality.HTML",
        translations=translations,
        lang=lang,
        content_html=content_html,
    )

# ============================================================
# Methodology Page
# ============================================================

@app.route("/information/methodology")
def methodology_page():
    lang = request.args.get("lang", "en")
    translations = get_translations(lang)
    return render_template(
        "MethodologyPage.HTML",
        translations=translations,
        lang=lang,
    )

# ============================================================
# Future Development
# ============================================================
@app.route("/information/future-development")
def future_development_page():
    lang = request.args.get("lang", "en")
    translations = get_translations(lang)
    return render_template(
        "FutureDevelopmentPage.HTML",
        translations=translations,
        lang=lang,
    )


if __name__ == "__main__":
    app.run(debug=True)