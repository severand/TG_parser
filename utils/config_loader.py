"""Configuration loader module."""

import json
from pathlib import Path
from typing import Dict, Any


class ConfigLoader:
    """Load configuration from JSON files."""
    
    def __init__(self, config_dir: str = "config"):
        self.config_dir = Path(config_dir)
    
    def load(self, filename: str = "config.default.json") -> Dict[str, Any]:
        """Load configuration from file.
        
        Args:
            filename: Config filename
            
        Returns:
            Configuration dictionary
        """
        config_path = self.config_dir / filename
        
        if not config_path.exists():
            return self._get_default_config()
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration.
        
        Returns:
            Default config dictionary
        """
        return {
            "max_workers": 4,
            "timeout": 10,
            "max_retries": 3,
            "retry_delay": 1,
            "parser": {},
            "network": {},
            "output": {},
            "logging": {}
        }
