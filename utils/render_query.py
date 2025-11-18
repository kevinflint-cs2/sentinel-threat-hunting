"""
KQL Query Renderer CLI Tool.

This script renders KQL query templates with variables from a YAML
configuration file and outputs the result for review before execution.
"""

import argparse
import sys
from pathlib import Path
from config_loader import load_config
from query_template import render_kql_file, get_template_variables


def main():
    """
    Main function to render KQL queries with config variables.
    
    Loads a YAML config file and renders a KQL query template,
    displaying the result for review.
    """
    # Set up argument parser
    parser = argparse.ArgumentParser(
        description="Render KQL query templates with YAML config variables",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Render with default config
  python utils/render_query.py queries/lateral-movement.kql
  
  # Render with custom config
  python utils/render_query.py queries/lateral-movement.kql -c investigations/my-case/config.yaml
  
  # Using Poetry
  poetry run python utils/render_query.py queries/lateral-movement.kql
        """
    )
    
    parser.add_argument(
        "kql_file",
        type=str,
        help="Path to the KQL query file with template variables"
    )
    
    parser.add_argument(
        "-c", "--config",
        type=str,
        default="investigations/example-case/config.yaml",
        help="Path to YAML config file (default: investigations/example-case/config.yaml)"
    )
    
    parser.add_argument(
        "--show-variables",
        action="store_true",
        help="Show template variables required by the query"
    )
    
    # Parse arguments
    args = parser.parse_args()
    
    # Validate KQL file exists
    kql_path = Path(args.kql_file)
    if not kql_path.exists():
        print(f"Error: KQL file not found: {args.kql_file}", file=sys.stderr)
        sys.exit(1)
    
    # Validate config file exists
    config_path = Path(args.config)
    if not config_path.exists():
        print(f"Error: Config file not found: {args.config}", file=sys.stderr)
        sys.exit(1)
    
    try:
        # Show template variables if requested
        if args.show_variables:
            with open(kql_path, 'r', encoding='utf-8') as f:
                template_content = f.read()
            
            variables = get_template_variables(template_content)
            print("=" * 70)
            print("TEMPLATE VARIABLES REQUIRED:")
            print("=" * 70)
            for var in variables:
                print(f"  - {var}")
            print("=" * 70)
            print()
        
        # Load configuration
        print(f"Loading config: {args.config}")
        config = load_config(args.config)
        print(f"✓ Loaded {len(config)} configuration variables")
        print()
        
        # Render the query
        print(f"Rendering query: {args.kql_file}")
        rendered_query = render_kql_file(args.kql_file, config)
        print("✓ Query rendered successfully")
        print()
        
        # Display the rendered query
        print("=" * 70)
        print("RENDERED KQL QUERY:")
        print("=" * 70)
        print(rendered_query)
        print("=" * 70)
        print()
        
        # Summary
        print("✓ Query ready for execution")
        print(f"  Config used: {args.config}")
        print(f"  Query file: {args.kql_file}")
        
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
