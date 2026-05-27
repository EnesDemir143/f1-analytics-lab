"""Build track_status.parquet — track status events from Fast-F1 sessions."""

from __future__ import annotations

import pandas as pd

from src.data.fetch_fastf1 import iter_sessions
from src.utils.paths import INTERIM_DIR

STATUS_MAP = {
    "1": "Green",
    "2": "Yellow",
    "4": "SC",
    "5": "VSC",
    "6": "Red",
}


def _map_status(code: str) -> str:
    """Map numeric track status code to human-readable string."""
    return STATUS_MAP.get(str(code).strip(), str(code).strip())


def build_track_status_dataframe(
    start: int = 2018, end: int = 2026, types: tuple[str, ...] = ("R",)
) -> pd.DataFrame:
    """Build unified track status DataFrame from all sessions.

    Returns:
        DataFrame with columns: season, round, time, status, message
    """
    all_status: list[pd.DataFrame] = []

    for session in iter_sessions(start, end, types):
        ts = session.track_status
        if ts is None or ts.empty:
            continue

        event = session.event
        df = ts.copy()
        df["season"] = int(session.event.year)
        df["round"] = int(event.get("RoundNumber", 0))

        # Rename columns
        df.rename(
            columns={
                "Time": "time",
                "Status": "status_code",
                "Message": "message",
            },
            inplace=True,
        )
        df["status"] = df["status_code"].apply(_map_status)

        keep = ["season", "round", "time", "status", "status_code", "message"]
        available = [c for c in keep if c in df.columns]
        all_status.append(df[available].copy())

    if not all_status:
        return pd.DataFrame()

    return pd.concat(all_status, ignore_index=True)


def build_track_status(
    start: int = 2018, end: int = 2026, types: tuple[str, ...] = ("R",)
) -> None:
    """Build and save track_status.parquet."""
    df = build_track_status_dataframe(start, end, types)
    dst = INTERIM_DIR / "track_status.parquet"
    dst.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(dst, index=False)
    print(f"✓ track_status.parquet — {len(df)} rows → {dst}")


if __name__ == "__main__":
    build_track_status()
