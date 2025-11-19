"""
Tests for Query Template Renderer.

This module contains pytest tests for the query_template module,
validating Jinja2 template rendering with KQL queries.
"""

import os
import tempfile

import pytest
import yaml
from jinja2 import TemplateSyntaxError, UndefinedError

from utils.config_loader import load_config
from utils.query_template import (
    get_template_variables,
    load_query_yaml,
    render_kql_file,
    render_kql_template,
)


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
| where DeviceName == "{{ device_name }}"
| where AccountName == "{{ user_name }}"
| where Timestamp >= datetime({{ start_time }})
| where Timestamp <= datetime({{ end_time }})
"""


@pytest.fixture
def simple_variables():
    """Return a simple variables dictionary."""
    return {
        "device_name": "TEST-DEVICE-001",
        "user_name": "test.user",
        "start_time": "2025-11-01T00:00:00Z",
        "end_time": "2025-11-17T23:59:59Z",
        "process_name": "powershell.exe",
    }


@pytest.fixture
def test_query_file_path():
    """Return path to test YAML query file."""
    return "tests/fixtures/test_query.yaml"


@pytest.fixture
def test_config_path():
    """Return path to test config file."""
    return "tests/fixtures/test_config.yaml"


@pytest.fixture
def temp_query_file():
    """Create a temporary YAML query file for testing."""
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
    variables: dict[str, str] = {}  # Empty - missing devicename

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
    variables: dict[str, str] = {}

    result = render_kql_template(template, variables)
    assert result == template


def test_render_template_extra_variables(simple_template):
    """Test that extra variables don't cause issues."""
    variables = {
        "devicename": "TEST-DEVICE-001",
        "extra_var": "not_used",
        "another_extra": "also_not_used",
    }

    result = render_kql_template(simple_template, variables)
    assert "TEST-DEVICE-001" in result
    assert "not_used" not in result


# Tests for load_query_yaml()
def test_load_query_yaml(test_query_file_path):
    """Test loading a YAML query file."""
    query_data = load_query_yaml(test_query_file_path)

    # Verify it's a dictionary
    assert isinstance(query_data, dict)

    # Verify required fields
    assert "kql" in query_data
    assert isinstance(query_data["kql"], str)

    # Verify metadata fields
    assert query_data["title"] == "Test Query for Unit Tests"
    assert query_data["id"] == "test-uuid-12345-67890"
    assert query_data["author"] == "Test Author"


def test_load_query_yaml_missing_kql_field(temp_query_file):
    """Test that ValueError is raised when kql field is missing."""
    # Create YAML without kql field
    query_data: dict[str, str] = {
        "title": "Test Query",
        "id": "test-123",
        "description": "Missing kql field",
    }

    with open(temp_query_file, "w") as f:
        yaml.dump(query_data, f)

    with pytest.raises(ValueError) as excinfo:
        load_query_yaml(temp_query_file)

    assert "must contain 'kql' field" in str(excinfo.value)


def test_load_query_yaml_invalid_kql_type(temp_query_file):
    """Test that ValueError is raised when kql field is not a string."""
    # Create YAML with kql as list instead of string
    query_data: dict[str, object] = {
        "title": "Test Query",
        "id": "test-123",
        "kql": ["not", "a", "string"],
    }

    with open(temp_query_file, "w") as f:
        yaml.dump(query_data, f)

    with pytest.raises(ValueError) as excinfo:
        load_query_yaml(temp_query_file)

    assert "must be a string" in str(excinfo.value)


def test_load_query_yaml_file_not_found():
    """Test that FileNotFoundError is raised for missing file."""
    with pytest.raises(FileNotFoundError) as excinfo:
        load_query_yaml("nonexistent/query.yaml")

    assert "Query YAML file not found" in str(excinfo.value)


def test_load_query_yaml_invalid_yaml(temp_query_file):
    """Test that YAMLError is raised for invalid YAML syntax."""
    # Write invalid YAML
    with open(temp_query_file, "w") as f:
        f.write("invalid:\n  yaml:\n    - missing\n  - indentation")

    with pytest.raises(yaml.YAMLError):
        load_query_yaml(temp_query_file)


