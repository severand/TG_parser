"""Delay generator for anti-detection purposes.

Generates random delays between requests to avoid detection.
"""

import time
import random
from typing import Union

from utils.logger import Logger

logger = Logger()


class DelayGenerator:
    """Generate random delays between requests.

    Provides methods to generate random delays and apply them
    to avoid bot detection.

    Example:
        >>> gen = DelayGenerator()
        >>> delay = gen.get_delay(1, 5)
        >>> delay
        3.427  # random float between 1 and 5
    """

    @staticmethod
    def get_delay(min_seconds: Union[int, float] = 1, max_seconds: Union[int, float] = 5) -> float:
        """Generate random delay in seconds.

        Args:
            min_seconds: Minimum delay in seconds (default: 1)
            max_seconds: Maximum delay in seconds (default: 5)

        Returns:
            Random delay as float between min and max

        Raises:
            ValueError: If min >= max or values are negative

        Example:
            >>> gen = DelayGenerator()
            >>> delay = gen.get_delay(1, 3)
            >>> 1 <= delay <= 3
            True
        """
        if min_seconds < 0 or max_seconds < 0:
            raise ValueError("Delay values must be non-negative")

        if min_seconds >= max_seconds:
            raise ValueError(f"min_seconds ({min_seconds}) must be < max_seconds ({max_seconds})")

        delay = random.uniform(min_seconds, max_seconds)
        logger.debug(f"Generated delay: {delay:.2f}s")
        return delay

    @staticmethod
    def apply_delay(
        min_seconds: Union[int, float] = 1,
        max_seconds: Union[int, float] = 5,
    ) -> None:
        """Generate and apply random delay.

        Args:
            min_seconds: Minimum delay in seconds (default: 1)
            max_seconds: Maximum delay in seconds (default: 5)

        Example:
            >>> DelayGenerator.apply_delay(1, 3)  # Sleeps 1-3 seconds
        """
        delay = DelayGenerator.get_delay(min_seconds, max_seconds)
        logger.debug(f"Applying delay: {delay:.2f}s")
        time.sleep(delay)
