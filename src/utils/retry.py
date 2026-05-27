"""Simple retry decorator with exponential backoff — no external deps."""

import time
from collections.abc import Callable
from functools import wraps
from typing import TypeVar

F = TypeVar("F", bound=Callable[..., object])


def retry(
    max_attempts: int = 3,
    base_delay: float = 2.0,
    max_delay: float = 30.0,
    exceptions: tuple[type[Exception], ...] = (Exception,),
) -> Callable[[F], F]:
    """Retry a function with exponential backoff on failure.

    Args:
        max_attempts: Maximum number of attempts.
        base_delay: Initial delay in seconds.
        max_delay: Maximum delay in seconds (cap).
        exceptions: Tuple of exception types to catch.

    Returns:
        Decorated function.

    Raises:
        The last exception after all attempts are exhausted.
    """
    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exc = None
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exc = e
                    if attempt < max_attempts:
                        delay = min(base_delay * (2 ** (attempt - 1)), max_delay)
                        print(
                            f"  ⚠ {func.__name__} failed (attempt {attempt}/{max_attempts}), "
                            f"retrying in {delay:.0f}s: {e}"
                        )
                        time.sleep(delay)
            raise last_exc  # type: ignore
        return wrapper  # type: ignore
    return decorator
