"""
Stain Time Configuration Module

YAML-based configuration management with dot-notation access.

@author: Sayumi Devasurendra
@version: 0.1.0
"""

import yaml
from pathlib import Path
from typing import Any, Dict


class StainTimeConfig:
    """Load and manage project configuration"""

    def __init__(self, config_path: str = "config/config.yaml"):
        """
        Initialize configuration loader

        Args:
            config_path: Path to YAML configuration file
        """
        self.config_path = Path(config_path)
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file"""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")

        with open(self.config_path, 'r') as f:
            config = yaml.safe_load(f)

        return config

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value using dot notation

        Args:
            key: Configuration key (e.g., 'data.image_size')
            default: Default value if key not found

        Returns:
            Configuration value
        """
        keys = key.split('.')
        value = self.config

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default

        return value

    def __getitem__(self, key: str) -> Any:
        """Allow dictionary-style access"""
        return self.get(key)

    def __repr__(self) -> str:
        return f"ConfigLoader(config_path='{self.config_path}')"
