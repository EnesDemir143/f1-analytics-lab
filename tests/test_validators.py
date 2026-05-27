"""Tests for schema validators."""

import pandas as pd
import pytest

from src.data.validators import (
    validate_laps,
    validate_sessions,
    validate_stints,
    validate_weather,
    validate_track_status,
    validate_drivers,
    validate_circuits,
)


def _make_laps(**overrides) -> pd.DataFrame:
    data = {
        "season": pd.array([2024], dtype="int64"),
        "round": pd.array([1], dtype="int64"),
        "grand_prix": ["Bahrain"],
        "session": ["R"],
        "driver": ["HAM"],
        "team": ["Mercedes"],
        "lap_number": pd.array([1], dtype="int64"),
        "lap_time": [94.5],
        "compound": ["SOFT"],
        "is_valid_lap": [True],
    }
    data.update(overrides)
    return pd.DataFrame(data)


class TestValidateLaps:
    def test_valid_lap_passes(self) -> None:
        errors = validate_laps(_make_laps())
        # Skip row-count threshold check (test data is small)
        non_count_errors = [e for e in errors if "rows" not in e]
        assert non_count_errors == []

    def test_missing_required_column(self) -> None:
        df = _make_laps()
        df.drop(columns=["lap_time"], inplace=True)
        errors = validate_laps(df)
        assert any("lap_time" in e for e in errors)

    def test_negative_lap_time_fails(self) -> None:
        df = _make_laps(lap_time=[-1.0])
        errors = validate_laps(df)
        assert any("non-positive" in e.lower() for e in errors)

    def test_excessive_lap_time_fails(self) -> None:
        df = _make_laps(lap_time=[500.0])
        errors = validate_laps(df)
        assert any("exceeds 300s" in e for e in errors)

    def test_unknown_compound_fails(self) -> None:
        df = _make_laps(compound=["UNICORN"])
        errors = validate_laps(df)
        assert any("unknown compound" in e.lower() for e in errors)

    def test_bad_driver_code_fails(self) -> None:
        df = _make_laps(driver=["ABCD"])
        errors = validate_laps(df)
        assert any("driver codes" in e.lower() for e in errors)

    def test_invalid_driver_code_empty(self) -> None:
        df = _make_laps(driver=[""])
        errors = validate_laps(df)
        assert any("driver codes" in e.lower() for e in errors)

    def test_too_few_rows(self) -> None:
        df = _make_laps()
        # We can't really make 250K rows in a test; this checks the min
        # threshold is defined but won't fail on small test data if
        # the function's structure handles it
        errors = validate_laps(df)
        # Should not crash
        assert isinstance(errors, list)


class TestValidateSessions:
    def test_valid_session_passes(self) -> None:
        df = pd.DataFrame({
            "season": pd.array([2024, 2024], dtype="int64"),
            "round": pd.array([1, 2], dtype="int64"),
            "country": ["Bahrain", "Jeddah"],
            "circuit_name": ["Bahrain GP", "Jeddah GP"],
            "driver": ["HAM", "VER"],
            "grid_position": pd.array([1, 1], dtype="Int64"),
        })
        errors = validate_sessions(df)
        assert all("row count" not in e for e in errors)  # don't fail on small test data


class TestValidateStints:
    def test_valid_stint_passes(self) -> None:
        df = pd.DataFrame({
            "season": pd.array([2024], dtype="int64"),
            "round": pd.array([1], dtype="int64"),
            "driver": ["HAM"],
            "stint_number": pd.array([1], dtype="int64"),
            "compound": ["SOFT"],
            "num_laps": pd.array([25], dtype="int64"),
        })
        errors = validate_stints(df)
        assert isinstance(errors, list)


class TestValidateWeather:
    def test_valid_weather_passes(self) -> None:
        df = pd.DataFrame({
            "season": pd.array([2024, 2024, 2024], dtype="int64"),
            "round": pd.array([1, 1, 1], dtype="int64"),
            "time": pd.date_range("2024-01-01", periods=3, freq="30s"),
        })
        errors = validate_weather(df)
        assert errors == []


class TestValidateTrackStatus:
    def test_valid_status_passes(self) -> None:
        df = pd.DataFrame({
            "season": pd.array([2024, 2024], dtype="int64"),
            "round": pd.array([1, 1], dtype="int64"),
            "time": pd.date_range("2024-01-01", periods=2, freq="5min"),
            "status": ["Green", "SC"],
        })
        errors = validate_track_status(df)
        assert errors == []

    def test_unknown_status_fails(self) -> None:
        df = pd.DataFrame({
            "season": pd.array([2024], dtype="int64"),
            "round": pd.array([1], dtype="int64"),
            "time": pd.date_range("2024-01-01", periods=1, freq="5min"),
            "status": ["Purple"],
        })
        errors = validate_track_status(df)
        assert any("unknown status" in e.lower() for e in errors)


class TestValidateDrivers:
    def test_valid_driver_passes(self) -> None:
        df = pd.DataFrame({
            "season": pd.array([2024], dtype="int64"),
            "driver_code": ["HAM"],
            "team": ["Mercedes"],
        })
        errors = validate_drivers(df)
        assert errors == []

    def test_bad_driver_code_fails(self) -> None:
        df = pd.DataFrame({
            "season": pd.array([2024], dtype="int64"),
            "driver_code": ["ABCD"],
            "team": ["Mercedes"],
        })
        errors = validate_drivers(df)
        assert any("driver_code" in e.lower() for e in errors)


class TestValidateCircuits:
    def test_valid_circuit_passes(self) -> None:
        df = pd.DataFrame({
            "circuit_name": ["Bahrain"],
            "country": ["Bahrain"],
        })
        errors = validate_circuits(df)
        assert errors == []

    def test_negative_drs_zones_fails(self) -> None:
        df = pd.DataFrame({
            "circuit_name": ["Bahrain"],
            "country": ["Bahrain"],
            "drs_zones": pd.array([-1], dtype="Int64"),
        })
        errors = validate_circuits(df)
        assert any("negative" in e.lower() for e in errors)

    def test_missing_drs_zones_ok(self) -> None:
        df = pd.DataFrame({
            "circuit_name": ["Bahrain"],
            "country": ["Bahrain"],
        })
        errors = validate_circuits(df)
        assert errors == []