def test_load_query_yaml_not_dict(temp_query_file):
    """Test that ValueError is raised when YAML is not a dictionary."""
    # Write YAML that parses to a list
    with open(temp_query_file, "w") as f:
        f.write("- item1\n- item2\n- item3")

    with pytest.raises(ValueError) as excinfo:
        load_query_yaml(temp_query_file)

    assert "must contain a dictionary" in str(excinfo.value)


# Tests for render_kql_file()
def test_render_kql_file(test_query_file_path, simple_variables):
    """Test loading and rendering a YAML query file."""
    result = render_kql_file(test_query_file_path, simple_variables)

    # Verify variables were substituted
    assert "TEST-DEVICE-001" in result
    assert "test.user" in result

    # Verify no template syntax remains
    assert "{{" not in result
    assert "}}" not in result


def test_render_kql_file_not_found():
    """Test that FileNotFoundError is raised for missing query file."""
    with pytest.raises(FileNotFoundError) as excinfo:
        render_kql_file("nonexistent/query.yaml", {})

    assert "Query YAML file not found" in str(excinfo.value)


def test_render_kql_file_with_missing_variable(test_query_file_path):
    """Test that UndefinedError is raised when variables are missing."""
    variables = {"device_name": "TEST"}  # Missing user_name variable

    with pytest.raises(UndefinedError):
        render_kql_file(test_query_file_path, variables)


def test_render_kql_file_empty_kql(temp_query_file):
    """Test rendering a query file with empty kql field."""
    # Create YAML with empty kql
    query_data = {"title": "Empty Query", "id": "test-456", "kql": ""}

    with open(temp_query_file, "w") as f:
        yaml.dump(query_data, f)

    result = render_kql_file(temp_query_file, {})
    assert result == ""


# Tests for render_kql_file() - removed old KQL file tests


# Tests for get_template_variables()
def test_get_template_variables_single(simple_template):
    """Test extracting a single variable from a template."""
    variables = get_template_variables(simple_template)

    assert variables == ["devicename"]


def test_get_template_variables_multiple(multi_variable_template):
    """Test extracting multiple variables from a template."""
    variables = get_template_variables(multi_variable_template)

    # Should be sorted
    assert variables == ["device_name", "end_time", "start_time", "user_name"]
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
def test_end_to_end_config_and_template(test_config_path, test_query_file_path):
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
    rendered_query = render_kql_file(test_query_file_path, config)

    # Verify expected variables were substituted (using new variable names)
    assert config["device_name"] in rendered_query
    assert config["user_name"] in rendered_query

    # Verify no template syntax remains
    assert "{{" not in rendered_query
    assert "}}" not in rendered_query

    # Verify query structure is maintained
    assert "DeviceProcessEvents" in rendered_query
    assert "where" in rendered_query.lower()


def test_end_to_end_extract_and_validate_variables(test_query_file_path):
    """Test extracting variables from query YAML and validating config has them."""
    # Load query data
    query_data = load_query_yaml(test_query_file_path)

    # Extract KQL template
    kql_template = query_data["kql"]

    # Extract required variables from KQL template
    required_vars = get_template_variables(kql_template)

    # Verify we found the expected variables
    assert "device_name" in required_vars
    assert "user_name" in required_vars

    # Load config and verify it has all required variables
    config = load_config("tests/fixtures/test_config.yaml")

    for var in required_vars:
        assert var in config, f"Config missing required variable: {var}"


def test_end_to_end_with_string_template(test_config_path):
    """Test full workflow with inline template string."""
    # Load config
    config = load_config(test_config_path)

    # Create inline template with updated variable names
    template = """
    DeviceNetworkEvents
    | where DeviceName == "{{ device_name }}"
    | where InitiatingProcessAccountName == "{{ user_name }}"
    | where RemoteIP == "{{ ip_address }}"
    | where Timestamp between (datetime({{ start_time }}) .. datetime({{ end_time }}))
    """

    # Render template
    result = render_kql_template(template, config)

    # Verify substitutions
    assert config["device_name"] in result
    assert config["user_name"] in result
    assert config["ip_address"] in result
    assert config["start_time"] in result
    assert config["end_time"] in result

    # Verify no template syntax remains
    assert "{{" not in result
    assert "}}" not in result
