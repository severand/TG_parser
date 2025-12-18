"""Input validation functions for Telegram Parser."""

import re
from typing import List
from utils.exceptions import ValidationException


class Validators:
    """Collection of validation functions."""

    TELEGRAM_URL_PATTERN = r'^(https?://)?(www\.)?t\.me/[a-zA-Z0-9_]{5,32}/?$'
    CHANNEL_USERNAME_PATTERN = r'^[a-zA-Z0-9_]{5,32}$'

    @staticmethod
    def validate_channel_url(url: str) -> bool:
        """Validate Telegram channel URL format."""
        if not isinstance(url, str):
            return False
        if not url or len(url.strip()) == 0:
            return False
        url = url.strip()
        # Also accept @channel format
        if url.startswith('@'):
            return len(url) > 5
        return bool(re.match(Validators.TELEGRAM_URL_PATTERN, url, re.IGNORECASE))

    @staticmethod
    def validate_keywords(keywords: List[str]) -> bool:
        """Validate search keywords list."""
        if not isinstance(keywords, list):
            return False
        if len(keywords) == 0:
            return False
        for keyword in keywords:
            if not isinstance(keyword, str):
                return False
            if not keyword.strip():
                return False
        return True

    @staticmethod
    def validate_config(config: dict) -> bool:
        """Validate configuration dictionary structure."""
        if not isinstance(config, dict):
            return False
        return True


# Function aliases for backward compatibility
def validate_channel_url(url: str) -> bool:
    """Validate channel URL."""
    return Validators.validate_channel_url(url)


def validate_keywords(keywords: List[str]) -> bool:
    """Validate keywords list."""
    return Validators.validate_keywords(keywords)


def validate_config(config: dict) -> bool:
    """Validate config dictionary."""
    return Validators.validate_config(config)
