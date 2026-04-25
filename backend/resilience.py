"""
Resilience patterns for handling failures gracefully.
Includes retries, circuit breakers, and timeout handling.
"""

import time
import functools
import threading
from typing import Callable, TypeVar
from logging_config import get_logger

logger = get_logger(__name__)

T = TypeVar('T')


def retry(max_attempts: int = 5, initial_delay: float = 1.0, max_delay: float = 60.0, backoff_multiplier: float = 2.0):
    """
    Decorator for exponential backoff retry logic, with special handling for rate limits.

    Args:
        max_attempts: Maximum number of attempts (default 5)
        initial_delay: Initial delay in seconds (default 1.0)
        max_delay: Maximum delay between retries (default 60.0)
        backoff_multiplier: Multiply delay by this factor each retry (default 2.0)

    Handles OpenAI 429 (rate limit) responses by respecting Retry-After headers.

    Example:
        @retry(max_attempts=5, initial_delay=2.0)
        def call_external_api():
            return requests.get('https://api.example.com')
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> T:
            from httpx import HTTPStatusError
            last_exception = None
            delay = initial_delay

            for attempt in range(1, max_attempts + 1):
                try:
                    logger.debug(f"Attempt {attempt}/{max_attempts} for {func.__name__}")
                    return func(*args, **kwargs)
                except HTTPStatusError as e:
                    last_exception = e
                    if attempt < max_attempts and e.response.status_code == 429:
                        # Check for Retry-After header from OpenAI
                        retry_after = e.response.headers.get("retry-after")
                        if retry_after:
                            try:
                                wait_time = float(retry_after)
                            except ValueError:
                                wait_time = min(delay, max_delay)
                        else:
                            wait_time = min(delay, max_delay)
                        logger.warning(
                            f"Rate limited (429) on attempt {attempt}, retrying in {wait_time:.1f}s",
                            extra={"function": func.__name__, "attempt": attempt, "wait_time": wait_time}
                        )
                        time.sleep(wait_time)
                        delay *= backoff_multiplier
                    elif attempt < max_attempts:
                        wait_time = min(delay, max_delay)
                        logger.warning(
                            f"Attempt {attempt} failed for {func.__name__}, retrying in {wait_time:.1f}s",
                            extra={"function": func.__name__, "attempt": attempt, "error": str(e)}
                        )
                        time.sleep(wait_time)
                        delay *= backoff_multiplier
                    else:
                        logger.error(
                            f"All {max_attempts} attempts failed for {func.__name__}",
                            extra={"function": func.__name__, "error": str(e)},
                            exc_info=True
                        )
                except Exception as e:
                    last_exception = e
                    if attempt < max_attempts:
                        wait_time = min(delay, max_delay)
                        logger.warning(
                            f"Attempt {attempt} failed for {func.__name__}, retrying in {wait_time:.1f}s",
                            extra={"function": func.__name__, "attempt": attempt, "error": str(e)}
                        )
                        time.sleep(wait_time)
                        delay *= backoff_multiplier
                    else:
                        logger.error(
                            f"All {max_attempts} attempts failed for {func.__name__}",
                            extra={"function": func.__name__, "error": str(e)},
                            exc_info=True
                        )

            raise last_exception

        return wrapper
    return decorator


class CircuitBreaker:
    """
    Circuit breaker pattern to prevent cascading failures.

    States: CLOSED (normal) → OPEN (failing) → HALF_OPEN (testing) → CLOSED

    Args:
        failure_threshold: Number of failures before opening circuit (default 5)
        recovery_timeout: Seconds to wait before trying HALF_OPEN (default 60)
        expected_exception: Exception types to count as failures (default Exception)
    """

    CLOSED = "CLOSED"
    OPEN = "OPEN"
    HALF_OPEN = "HALF_OPEN"

    def __init__(self, failure_threshold: int = 5, recovery_timeout: float = 60.0, expected_exception: type = Exception):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        self.failure_count = 0
        self.last_failure_time = None
        self.state = self.CLOSED
        logger.info(f"CircuitBreaker initialized with threshold={failure_threshold}, timeout={recovery_timeout}s")

    def call(self, func: Callable[..., T], *args, **kwargs) -> T:
        """Execute function through circuit breaker."""
        if self.state == self.OPEN:
            if time.time() - self.last_failure_time > self.recovery_timeout:
                self.state = self.HALF_OPEN
                logger.info(f"CircuitBreaker entering HALF_OPEN state for {func.__name__}")
            else:
                raise RuntimeError(f"Circuit breaker OPEN for {func.__name__}")

        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except self.expected_exception:
            self._on_failure(func.__name__)
            raise

    def _on_success(self):
        """Called on successful execution."""
        if self.state == self.HALF_OPEN:
            self.state = self.CLOSED
            self.failure_count = 0
            logger.info("CircuitBreaker reset to CLOSED")
        elif self.state == self.CLOSED:
            self.failure_count = max(0, self.failure_count - 1)

    def _on_failure(self, func_name: str):
        """Called on failure."""
        self.failure_count += 1
        self.last_failure_time = time.time()

        if self.failure_count >= self.failure_threshold:
            self.state = self.OPEN
            logger.error(
                f"CircuitBreaker OPEN for {func_name} after {self.failure_count} failures",
                extra={"function": func_name, "failure_count": self.failure_count}
            )
        else:
            logger.warning(
                f"Failure #{self.failure_count}/{self.failure_threshold} for {func_name}",
                extra={"function": func_name, "failure_count": self.failure_count}
            )


class RateLimiter:
    """
    Simple rate limiter to prevent overwhelming services.

    Args:
        max_calls: Maximum number of calls allowed
        time_window: Time window in seconds
    """

    def __init__(self, max_calls: int, time_window: float):
        self.max_calls = max_calls
        self.time_window = time_window
        self.calls = []
        self._lock = threading.Lock()

    def allow_request(self) -> bool:
        """Check if request is allowed under rate limit."""
        with self._lock:
            now = time.time()
            # Remove old calls outside the time window
            self.calls = [call_time for call_time in self.calls if now - call_time < self.time_window]

            if len(self.calls) < self.max_calls:
                self.calls.append(now)
                return True
            return False

    def wait_if_needed(self):
        """Wait if needed to respect rate limit."""
        if not self.allow_request():
            with self._lock:
                oldest_call = self.calls[0] if self.calls else time.time()
                wait_time = self.time_window - (time.time() - oldest_call)
                if wait_time > 0:
                    logger.debug(f"Rate limit reached, waiting {wait_time:.2f}s")
                    # Release lock while sleeping to avoid blocking other threads
            time.sleep(max(0, wait_time))
            self.allow_request()


class PerIPRateLimiter:
    """
    Per-client-IP rate limiter for HTTP middleware.
    Thread-safe wrapper maintaining separate RateLimiter per IP.
    """

    def __init__(self, max_calls: int, time_window: float):
        self.max_calls = max_calls
        self.time_window = time_window
        self._limiters: dict[str, RateLimiter] = {}
        self._lock = threading.Lock()

    def allow_request(self, ip: str) -> bool:
        """Check if request from IP is allowed under rate limit."""
        with self._lock:
            if ip not in self._limiters:
                self._limiters[ip] = RateLimiter(self.max_calls, self.time_window)
            limiter = self._limiters[ip]

        return limiter.allow_request()
