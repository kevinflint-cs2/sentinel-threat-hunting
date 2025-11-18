"""
Tests for Query Template Renderer.

This module contains pytest tests for the query_template module,
validating Jinja2 template rendering with KQL queries.
"""

import pytest
import tempfile
import os
from pathlib import Path
from jinja2 import UndefinedError, TemplateSyntaxError
from utils.query_template import (
    render_kql_template,
    render_kql_file,
    get_template_variables
)
from utils.config_loader import load_config


# Fixtures
@pytest.fixture
def simple_template():
    """Return a simple KQL template with one variable."""
    return "DeviceEvents | where DeviceName == '{{ devicename }}'"


@pytest.fixture
def multi_variable_template():
    """Return a KQL template with multiple variables."""
    return """
DeviceEvents
| where DeviceName == "{{ devicename }}"
| where AccountName == "{{ username }}"
| where Timestamp >= datetime({{ start_time }})
| where Timestamp <= datetime({{ end_time }})
"""


@pytest.fixture
def simple_variables():
    """Return a simple variables dictionary."""
    return {
        "devicename": "TEST-DEVICE-001",
        "username": "test.user",
        "start_time": "2025-11-01T00:00:00Z",
        "end_time": "2025-11-17T23:59:59Z",
        "process_name": "powershell.exe"
    }


@pytest.fixture
def test_kql_file_path():
    """Return path to test KQL file."""
    return "tests/fixtures/test_query.kql"


@pytest.fixture
def test_config_path():
    """Return path to test config file."""
    return "tests/fixtures/test_config.yaml"


@pytest.fixture
def temp_kql_file():
    """Create a temporary KQL file for testing."""
    temp_file = tempfile.NamedTemporaryFile(
        mode='w',
        suffix='.kql',
        delete=False,
        encoding='utf-8'
    )
    temp_file.close()  # Close file before yielding to avoid Windows lock issues
    yield temp_file.name
    # Cleanup
    try:
        if os.path.exists(temp_file.name):
            os.unlink(temp_file.name)
    except PermissionError:
        pass  # File may still be locked on Windows


# Tests for render_kql_template()
def test_render_simple_template(simple_template):
    """Test basic variable substitution in a template."""
    variables = {"devicename": "TEST-DEVICE-001"}
    result = render_kql_template(simple_template, variables)
    
    # Verify variable was substituted
    assert "TEST-DEVICE-001" in result
    assert "{{ devicename }}" not in result
    assert "{{" not in result


def test_render_multiple_variables(multi_variable_template, simple_variables):
    """Test substitution of multiple variables in a template."""
    result = render_kql_template(multi_variable_template, simple_variables)
    
    # Verify all variables were substituted
    assert "TEST-DEVICE-001" in result
    assert "test.user" in result
    assert "2025-11-01T00:00:00Z" in result
    assert "2025-11-17T23:59:59Z" in result
    
    # Verify no template syntax remains
    assert "{{" not in result
    assert "}}" not in result


def test_render_with_missing_variable(simple_template):
    """Test that UndefinedError is raised when variable is missing."""
    variables = {}  # Empty - missing devicename
    
    with pytest.raises(UndefinedError) as excinfo:
        render_kql_template(simple_template, variables)
    
    assert "devicename" in str(excinfo.value)


def test_render_template_invalid_syntax():
    """Test that TemplateSyntaxError is raised for invalid Jinja2 syntax."""
    invalid_template = "WHERE Device == '{{ devicename }'"  # Missing closing }}
    variables = {"devicename": "TEST"}
    
    with pytest.raises(TemplateSyntaxError):
        render_kql_template(invalid_template, variables)


def test_render_template_no_variables():
    """Test rendering a template with no variables."""
    template = "DeviceEvents | take 10"
    variables = {}
    
    result = render_kql_template(template, variables)
    assert result == template


def test_render_template_extra_variables(simple_template):
    """Test that extra variables don't cause issues."""
    variables = {
        "devicename": "TEST-DEVICE-001",
        "extra_var": "not_used",
        "another_extra": "also_not_used"
    }
    
    result = render_kql_template(simple_template, variables)
    assert "TEST-DEVICE-001" in result
    assert "not_used" not in result


# Tests for render_kql_file()
def test_render_kql_file(test_kql_file_path, simple_variables):
    """Test loading and rendering a KQL file."""
    result = render_kql_file(test_kql_file_path, simple_variables)
    
    # Verify variables were substituted
    assert "TEST-DEVICE-001" in result
    assert "test.user" in result
    
    # Verify no template syntax remains
    assert "{{" not in result
    assert "}}" not in result


