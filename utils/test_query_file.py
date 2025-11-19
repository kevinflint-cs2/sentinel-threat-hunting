"""Validate and test execution of a YAML-based KQL query file.

This script is modeled after `build_test_security_incident_query.py` and is
intended to be run from the repository root. It will:

- Read a YAML query file.
- Validate that it has the expected structure.
- Render the templated KQL using an investigation config.
- Connect to a Log Analytics / Sentinel workspace.
- Execute the rendered KQL.
- Report any validation or execution issues.
"""

from __future__ import annotations

import logging
import os
import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Any

import pandas as pd  # noqa: F401  # imported for symmetry with notebook
import yaml
from azure.identity import DefaultAzureCredential
from azure.monitor.query import LogsQueryClient
from dotenv import load_dotenv

from utils.config_loader import load_config
from utils.kql_query import execute_kql_query
from utils.query_template import render_kql_file

logger = logging.getLogger(__name__)


@dataclass
class QueryFileValidationResult:
    """Represents the outcome of validating a YAML query file."""

    is_valid: bool
    errors: list[str]


REQUIRED_TOP_LEVEL_FIELDS = [
    "title",
    "id",
    "status",
    "description",
    "references",
    "author",
    "date",
    "modified",
    "tags",
    "logsource",
    "kql",
    "falsepositives",
    "level",
]

REQUIRED_LOGSOURCE_FIELDS = ["product", "table", "category"]

ALLOWED_STATUS_VALUES = {"test", "experimental", "stable"}
ALLOWED_LEVEL_VALUES = {"low", "medium", "high", "critical"}


def validate_query_yaml(yaml_data: dict[str, Any]) -> QueryFileValidationResult:
    """Validate that the YAML data roughly matches the expected schema.

    This is intentionally lightweight and focused on catching obvious
    structural issues before attempting to render and execute the query.
    """

    errors: list[str] = []

    for field in REQUIRED_TOP_LEVEL_FIELDS:
        if field not in yaml_data:
            errors.append(f"Missing required top-level field: {field}")

    logsource = yaml_data.get("logsource", {})
    if not isinstance(logsource, dict):
        errors.append("Field 'logsource' must be a mapping/dictionary.")
    else:
        for field in REQUIRED_LOGSOURCE_FIELDS:
            if field not in logsource:
                errors.append(f"Missing required logsource field: {field}")

    kql_value = yaml_data.get("kql")
    if not isinstance(kql_value, str) or not kql_value.strip():
        errors.append("Field 'kql' must be a non-empty string.")

    # Basic UUID v4 shape check for id
    rule_id = yaml_data.get("id")
    if isinstance(rule_id, str):
        try:
            parsed_uuid = uuid.UUID(rule_id)
            if parsed_uuid.version != 4:
                errors.append("Field 'id' must be a UUID v4.")
        except (ValueError, AttributeError):
            errors.append("Field 'id' must be a valid UUID string.")
    else:
        errors.append("Field 'id' must be a string UUID.")

    # Status and level should be from allowed sets
    status = yaml_data.get("status")
    if status not in ALLOWED_STATUS_VALUES:
        errors.append(
            "Field 'status' must be one of: " + ", ".join(sorted(ALLOWED_STATUS_VALUES)),
        )

    level = yaml_data.get("level")
    if level not in ALLOWED_LEVEL_VALUES:
        errors.append(
            "Field 'level' must be one of: " + ", ".join(sorted(ALLOWED_LEVEL_VALUES)),
        )

    is_valid = len(errors) == 0
    return QueryFileValidationResult(is_valid=is_valid, errors=errors)


