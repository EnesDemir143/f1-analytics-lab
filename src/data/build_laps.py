"""Build laps.parquet — the main lap-level table with weather join."""

from __future__ import annotations

import pandas as pd

from src.data.fetch_fastf1 import iter_sessions
from src.utils.paths import INTERIM_DIR

# Circuit lap records (seconds) for is_valid_lap threshold.
# Values are approximate race lap records for each circuit.
# Extended per Research + Context decisions.
CIRCUIT_LAP_RECORDS: dict[str, float] = {
    "Bahrain": 90.0,
    "Jeddah": 87.0,
    "Albert Park": 78.0,
    "Baku": 101.0,
    "Catalunya": 75.0,
    "Monaco": 70.0,
    "Montreal": 71.0,
    "Silverstone": 85.0,
    "Spielberg": 63.0,
    "Hungaroring": 76.0,
    "Spa": 102.0,
    "Zandvoort": 70.0,
    "Monza": 79.0,
    "Marina Bay": 91.0,
    "Suzuka": 88.0,
    "Lusail": 81.0,
    "Yas Marina": 83.0,
    "Austin": 92.0,
    "Mexico City": 77.0,
    "Interlagos": 69.0,
    "Las Vegas": 81.0,
    "Shanghai": 92.0,
    "Miami": 88.0,
    "Imola": 75.0,
    "Portimao": 77.0,
    "Istanbul": 83.0,
    "Sochi": 85.0,
    "Mugello": 73.0,
    "Nurburgring": 79.0,
    "Sakhir": 89.0,
    "Losail": 81.0,
    "Ricardo Tormo": 71.0,
}

STATUS_MAP = {
    "1": "Green",
    "2": "Yellow",
    "4": "SC",
    "5": "VSC",
    "6": "Red",
}


def _map_track_status(track_status_str: str) -> str:
    """Map Fast-F1 numeric track status to readable string."""
    parts = str(track_status_str).strip().split(",")
    mapped = []
    for p in parts:
        mapped.append(STATUS_MAP.get(p.strip(), p.strip()))
    return ", ".join(mapped)


def _get_circuit_lap_record(circuit_name: str) -> float:
    """Look up approximate lap record for a circuit."""
    for key, record in CIRCUIT_LAP_RECORDS.items():
        if key.lower() in circuit_name.lower():
            return record
    return 999.0  # fallback — permissive


def _is_valid_lap(row: pd.Series, lap_record: float) -> bool:
    """Check whether a lap passes the baseline validity rules.

    Rules (from GA-04 in CONTEXT.md):
        - lap_time > 0
        - lap_time < circuit_lap_record * 1.4
        - compound not null
        - driver not null
    """
    if pd.isna(row.get("lap_time")) or row["lap_time"] <= 0:
        return False
    if row["lap_time"] >= lap_record * 1.4:
        return False
    if pd.isna(row.get("compound")) or str(row["compound"]).strip() == "":
        return False
    return not (pd.isna(row.get("driver")) or str(row["driver"]).strip() == "")


def _seconds(td) -> float | None:
    """Convert timedelta to seconds safely."""
    if pd.isna(td):
        return None
    return td.total_seconds()


