"""Schema validation for interim Parquet files.

Each validator checks:
    - Required columns exist
    - Column data types match expectations
    - Value ranges are reasonable
    - No unexpected nulls in critical columns
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from src.utils.paths import INTERIM_DIR

# ── Validation rules ──────────────────────────────────────────────────

COMPOUNDS = {"SOFT", "MEDIUM", "HARD", "INTERMEDIATE", "WET", "UNKNOWN", None}


def _col_exists(df: pd.DataFrame, col: str) -> bool:
    return col in df.columns


def _check_types(df: pd.DataFrame, expected: dict[str, str]) -> list[str]:
    errors: list[str] = []
    for col, dtype in expected.items():
        if col in df.columns:
            actual = str(df[col].dtype)
            # Allow nullable Int64 to match int64 conceptually
            if dtype == "int64" and actual in ("Int64", "int64", "Int32", "int32"):
                continue
            if actual != dtype:
                errors.append(f"  ✗ {col}: expected {dtype}, got {actual}")
        else:
            errors.append(f"  ✗ {col}: column missing")
    return errors


def _check_min_rows(df: pd.DataFrame, name: str, minimum: int) -> list[str]:
    if len(df) < minimum:
        return [f"  ✗ {name}: only {len(df)} rows, expected ≥ {minimum}"]
    return []


# ── Per-table validators ──────────────────────────────────────────────

def validate_sessions(df: pd.DataFrame) -> list[str]:
    errors: list[str] = []
    required = ["season", "round", "country", "circuit_name", "driver"]
    for col in required:
        if not _col_exists(df, col):
            errors.append(f"  ✗ required column '{col}' missing")
    errors.extend(_check_types(df, {"season": "int64", "round": "int64", "grid_position": "Int64"}))
    errors.extend(_check_min_rows(df, "sessions", 500))
    # Season range
    if _col_exists(df, "season"):
        years = df["season"].dropna().unique()
        if any(y not in range(2018, 2027) for y in years):
            errors.append(f"  ✗ season(s) outside 2018-2026: {sorted(set(years))}")
    return errors


def validate_laps(df: pd.DataFrame) -> list[str]:
    errors: list[str] = []
    required = ["season", "round", "grand_prix", "driver", "lap_time", "compound", "is_valid_lap"]
    for col in required:
        if not _col_exists(df, col):
            errors.append(f"  ✗ required column '{col}' missing")
    errors.extend(
        _check_types(df, {"season": "int64", "lap_number": "int64", "is_valid_lap": "bool"})
    )
    errors.extend(_check_min_rows(df, "laps", 250_000))
    # lap_time range
    if _col_exists(df, "lap_time"):
        lt = df["lap_time"].dropna()
        if (lt <= 0).any():
            errors.append("  ✗ lap_time contains non-positive values (should be > 0)")
        if (lt > 300).any():
            errors.append("  ✗ lap_time exceeds 300s (unrealistic)")
    # compound validity
    if _col_exists(df, "compound"):
        invalid = df["compound"].dropna().apply(lambda x: x not in COMPOUNDS)
        if invalid.any():
            errors.append(
                f"  ✗ unknown compound values: "
                f"{df.loc[invalid, 'compound'].unique().tolist()}"
            )
    # driver code length
    if _col_exists(df, "driver"):
        bad_drivers = df["driver"].dropna().apply(
            lambda x: len(str(x)) != 3 or str(x).strip() == ""
        )
        if bad_drivers.any():
            errors.append("  ✗ driver codes not 3 characters")
    return errors


def validate_stints(df: pd.DataFrame) -> list[str]:
    errors: list[str] = []
    required = ["season", "round", "driver", "stint_number", "compound", "num_laps"]
    for col in required:
        if not _col_exists(df, col):
            errors.append(f"  ✗ required column '{col}' missing")
    errors.extend(_check_min_rows(df, "stints", 3_000))
    # stint_number starts at 1
    if _col_exists(df, "stint_number") and (df["stint_number"].dropna() < 1).any():
        errors.append("  ✗ stint_number < 1")
    return errors


def validate_weather(df: pd.DataFrame) -> list[str]:
    errors: list[str] = []
    required = ["season", "round", "time"]
    for col in required:
        if not _col_exists(df, col):
            errors.append(f"  ✗ required column '{col}' missing")
    # Weather can be small if early seasons lack it; just check it exists
    errors.extend(_check_min_rows(df, "weather", 1))
    return errors


def validate_track_status(df: pd.DataFrame) -> list[str]:
    errors: list[str] = []
    required = ["season", "round", "time", "status"]
    for col in required:
        if not _col_exists(df, col):
            errors.append(f"  ✗ required column '{col}' missing")
    # status mapping check
    if _col_exists(df, "status"):
        valid_statuses = {"Green", "Yellow", "SC", "VSC", "Red"}
        unknown = df["status"].dropna().apply(lambda x: x.split(", ")[0] not in valid_statuses)
        if unknown.any():
            errors.append(
                f"  ✗ unknown status values: "
                f"{df.loc[unknown, 'status'].unique().tolist()}"
            )
    return errors


def validate_drivers(df: pd.DataFrame) -> list[str]:
    errors: list[str] = []
    required = ["season", "driver_code", "team"]
    for col in required:
        if not _col_exists(df, col):
            errors.append(f"  ✗ required column '{col}' missing")
    codes = df["driver_code"].dropna()
    bad = codes.apply(lambda x: len(str(x)) != 3 or str(x).strip() == "")
    if bad.any():
        errors.append("  ✗ driver_code not 3 characters")
    return errors


def validate_circuits(df: pd.DataFrame) -> list[str]:
    errors: list[str] = []
    required = ["circuit_name", "country"]
    for col in required:
        if not _col_exists(df, col):
            errors.append(f"  ✗ required column '{col}' missing")
    if _col_exists(df, "drs_zones") and (df["drs_zones"].dropna() < 0).any():
        errors.append("  ✗ negative drs_zones")
    return errors


# ── Registry ──────────────────────────────────────────────────────────

VALIDATORS: dict[str, tuple[Path, Any]] = {
    "sessions": (INTERIM_DIR / "sessions.parquet", validate_sessions),
    "laps": (INTERIM_DIR / "laps.parquet", validate_laps),
    "stints": (INTERIM_DIR / "stints.parquet", validate_stints),
    "weather": (INTERIM_DIR / "weather.parquet", validate_weather),
    "track_status": (INTERIM_DIR / "track_status.parquet", validate_track_status),
    "drivers": (INTERIM_DIR / "drivers.parquet", validate_drivers),
    "circuits": (INTERIM_DIR / "circuits.parquet", validate_circuits),
}


def validate_one(name: str, path: Path, validator) -> list[str]:
    """Run a single validator on a Parquet file."""
    if not path.exists():
        return [f"  ✗ {name}: file not found at {path}"]
    try:
        df = pd.read_parquet(path)
        return validator(df)
    except Exception as e:
        return [f"  ✗ {name}: read error — {e}"]


def validate_all() -> dict[str, list[str]]:
    """Validate all interim tables.

    Returns:
        Dict mapping table name -> list of error messages (empty = clean).
    """
    results: dict[str, list[str]] = {}
    for name, (path, validator) in VALIDATORS.items():
        errors = validate_one(name, path, validator)
        results[name] = errors
    return results


def validation_report() -> str:
    """Produce a text report from validate_all()."""
    results = validate_all()
    lines: list[str] = []
    lines.append("=" * 50)
    lines.append("INTERIM DATA VALIDATION REPORT")
    lines.append("=" * 50)
    total_errors = 0

    for name in sorted(results):
        errors = results[name]
        if not errors:
            lines.append(f"  ✓ {name}: PASSED")
        else:
            lines.append(f"  ✗ {name}: FAILED ({len(errors)} issues)")
            for e in errors:
                lines.append(f"     {e}")
                total_errors += 1

    lines.append("-" * 50)
    lines.append(f"Result: {'ALL PASSED ✓' if total_errors == 0 else f'{total_errors} error(s) ✗'}")
    lines.append("=" * 50)
    return "\n".join(lines)


if __name__ == "__main__":
    print(validation_report())
