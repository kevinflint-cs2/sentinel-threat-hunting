"""Build and test the Security Incident Analysis KQL query.

This script mirrors the logic in `threat-hunting-build-test-kql.ipynb` so it can
be run as a standard Python script from the repository root.
"""

from __future__ import annotations

import os
import uuid
from datetime import datetime

import pandas as pd  # noqa: F401  # imported for symmetry with notebook
import yaml
from azure.identity import DefaultAzureCredential
from azure.monitor.query import LogsQueryClient
from dotenv import load_dotenv

from utils.config_loader import load_config
from utils.kql_query import execute_kql_query
from utils.query_template import render_kql_file


def main() -> None:
    """Build the YAML rule, render KQL with an investigation config, and execute it."""

    # Load environment variables (e.g., SENTINEL_WORKSPACE_ID)
    load_dotenv()

    credential = DefaultAzureCredential()
    client = LogsQueryClient(credential=credential)

    workspace_id = os.getenv("SENTINEL_WORKSPACE_ID")
    if not workspace_id:
        raise ValueError("SENTINEL_WORKSPACE_ID environment variable is not set.")

    # ---------------------------------------------------------------------
    # Define rule metadata and templated KQL
    # ---------------------------------------------------------------------
    rule_title = "Security Incident Analysis"
    rule_description = (
        "Identifies Microsoft Sentinel Incidents created in response to security alerts, "
        "providing insights into potential threats and vulnerabilities within the environment."
    )
    rule_file_name = "security_incident_analysis.yaml"
    rule_save_path = os.path.join("queries", "analysis", "xdr", rule_file_name)
    rule_references = [
        "https://learn.microsoft.com/en-us/azure/sentinel/manage-soc-with-incident-metrics",
        "https://learn.microsoft.com/en-us/azure/azure-monitor/reference/tables/securityincident",
    ]
    rule_author = "Kevin Flint"
    rule_tags = [
        "xdr",
        "security incident",
        "microsoft sentinel",
        "incident analysis",
        "threat detection",
    ]
    rule_table = "SecurityIncident"
    rule_category = "xdr"
    rule_false_positives = [
        "Legitimate security incidents created by security operations teams.",
        "Incidents generated from known benign alerts or activities.",
        "RH Red Team activity and/or Protivity Offensive Security activity.",
    ]
    rule_level = "high"
    rule_kql_query = (
        "SecurityIncident\n"
        "| where TimeGenerated between (datetime({{ start_time }}) .. datetime({{ end_time }}))\n"
        '{% if device_name and user_name %}| where * contains "{{ device_name }}" or * contains "{{ user_name }}"\n'
        '{% elif device_name %}| where * contains "{{ device_name }}"\n'
        '{% elif user_name %}| where * contains "{{ user_name }}"\n'
        "{% endif %}"
    )

    analytic_rule_dict = {
        "title": rule_title,
        "id": str(uuid.uuid4()),
        "status": "test",
        "description": rule_description,
        "references": rule_references,
        "author": rule_author,
        "date": datetime.now().strftime("%Y-%m-%d"),
        "modified": datetime.now().strftime("%Y-%m-%d"),
        "tags": rule_tags,
        "logsource": {
            "product": "windows",
            "table": rule_table,
            "category": rule_category,
        },
        "kql": rule_kql_query.strip(),
        "falsepositives": rule_false_positives,
        "level": rule_level,
    }

    analytic_rule_yaml = yaml.dump(
        analytic_rule_dict,
        default_flow_style=False,
        sort_keys=False,
    )

    # Validate round-trip YAML
    parsed_yaml = yaml.safe_load(analytic_rule_yaml)
    print("✓ Valid YAML for analytic rule")
    print(f"Title: {parsed_yaml['title']}")
    print(f"ID: {parsed_yaml['id']}")

    os.makedirs(os.path.dirname(rule_save_path), exist_ok=True)
    with open(rule_save_path, "w", encoding="utf-8") as file:
        file.write(analytic_rule_yaml)
    print(f"✓ Analytic rule saved to {rule_save_path}")

    # ---------------------------------------------------------------------
    # Load investigation config and render the KQL
    # ---------------------------------------------------------------------
    investigation_config_path = os.path.join("investigations", "rtbt", "config.yaml")
    if not os.path.exists(investigation_config_path):
        raise FileNotFoundError(
            f"Config file not found at {investigation_config_path}",
        )

    print(f"Investigation config file path: {investigation_config_path}")
    config = load_config(str(investigation_config_path))

    # Support both device_name/user_name and devicename/username keys
    device_name = config.get("device_name") or config.get("devicename")
    user_name = config.get("user_name") or config.get("username")

    print(f"Device Name from config: {device_name}")
    print(f"Username from config: {user_name}")
    print(f"Start Time from config: {config['start_time']}")
    print(f"End Time from config: {config['end_time']}")

    rendered_query = render_kql_file(str(rule_save_path), config)
    print("\nRendered KQL query:\n")
    print(rendered_query)

    # ---------------------------------------------------------------------
    # Execute the rendered KQL against the Sentinel workspace
    # ---------------------------------------------------------------------
    df = execute_kql_query(
        client=client,
        workspace_id=workspace_id,
        kql_query=rendered_query,
    )

    print("\nQuery execution completed. Sample results:")
    with pd.option_context("display.max_rows", 5, "display.max_columns", None):
        print(df.head())


if __name__ == "__main__":  # pragma: no cover
    main()
