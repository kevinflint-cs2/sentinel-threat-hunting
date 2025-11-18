"""
KQL Query Template Renderer.

This module provides functionality to render KQL query templates with
variables using Jinja2 templating engine. Supports loading templates
from strings or files and substituting variables from configuration
dictionaries.
"""

from typing import List
from pathlib import Path
from jinja2 import Environment, StrictUndefined, meta, TemplateSyntaxError


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
        raise TemplateSyntaxError(
            f"Invalid template syntax: {str(e)}",
            e.lineno
        ) from e


def render_kql_file(kql_file_path: str, variables: dict) -> str:
    """
    Load KQL file and render with variables.
    
    This function reads a KQL query file from disk and renders it with
    the provided variables. It's a convenience wrapper around
    render_kql_template() for file-based queries.
    
    Parameters:
    -----------
    kql_file_path : str
        Absolute or relative path to .kql file containing template
        variables.
    variables : dict
        Dictionary of variable names and their values for substitution.
        
    Returns:
    --------
    str
        Rendered KQL query string with all variables substituted.
        
    Raises:
    -------
    FileNotFoundError
        If the specified KQL file does not exist.
    jinja2.UndefinedError
        If the template references variables not present in the
        variables dictionary.
    jinja2.TemplateSyntaxError
        If the template contains invalid Jinja2 syntax.
        
    Examples:
    ---------
    >>> variables = {"devicename": "TEST-001", "username": "admin"}
    >>> query = render_kql_file("queries/lateral-movement.kql", variables)
    >>> print(query)
    """
    # Convert to Path object for better path handling
    kql_file = Path(kql_file_path)
    
    # Check if file exists
    if not kql_file.exists():
        raise FileNotFoundError(
            f"KQL query file not found: {kql_file_path}"
        )
    
    # Read the template file
    try:
        with open(kql_file, 'r', encoding='utf-8') as f:
            template_string = f.read()
    except Exception as e:
        raise IOError(
            f"Failed to read KQL file: {kql_file_path}\n{str(e)}"
        ) from e
    
    # Render the template with variables
    return render_kql_template(template_string, variables)


def get_template_variables(template_string: str) -> List[str]:
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
        return sorted(list(variables))
    except TemplateSyntaxError:
        # If template is invalid, return empty list
        # The actual rendering will raise the proper error
        return []
