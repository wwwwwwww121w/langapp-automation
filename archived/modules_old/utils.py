"""
Utility functions for error handling, retry logic, and common operations
"""

import time
import logging
import functools
from typing import Callable, Any, Optional, List
from pathlib import Path

logger = logging.getLogger(__name__)


def retry(max_attempts: int = 3, delay: float = 1.0, backoff: float = 2.0,
          exceptions: tuple = (Exception,), on_retry: Callable = None):
    """
    Decorator for retrying function calls with exponential backoff

    Args:
        max_attempts: Maximum number of attempts
        delay: Initial delay in seconds between retries
        backoff: Multiplier for delay after each retry
        exceptions: Tuple of exceptions to catch
        on_retry: Callback function called on retry with (attempt, exception, delay)
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            last_exception = None
            current_delay = delay

            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_attempts:
                        if on_retry:
                            on_retry(attempt, e, current_delay)
                        logger.warning(
                            f"Attempt {attempt}/{max_attempts} failed for {func.__name__}: {e}. "
                            f"Retrying in {current_delay:.1f}s..."
                        )
                        time.sleep(current_delay)
                        current_delay *= backoff
                    else:
                        logger.error(f"All {max_attempts} attempts failed for {func.__name__}: {e}")

            if last_exception:
                raise last_exception
            return None

        return wrapper
    return decorator


def exponential_backoff_sleep(attempt: int, base_delay: float = 1.0, max_delay: float = 300.0):
    """Calculate and sleep with exponential backoff"""
    delay = min(base_delay * (2 ** attempt), max_delay)
    logger.info(f"Waiting {delay:.1f}s before retry...")
    time.sleep(delay)


def batch_process(items: List[Any], batch_size: int = 10,
                  process_fn: Callable = None, on_error: Callable = None) -> dict:
    """
    Process items in batches with error handling

    Args:
        items: List of items to process
        batch_size: Size of each batch
        process_fn: Function to process each item
        on_error: Error handler function

    Returns:
        dict with 'successful', 'failed', 'results'
    """
    results = {
        'successful': [],
        'failed': [],
        'results': []
    }

    if not process_fn:
        return results

    for i, item in enumerate(items):
        try:
            result = process_fn(item)
            results['successful'].append(item)
            results['results'].append(result)

            if (i + 1) % batch_size == 0:
                logger.info(f"Processed {i + 1}/{len(items)} items")

        except Exception as e:
            logger.error(f"Error processing item {i}: {e}")
            results['failed'].append({'item': item, 'error': str(e)})
            if on_error:
                on_error(item, e)

    logger.info(f"Batch processing complete: {len(results['successful'])} successful, {len(results['failed'])} failed")
    return results


def ensure_dir(path: str) -> str:
    """Ensure directory exists and return path"""
    Path(path).mkdir(parents=True, exist_ok=True)
    return path


def file_size_mb(filepath: str) -> float:
    """Get file size in MB"""
    try:
        return Path(filepath).stat().st_size / (1024 * 1024)
    except:
        return 0.0


def safe_json_load(filepath: str, default: Any = None) -> Any:
    """Safely load JSON file with fallback"""
    import json
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.warning(f"Could not load JSON from {filepath}: {e}")
        return default


def safe_json_dump(data: Any, filepath: str, indent: int = 2) -> bool:
    """Safely dump JSON to file"""
    import json
    try:
        ensure_dir(str(Path(filepath).parent))
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=indent)
        return True
    except Exception as e:
        logger.error(f"Could not save JSON to {filepath}: {e}")
        return False


def validate_config(config_dict: dict, required_keys: List[str]) -> tuple:
    """
    Validate configuration dictionary

    Returns:
        (is_valid, missing_keys)
    """
    missing = [k for k in required_keys if k not in config_dict or not config_dict[k]]
    return len(missing) == 0, missing


class ProgressTracker:
    """Track progress of long-running tasks"""

    def __init__(self, total: int, name: str = "Task"):
        self.total = total
        self.current = 0
        self.name = name
        self.start_time = time.time()

    def update(self, increment: int = 1, message: str = None):
        """Update progress"""
        self.current += increment
        percent = (self.current / self.total) * 100 if self.total > 0 else 0
        elapsed = time.time() - self.start_time

        msg = f"[{self.name}] {self.current}/{self.total} ({percent:.1f}%)"
        if elapsed > 0:
            rate = self.current / elapsed
            remaining = (self.total - self.current) / rate if rate > 0 else 0
            msg += f" - ETA: {remaining:.0f}s"

        if message:
            msg += f" - {message}"

        logger.info(msg)

    def done(self):
        """Mark as complete"""
        elapsed = time.time() - self.start_time
        logger.info(f"[{self.name}] Completed in {elapsed:.1f}s")


class CircuitBreaker:
    """Simple circuit breaker for failing operations"""

    def __init__(self, failure_threshold: int = 5, reset_timeout: float = 60.0):
        self.failure_threshold = failure_threshold
        self.reset_timeout = reset_timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.is_open = False

    def call(self, func: Callable, *args, **kwargs) -> tuple:
        """
        Execute function with circuit breaker

        Returns:
            (success: bool, result: Any)
        """
        if self.is_open:
            if (time.time() - self.last_failure_time) > self.reset_timeout:
                logger.info("Circuit breaker: Attempting reset")
                self.is_open = False
                self.failure_count = 0
            else:
                logger.warning("Circuit breaker: OPEN - operation blocked")
                return False, None

        try:
            result = func(*args, **kwargs)
            self.failure_count = 0
            return True, result
        except Exception as e:
            self.failure_count += 1
            self.last_failure_time = time.time()

            if self.failure_count >= self.failure_threshold:
                self.is_open = True
                logger.error(f"Circuit breaker: OPEN after {self.failure_count} failures")

            return False, str(e)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    @retry(max_attempts=3, delay=0.5)
    def test_function():
        import random
        if random.random() < 0.7:
            raise ValueError("Random failure")
        return "Success!"

    try:
        result = test_function()
        print(f"Result: {result}")
    except Exception as e:
        print(f"Failed: {e}")
