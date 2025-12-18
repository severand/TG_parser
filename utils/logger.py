"""Centralized logging module for Telegram Parser."""

import logging
import logging.handlers
from pathlib import Path
from typing import Optional


class Logger:
    """Centralized logger for the application (Singleton)."""

    _instance: Optional['Logger'] = None
    _logger: Optional[logging.Logger] = None
    _initialized: bool = False

    def __new__(cls) -> 'Logger':
        """Implement singleton pattern."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    def get_instance(cls) -> 'Logger':
        """Get singleton instance.
        
        Returns:
            Singleton Logger instance
        """
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(
        self,
        name: str = "telegram_parser",
        level: int = logging.INFO,
        log_file: Optional[str] = None,
        console_output: bool = True,
    ) -> None:
        """Initialize Logger."""
        if self._initialized:
            return

        self._name = name
        self._level = level
        self._log_file = log_file or "logs/parser.log"
        self._console_output = console_output

        self._setup_logger()
        self.__class__._initialized = True

    def _setup_logger(self) -> None:
        """Set up logger with handlers and formatters."""
        self._logger = logging.getLogger(self._name)
        self._logger.setLevel(self._level)
        self._logger.propagate = False
        self._logger.handlers = []

        formatter = logging.Formatter(
            fmt='[%(asctime)s] [%(levelname)-8s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S',
        )

        if self._console_output:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(self._level)
            console_handler.setFormatter(formatter)
            self._logger.addHandler(console_handler)

        try:
            log_path = Path(self._log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)

            file_handler = logging.handlers.RotatingFileHandler(
                filename=log_path,
                maxBytes=10 * 1024 * 1024,
                backupCount=5,
                encoding='utf-8',
            )
            file_handler.setLevel(self._level)
            file_handler.setFormatter(formatter)
            self._logger.addHandler(file_handler)
        except Exception:
            pass

    def debug(self, message: str, *args, **kwargs) -> None:
        """Log debug message."""
        if self._logger:
            self._logger.debug(message, *args, **kwargs)

    def info(self, message: str, *args, **kwargs) -> None:
        """Log info message."""
        if self._logger:
            self._logger.info(message, *args, **kwargs)

    def warning(self, message: str, *args, **kwargs) -> None:
        """Log warning message."""
        if self._logger:
            self._logger.warning(message, *args, **kwargs)

    def error(self, message: str, *args, **kwargs) -> None:
        """Log error message."""
        if self._logger:
            self._logger.error(message, *args, **kwargs)

    def critical(self, message: str, *args, **kwargs) -> None:
        """Log critical message."""
        if self._logger:
            self._logger.critical(message, *args, **kwargs)

    def set_level(self, level: int) -> None:
        """Change logging level."""
        if self._logger:
            self._logger.setLevel(level)
            for handler in self._logger.handlers:
                handler.setLevel(level)
