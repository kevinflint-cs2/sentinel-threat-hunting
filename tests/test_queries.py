#!/usr/bin/env python3
"""
KQL Query Test Runner
Tests KQL queries against sample data or Sentinel workspace
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path


class KQLTester:
    def __init__(self, workspace_id: str | None = None, tenant_id: str | None = None):
        self.workspace_id = workspace_id
        self.tenant_id = tenant_id
        self.token = None

    def authenticate(self):
        """Authenticate to Azure using managed identity or service principal"""
        if not self.workspace_id or not self.tenant_id:
            return False

        # This would use Azure authentication in production
        # For now, just check if credentials are available
        return False

    def test_query_syntax(self, query: str) -> dict:
        """Test query syntax without execution"""
        result: dict = {
            "syntax_valid": True,
            "has_time_filter": "TimeGenerated > ago(" in query,
            "has_summarize": "summarize" in query.lower(),
            "has_project": "project" in query.lower(),
            "line_count": len(query.split("\n")),
            "error": "",
        }

        # Basic syntax checks
        if query.count("(") != query.count(")"):
            result["syntax_valid"] = False
            result["error"] = "Unmatched parentheses"

        if query.count("|") == 0:
            result["syntax_valid"] = False
            result["error"] = "No pipe operators found"

        return result

    def execute_query(self, query: str) -> dict:
        """Execute query against Sentinel workspace (placeholder)"""
        if not self.token:
            return {"executed": False, "error": "Not authenticated to workspace"}

        # In production, this would call the Log Analytics API
        # POST https://api.loganalytics.io/v1/workspaces/{workspaceId}/query
        return {
            "executed": True,
            "row_count": 0,
            "execution_time_ms": 0,
            "note": "Execution against live workspace would occur here",
        }

    def test_query_file(self, filepath: Path) -> dict:
        """Test all queries in a file"""

        with open(filepath, encoding="utf-8") as f:
            content = f.read()

        # Extract queries
        queries = self._extract_queries(content)

        passed_count = 0
        failed_count = 0
        query_results: list[dict] = []

        for idx, query in enumerate(queries, 1):
            test_result = self.test_query_syntax(query)

            if test_result["syntax_valid"]:
                passed_count += 1
            else:
                failed_count += 1

            query_results.append({"query_number": idx, "result": test_result})

        results = {
            "file": filepath.name,
            "total_queries": len(queries),
            "passed": passed_count,
            "failed": failed_count,
            "query_results": query_results,
        }

        return results

    def _extract_queries(self, content: str) -> list[str]:
        """Extract KQL queries from file"""
        # Remove comment blocks
        content = "\n".join(
            [line for line in content.split("\n") if not line.strip().startswith("//")]
        )

        # Split on common patterns
        queries = []
        current_query = []

        for line in content.split("\n"):
            line = line.strip()
            if line:
                current_query.append(line)
            elif current_query and any(
                kw in " ".join(current_query).lower() for kw in ["where", "summarize", "project"]
            ):
                queries.append("\n".join(current_query))
                current_query = []

        if current_query:
            queries.append("\n".join(current_query))

        return [q for q in queries if len(q) > 50]  # Filter out fragments


def main():
    """Main test runner"""
    workspace_id = os.getenv("SENTINEL_WORKSPACE_ID")
    tenant_id = os.getenv("AZURE_TENANT_ID")

    query_dir = Path(__file__).parent.parent / "queries"

    if not query_dir.exists():
        sys.exit(1)

    tester = KQLTester(workspace_id, tenant_id)
    tester.authenticate()

    all_results = []
    total_passed = 0
    total_failed = 0

    for kql_file in sorted(query_dir.glob("*.kql")):
        results = tester.test_query_file(kql_file)
        all_results.append(results)
        total_passed += results["passed"]
        total_failed += results["failed"]

    # Summary

    for result in all_results:
        "✅" if result["failed"] == 0 else "❌"

    # Save results
    results_file = Path(__file__).parent / "test-results.json"
    with open(results_file, "w") as f:
        json.dump(
            {
                "timestamp": datetime.now().isoformat(),
                "total_passed": total_passed,
                "total_failed": total_failed,
                "results": all_results,
            },
            f,
            indent=2,
        )

    sys.exit(0 if total_failed == 0 else 1)


if __name__ == "__main__":
    main()
