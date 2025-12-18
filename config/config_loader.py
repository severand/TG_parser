"""Configuration loader module for Telegram Parser.

Handles loading, validating, and merging configuration from multiple sources
(JSON files, environment, defaults).
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class ConfigLoader:
    """Load and manage configuration for the parser.

    Provides methods to:
    - Load configuration from JSON files
    - Validate configuration structure
    - Apply defaults from default config
    - Access configuration values

    Example:
        >>> loader = ConfigLoader()
        >>> config = loader.load('config/config.json')
        >>> timeout = loader.get('parser.timeout')
        >>> max_threads = loader.get('parser.max_threads', 5)
    """

    def __init__(self) -> None:
        """Initialize ConfigLoader."""
        self._config: Dict[str, Any] = {}
        self._default_config: Dict[str, Any] = {}
        self._loaded_path: Optional[Path] = None

    def load(self, config_path: str, apply_defaults: bool = True) -> Dict[str, Any]:
        """Load configuration from JSON file.

        Loads configuration from specified JSON file. Optionally merges with
        default configuration to fill in missing keys.

        Args:
            config_path: Path to configuration JSON file
            apply_defaults: Whether to merge with default config (default: True)

        Returns:
            Loaded and merged configuration dictionary

        Raises:
            FileNotFoundError: If configuration file doesn't exist
            json.JSONDecodeError: If JSON is invalid
            ValueError: If configuration structure is invalid

        Example:
            >>> loader = ConfigLoader()
            >>> config = loader.load('config/config.json')
            >>> config['parser']['timeout']
            30
        """
        config_path = Path(config_path)

        # Check if file exists
        if not config_path.exists():
            raise FileNotFoundError(
                f"Configuration file not found: {config_path.absolute()}"
            )

        try:
            # Load from file
            with open(config_path, 'r', encoding='utf-8') as f:
                self._config = json.load(f)
            logger.info(f"Loaded configuration from {config_path}")
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in configuration file: {e}")
            raise json.JSONDecodeError(
                f"Invalid JSON in {config_path}: {str(e)}",
                e.doc,
                e.pos
            ) from e
        except Exception as e:
            logger.error(f"Failed to read configuration file: {e}")
            raise

        # Store path for reference
        self._loaded_path = config_path.absolute()

        # Validate structure
        self.validate(self._config)

        # Apply defaults if requested
        if apply_defaults:
            self._apply_defaults()

        logger.debug(f"Configuration loaded successfully from {config_path}")
        return self._config

    def load_defaults(self, defaults_path: str = "config/config.default.json") -> Dict[str, Any]:
        """Load default configuration.

        Loads default configuration from JSON file. Used as fallback for missing
        configuration keys.

        Args:
            defaults_path: Path to default configuration file (default: config/config.default.json)

        Returns:
            Default configuration dictionary

        Raises:
            FileNotFoundError: If default config file doesn't exist
            json.JSONDecodeError: If JSON is invalid

        Example:
            >>> loader = ConfigLoader()
            >>> defaults = loader.load_defaults()
        """
        defaults_path = Path(defaults_path)

        if not defaults_path.exists():
            logger.warning(f"Default config file not found: {defaults_path}")
            return {}

        try:
            with open(defaults_path, 'r', encoding='utf-8') as f:
                self._default_config = json.load(f)
            logger.info(f"Loaded default configuration from {defaults_path}")
            return self._default_config
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in default config file: {e}")
            raise
        except Exception as e:
            logger.error(f"Failed to load default configuration: {e}")
            raise

    def validate(self, config: Dict[str, Any]) -> bool:
        """Validate configuration structure.

        Checks that configuration has required structure and correct types.

        Args:
            config: Configuration dictionary to validate

        Returns:
            True if valid

        Raises:
            ValueError: If configuration is invalid

        Example:
            >>> loader = ConfigLoader()
            >>> config = {'parser': {'timeout': 30}}
            >>> loader.validate(config)
            True
        """
        if not isinstance(config, dict):
            raise ValueError("Configuration must be a dictionary")

        # Check for required top-level keys
        required_keys = ['parser', 'network', 'output', 'logging']
        for key in required_keys:
            if key not in config:
                logger.warning(f"Missing configuration section: {key}")

        # Validate parser section
        if 'parser' in config:
            parser_config = config['parser']
            if not isinstance(parser_config, dict):
                raise ValueError("'parser' section must be a dictionary")

            # Validate parser types
            parser_validations = {
                'max_threads': int,
                'timeout': int,
                'max_retries': int,
                'delay_min': (int, float),
                'delay_max': (int, float),
                'max_messages_per_channel': int,
            }

            for key, expected_type in parser_validations.items():
                if key in parser_config:
                    value = parser_config[key]
                    if not isinstance(value, expected_type):
                        raise ValueError(
                            f"'parser.{key}' must be type {expected_type}, "
                            f"got {type(value).__name__}"
                        )

        # Validate network section
        if 'network' in config:
            network_config = config['network']
            if not isinstance(network_config, dict):
                raise ValueError("'network' section must be a dictionary")

            network_validations = {
                'use_proxy': bool,
                'verify_ssl': bool,
                'follow_redirects': bool,
            }

            for key, expected_type in network_validations.items():
                if key in network_config:
                    value = network_config[key]
                    if not isinstance(value, expected_type):
                        raise ValueError(
                            f"'network.{key}' must be type {expected_type}, "
                            f"got {type(value).__name__}"
                        )

        # Validate logging section
        if 'logging' in config:
            logging_config = config['logging']
            if not isinstance(logging_config, dict):
                raise ValueError("'logging' section must be a dictionary")

            if 'level' in logging_config:
                valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
                if logging_config['level'] not in valid_levels:
                    raise ValueError(
                        f"'logging.level' must be one of {valid_levels}, "
                        f"got {logging_config['level']}"
                    )

        logger.debug("Configuration validation passed")
        return True

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by dot-notation key.

        Supports nested access using dot notation (e.g., 'parser.timeout').

        Args:
            key: Configuration key in dot notation (e.g., 'parser.timeout')
            default: Default value if key not found (default: None)

        Returns:
            Configuration value or default if not found

        Example:
            >>> loader = ConfigLoader()
            >>> loader.load('config/config.json')
            >>> timeout = loader.get('parser.timeout')
            >>> max_threads = loader.get('parser.max_threads', 5)
        """
        keys = key.split('.')
        current = self._config

        try:
            for k in keys:
                current = current[k]
            return current
        except (KeyError, TypeError):
            return default

    def get_all(self) -> Dict[str, Any]:
        """Get entire configuration dictionary.

        Returns:
            Complete configuration dictionary

        Example:
            >>> loader = ConfigLoader()
            >>> loader.load('config/config.json')
            >>> all_config = loader.get_all()
        """
        return self._config.copy()

    def _apply_defaults(self) -> None:
        """Apply default configuration values for missing keys.

        Recursively merges default configuration with loaded configuration,
        filling in any missing keys.

        Loaded configuration takes precedence over defaults.
        """
        if not self._default_config:
            return

        def merge_dicts(user_config: Dict[str, Any], defaults: Dict[str, Any]) -> Dict[str, Any]:
            """Recursively merge user config with defaults."""
            result = defaults.copy()
            for key, value in user_config.items():
                if isinstance(value, dict) and key in defaults and isinstance(defaults[key], dict):
                    result[key] = merge_dicts(value, defaults[key])
                else:
                    result[key] = value
            return result

        self._config = merge_dicts(self._config, self._default_config)
        logger.debug("Applied default configuration values")

    def __repr__(self) -> str:
        """String representation."""
        path = self._loaded_path or "not loaded"
        return f"ConfigLoader(loaded_from={path})"
