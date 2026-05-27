"""Build stints.parquet — stint-level aggregation from lap data."""

from __future__ import annotations

import pandas as pd

from src.data.fetch_fastf1 import iter_sessions
from src.utils.paths import INTERIM_DIR


def build_stints_dataframe(
    start: int = 2018, end: int = 2026, types: tuple[str, ...] = ("R",)
) -> pd.DataFrame:
    """Build stint-level DataFrame from session lap data.

    Detects stint boundaries based on compound changes and pit_in flags.

    Returns:
        DataFrame with columns:
            season, round, driver, stint_number, start_lap, end_lap,
            compound, num_laps, avg_lap_time,
            stint_start_tyre_age, stint_end_tyre_age
    """
    rows: list[dict] = []

    for session in iter_sessions(start, end, types):
        laps = session.laps
        if laps is None or laps.empty:
            continue

        event = session.event
        season = int(session.event.year)
        gp_round = int(event.get("RoundNumber", 0))

        for driver in laps["Driver"].unique():
            driver_laps = laps[laps["Driver"] == driver].sort_values("LapNumber")
            if driver_laps.empty:
                continue

            current_stint: list = []
            all_stints: list[list] = []

            for _, lap_row in driver_laps.iterrows():
                if current_stint and (
                    lap_row.get("Compound", "") != current_stint[-1].get("Compound", "")
                    or _has_pit(current_stint[-1])
                ):
                    all_stints.append(current_stint)
                    current_stint = []
                current_stint.append(lap_row)

            if current_stint:
                all_stints.append(current_stint)

            for stint_idx, stint in enumerate(all_stints, 1):
                if not stint:
                    continue
                stint_df = pd.DataFrame(stint)
                num_laps = len(stint)
                avg_lap = stint_df["LapTime"].apply(
                    lambda x: x.total_seconds() if pd.notna(x) else None
                ).mean()
                compound = stint[0].get("Compound", None)
                if pd.isna(compound) or str(compound).strip() == "":
                    compound = None
                start_tyre_age = (
                    int(stint[0].get("TyreLife", 0))
                    if pd.notna(stint[0].get("TyreLife"))
                    else 0
                )
                end_tyre_age = (
                    int(stint[-1].get("TyreLife", 0))
                    if pd.notna(stint[-1].get("TyreLife"))
                    else 0
                )

                rows.append(
                    {
                        "season": season,
                        "round": gp_round,
                        "driver": stint[0].get("Driver", ""),
                        "stint_number": stint_idx,
                        "start_lap": int(stint[0].get("LapNumber", 1)),
                        "end_lap": int(stint[-1].get("LapNumber", 1)),
                        "compound": compound,
                        "num_laps": num_laps,
                        "avg_lap_time": avg_lap,
                        "stint_start_tyre_age": start_tyre_age,
                        "stint_end_tyre_age": end_tyre_age,
                    }
                )

    return pd.DataFrame(rows)


def _has_pit(lap_row) -> bool:
    """Check if a lap row indicates a pit entry."""
    pit_time = lap_row.get("PitInTime")
    return pd.notna(pit_time) and pit_time != ""


def build_stints(
    start: int = 2018, end: int = 2026, types: tuple[str, ...] = ("R",)
) -> None:
    """Build and save stints.parquet."""
    df = build_stints_dataframe(start, end, types)
    dst = INTERIM_DIR / "stints.parquet"
    dst.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(dst, index=False)
    print(f"✓ stints.parquet — {len(df)} rows → {dst}")


if __name__ == "__main__":
    build_stints()
