"""Find hospitals for ScanWait Wales using Postcodes.io + free OSRM road routing.

1. Validate and geocode the Welsh postcode via Postcodes.io.
2. Keep only hospitals that offer the chosen scan.
3. Rank hospitals by straight-line Haversine distance and keep the nearest three.
4. Query the free public OSRM (OpenStreetMap Routing Machine) API for driving
   and walking distance and duration (no API key required).
"""

from __future__ import annotations

import logging
from pathlib import Path
import sys

sys.dont_write_bytecode = True

from typing import Any
from urllib.parse import quote

import numpy as np
import pandas as pd
import requests

LOGGER = logging.getLogger(__name__)

FLASK_APP_DIR = Path(__file__).resolve().parent.parent
if str(FLASK_APP_DIR) not in sys.path:
    sys.path.insert(0, str(FLASK_APP_DIR))

from scan_config import SCAN_SERVICE_MAP  # noqa: E402

HOSPITAL_DATA_FILE = (
    FLASK_APP_DIR
    / "reference_datasets"
    / "selected_hospitals_services_coordinates.csv"
)

OSRM_BASE_URL = "https://router.project-osrm.org/route/v1"
OSRM_HEADERS = {
    "User-Agent": "ScanWaitWales/1.0 (NHS Wales diagnostic wait-time informational tool)",
}

PUBLIC_HOSPITAL_COLUMNS = [
    "Hospital Name",
    "Hospital Name (Welsh)",
    "Postcode",
    "Health board",
    "driving_distance",
    "driving_duration",
    "walking_distance",
    "walking_duration",
    "_distance_miles",
]


class PostcodeServiceUnavailable(RuntimeError):
    """Raised when Postcodes.io cannot be reached or returns an invalid reply."""


def _require_columns(
    dataframe: pd.DataFrame,
    required_columns: set[str],
    filename: str,
) -> None:
    """Verify that the hospital reference CSV has the required columns."""
    missing_columns = required_columns - set(dataframe.columns)
    if missing_columns:
        raise ValueError(
            f"{filename} is missing required columns: "
            + ", ".join(sorted(missing_columns))
        )


def load_hospital_data() -> pd.DataFrame:
    """Load the canonical hospital coordinates and service table."""
    hospitals = pd.read_csv(HOSPITAL_DATA_FILE)

    _require_columns(
        hospitals,
        {
            "Hospital Name",
            "Postcode",
            "Health board",
            "lat",
            "long",
        },
        HOSPITAL_DATA_FILE.name,
    )

    duplicate_hospital_names = hospitals["Hospital Name"].duplicated(keep=False)
    if duplicate_hospital_names.any():
        duplicate_names = sorted(
            hospitals.loc[duplicate_hospital_names, "Hospital Name"]
            .astype(str)
            .unique()
        )
        raise ValueError(
            f"{HOSPITAL_DATA_FILE.name} contains duplicate hospital names: "
            + ", ".join(duplicate_names)
        )

    hospitals["lat"] = pd.to_numeric(hospitals["lat"], errors="coerce")
    hospitals["long"] = pd.to_numeric(hospitals["long"], errors="coerce")
    return hospitals


HOSPITALS = load_hospital_data()


def get_welsh_hospital_name(english_name: str) -> str:
    """Return the Welsh name for a hospital, or the English name if not found."""
    if "Hospital Name (Welsh)" not in HOSPITALS.columns:
        return english_name
    match = HOSPITALS.loc[
        HOSPITALS["Hospital Name"] == english_name,
        "Hospital Name (Welsh)",
    ]
    if match.empty:
        return english_name
    return str(match.iloc[0])


