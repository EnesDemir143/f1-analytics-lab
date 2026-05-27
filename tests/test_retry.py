"""Tests for retry helper."""

import time
from unittest.mock import patch

import pytest

from src.utils.retry import retry


def test_retry_success_first_try() -> None:
    """Function succeeds on first attempt — no retries needed."""
    call_count = 0

    @retry(max_attempts=3)
    def work() -> str:
        nonlocal call_count
        call_count += 1
        return "ok"

    assert work() == "ok"
    assert call_count == 1


def test_retry_succeeds_on_retry() -> None:
    """Function fails twice then succeeds."""
    call_count = 0

    @retry(max_attempts=3, base_delay=0.01)
    def work() -> str:
        nonlocal call_count
        call_count += 1
        if call_count < 3:
            raise ValueError("not yet")
        return "ok"

    assert work() == "ok"
    assert call_count == 3


def test_retry_exhausted() -> None:
    """All attempts exhausted — raises the last exception."""
    call_count = 0

    @retry(max_attempts=3, base_delay=0.01)
    def work() -> str:
        nonlocal call_count
        call_count += 1
        raise ValueError("always fails")

    with pytest.raises(ValueError, match="always fails"):
        work()
    assert call_count == 3


def test_retry_exponential_backoff() -> None:
    """Delays grow exponentially between attempts."""
    delays: list[float] = []

    original_sleep = time.sleep

    def tracking_sleep(delay: float) -> None:
        delays.append(delay)
        original_sleep(0)  # don't actually wait in tests

    @retry(max_attempts=4, base_delay=2.0, max_delay=30.0)
    def work() -> str:
        raise ValueError("fail")

    with patch("time.sleep", side_effect=tracking_sleep):
        with pytest.raises(ValueError):
            work()

    # With max_attempts=4, we expect 3 sleeps: 2, 4, 8
    assert len(delays) == 3
    assert delays[0] == pytest.approx(2.0, rel=0.5)
    assert delays[1] == pytest.approx(4.0, rel=0.5)
    assert delays[2] == pytest.approx(8.0, rel=0.5)


def test_retry_specific_exception() -> None:
    """Only catches specified exception types."""

    @retry(max_attempts=2, base_delay=0.01, exceptions=(ValueError,))
    def work() -> str:
        raise TypeError("not caught")

    with pytest.raises(TypeError):
        work()
