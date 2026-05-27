"""Build sessions.parquet — event metadata + results."""

from __future__ import annotations

import pandas as pd

from src.data.fetch_fastf1 import iter_sessions
from src.utils.paths import INTERIM_DIR


def build_sessions_dataframe(
    start: int = 2018, end: int = 2026, types: tuple[str, ...] = ("R",)
) -> pd.DataFrame:
    """Iterate sessions and build a unified sessions DataFrame.

    Returns:
        DataFrame with columns:
            season, round, country, circuit_name, session_type, date,
            driver, team, grid_position, finish_position, status
    """
    rows: list[dict] = []

    for session in iter_sessions(start, end, types):
        event = session.event
        results = session.results
        if results is None or results.empty:
            continue

        session_date = event.get("EventDate")
        # fastf1 may return various date-like types; normalise
        if session_date is not None:
            session_date = pd.Timestamp(session_date).isoformat()

        for _, r in results.iterrows():
            rows.append(
                {
                    "season": int(session.event.year),
                    "round": int(event.get("RoundNumber", 0)),
                    "country": event.get("Country", ""),
                    "circuit_name": event.get("EventName", ""),
                    "session_type": session.name,
                    "date": session_date,
                    "driver": r.get("Abbreviation", ""),
                    "team": r.get("TeamName", ""),
                    "grid_position": (
                        int(r["GridPosition"]) if pd.notna(r.get("GridPosition")) else None
                    ),
                    "finish_position": (
                        int(r["Position"]) if pd.notna(r.get("Position")) else None
                    ),
                    "status": r.get("Status", ""),
                }
            )

    df = pd.DataFrame(rows)

    # Schema enforcement
    expected_types = {
        "season": "int64",
        "round": "int64",
        "country": "object",
        "circuit_name": "object",
        "session_type": "object",
        "date": "object",
        "driver": "object",
        "team": "object",
        "grid_position": "Int64",  # nullable int
        "finish_position": "Int64",
        "status": "object",
    }
    from contextlib import suppress

    for col, dtype in expected_types.items():
        if col in df.columns and df[col].dtype.name != dtype:
            with suppress(ValueError, TypeError):
                df[col] = df[col].astype(dtype)

    return df


def build_sessions(
    start: int = 2018, end: int = 2026, types: tuple[str, ...] = ("R",)
) -> None:
    """Build and save sessions.parquet."""
    df = build_sessions_dataframe(start, end, types)
    dst = INTERIM_DIR / "sessions.parquet"
    dst.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(dst, index=False)
    print(f"✓ sessions.parquet — {len(df)} rows → {dst}")


if __name__ == "__main__":
    build_sessions()
