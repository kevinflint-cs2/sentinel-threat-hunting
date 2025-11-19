"""Hailmary runner: validate, render, and execute all YAML queries.

- Uses .env for configuration.
- Loads a single investigation config.
- Finds all .yaml files under queries/.
- For each file:
  - Validates basic structure.
  - Renders templated KQL.
  - Executes against the configured workspace.
  - Writes results to CSV under INVESTIGATION_RESULTS_PATH.
- Continues on errors and prints a summary at the end.
"""

from __future__ import annotations

import logging
import os
import uuid
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml
from azure.identity import DefaultAzureCredential
from azure.monitor.query import LogsQueryClient
from dotenv import load_dotenv

from utils.config_loader import load_config
from utils.kql_query import execute_kql_query
from utils.query_template import render_kql_file

logger = logging.getLogger(__name__)


@dataclass
class FileRunResult:
    path: Path
    yaml_ok: bool
    render_ok: bool
    exec_ok: bool
    record_count: int
    error: str | None = None


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


def validate_basic_yaml(yaml_data: dict[str, Any]) -> list[str]:
    errors: list[str] = []

    for field in REQUIRED_TOP_LEVEL_FIELDS:
        if field not in yaml_data:
            errors.append(f"Missing required top-level field: {field}")

    kql_value = yaml_data.get("kql")
    if not isinstance(kql_value, str) or not kql_value.strip():
        errors.append("Field 'kql' must be a non-empty string.")

    rule_id = yaml_data.get("id")
    if isinstance(rule_id, str):
        try:
            uuid.UUID(rule_id)
        except (ValueError, AttributeError):
            errors.append("Field 'id' must be a valid UUID string.")
    else:
        errors.append("Field 'id' must be a string UUID.")

    return errors


def discover_query_files(root: Path) -> list[Path]:
    return sorted(root.rglob("*.yaml"))


def ensure_results_path(base_path: Path, query_root: Path, query_file: Path) -> Path:
    relative = query_file.relative_to(query_root)
    target = base_path / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    return target.with_suffix(".csv")


def main() -> None:
    load_dotenv()

    workspace_id = os.getenv("SENTINEL_WORKSPACE_ID")
    if not workspace_id:
        raise ValueError("SENTINEL_WORKSPACE_ID environment variable is not set.")

    repo_root = Path(__file__).resolve().parent.parent
    queries_root = repo_root / "queries"

    # Investigation config determines the investigation folder; default to example-case
    config_env = os.getenv(
        "INVESTIGATION_CONFIG_PATH",
        str(repo_root / "investigations" / "example-case" / "config.yaml"),
    )
    config_path = Path(config_env)

    # Prefer explicit INVESTIGATION_PATH (e.g. investigations/rtbt) if set,
    # otherwise derive from the config file's parent directory.
    investigation_path_env = os.getenv("INVESTIGATION_PATH")
    if investigation_path_env:
        investigation_root = Path(investigation_path_env)
        if not investigation_root.is_absolute():
            investigation_root = repo_root / investigation_root
    else:
        investigation_root = config_path.parent

    results_root = Path(
        os.getenv(
            "INVESTIGATION_RESULTS_PATH",
            investigation_root / "results",
        ),
    )

    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found at {config_path}")

    logger.info("Workspace ID: %s", workspace_id)
    logger.info("Config path: %s", config_path)
    logger.info("Queries root: %s", queries_root)
    logger.info("Results root: %s", results_root)

    config = load_config(str(config_path))

    credential = DefaultAzureCredential()
    client = LogsQueryClient(credential=credential)

    query_files = discover_query_files(queries_root)
    if not query_files:
        logger.warning("No YAML query files found under queries/.")
        return

    logger.info("Discovered %d YAML query files.\n", len(query_files))

    results: list[FileRunResult] = []

    for path in query_files:
        logger.info("=== %s ===", path)
        record_count = 0
        yaml_ok = False
        render_ok = False
        exec_ok = False
        error: str | None = None

        try:
            with path.open("r", encoding="utf-8") as fh:
                yaml_data = yaml.safe_load(fh)

            yaml_errors = validate_basic_yaml(yaml_data or {})
            if yaml_errors:
                logger.error("[YAML CHECK] ❌ FAILED")
                for e in yaml_errors:
                    logger.error("  - %s", e)
                error = "; ".join(yaml_errors)
                results.append(
                    FileRunResult(
                        path=path,
                        yaml_ok=False,
                        render_ok=False,
                        exec_ok=False,
                        record_count=0,
                        error=error,
                    ),
                )
                logger.info("")
                continue

            yaml_ok = True
            logger.info("[YAML CHECK] ✅ PASSED")

            try:
                rendered_query = render_kql_file(str(path), config)
            except Exception as exc:  # noqa: BLE001
                logger.error("[RENDER] ❌ FAILED")
                error = f"Render error: {type(exc).__name__}: {exc}"
                logger.error("  %s", error)
                results.append(
                    FileRunResult(
                        path=path,
                        yaml_ok=yaml_ok,
                        render_ok=False,
                        exec_ok=False,
                        record_count=0,
                        error=error,
                    ),
                )
                logger.info("")
                continue

            render_ok = True
            logger.info("[RENDER] ✅ SUCCEEDED")

            try:
                df = execute_kql_query(
                    client=client,
                    workspace_id=workspace_id,
                    kql_query=rendered_query,
                )
            except Exception as exc:  # noqa: BLE001
                logger.error("[QUERY EXECUTION] ❌ FAILED")
                error = f"Execution error: {type(exc).__name__}: {exc}"
                logger.error("  %s", error)
                results.append(
                    FileRunResult(
                        path=path,
                        yaml_ok=yaml_ok,
                        render_ok=render_ok,
                        exec_ok=False,
                        record_count=0,
                        error=error,
                    ),
                )
                logger.info("")
                continue

            exec_ok = True
            record_count = len(df.index)
            logger.info("[QUERY EXECUTION] ✅ SUCCEEDED")
            logger.info("[RESULTS] Records returned: %d", record_count)

            results_path = ensure_results_path(results_root, queries_root, path)
            with results_path.open("w", encoding="utf-8", newline="") as fh:
                df.to_csv(fh, index=False)
            logger.info("[EXPORT] ✅ Wrote results to %s", results_path)

            results.append(
                FileRunResult(
                    path=path,
                    yaml_ok=yaml_ok,
                    render_ok=render_ok,
                    exec_ok=exec_ok,
                    record_count=record_count,
                    error=None,
                ),
            )
            logger.info("")

        except Exception as exc:  # noqa: BLE001
            error = f"Unexpected error: {type(exc).__name__}: {exc}"
            logger.error("[FATAL] ❌ UNEXPECTED ERROR")
            logger.exception("  %s", error)
            results.append(
                FileRunResult(
                    path=path,
                    yaml_ok=yaml_ok,
                    render_ok=render_ok,
                    exec_ok=exec_ok,
                    record_count=record_count,
                    error=error,
                ),
            )
            logger.info("")

    # Summary
    total = len(results)
    successes = sum(1 for r in results if r.exec_ok)
    failures = total - successes

    logger.info("=== SUMMARY ===")
    logger.info("Total files processed: %d", total)
    logger.info("Successful executions: %d", successes)
    logger.info("Failed executions: %d", failures)

    if failures:
        logger.info("\nFailures:")
        for r in results:
            if not r.exec_ok:
                logger.error("- %s: %s", r.path, r.error)

    logger.info("\nCompleted at %s", datetime.now().isoformat() + "Z")


if __name__ == "__main__":
    main()