def build_laps_dataframe(
    start: int = 2018, end: int = 2026, types: tuple[str, ...] = ("R",)
) -> pd.DataFrame:
    """Build unified lap-level DataFrame with weather join.

    Returns:
        DataFrame with lap-level data and weather features merged.
    """
    all_laps: list[pd.DataFrame] = []
    weather_data: list[pd.DataFrame] = []

    for session in iter_sessions(start, end, types):
        laps = session.laps
        if laps is None or laps.empty:
            continue

        event = session.event
        gp_name = event.get("EventName", "")
        circuit_lap_record = _get_circuit_lap_record(gp_name)

        lap_df = laps.copy()
        lap_df["season"] = int(session.event.year)
        lap_df["round"] = int(event.get("RoundNumber", 0))
        lap_df["grand_prix"] = gp_name
        lap_df["session"] = session.name

        # Rename / normalise columns
        lap_df["lap_time"] = lap_df["LapTime"].apply(_seconds)
        lap_df["sector1_time"] = lap_df["Sector1Time"].apply(_seconds)
        lap_df["sector2_time"] = lap_df["Sector2Time"].apply(_seconds)
        lap_df["sector3_time"] = lap_df["Sector3Time"].apply(_seconds)
        lap_df["driver"] = lap_df["Driver"]
        lap_df["team"] = lap_df["Team"]
        lap_df["compound"] = lap_df["Compound"]
        lap_df["tyre_life"] = lap_df["TyreLife"]
        lap_df["stint"] = lap_df["Stint"]
        lap_df["lap_number"] = lap_df["LapNumber"]
        lap_df["pit_in"] = lap_df["PitInTime"].apply(lambda x: pd.notna(x))
        lap_df["pit_out"] = lap_df["PitOutTime"].apply(lambda x: pd.notna(x))
        lap_df["position"] = lap_df["Position"]
        lap_df["is_deleted"] = lap_df.get("Deleted", False)
        lap_df["lap_start_time"] = lap_df["Time"]
        # Track status — map from numeric codes
        if "TrackStatus" in lap_df.columns:
            lap_df["track_status"] = lap_df["TrackStatus"].apply(_map_track_status)
        else:
            lap_df["track_status"] = "Unknown"

        # is_valid_lap (baseline, GA-04)
        lap_df["is_valid_lap"] = lap_df.apply(
            lambda r: _is_valid_lap(r, circuit_lap_record), axis=1
        )

        # Keep only columns we care about
        keep = [
            "season",
            "round",
            "grand_prix",
            "session",
            "driver",
            "team",
            "lap_number",
            "lap_time",
            "sector1_time",
            "sector2_time",
            "sector3_time",
            "compound",
            "tyre_life",
            "stint",
            "pit_in",
            "pit_out",
            "track_status",
            "position",
            "is_deleted",
            "is_valid_lap",
            "lap_start_time",
        ]
        available = [c for c in keep if c in lap_df.columns]
        all_laps.append(lap_df[available].copy())

        # Weather data — collect for later merge_asof
        wd = session.weather_data
        if wd is not None and not wd.empty:
            wd_copy = wd.copy()
            wd_copy["season"] = int(session.event.year)
            wd_copy["round"] = int(event.get("RoundNumber", 0))
            weather_data.append(wd_copy)

    if not all_laps:
        return pd.DataFrame()

    full_laps = pd.concat(all_laps, ignore_index=True)

    # ── Weather merge (GA-03) ───────────────────────────────────────
    if weather_data:
        full_weather = pd.concat(weather_data, ignore_index=True)
        # Sort both for merge_asof
        full_laps_sorted = full_laps.sort_values("lap_start_time").reset_index(drop=True)
        full_weather_sorted = full_weather.sort_values("Time").reset_index(drop=True)

        # Rename weather columns to avoid collision
        weather_for_merge = full_weather_sorted.rename(
            columns={
                "AirTemp": "air_temp",
                "TrackTemp": "track_temp",
                "Humidity": "humidity",
                "WindSpeed": "wind_speed",
                "WindDirection": "wind_direction",
                "Rainfall": "rainfall",
            }
        )

        full_laps_merged = pd.merge_asof(
            full_laps_sorted,
            weather_for_merge[
                ["Time", "air_temp", "track_temp", "humidity",
                 "wind_speed", "wind_direction", "rainfall"]
            ],
            left_on="lap_start_time",
            right_on="Time",
            direction="nearest",
        )
        full_laps_merged.drop(columns=["Time"], inplace=True)
        full_laps = full_laps_merged

    return full_laps


def build_laps(
    start: int = 2018, end: int = 2026, types: tuple[str, ...] = ("R",)
) -> None:
    """Build and save laps.parquet."""
    df = build_laps_dataframe(start, end, types)
    dst = INTERIM_DIR / "laps.parquet"
    dst.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(dst, index=False)
    print(f"✓ laps.parquet — {len(df)} rows → {dst}")


if __name__ == "__main__":
    build_laps()
