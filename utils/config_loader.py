"""
Configuration Loader for Investigation Variables.

This module provides functionality to load and validate YAML configuration
files containing variables used in KQL query templates for threat hunting
investigations.
"""

from pathlib import Path
from typing import Optional

import yaml


def load_config(config_path: str) -> dict:
    """
    Load YAML configuration file and return as dictionary.

    This function reads a YAML configuration file from the specified path
    and returns its contents as a Python dictionary. It performs basic
    validation to ensure the file exists and contains valid YAML.

    Parameters:
    -----------
    config_path : str
        Absolute or relative path to the YAML configuration file.

    Returns:
    --------
    dict
        Dictionary containing configuration variables from the YAML file.

    Raises:
    -------
    FileNotFoundError
        If the specified config file does not exist.
    yaml.YAMLError
        If the config file contains invalid YAML syntax.
    ValueError
        If the config file is empty or does not contain a valid dictionary.

    Examples:
    ---------
    >>> config = load_config("investigations/case-001/config.yaml")
    >>> print(config["devicename"])
    'DESKTOP-ABC123'
    """
    # Convert to Path object for better path handling
    config_file = Path(config_path)

    # Check if file exists
    if not config_file.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")

    # Load YAML file
    try:
        with open(config_file, encoding="utf-8") as f:
            config_data = yaml.safe_load(f)
    except yaml.YAMLError as e:
        raise yaml.YAMLError(f"Invalid YAML in configuration file: {config_path}\n{str(e)}") from e

    # Validate that we got a dictionary
    if config_data is None:
        raise ValueError(f"Configuration file is empty: {config_path}")

    if not isinstance(config_data, dict):
        raise ValueError(
            f"Configuration file must contain a YAML dictionary, "
            f"got {type(config_data).__name__}: {config_path}"
        )

    return config_data


def validate_config(config: dict, required_fields: Optional[list[str]] = None) -> bool:
    """
    Validate configuration dictionary has required fields.

    This function checks that a configuration dictionary contains all
    necessary fields and that they have non-empty values. If no required
    fields are specified, it only validates that the config is not empty.

    Parameters:
    -----------
    config : dict
        Configuration dictionary to validate.
    required_fields : Optional[list[str]], optional
        List of field names that must be present in the config.
        If None, only validates that config is not empty.

    Returns:
    --------
    bool
        True if validation passes.

    Raises:
    -------
    ValueError
        If config is empty, not a dictionary, or missing required fields.

    Examples:
    ---------
    >>> config = {"devicename": "TEST-001", "username": "admin"}
    >>> validate_config(config, ["devicename", "username"])
    True

    >>> validate_config(config, ["devicename", "missing_field"])
    ValueError: Missing required configuration fields: missing_field
    """
    # Validate config is a dictionary
    if not isinstance(config, dict):
        raise ValueError(f"Configuration must be a dictionary, " f"got {type(config).__name__}")

    # Validate config is not empty
    if not config:
        raise ValueError("Configuration dictionary is empty")

    # If no required fields specified, validation passes
    if required_fields is None:
        return True

    # Check for required fields
    missing_fields = []
    empty_fields = []

    for field in required_fields:
        if field not in config:
            missing_fields.append(field)
        elif config[field] is None or config[field] == "":
            empty_fields.append(field)

    # Raise error if any required fields are missing
    if missing_fields:
        raise ValueError(f"Missing required configuration fields: " f"{', '.join(missing_fields)}")

    # Raise error if any required fields are empty
    if empty_fields:
        raise ValueError(
            f"Required configuration fields cannot be empty: " f"{', '.join(empty_fields)}"
        )

    return True
