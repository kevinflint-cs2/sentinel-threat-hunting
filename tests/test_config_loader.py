"""
Tests for Configuration Loader.

This module contains pytest tests for the config_loader module,
validating YAML configuration loading and validation functionality.
"""

import os
import tempfile

import pytest
import yaml

from utils.config_loader import load_config, validate_config


# Fixtures
@pytest.fixture
def test_config_path():
    """Return path to test configuration file."""
    return "tests/fixtures/test_config.yaml"


@pytest.fixture
def valid_config():
    """Return a valid configuration dictionary."""
    return {
        "devicename": "TEST-DEVICE",
        "username": "test.user",
        "start_time": "2025-11-01T00:00:00Z",
        "end_time": "2025-11-17T23:59:59Z",
    }


@pytest.fixture
def temp_yaml_file():
    """Create a temporary YAML file for testing."""
    temp_file = tempfile.NamedTemporaryFile(
        mode="w", suffix=".yaml", delete=False, encoding="utf-8"
    )
    temp_file.close()  # Close file before yielding to avoid Windows lock issues
    yield temp_file.name
    # Cleanup
    try:
        if os.path.exists(temp_file.name):
            os.unlink(temp_file.name)
    except PermissionError:
        pass  # File may still be locked on Windows


# Tests for load_config()
def test_load_valid_config(test_config_path):
    """Test loading a valid YAML configuration file."""
    config = load_config(test_config_path)

    # Verify config is a dictionary
    assert isinstance(config, dict)

    # Verify config is not empty
    assert len(config) > 0

    # Verify expected keys exist
    assert "device_name" in config
    assert "user_name" in config
    assert "start_time" in config


def test_load_config_file_not_found():
    """Test that FileNotFoundError is raised for missing config file."""
    with pytest.raises(FileNotFoundError) as excinfo:
        load_config("nonexistent/path/config.yaml")

    assert "Configuration file not found" in str(excinfo.value)


def test_load_config_invalid_yaml(temp_yaml_file):
    """Test that YAMLError is raised for invalid YAML syntax."""
    # Write invalid YAML to temp file
    with open(temp_yaml_file, "w") as f:
        f.write("invalid: yaml: syntax: here:\n  - broken")

    with pytest.raises(yaml.YAMLError) as excinfo:
        load_config(temp_yaml_file)

    assert "Invalid YAML" in str(excinfo.value)


def test_load_config_empty_file(temp_yaml_file):
    """Test that ValueError is raised for empty config file."""
    # Create empty file
    with open(temp_yaml_file, "w") as f:
        f.write("")

    with pytest.raises(ValueError) as excinfo:
        load_config(temp_yaml_file)

    assert "empty" in str(excinfo.value).lower()


def test_load_config_not_dict(temp_yaml_file):
    """Test that ValueError is raised when YAML is not a dictionary."""
    # Write YAML list instead of dict
    with open(temp_yaml_file, "w") as f:
        f.write("- item1\n- item2\n- item3")

    with pytest.raises(ValueError) as excinfo:
        load_config(temp_yaml_file)

    assert "must contain a YAML dictionary" in str(excinfo.value)


def test_config_contains_expected_keys(test_config_path):
    """Test that test fixture config contains all expected keys."""
    config = load_config(test_config_path)

    # Verify all expected keys from test fixture
    expected_keys = [
        "investigation_name",
        "investigator",
        "created_date",
        "start_time",
        "end_time",
        "device_name",
        "user_name",
        "ip_address",
        "domain",
        "process_name",
        "parent_process",
        "file_path",
        "suspicious_hash",
        "known_bad_ip",
    ]

    for key in expected_keys:
        assert key in config, f"Expected key '{key}' not found in config"


# Tests for validate_config()
def test_validate_config_with_required_fields(valid_config):
    """Test validation with required fields present."""
    required = ["devicename", "username"]
    result = validate_config(valid_config, required)
    assert result is True


def test_validate_config_missing_required_fields(valid_config):
    """Test that ValueError is raised when required fields are missing."""
    required = ["devicename", "missing_field", "another_missing"]

    with pytest.raises(ValueError) as excinfo:
        validate_config(valid_config, required)

    error_msg = str(excinfo.value)
    assert "Missing required configuration fields" in error_msg
    assert "missing_field" in error_msg


def test_validate_config_empty_required_field(valid_config):
    """Test that ValueError is raised when required field is empty."""
    config_with_empty = valid_config.copy()
    config_with_empty["devicename"] = ""

    required = ["devicename", "username"]

    with pytest.raises(ValueError) as excinfo:
        validate_config(config_with_empty, required)

    assert "cannot be empty" in str(excinfo.value)
    assert "devicename" in str(excinfo.value)


def test_validate_config_none_required_field(valid_config):
    """Test that ValueError is raised when required field is None."""
    config_with_none = valid_config.copy()
    config_with_none["username"] = None

    required = ["devicename", "username"]

    with pytest.raises(ValueError) as excinfo:
        validate_config(config_with_none, required)

    assert "cannot be empty" in str(excinfo.value)
    assert "username" in str(excinfo.value)


def test_validate_config_no_requirements(valid_config):
    """Test validation without required fields (only checks not empty)."""
    result = validate_config(valid_config, None)
    assert result is True


def test_validate_config_empty_dict():
    """Test that ValueError is raised for empty config dictionary."""
    with pytest.raises(ValueError) as excinfo:
        validate_config({})

    assert "empty" in str(excinfo.value).lower()


def test_validate_config_not_dict():
    """Test that ValueError is raised when config is not a dictionary."""
    with pytest.raises(ValueError) as excinfo:
        validate_config(["not", "a", "dict"])  # type: ignore[arg-type]

    assert "must be a dictionary" in str(excinfo.value)


def test_validate_config_all_fields_present(test_config_path):
    """Test validation passes when all fields from config are required."""
    config = load_config(test_config_path)
    required_fields = list(config.keys())

    # Should pass - all fields are present
    result = validate_config(config, required_fields)
    assert result is True
