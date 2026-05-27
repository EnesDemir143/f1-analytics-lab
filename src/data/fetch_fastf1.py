"""Fast-F1 session iterator with caching, retry, and progress tracking.

Provides the core iteration primitive for the data pipeline:
iter_sessions() yields loaded Fast-F1 session objects across season ranges.

Dependencies:
    - fastf1 (with cache enabled)
    - tqdm (progress bar)
"""

from __future__ import annotations

from collections.abc import Generator, Sequence

import fastf1
import pandas as pd
from tqdm.auto import tqdm

from src.utils.config import load_config
from src.utils.paths import RAW_DIR
from src.utils.retry import retry

# ── Cache ─────────────────────────────────────────────────────────────

_CACHE_ENABLED = False


def _ensure_cache() -> None:
    """Enable Fast-F1 cache once (idempotent)."""
    global _CACHE_ENABLED  # noqa: PLW0603
    if not _CACHE_ENABLED:
        cache_dir = str(RAW_DIR / "fastf1_cache")
        fastf1.Cache.enable_cache(cache_dir)
        _CACHE_ENABLED = True


# ── Config ────────────────────────────────────────────────────────────

def _get_seasons(cfg: dict | None = None) -> list[int]:
    """Read season list from config, falling back to 2018-2026."""
    if cfg is None:
        cfg = load_config("data")
    return cfg.get("seasons", list(range(2018, 2027)))


def _get_session_types(cfg: dict | None = None) -> list[str]:
    """Read session types from config."""
    if cfg is None:
        cfg = load_config("data")
    return cfg.get("sessions", {}).get("race", ["R"])


# ── Retry helpers ─────────────────────────────────────────────────────

@retry(max_attempts=3, base_delay=2.0)
def _load_event_schedule(season: int) -> pd.DataFrame:
    """Fetch event schedule for a season with retry."""
    return fastf1.get_event_schedule(season)


@retry(max_attempts=3, base_delay=2.0)
def _load_session(year: int, gp: str | int, session_type: str) -> fastf1.core.Session:
    """Get and load a single session with retry."""
    session = fastf1.get_session(year, gp, session_type)
    session.load()
    return session


# ── Public API ────────────────────────────────────────────────────────

def iter_sessions(
    start: int = 2018,
    end: int = 2026,
    types: Sequence[str] = ("R",),
    skip_existing: bool = True,
) -> Generator[fastf1.core.Session, None, None]:
    """Yield loaded Fast-F1 sessions across seasons.

    Args:
        start: First season (inclusive).
        end: Last season (inclusive).
        types: Session type codes, e.g. ('R', 'Q', 'FP2').
        skip_existing: If True, skip sessions whose laps data already
            exists in interim/. Uses a heuristic check.

    Yields:
        Loaded ``fastf1.core.Session`` objects.
    """
    _ensure_cache()
    cfg = load_config("data")

    seasons = [y for y in _get_seasons(cfg) if start <= y <= end]
    session_types = list(types)

    # Count total (season, round, type) triples for progress bar
    total = 0
    schedule_cache: dict[int, pd.DataFrame] = {}
    for season in seasons:
        schedule = _load_event_schedule(season)
        schedule_cache[season] = schedule
        total += len(schedule) * len(session_types)

    with tqdm(total=total, desc="Loading sessions", unit="session") as pbar:
        for season in seasons:
            schedule = schedule_cache[season]
            for _, event_row in schedule.iterrows():
                gp_name = event_row.get("EventName", "")
                gp_round = int(event_row.get("RoundNumber", 0))

                for stype in session_types:
                    try:
                        session = _load_session(season, gp_round, stype)

                        # Heuristic skip: if laps attribute exists and is non-empty,
                        # we consider it loaded (fastf1 handles its own caching)
                        if skip_existing and session.laps is not None and len(session.laps) > 0:
                            pbar.update(1)
                            pbar.set_postfix_str(f"{season} {gp_name} {stype}")
                            yield session
                        else:
                            pbar.update(1)
                            pbar.set_postfix_str(f"{season} {gp_name} {stype} (no laps — skipped)")

                    except Exception:
                        pbar.update(1)
                        pbar.set_postfix_str(f"{season} {gp_name} {stype} ⚠ failed")
                        # Continue to next session — one failure should not
                        # break the entire pipeline
                        continue