def main() -> None:
    """Validate a YAML query file, render its KQL, and execute it.

    By default, this prints a simple, color-coded summary view showing:
    - Whether YAML structure validation passed.
    - Whether query execution succeeded.
    - The number of records returned by the query.

    Set the environment variable `DETAILED_OUTPUT=1` to see the
    full, verbose output (YAML details, config summary, rendered
    KQL, and sample results).
    """

    # Load environment variables (e.g., SENTINEL_WORKSPACE_ID)
    load_dotenv()

    detailed_output = os.getenv("DETAILED_OUTPUT", "0") == "1"

    workspace_id = os.getenv("SENTINEL_WORKSPACE_ID")
    if not workspace_id:
        raise ValueError(
            "SENTINEL_WORKSPACE_ID environment variable is not set.",
        )

    # Allow overriding defaults via environment variables
    query_file_path = os.getenv(
        "QUERY_FILE_PATH",
        os.path.join("queries", "analysis", "xdr", "powershell-activity-analysis.yaml"),
    )
    investigation_config_path = os.getenv(
        "INVESTIGATION_CONFIG_PATH",
        os.path.join("investigations", "rtbt", "config.yaml"),
    )

    if not os.path.exists(query_file_path):
        raise FileNotFoundError(f"Query file not found at {query_file_path}")

    if not os.path.exists(investigation_config_path):
        raise FileNotFoundError(
            f"Config file not found at {investigation_config_path}",
        )

    if detailed_output:
        logger.info("Query file path: %s", query_file_path)
        logger.info("Investigation config file path: %s", investigation_config_path)

    # ------------------------------------------------------------------
    # Read and validate YAML
    # ------------------------------------------------------------------
    with open(query_file_path, encoding="utf-8") as file:
        yaml_data = yaml.safe_load(file)

    validation_result = validate_query_yaml(yaml_data)

    if not validation_result.is_valid:
        logger.error("[YAML CHECK] ❌ FAILED")
        if detailed_output:
            logger.error("YAML validation errors:")
            for err in validation_result.errors:
                logger.error("  - %s", err)
        return

    logger.info("[YAML CHECK] ✅ PASSED")

    if detailed_output:
        logger.info("Title: %s", yaml_data.get("title"))
        logger.info("ID: %s", yaml_data.get("id"))
        logger.info("Status: %s", yaml_data.get("status"))
        logger.info("Logsource table: %s", yaml_data.get("logsource", {}).get("table"))

    # ------------------------------------------------------------------
    # Load investigation config and render the KQL
    # ------------------------------------------------------------------
    config = load_config(str(investigation_config_path))

    if detailed_output:
        logger.info("\nLoaded investigation config summary:")
        for key in [
            "device_name",
            "devicename",
            "user_name",
            "username",
            "start_time",
            "end_time",
        ]:
            if key in config:
                logger.info("  %s: %s", key, config[key])

    try:
        rendered_query = render_kql_file(str(query_file_path), config)
    except Exception as exc:  # noqa: BLE001
        logger.error("[RENDER] ❌ FAILED")
        if detailed_output:
            logger.exception("Error while rendering KQL query: %s: %s", type(exc).__name__, exc)
        return

    logger.info("[RENDER] ✅ SUCCEEDED")

    if detailed_output:
        logger.info("\nRendered KQL query:\n")
        logger.info("%s", rendered_query)

    # ------------------------------------------------------------------
    # Execute the rendered KQL against the Sentinel workspace
    # ------------------------------------------------------------------
    credential = DefaultAzureCredential()
    client = LogsQueryClient(credential=credential)

    if detailed_output:
        logger.info("\nExecuting query against workspace...")

    try:
        df = execute_kql_query(
            client=client,
            workspace_id=workspace_id,
            kql_query=rendered_query,
        )
    except Exception as exc:  # noqa: BLE001
        logger.error("[QUERY EXECUTION] ❌ FAILED")
        logger.exception("Error: %s: %s", type(exc).__name__, exc)
        if detailed_output:
            logger.info("\nFull traceback available with DETAILED_OUTPUT=1")
        return

    record_count = len(df.index)
    logger.info("[QUERY EXECUTION] ✅ SUCCEEDED")
    logger.info("[RESULTS] Records returned: %d", record_count)

    if detailed_output:
        logger.info("\nQuery execution completed. Sample results:")
        with pd.option_context("display.max_rows", 5, "display.max_columns", None):
            logger.info("%s", df.head())

    logger.info("\n✓ Query file validation and execution completed successfully at")
    logger.info("  %sZ", datetime.now().isoformat())


if __name__ == "__main__":  # pragma: no cover
    main()
