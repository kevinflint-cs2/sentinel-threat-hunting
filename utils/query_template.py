"""
KQL Query Template Renderer.

This module provides functionality to render KQL query templates with
variables using Jinja2 templating engine. Supports loading templates
from strings or files and substituting variables from configuration
dictionaries.
"""

from pathlib import Path

import yaml
from jinja2 import Environment, StrictUndefined, TemplateSyntaxError, meta


def render_kql_template(template_string: str, variables: dict) -> str:
    """
    Render KQL query template with variables using Jinja2.

    This function takes a KQL query string containing Jinja2 template
    variables (e.g., {{ devicename }}) and substitutes them with values
    from the provided variables dictionary. Uses strict undefined mode
    to ensure all variables are provided.

    Parameters:
    -----------
    template_string : str
        KQL query string with {{ variable }} placeholders.
    variables : dict
        Dictionary of variable names and their values for substitution.

    Returns:
    --------
    str
        Rendered KQL query string with all variables substituted.

    Raises:
    -------
    jinja2.UndefinedError
        If the template references variables not present in the
        variables dictionary.
    jinja2.TemplateSyntaxError
        If the template contains invalid Jinja2 syntax.

    Examples:
    ---------
    >>> template = "DeviceEvents | where DeviceName == '{{ devicename }}'"
    >>> variables = {"devicename": "TEST-001"}
    >>> result = render_kql_template(template, variables)
    >>> print(result)
    "DeviceEvents | where DeviceName == 'TEST-001'"
    """
    # Create Jinja2 environment with strict undefined checking
    # This ensures we catch any missing variables immediately
    env = Environment(undefined=StrictUndefined)

    try:
        # Parse and render the template
        template = env.from_string(template_string)
        rendered = template.render(variables)
        return rendered
    except TemplateSyntaxError as e:
        raise TemplateSyntaxError(f"Invalid template syntax: {str(e)}", e.lineno) from e


def load_query_yaml(yaml_file_path: str) -> dict:
    """
    Load query YAML file and return parsed structure.

    This function reads a YAML query file containing query metadata
    and the KQL template. Validates that the file contains the required
    'kql' field.

    Parameters:
    -----------
    yaml_file_path : str
        Absolute or relative path to .yaml query file.

    Returns:
    --------
    Dict
        Parsed YAML structure containing query metadata and KQL template.

    Raises:
    -------
    FileNotFoundError
        If the specified YAML file does not exist.
    ValueError
        If the YAML file is missing the 'kql' field or is not a dictionary.
    yaml.YAMLError
        If the file contains invalid YAML syntax.

    Examples:
    ---------
    >>> query_data = load_query_yaml("queries/analysis/xdr/process_chain.yaml")
    >>> print(query_data['title'])
    >>> print(query_data['kql'])
    """
    # Convert to Path object for better path handling
    yaml_file = Path(yaml_file_path)

    # Check if file exists
    if not yaml_file.exists():
        raise FileNotFoundError(f"Query YAML file not found: {yaml_file_path}")

    # Read and parse the YAML file
    try:
        with open(yaml_file, encoding="utf-8") as f:
            query_data = yaml.safe_load(f)
    except yaml.YAMLError as e:
        raise yaml.YAMLError(f"Failed to parse YAML file: {yaml_file_path}\n{str(e)}") from e
    except Exception as e:
        raise OSError(f"Failed to read YAML file: {yaml_file_path}\n{str(e)}") from e

    # Validate that the result is a dictionary
    if not isinstance(query_data, dict):
        raise ValueError(
            f"Query YAML must contain a dictionary structure, got {type(query_data).__name__}"
        )

    # Validate that 'kql' field exists
    if "kql" not in query_data:
        raise ValueError(f"Query YAML must contain 'kql' field: {yaml_file_path}")

    # Validate that 'kql' field is a string
    if not isinstance(query_data["kql"], str):
        raise ValueError(
            f"Query 'kql' field must be a string, got {type(query_data['kql']).__name__}"
        )

    return query_data


def render_kql_file(yaml_file_path: str, variables: dict) -> str:
    """
    Load YAML query file, extract KQL field, and render with variables.

    This function reads a YAML query file from disk, extracts the KQL
    template from the 'kql' field, and renders it with the provided
    variables. It's a convenience wrapper that combines load_query_yaml()
    and render_kql_template().

    Parameters:
    -----------
    yaml_file_path : str
        Absolute or relative path to .yaml query file containing the
        'kql' field with template variables.
    variables : dict
        Dictionary of variable names and their values for substitution.

    Returns:
    --------
    str
        Rendered KQL query string with all variables substituted.

    Raises:
    -------
    FileNotFoundError
        If the specified YAML file does not exist.
    ValueError
        If the YAML file is missing the 'kql' field.
    jinja2.UndefinedError
        If the template references variables not present in the
        variables dictionary.
    jinja2.TemplateSyntaxError
        If the template contains invalid Jinja2 syntax.
    yaml.YAMLError
        If the file contains invalid YAML syntax.

    Examples:
    ---------
    >>> variables = {"device_name": "TEST-001", "user_name": "admin"}
    >>> query = render_kql_file("queries/analysis/xdr/process_chain.yaml", variables)
    >>> print(query)
    """
    # Load the YAML query file
    query_data = load_query_yaml(yaml_file_path)

    # Extract the KQL template string
    template_string = query_data["kql"]

    # Render the template with variables
    return render_kql_template(template_string, variables)


def get_template_variables(template_string: str) -> list[str]:
    """
    Extract all variable names from a Jinja2 template.

    This function parses a template string and returns a list of all
    variable names found in the template. Useful for validation and
    determining which variables are required by a template.

    Parameters:
    -----------
    template_string : str
        Template string to analyze for variables.

    Returns:
    --------
    List[str]
        Sorted list of unique variable names found in the template.
        Returns empty list if no variables are found.

    Examples:
    ---------
    >>> template = "WHERE Device == '{{ devicename }}' AND User == '{{ username }}'"
    >>> variables = get_template_variables(template)
    >>> print(variables)
    ['devicename', 'username']
    """
    # Create Jinja2 environment for parsing
    env = Environment()

    try:
        # Parse the template to get AST
        ast = env.parse(template_string)

        # Extract undeclared variables (those that need to be provided)
        variables = meta.find_undeclared_variables(ast)

        # Return sorted list for consistency
        return sorted(variables)
    except TemplateSyntaxError:
        # If template is invalid, return empty list
        # The actual rendering will raise the proper error
        return []
