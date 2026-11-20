"""Build hospital-to-scan waiting-time lookup and load coordinates for heatmaps."""

from __future__ import annotations

import csv
import sys

sys.dont_write_bytecode = True

from scan_config import (
    get_hospital_choices,
    get_scan_choices,
    hospital_has_service,
)
from scanwait import get_typical_wait_weeks


def build_waiting_time_map(waiting_data, adult: int = 1):
    """Build a hospital-to-scan waiting-time lookup for heatmaps."""
    waiting_time_map = {}
    for hospital in get_hospital_choices():
        waiting_time_map[hospital] = {}
        for service in get_scan_choices():
            if hospital_has_service(hospital, service):
                wait_weeks = get_typical_wait_weeks(
                    waiting_data,
                    service,
                    hospital,
                    adult=adult,
                )
                waiting_time_map[hospital][service] = wait_weeks
    return waiting_time_map


def load_hospital_coordinates(csv_file):
    """Read hospital map locations from the canonical reference CSV file."""
    coordinates = {}
    with csv_file.open(
        mode="r",
        encoding="utf-8-sig",
        newline="",
    ) as file:
        rows = csv.DictReader(file)
        for row in rows:
            hospital_name = row["Hospital Name"].strip()
            latitude = row["lat"].strip()
            longitude = row["long"].strip()
            if not hospital_name or not latitude or not longitude:
                continue
            coordinates[hospital_name] = {
                "lat": float(latitude),
                "long": float(longitude),
            }
    return coordinates
