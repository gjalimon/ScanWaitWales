"""Hospital and service configuration loaded from one canonical CSV source.

The CSV is expected to contain hospital metadata through the ``Type`` column.
Every column after ``Type`` is treated as a service. A value of 1 means the
service is available at that hospital; 0 means it is not available.
"""

from __future__ import annotations

import csv
from functools import lru_cache
from pathlib import Path
from typing import Final

BASE_DIR: Final[Path] = Path(__file__).resolve().parent

HOSPITAL_SERVICES_FILE: Final[Path] = (
    BASE_DIR
    / "reference_datasets"
    / "selected_hospitals_services_coordinates.csv"
)

HOSPITAL_COLUMN: Final[str] = "Hospital Name"
TYPE_COLUMN: Final[str] = "Type"

# Exact CSV/StatsWales service name -> user-facing name.
# Edit the values on the right to rename services in the website.
#######################
# IMPORTANT - SERVICE_DISPLAY_NAMES & SERVICE_DISPLAY ORDER pull from this file into visualisations.py & app.py, so DO. NOT. MOVE. (please, thanks :D )
########################
SERVICE_DISPLAY_NAMES: Final[dict[str, str]] = {
    "Non Cardiac Computed Tomography": "CT",
    "Cardiac Computed Tomography (Cardiac CT)": "CT [Cardiac only]",
    "Non Cardiac Magnetic Resonance Imaging (MRI)": "MRI",
    "Cardiac Magnetic Resonance Imaging (Cardiac MRI)": "MRI [Cardiac only]",
    "Myocardial Perfusion Scanning": (
        "Nuclear Medicine [Cardiac / Myocardial Perfusion]"
    ),
    "Non Cardiac Nuclear Medicine": "Nuclear Medicine",
    "Fluoroscopy": "Fluoroscopy",
    "Diagnostic Angiography": "Diagnostic Angiography",
    "Non-Obstetric Ultrasound": "Ultrasound [Not pregnancy related]",
}

# Order the scan choices as they should appear to the user.
SERVICE_DISPLAY_ORDER: Final[list[str]] = [
    "CT",
    "CT [Cardiac only]",
    "MRI",
    "MRI [Cardiac only]",
    "Ultrasound [Not pregnancy related]",
    "Nuclear Medicine",
    "Nuclear Medicine [Cardiac / Myocardial Perfusion]",
    "Fluoroscopy",
    "Diagnostic Angiography",
]


class HospitalServiceConfigError(RuntimeError):
    """Raised when the canonical hospital/service CSV is missing or invalid."""


def _is_available(value: object, *, hospital: str, service: str) -> bool:
    """Convert a CSV dummy value to a boolean and reject non-binary values."""
    normalised = str(value).strip().lower()
    if normalised in {"1", "1.0", "true", "yes"}:
        return True
    if normalised in {"0", "0.0", "false", "no", ""}:
        return False

    raise HospitalServiceConfigError(
        f"Invalid availability value {value!r} for {service!r} at {hospital!r}; "
        "expected 1 or 0."
    )


def _display_name(source_service: str) -> str:
    """Return the user-facing name for an exact source service name."""
    return SERVICE_DISPLAY_NAMES.get(source_service, source_service).strip()


def _order_scan_choices(available_choices: set[str]) -> list[str]:
    """Return available scan names in the preferred website order."""
    ordered_choices = [
        display_name
        for display_name in SERVICE_DISPLAY_ORDER
        if display_name in available_choices
    ]

    # Include any new CSV services not yet added to SERVICE_DISPLAY_ORDER.
    remaining_choices = sorted(
        available_choices - set(ordered_choices)
    )

    return ordered_choices + remaining_choices


