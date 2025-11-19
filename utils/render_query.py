"""KQL Query Renderer CLI Tool.

This script renders KQL query templates with variables from a YAML
configuration file and outputs the result for review before execution.
"""

import argparse
import logging
import os
import sys
from pathlib import Path

from config_loader import load_config
from dotenv import load_dotenv
from query_template import get_template_variables, load_query_yaml, render_kql_file

logger = logging.getLogger(__name__)


def main():
    """
    Main function to render KQL queries with config variables.

    Loads a YAML config file and renders a KQL query template,
    displaying the result for review.
    """
    # Load environment variables from .env (if present) so users can
    # define default config/query paths via environment.
    load_dotenv()

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
        nargs="?",
        default=os.getenv("QUERY_FILE_PATH"),
        help=(
            "Path to the YAML query file containing metadata and KQL template "
            "(default: QUERY_FILE_PATH from .env, if set)"
        ),
    )

    parser.add_argument(
        "-c",
        "--config",
        type=str,
        default=os.getenv(
            "INVESTIGATION_CONFIG_PATH",
            "investigations/example-case/config.yaml",
        ),
        help=(
            "Path to YAML config file "
            "(default: investigations/example-case/config.yaml or "
            "INVESTIGATION_CONFIG_PATH from .env)"
        ),
    )

    parser.add_argument(
        "--show-variables",
        action="store_true",
        help="Show template variables required by the query",
    )

    # Parse arguments
    args = parser.parse_args()

    # Ensure we have a query file, either from CLI or environment
    if not args.query_file:
        logger.error(
            "Error: No query file provided. Pass a path as an argument or set QUERY_FILE_PATH in .env."
        )
        sys.exit(1)

    # Validate query file exists
    query_path = Path(args.query_file)
    if not query_path.exists():
        logger.error("Error: Query file not found: %s", args.query_file)
        sys.exit(1)

    # Validate config file exists
    config_path = Path(args.config)
    if not config_path.exists():
        logger.error("Error: Config file not found: %s", args.config)
        sys.exit(1)

    try:
        # Load query metadata
        query_data = load_query_yaml(args.query_file)

        # Display query metadata
        logger.info("%s", "=" * 70)
        logger.info("QUERY METADATA:")
        logger.info("%s", "=" * 70)
        logger.info("Title: %s", query_data.get("title", "N/A"))
        logger.info("ID: %s", query_data.get("id", "N/A"))
        logger.info("Author: %s", query_data.get("author", "N/A"))
        logger.info("Status: %s", query_data.get("status", "N/A"))
        logger.info("Level: %s", query_data.get("level", "N/A"))

        if "tags" in query_data and query_data["tags"]:
            logger.info("Tags: %s", ", ".join(query_data["tags"]))

        if "description" in query_data:
            logger.info("\nDescription:\n  %s", query_data["description"])

        if "logsource" in query_data:
            logsource = query_data["logsource"]
            logger.info("\nLog Source:")
            if "product" in logsource:
                logger.info("  Product: %s", logsource["product"])
            if "table" in logsource:
                logger.info("  Table: %s", logsource["table"])
            if "category" in logsource:
                logger.info("  Category: %s", logsource["category"])

        logger.info("%s", "=" * 70)
        logger.info("")

        # Show template variables if requested
        if args.show_variables:
            kql_template = query_data["kql"]
            variables = get_template_variables(kql_template)
            logger.info("%s", "=" * 70)
            logger.info("TEMPLATE VARIABLES REQUIRED:")
            logger.info("%s", "=" * 70)
            for var in variables:
                logger.info("  - %s", var)
            logger.info("%s", "=" * 70)
            logger.info("")

        # Load configuration
        logger.info("Loading config: %s", args.config)
        config = load_config(args.config)
        logger.info("✓ Loaded %d configuration variables", len(config))
        logger.info("")

        # Render the query
        logger.info("Rendering query: %s", args.query_file)
        rendered_query = render_kql_file(args.query_file, config)
        logger.info("✓ Query rendered successfully")
        logger.info("")

        # Display the rendered query
        logger.info("%s", "=" * 70)
        logger.info("RENDERED KQL QUERY:")
        logger.info("%s", "=" * 70)
        logger.info("%s", rendered_query)
        logger.info("%s", "=" * 70)
        logger.info("")

        # Summary
        logger.info("✓ Query ready for execution")
        logger.info("  Config used: %s", args.config)
        logger.info("  Query file: %s", args.query_file)

    except Exception as e:
        logger.exception("Error: %s", str(e))
        sys.exit(1)


if __name__ == "__main__":
    main()
