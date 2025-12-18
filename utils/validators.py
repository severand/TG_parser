"""Input validation functions for Telegram Parser.

Provides validators for:
- Channel URLs and usernames
- Keywords and search terms
- Configuration structures
- Messages and metadata
- Email addresses
"""

import re
from typing import List

from utils.exceptions import ValidationException


class Validators:
    """Collection of validation functions.

    Static methods for validating various types of input data.

    Example:
        >>> if Validators.validate_channel_url(url):
        ...     print("Valid URL")
    """

    # Regex patterns
    TELEGRAM_URL_PATTERN = r'^(https?://)?(www\.)?t\.me/[a-zA-Z0-9_]{5,32}/?$'
    EMAIL_PATTERN = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    CHANNEL_USERNAME_PATTERN = r'^[a-zA-Z0-9_]{5,32}$'
    HASHTAG_PATTERN = r'^#[a-zA-Z0-9_]+$'

    @staticmethod
    def validate_channel_url(url: str) -> bool:
        """Validate Telegram channel URL format.

        Checks if URL is in valid Telegram channel format.
        Accepts formats:
        - t.me/channel_name
        - https://t.me/channel_name
        - https://www.t.me/channel_name

        Args:
            url: URL to validate

        Returns:
            True if valid, False otherwise

        Raises:
            ValidationException: If URL is None or not a string

        Example:
            >>> Validators.validate_channel_url("https://t.me/mychannel")
            True
            >>> Validators.validate_channel_url("invalid")
            False
        """
        if not isinstance(url, str):
            raise ValidationException(f"URL must be string, got {type(url).__name__}")

        if not url or len(url.strip()) == 0:
            raise ValidationException("URL cannot be empty")

        url = url.strip()
        return bool(re.match(Validators.TELEGRAM_URL_PATTERN, url, re.IGNORECASE))

    @staticmethod
    def validate_channel_username(username: str) -> bool:
        """Validate Telegram channel username format.

        Channel username must:
        - Be 5-32 characters long
        - Contain only alphanumeric characters and underscores
        - Start with letter or number (not underscore)

        Args:
            username: Username to validate

        Returns:
            True if valid, False otherwise

        Raises:
            ValidationException: If username is not a string

        Example:
            >>> Validators.validate_channel_username("my_channel")
            True
            >>> Validators.validate_channel_username("short")
            False
        """
        if not isinstance(username, str):
            raise ValidationException(f"Username must be string, got {type(username).__name__}")

        if not username or len(username.strip()) == 0:
            raise ValidationException("Username cannot be empty")

        username = username.strip().lstrip('@')
        return bool(re.match(Validators.CHANNEL_USERNAME_PATTERN, username))

    @staticmethod
    def validate_keywords(keywords: List[str]) -> bool:
        """Validate search keywords list.

        Each keyword must:
        - Be non-empty string
        - Not exceed 100 characters
        - Not be only whitespace

        Args:
            keywords: List of keywords to validate

        Returns:
            True if valid, False otherwise

        Raises:
            ValidationException: If not a list or contains invalid items

        Example:
            >>> Validators.validate_keywords(["python", "parser"])
            True
            >>> Validators.validate_keywords([])
            False
        """
        if not isinstance(keywords, list):
            raise ValidationException(f"Keywords must be list, got {type(keywords).__name__}")

        if len(keywords) == 0:
            raise ValidationException("Keywords list cannot be empty")

        for keyword in keywords:
            if not isinstance(keyword, str):
                raise ValidationException(
                    f"Each keyword must be string, got {type(keyword).__name__}"
                )

            keyword_stripped = keyword.strip()
            if not keyword_stripped:
                raise ValidationException("Keywords cannot be empty or whitespace")

            if len(keyword_stripped) > 100:
                raise ValidationException("Keyword exceeds 100 characters")

            if len(keyword_stripped) < 2:
                raise ValidationException("Keyword must be at least 2 characters")

        return True

    @staticmethod
    def validate_config(config: dict) -> bool:
        """Validate configuration dictionary structure.

        Checks for required sections and valid types.

        Args:
            config: Configuration dictionary

        Returns:
            True if valid, False otherwise

        Raises:
            ValidationException: If config is not dict or missing required sections

        Example:
            >>> config = {'parser': {}, 'network': {}, 'output': {}, 'logging': {}}
            >>> Validators.validate_config(config)
            True
        """
        if not isinstance(config, dict):
            raise ValidationException(f"Config must be dict, got {type(config).__name__}")

        required_sections = ['parser', 'network', 'output', 'logging']
        missing = [s for s in required_sections if s not in config]

        if missing:
            raise ValidationException(f"Config missing required sections: {missing}")

        # Validate parser section
        if not isinstance(config.get('parser'), dict):
            raise ValidationException("'parser' section must be dict")

        # Validate network section
        if not isinstance(config.get('network'), dict):
            raise ValidationException("'network' section must be dict")

        # Validate output section
        if not isinstance(config.get('output'), dict):
            raise ValidationException("'output' section must be dict")

        # Validate logging section
        if not isinstance(config.get('logging'), dict):
            raise ValidationException("'logging' section must be dict")

        return True

    @staticmethod
    def validate_message(message: dict) -> bool:
        """Validate message dictionary structure.

        Message must have required fields with correct types.

        Args:
            message: Message dictionary to validate

        Returns:
            True if valid, False otherwise

        Raises:
            ValidationException: If message structure is invalid

        Example:
            >>> msg = {
            ...     'id': '123',
            ...     'channel_id': 'ch123',
            ...     'text': 'Hello',
            ...     'timestamp': '2025-01-01T00:00:00Z'
            ... }
            >>> Validators.validate_message(msg)
            True
        """
        if not isinstance(message, dict):
            raise ValidationException(f"Message must be dict, got {type(message).__name__}")

        required_fields = {'id', 'channel_id', 'text', 'timestamp'}
        missing = required_fields - set(message.keys())

        if missing:
            raise ValidationException(f"Message missing required fields: {missing}")

        # Validate field types
        if not isinstance(message['id'], str):
            raise ValidationException("Message 'id' must be string")

        if not isinstance(message['channel_id'], str):
            raise ValidationException("Message 'channel_id' must be string")

        if not isinstance(message['text'], str):
            raise ValidationException("Message 'text' must be string")

        if not isinstance(message['timestamp'], str):
            raise ValidationException("Message 'timestamp' must be string")

        # Validate non-empty
        if not message['id'].strip():
            raise ValidationException("Message 'id' cannot be empty")

        if not message['text'].strip():
            raise ValidationException("Message 'text' cannot be empty")

        return True

    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email address format.

        Checks basic email format (not comprehensive, just basic validation).

        Args:
            email: Email address to validate

        Returns:
            True if valid, False otherwise

        Raises:
            ValidationException: If email is not a string

        Example:
            >>> Validators.validate_email("user@example.com")
            True
            >>> Validators.validate_email("invalid")
            False
        """
        if not isinstance(email, str):
            raise ValidationException(f"Email must be string, got {type(email).__name__}")

        if not email or len(email.strip()) == 0:
            raise ValidationException("Email cannot be empty")

        email = email.strip().lower()

        if len(email) > 254:
            raise ValidationException("Email exceeds 254 characters")

        return bool(re.match(Validators.EMAIL_PATTERN, email))

    @staticmethod
    def validate_hashtags(hashtags: List[str]) -> bool:
        """Validate hashtags list.

        Each hashtag must start with # and contain valid characters.

        Args:
            hashtags: List of hashtags to validate

        Returns:
            True if valid, False otherwise

        Raises:
            ValidationException: If hashtags list is invalid

        Example:
            >>> Validators.validate_hashtags(["#python", "#parser"])
            True
        """
        if not isinstance(hashtags, list):
            raise ValidationException(f"Hashtags must be list, got {type(hashtags).__name__}")

        if len(hashtags) == 0:
            return True  # Empty list is valid

        for hashtag in hashtags:
            if not isinstance(hashtag, str):
                raise ValidationException(
                    f"Each hashtag must be string, got {type(hashtag).__name__}"
                )

            hashtag_stripped = hashtag.strip()
            if not hashtag_stripped:
                raise ValidationException("Hashtag cannot be empty")

            if not hashtag_stripped.startswith('#'):
                hashtag_stripped = '#' + hashtag_stripped

            if not re.match(Validators.HASHTAG_PATTERN, hashtag_stripped):
                raise ValidationException(f"Invalid hashtag format: {hashtag}")

        return True