@lru_cache(maxsize=1)
def _load_catalog() -> tuple[tuple[str, ...], dict[str, tuple[str, ...]]]:
    """Load service headers and each hospital's available source services."""
    try:
        source = HOSPITAL_SERVICES_FILE.open(newline="", encoding="utf-8-sig")
    except FileNotFoundError as exc:
        raise HospitalServiceConfigError(
            f"Canonical hospital/service file not found: {HOSPITAL_SERVICES_FILE}"
        ) from exc

    with source:
        reader = csv.DictReader(source)
        headers = reader.fieldnames or []

        if HOSPITAL_COLUMN not in headers:
            raise HospitalServiceConfigError(
                f"Required column {HOSPITAL_COLUMN!r} is missing from "
                f"{HOSPITAL_SERVICES_FILE.name}."
            )
        if TYPE_COLUMN not in headers:
            raise HospitalServiceConfigError(
                f"Required column {TYPE_COLUMN!r} is missing from "
                f"{HOSPITAL_SERVICES_FILE.name}."
            )

        type_index = headers.index(TYPE_COLUMN)
        service_columns = tuple(
            column.strip()
            for column in headers[type_index + 1 :]
            if column.strip()
        )

        if not service_columns:
            raise HospitalServiceConfigError(
                f"No service columns were found after {TYPE_COLUMN!r}."
            )

        hospital_services: dict[str, set[str]] = {}

        for row_number, row in enumerate(reader, start=2):
            hospital = (row.get(HOSPITAL_COLUMN) or "").strip()
            if not hospital:
                raise HospitalServiceConfigError(
                    f"Missing hospital name on CSV row {row_number}."
                )

            available = hospital_services.setdefault(hospital, set())

            for service in service_columns:
                if _is_available(
                    row.get(service, ""),
                    hospital=hospital,
                    service=service,
                ):
                    available.add(service)

    if not hospital_services:
        raise HospitalServiceConfigError(
            f"No hospitals were found in {HOSPITAL_SERVICES_FILE.name}."
        )

    immutable_map = {
        hospital: tuple(
            service
            for service in service_columns
            if service in available_services
        )
        for hospital, available_services in hospital_services.items()
    }

    return service_columns, immutable_map


def get_hospital_choices() -> list[str]:
    """Return selected hospital sites from the canonical CSV."""
    _, hospital_services = _load_catalog()
    return sorted(hospital_services)


def get_scan_service_map() -> dict[str, list[str]]:
    """Map user-facing scan names to exact StatsWales service names."""
    service_columns, hospital_services = _load_catalog()

    services_used = {
        service
        for available_services in hospital_services.values()
        for service in available_services
    }

    scan_service_map: dict[str, list[str]] = {}

    for source_service in service_columns:
        if source_service not in services_used:
            continue

        display_name = _display_name(source_service)
        if not display_name:
            raise HospitalServiceConfigError(
                f"The display name for service {source_service!r} cannot be blank."
            )

        scan_service_map.setdefault(display_name, []).append(source_service)

    return scan_service_map


def get_scan_choices(hospital_name: str | None = None) -> list[str]:
    """Return scans in the preferred order, optionally for one hospital."""
    _, hospital_services = _load_catalog()

    if hospital_name is None:
        available_choices = set(get_scan_service_map())
    else:
        available_source_services = hospital_services.get(
            hospital_name,
            (),
        )
        available_choices = {
            _display_name(source_service)
            for source_service in available_source_services
        }

    return _order_scan_choices(available_choices)


def get_hospital_service_map() -> dict[str, list[str]]:
    """Return each hospital with its user-facing service names."""
    return {
        hospital: get_scan_choices(hospital)
        for hospital in get_hospital_choices()
    }


def hospital_has_service(
    hospital_name: str,
    display_name: str,
) -> bool:
    """Return whether a hospital provides the selected user-facing scan."""
    _, hospital_services = _load_catalog()

    available_source_services = set(
        hospital_services.get(hospital_name, ())
    )
    selected_source_services = get_scan_service_map().get(
        display_name,
        [],
    )

    return any(
        source_service in available_source_services
        for source_service in selected_source_services
    )


def get_source_service_names(display_name: str) -> list[str]:
    """Resolve a user-facing scan name to exact StatsWales service values."""
    return list(get_scan_service_map().get(display_name, []))


# Backwards-compatible mapping used by scanwait.py and calculation code.
SCAN_SERVICE_MAP: Final[dict[str, list[str]]] = get_scan_service_map()
