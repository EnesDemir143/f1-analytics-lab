"""YAML configuration reader with path resolution."""

from pathlib import Path
from typing import Any

import yaml

from .paths import CONFIGS_DIR


def load_config(name: str) -> dict[str, Any]:
    """Load a YAML config file from configs/ directory.

    Args:
        name: Config file name (with or without .yaml extension).

    Returns:
        Parsed YAML as dictionary.
    """
    if not name.endswith((".yaml", ".yml")):
        name = f"{name}.yaml"

    path = CONFIGS_DIR / name
    if not path.exists():
        raise FileNotFoundError(f"Config not found: {path}")

    with open(path) as f:
        return yaml.safe_load(f)


def load_all_configs() -> dict[str, dict[str, Any]]:
    """Load all config files and return merged configuration."""
    configs = {}
    for name in ["data", "features", "models", "wandb"]:
        try:
            configs[name] = load_config(name)
        except FileNotFoundError:
            configs[name] = {}
    return configs
