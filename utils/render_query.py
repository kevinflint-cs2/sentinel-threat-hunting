"""
KQL Query Renderer CLI Tool.

This script renders KQL query templates with variables from a YAML
configuration file and outputs the result for review before execution.
"""

import argparse
import sys
from pathlib import Path

from config_loader import load_config
from query_template import get_template_variables, load_query_yaml, render_kql_file


def main():
    """
    Main function to render KQL queries with config variables.

    Loads a YAML config file and renders a KQL query template,
    displaying the result for review.
    """
    # Set up argument parser
    parser = argparse.ArgumentParser(
        description="Render KQL query templates from YAML query files with YAML config variables",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Render with default config
  python utils/render_query.py queries/analysis/xdr/process_chain_analysis.yaml

  # Render with custom config
  python utils/render_query.py queries/analysis/xdr/process_chain_analysis.yaml -c investigations/my-case/config.yaml

  # Using Poetry
  poetry run python utils/render_query.py queries/analysis/xdr/process_chain_analysis.yaml

  # Using poe task
  poe render queries/analysis/xdr/process_chain_analysis.yaml
        """,
    )

    parser.add_argument(
        "query_file",
        type=str,
        help="Path to the YAML query file containing metadata and KQL template",
    )

    parser.add_argument(
        "-c",
        "--config",
        type=str,
        default="investigations/example-case/config.yaml",
        help="Path to YAML config file (default: investigations/example-case/config.yaml)",
    )

    parser.add_argument(
        "--show-variables",
        action="store_true",
        help="Show template variables required by the query",
    )

    # Parse arguments
    args = parser.parse_args()

    # Validate query file exists
    query_path = Path(args.query_file)
    if not query_path.exists():
        print(f"Error: Query file not found: {args.query_file}", file=sys.stderr)
        sys.exit(1)

    # Validate config file exists
    config_path = Path(args.config)
    if not config_path.exists():
        print(f"Error: Config file not found: {args.config}", file=sys.stderr)
        sys.exit(1)

    try:
        # Load query metadata
        query_data = load_query_yaml(args.query_file)

        # Display query metadata
        print("=" * 70)
        print("QUERY METADATA:")
        print("=" * 70)
        print(f"Title: {query_data.get('title', 'N/A')}")
        print(f"ID: {query_data.get('id', 'N/A')}")
        print(f"Author: {query_data.get('author', 'N/A')}")
        print(f"Status: {query_data.get('status', 'N/A')}")
        print(f"Level: {query_data.get('level', 'N/A')}")

        if "tags" in query_data and query_data["tags"]:
            print(f"Tags: {', '.join(query_data['tags'])}")

        if "description" in query_data:
            print(f"\nDescription:\n  {query_data['description']}")

        if "logsource" in query_data:
            logsource = query_data["logsource"]
            print("\nLog Source:")
            if "product" in logsource:
                print(f"  Product: {logsource['product']}")
            if "table" in logsource:
                print(f"  Table: {logsource['table']}")
            if "category" in logsource:
                print(f"  Category: {logsource['category']}")

        print("=" * 70)
        print()

        # Show template variables if requested
        if args.show_variables:
            kql_template = query_data["kql"]
            variables = get_template_variables(kql_template)
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
        print(f"Rendering query: {args.query_file}")
        rendered_query = render_kql_file(args.query_file, config)
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
        print(f"  Query file: {args.query_file}")

    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
