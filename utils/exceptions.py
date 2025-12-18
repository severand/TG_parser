
"""Custom exception classes for Telegram Parser.

Defines a hierarchy of exceptions for different error types:
- ParserException (base)
  - ConfigException
  - NetworkException
  - ValidationException
  - StorageException
"""


class ParserException(Exception):
    """Base exception for all parser errors.

    All application-specific exceptions inherit from this class.

    Example:
        >>> try:
        ...     # parser code
        ... except ParserException as e:
        ...     logger.error(f"Parser error: {e}")
    """

    pass


class ConfigException(ParserException):
    """Exception raised for configuration errors.

    Raised when configuration is missing, invalid, or cannot be loaded.

    Example:
        >>> raise ConfigException("Config file not found at /path/to/config.json")
    """

    pass


class NetworkException(ParserException):
    """Exception raised for network-related errors.

    Raised for HTTP errors, timeouts, connection failures, etc.

    Example:
        >>> raise NetworkException("Connection timeout after 30 seconds")
    """

    pass


class ValidationException(ParserException):
    """Exception raised for validation errors.

    Raised when input data fails validation checks.

    Example:
        >>> raise ValidationException("Invalid channel URL format")
    """

    pass


class StorageException(ParserException):
    """Exception raised for storage/persistence errors.

    Raised when file I/O, caching, or database operations fail.

    Example:
        >>> raise StorageException("Failed to write to storage: disk full")
    """

    pass

class RateLimitException(NetworkException):
    """Exception raised when rate limited by server.

    Raised when receiving 429 status or similar rate limiting response.

    Example:
        >>> raise RateLimitException("Rate limited, retry after 60 seconds")
    """

    pass