def lookup_postcode(postcode: str) -> dict[str, Any]:
    """Validate a Welsh postcode via Postcodes.io and return its coordinates."""
    normalised_postcode = "".join(str(postcode or "").upper().split())
    if not normalised_postcode:
        raise ValueError("Please enter a postcode.")

    encoded_postcode = quote(normalised_postcode, safe="")
    postcode_url = f"https://api.postcodes.io/postcodes/{encoded_postcode}"

    try:
        response = requests.get(postcode_url, timeout=5)
    except requests.RequestException as error:
        raise PostcodeServiceUnavailable(
            "The postcode service is currently unavailable."
        ) from error

    if response.status_code == 404:
        raise ValueError("The postcode could not be found.")

    try:
        response.raise_for_status()
    except requests.HTTPError as error:
        raise PostcodeServiceUnavailable(
            "The postcode service returned an error."
        ) from error

    try:
        result = response.json().get("result")
    except ValueError as error:
        raise PostcodeServiceUnavailable(
            "The postcode service returned an invalid response."
        ) from error

    if not result:
        raise ValueError("No information was found for that postcode.")

    if result.get("country") != "Wales":
        raise ValueError("Please enter a postcode in Wales.")

    latitude = result.get("latitude")
    longitude = result.get("longitude")
    if latitude is None or longitude is None:
        raise ValueError("Coordinates were not available for that postcode.")

    return {
        "postcode": result.get("postcode", normalised_postcode),
        "latitude": float(latitude),
        "longitude": float(longitude),
        "health_board": result.get("nhs_ha") or "Health board unavailable",
    }


def _eligible_hospitals(scan_choice: str) -> pd.DataFrame:
    """Keep only hospitals that offer the chosen scan."""
    if scan_choice not in SCAN_SERVICE_MAP:
        raise ValueError("Please select a valid scan.")

    scan_columns = SCAN_SERVICE_MAP[scan_choice]
    missing_columns = [
        column for column in scan_columns if column not in HOSPITALS.columns
    ]
    if missing_columns:
        raise ValueError(
            "The scan availability file is missing columns: "
            + ", ".join(missing_columns)
        )

    availability_values = HOSPITALS[scan_columns].apply(
        pd.to_numeric,
        errors="coerce",
    )
    offers_scan = availability_values.fillna(0).gt(0).any(axis=1)

    eligible_hospitals = HOSPITALS.loc[offers_scan].copy()
    eligible_hospitals = eligible_hospitals.drop_duplicates(
        subset=["Hospital Name"]
    )

    if eligible_hospitals.empty:
        raise ValueError("No hospitals were found for that scan.")

    return eligible_hospitals


def _add_straight_line_distance(
    hospitals: pd.DataFrame,
    user_latitude: float,
    user_longitude: float,
) -> pd.DataFrame:
    """Measure the straight-line Haversine distance (miles) to each hospital."""
    results = hospitals.dropna(subset=["lat", "long"]).copy()
    if results.empty:
        raise ValueError(
            "No coordinate data is available for hospitals offering this scan."
        )

    user_latitude_radians = np.radians(float(user_latitude))
    user_longitude_radians = np.radians(float(user_longitude))

    hospital_latitudes = np.radians(results["lat"].to_numpy(dtype=float))
    hospital_longitudes = np.radians(results["long"].to_numpy(dtype=float))

    latitude_difference = hospital_latitudes - user_latitude_radians
    longitude_difference = hospital_longitudes - user_longitude_radians

    haversine_value = (
        np.sin(latitude_difference / 2) ** 2
        + np.cos(user_latitude_radians)
        * np.cos(hospital_latitudes)
        * np.sin(longitude_difference / 2) ** 2
    )
    haversine_value = np.clip(haversine_value, 0, 1)

    angular_distance = 2 * np.arctan2(
        np.sqrt(haversine_value),
        np.sqrt(1 - haversine_value),
    )

    earth_radius_miles = 3958.7613
    results["_distance_miles"] = earth_radius_miles * angular_distance
    return results


def format_duration(total_minutes: int) -> str:
    """Convert total minutes into an HHhr MMm or X mins string format."""
    hours = total_minutes // 60
    mins = total_minutes % 60
    if hours == 0:
        return f"{mins} mins"
    return f"{hours:02d}hr {mins:02d}m"


