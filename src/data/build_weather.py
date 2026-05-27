"""Build weather.parquet — raw weather data from Fast-F1 sessions."""

from __future__ import annotations

import pandas as pd

from src.data.fetch_fastf1 import iter_sessions
from src.utils.paths import INTERIM_DIR


def build_weather_dataframe(
    start: int = 2018, end: int = 2026, types: tuple[str, ...] = ("R",)
) -> pd.DataFrame:
    """Build unified weather DataFrame from all sessions.

    Returns:
        DataFrame with columns:
            season, round, time, air_temp, track_temp, humidity,
            wind_speed, wind_direction, rainfall
    """
    all_weather: list[pd.DataFrame] = []

    for session in iter_sessions(start, end, types):
        wd = session.weather_data
        if wd is None or wd.empty:
            continue

        event = session.event
        df = wd.copy()
        df["season"] = int(session.event.year)
        df["round"] = int(event.get("RoundNumber", 0))
        df.rename(
            columns={
                "Time": "time",
                "AirTemp": "air_temp",
                "TrackTemp": "track_temp",
                "Humidity": "humidity",
                "WindSpeed": "wind_speed",
                "WindDirection": "wind_direction",
                "Rainfall": "rainfall",
            },
            inplace=True,
        )

        keep = [
            "season",
            "round",
            "time",
            "air_temp",
            "track_temp",
            "humidity",
            "wind_speed",
            "wind_direction",
            "rainfall",
        ]
        available = [c for c in keep if c in df.columns]
        all_weather.append(df[available].copy())

    if not all_weather:
        return pd.DataFrame()

    return pd.concat(all_weather, ignore_index=True)


def build_weather(
    start: int = 2018, end: int = 2026, types: tuple[str, ...] = ("R",)
) -> None:
    """Build and save weather.parquet."""
    df = build_weather_dataframe(start, end, types)
    dst = INTERIM_DIR / "weather.parquet"
    dst.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(dst, index=False)
    print(f"✓ weather.parquet — {len(df)} rows → {dst}")


if __name__ == "__main__":
    build_weather()