def test_render_kql_file_not_found():
    """Test that FileNotFoundError is raised for missing KQL file."""
    with pytest.raises(FileNotFoundError) as excinfo:
        render_kql_file("nonexistent/query.kql", {})
    
    assert "KQL query file not found" in str(excinfo.value)


def test_render_kql_file_with_missing_variable(test_kql_file_path):
    """Test that UndefinedError is raised when variables are missing."""
    variables = {"devicename": "TEST"}  # Missing other required variables
    
    with pytest.raises(UndefinedError):
        render_kql_file(test_kql_file_path, variables)


def test_render_kql_file_empty_file(temp_kql_file):
    """Test rendering an empty KQL file."""
    # Create empty file
    with open(temp_kql_file, 'w') as f:
        f.write("")
    
    result = render_kql_file(temp_kql_file, {})
    assert result == ""


# Tests for get_template_variables()
def test_get_template_variables_single(simple_template):
    """Test extracting a single variable from a template."""
    variables = get_template_variables(simple_template)
    
    assert variables == ["devicename"]


def test_get_template_variables_multiple(multi_variable_template):
    """Test extracting multiple variables from a template."""
    variables = get_template_variables(multi_variable_template)
    
    # Should be sorted
    assert variables == ["devicename", "end_time", "start_time", "username"]
    assert len(variables) == 4


def test_get_template_variables_none():
    """Test template with no variables returns empty list."""
    template = "DeviceEvents | take 10"
    variables = get_template_variables(template)
    
    assert variables == []


def test_get_template_variables_duplicate():
    """Test that duplicate variables are only listed once."""
    template = """
    WHERE Device == '{{ devicename }}'
    OR Device == '{{ devicename }}'
    OR Device == '{{ devicename }}'
    """
    variables = get_template_variables(template)
    
    assert variables == ["devicename"]
    assert len(variables) == 1


def test_get_template_variables_invalid_syntax():
    """Test that invalid syntax returns empty list."""
    invalid_template = "WHERE Device == '{{ devicename }'"
    variables = get_template_variables(invalid_template)
    
    # Should return empty list rather than raise error
    assert variables == []


# Integration Tests
def test_end_to_end_config_and_template(test_config_path, test_kql_file_path):
    """
    Test full workflow: load config -> render template -> verify output.
    
    This is the main integration test that validates the complete workflow.
    When new variables are added to the system, this test should be updated.
    """
    # Load test config
    config = load_config(test_config_path)
    
    # Verify config loaded successfully
    assert isinstance(config, dict)
    assert len(config) > 0
    
    # Render KQL template with config variables
    rendered_query = render_kql_file(test_kql_file_path, config)
    
    # Verify all expected variables were substituted
    assert config["devicename"] in rendered_query
    assert config["username"] in rendered_query
    assert config["start_time"] in rendered_query
    assert config["end_time"] in rendered_query
    assert config["process_name"] in rendered_query
    
    # Verify no template syntax remains
    assert "{{" not in rendered_query
    assert "}}" not in rendered_query
    
    # Verify query structure is maintained
    assert "DeviceEvents" in rendered_query
    assert "where" in rendered_query.lower()


def test_end_to_end_extract_and_validate_variables(test_kql_file_path):
    """Test extracting variables from template and validating config has them."""
    # Read the test query file
    with open(test_kql_file_path, 'r') as f:
        template = f.read()
    
    # Extract required variables
    required_vars = get_template_variables(template)
    
    # Verify we found the expected variables
    assert "devicename" in required_vars
    assert "username" in required_vars
    assert "start_time" in required_vars
    assert "end_time" in required_vars
    assert "process_name" in required_vars
    
    # Load config and verify it has all required variables
    config = load_config("tests/fixtures/test_config.yaml")
    
    for var in required_vars:
        assert var in config, f"Config missing required variable: {var}"


def test_end_to_end_with_string_template(test_config_path):
    """Test full workflow with inline template string."""
    # Load config
    config = load_config(test_config_path)
    
    # Create inline template
    template = """
    DeviceNetworkEvents
    | where DeviceName == "{{ devicename }}"
    | where InitiatingProcessAccountName == "{{ username }}"
    | where RemoteIP == "{{ ip_address }}"
    | where Timestamp between (datetime({{ start_time }}) .. datetime({{ end_time }}))
    """
    
    # Render template
    result = render_kql_template(template, config)
    
    # Verify substitutions
    assert config["devicename"] in result
    assert config["username"] in result
    assert config["ip_address"] in result
    assert config["start_time"] in result
    assert config["end_time"] in result
    
    # Verify no template syntax remains
    assert "{{" not in result
    assert "}}" not in result