def _add_osrm_travel_information(
    hospitals: pd.DataFrame,
    user_latitude: float,
    user_longitude: float,
) -> pd.DataFrame:
    """Query the free public OSRM API for driving and walking distance & duration."""
    results = hospitals.dropna(subset=["lat", "long"]).copy()
    if results.empty:
        raise ValueError(
            "No coordinate data is available for hospitals offering this scan."
        )

    for column_name in (
        "driving_distance",
        "driving_duration",
        "walking_distance",
        "walking_duration",
    ):
        results[column_name] = "Unavailable"

    for index, hospital in results.iterrows():
        dest_lat = float(hospital["lat"])
        dest_lon = float(hospital["long"])
        # OSRM expects coordinates as longitude,latitude
        coords_segment = f"{float(user_longitude)},{float(user_latitude)};{dest_lon},{dest_lat}"

        for travel_mode, osrm_profile in [("driving", "driving"), ("walking", "foot")]:
            distance_column = f"{travel_mode}_distance"
            duration_column = f"{travel_mode}_duration"

            route_url = (
                f"{OSRM_BASE_URL}/{osrm_profile}/{coords_segment}"
                "?overview=false&alternatives=false&steps=false"
            )

            try:
                response = requests.get(
                    route_url,
                    headers=OSRM_HEADERS,
                    timeout=6,
                )
                if response.status_code == 200:
                    payload = response.json()
                    routes = payload.get("routes", [])
                    if payload.get("code") == "Ok" and routes:
                        route = routes[0]
                        distance_meters = float(route.get("distance", 0.0))
                        distance_miles = distance_meters * 0.000621371
                        results.at[index, distance_column] = f"{distance_miles:.1f} mi"

                        duration_seconds = float(route.get("duration", 0.0))
                        mins = max(1, round(duration_seconds / 60.0))
                        results.at[index, duration_column] = format_duration(mins)
            except Exception as error:
                LOGGER.warning(
                    "OSRM %s route lookup failed for %s: %s",
                    travel_mode,
                    hospital.get("Hospital Name"),
                    error,
                )

    return results


def _public_hospital_records(hospitals: pd.DataFrame) -> list[dict[str, Any]]:
    """Prepare hospital records for Jinja templates."""
    available_columns = [
        column_name
        for column_name in PUBLIC_HOSPITAL_COLUMNS
        if column_name in hospitals.columns
    ]
    return hospitals[available_columns].to_dict(orient="records")


def get_nearest_hospitals(
    postcode: str,
    scan_choice: str,
    limit: int = 3,
) -> dict[str, Any]:
    """Return the nearest hospitals that offer the chosen scan with OSRM travel info."""
    if limit < 1:
        raise ValueError("The hospital limit must be at least 1.")

    postcode_details = lookup_postcode(postcode)
    eligible_hospitals = _eligible_hospitals(scan_choice)

    ranked_hospitals = _add_straight_line_distance(
        eligible_hospitals,
        postcode_details["latitude"],
        postcode_details["longitude"],
    )

    nearest_hospitals = ranked_hospitals.nsmallest(
        limit,
        "_distance_miles",
    ).copy()

    nearest_hospitals = _add_osrm_travel_information(
        nearest_hospitals,
        postcode_details["latitude"],
        postcode_details["longitude"],
    )

    return {
        "mode": "nearest",
        "postcode": postcode_details["postcode"],
        "health_board": postcode_details["health_board"],
        "hospitals": _public_hospital_records(nearest_hospitals),
    }


def get_hospitals_offering_scan(scan_choice: str) -> dict[str, Any]:
    """Return every hospital that offers the chosen scan sorted A-to-Z."""
    eligible_hospitals = _eligible_hospitals(scan_choice)
    eligible_hospitals = eligible_hospitals.sort_values(
        "Hospital Name",
        key=lambda names: names.astype(str).str.casefold(),
    )

    return {
        "mode": "all",
        "postcode": None,
        "health_board": None,
        "hospitals": _public_hospital_records(eligible_hospitals),
    }
