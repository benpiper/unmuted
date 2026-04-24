"""Unit tests for resilience patterns."""

import pytest
import time
from resilience import retry, CircuitBreaker, RateLimiter


class TestRetry:
    """Test retry decorator with exponential backoff."""

    def test_success_on_first_attempt(self):
        """Test successful function call on first attempt."""
        call_count = 0

        @retry(max_attempts=3, initial_delay=0.01)
        def success_func():
            nonlocal call_count
            call_count += 1
            return "success"

        result = success_func()
        assert result == "success"
        assert call_count == 1

    def test_retry_on_failure_then_success(self):
        """Test function that fails first, then succeeds."""
        call_count = 0

        @retry(max_attempts=3, initial_delay=0.01)
        def failing_then_success():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise ValueError("First attempt fails")
            return "success"

        result = failing_then_success()
        assert result == "success"
        assert call_count == 2

    def test_max_attempts_exceeded(self):
        """Test that exception is raised after max attempts."""
        call_count = 0

        @retry(max_attempts=2, initial_delay=0.01)
        def always_fails():
            nonlocal call_count
            call_count += 1
            raise ValueError("Always fails")

        with pytest.raises(ValueError):
            always_fails()

        assert call_count == 2

    def test_exponential_backoff(self):
        """Test that backoff delay increases exponentially."""
        @retry(max_attempts=3, initial_delay=0.01, backoff_multiplier=2.0)
        def test_func():
            raise ValueError("Test")

        start = time.time()
        with pytest.raises(ValueError):
            test_func()
        elapsed = time.time() - start

        # Should have delays of ~0.01 + ~0.02 = 0.03 seconds minimum
        assert elapsed >= 0.02


class TestCircuitBreaker:
    """Test circuit breaker pattern."""

    def test_circuit_closes_initially(self):
        """Test that circuit is initially closed."""
        cb = CircuitBreaker(failure_threshold=3)
        assert cb.state == CircuitBreaker.CLOSED

    def test_circuit_opens_after_threshold(self):
        """Test that circuit opens after failure threshold."""
        cb = CircuitBreaker(failure_threshold=2)

        def failing_func():
            raise ValueError("Test failure")

        # First failure
        with pytest.raises(ValueError):
            cb.call(failing_func)
        assert cb.state == CircuitBreaker.CLOSED

        # Second failure - should open
        with pytest.raises(ValueError):
            cb.call(failing_func)
        assert cb.state == CircuitBreaker.OPEN

    def test_circuit_blocks_when_open(self):
        """Test that circuit blocks calls when open."""
        cb = CircuitBreaker(failure_threshold=1, recovery_timeout=10)

        def failing_func():
            raise ValueError("Test")

        # Open the circuit
        with pytest.raises(ValueError):
            cb.call(failing_func)

        # Circuit should block further calls
        with pytest.raises(RuntimeError, match="Circuit breaker OPEN"):
            cb.call(failing_func)

    def test_circuit_half_open_after_timeout(self):
        """Test that circuit enters half-open after timeout."""
        cb = CircuitBreaker(failure_threshold=1, recovery_timeout=0.05)

        def failing_func():
            raise ValueError("Test")

        # Open the circuit
        with pytest.raises(ValueError):
            cb.call(failing_func)
        assert cb.state == CircuitBreaker.OPEN

        # Wait for recovery timeout
        time.sleep(0.1)

        # Circuit should be in half-open state
        def success_func():
            return "success"

        result = cb.call(success_func)
        assert result == "success"
        assert cb.state == CircuitBreaker.CLOSED


class TestRateLimiter:
    """Test rate limiting."""

    def test_allows_calls_under_limit(self):
        """Test that calls under limit are allowed."""
        limiter = RateLimiter(max_calls=3, time_window=1.0)

        assert limiter.allow_request() is True
        assert limiter.allow_request() is True
        assert limiter.allow_request() is True

    def test_blocks_calls_over_limit(self):
        """Test that calls over limit are blocked."""
        limiter = RateLimiter(max_calls=2, time_window=1.0)

        assert limiter.allow_request() is True
        assert limiter.allow_request() is True
        assert limiter.allow_request() is False

    def test_limit_resets_after_window(self):
        """Test that limit resets after time window."""
        limiter = RateLimiter(max_calls=1, time_window=0.05)

        assert limiter.allow_request() is True
        assert limiter.allow_request() is False

        # Wait for window to pass
        time.sleep(0.1)

        # Should allow again
        assert limiter.allow_request() is True
