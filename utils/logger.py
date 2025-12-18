"""Centralized logging module for Telegram Parser.

Provides a singleton Logger instance used throughout the application for
structured logging with both console and file output.
"""

import logging
import logging.handlers
from pathlib import Path
from typing import Optional


class Logger:
    """Centralized logger for the application.

    Provides singleton-pattern logger with:
    - Console output (with colors via coloredlogs if available)
    - File output with rotation
    - Configurable log levels
    - Consistent formatting

    Example:
        >>> logger = Logger()
        >>> logger.info("Starting parser")
        >>> logger.error("Failed to parse channel", extra={"channel_id": "123"})
    """

    _instance: Optional['Logger'] = None
    _logger: Optional[logging.Logger] = None

    def __new__(cls) -> 'Logger':
        """Implement singleton pattern.

        Returns:
            Singleton Logger instance
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(
        self,
        name: str = "telegram_parser",
        level: int = logging.INFO,
        log_file: Optional[str] = None,
        console_output: bool = True,
    ) -> None:
        """Initialize Logger.

        Args:
            name: Logger name (default: "telegram_parser")
            level: Logging level (default: INFO)
            log_file: Path to log file (default: logs/parser.log)
            console_output: Whether to output to console (default: True)
        """
        if self._initialized:
            return

        self._name = name
        self._level = level
        self._log_file = log_file or "logs/parser.log"
        self._console_output = console_output

        self._setup_logger()
        self._initialized = True

    def _setup_logger(self) -> None:
        """Set up logger with handlers and formatters."""
        # Get or create logger
        self._logger = logging.getLogger(self._name)
        self._logger.setLevel(self._level)
        self._logger.propagate = False

        # Remove existing handlers to avoid duplicates
        self._logger.handlers = []

        # Create formatter
        formatter = logging.Formatter(
            fmt='[%(asctime)s] [%(levelname)-8s] [%(name)s:%(funcName)s:%(lineno)d] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S',
        )

        # Add console handler
        if self._console_output:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(self._level)
            console_handler.setFormatter(formatter)
            self._logger.addHandler(console_handler)

        # Add file handler
        try:
            log_path = Path(self._log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)

            file_handler = logging.handlers.RotatingFileHandler(
                filename=log_path,
                maxBytes=10 * 1024 * 1024,  # 10 MB
                backupCount=5,
                encoding='utf-8',
            )
            file_handler.setLevel(self._level)
            file_handler.setFormatter(formatter)
            self._logger.addHandler(file_handler)
        except Exception as e:
            self.warning(f"Failed to set up file logging: {e}")

    def debug(self, message: str, *args, **kwargs) -> None:
        """Log debug message.

        Args:
            message: Log message
            *args: Format arguments
            **kwargs: Additional keyword arguments
        """
        self._logger.debug(message, *args, **kwargs)

    def info(self, message: str, *args, **kwargs) -> None:
        """Log info message.

        Args:
            message: Log message
            *args: Format arguments
            **kwargs: Additional keyword arguments

        Example:
            >>> logger.info("Starting parser", extra={"channels": 5})
        """
        self._logger.info(message, *args, **kwargs)

    def warning(self, message: str, *args, **kwargs) -> None:
        """Log warning message.

        Args:
            message: Log message
            *args: Format arguments
            **kwargs: Additional keyword arguments
        """
        self._logger.warning(message, *args, **kwargs)

    def error(self, message: str, *args, **kwargs) -> None:
        """Log error message.

        Args:
            message: Log message
            *args: Format arguments
            **kwargs: Additional keyword arguments

        Example:
            >>> logger.error("Failed to parse channel", extra={"error": str(e)})
        """
        self._logger.error(message, *args, **kwargs)

    def critical(self, message: str, *args, **kwargs) -> None:
        """Log critical message.

        Args:
            message: Log message
            *args: Format arguments
            **kwargs: Additional keyword arguments
        """
        self._logger.critical(message, *args, **kwargs)

    def set_level(self, level: int) -> None:
        """Change logging level.

        Args:
            level: New logging level (e.g., logging.DEBUG, logging.INFO)

        Example:
            >>> logger = Logger()
            >>> logger.set_level(logging.DEBUG)
        """
        self._logger.setLevel(level)
        for handler in self._logger.handlers:
            handler.setLevel(level)

    def __repr__(self) -> str:
        """String representation."""
        return f"Logger(name={self._name}, level={logging.getLevelName(self._level)})"
