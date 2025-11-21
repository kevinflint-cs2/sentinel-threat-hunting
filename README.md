---
post_title: "Microsoft Sentinel Threat Hunting — AI-Assisted Query Creation"
author1: "Kevin Flint"
post_slug: "sentinel-threat-hunting"
microsoft_alias: "kevfli02"
featured_image: ""
categories: ["Security", "Threat Hunting", "Azure Sentinel"]
tags: ["KQL", "AI", "Threat Hunting", "Automation"]
ai_note: "AI used for README and query creation guidance"
summary: "AI-assisted platform for creating, testing, and analyzing Microsoft Sentinel KQL queries with investigation-driven workflows."
post_date: "2025-11-21"
---

## Microsoft Sentinel Threat Hunting — AI-Assisted Query Creation

### Overview

This repository provides a streamlined, investigation-driven workflow for security analysts to create, test, and analyze KQL queries for Microsoft Sentinel. Leveraging AI prompts and automation, it enables rapid development and validation of queries tailored to specific investigations.

#### Key Features

- **AI-Powered Query Creation:** Use `.github/prompts` to guide KQL query design and refinement.
- **Investigation Workflow:** Organize investigations in dedicated folders with configuration files.
- **Automated Query Testing:** Validate queries using `utils/test_query_file.py` and batch test with `utils/hailmary_runner.py`.
- **Configurable Environment:** Easily set investigation parameters and environment variables for reproducible results.

### Repository Structure

| Folder/File         | Purpose                                                      |
|---------------------|-------------------------------------------------------------|
| `.github/prompts/`  | AI prompt files for query creation and workflow guidance     |
| `queries/`          | KQL query templates and examples                            |
| `utils/`            | Python utilities for query rendering, testing, and automation|
| `investigations/`   | Investigation folders with config files                      |
| `tests/`            | Test scripts and fixtures                                   |
| `README.md`         | Project documentation                                       |

### Quick Start

#### Prerequisites

- Azure Subscription with Microsoft Sentinel enabled
- Log Analytics workspace configured
- Python 3.12+ and [Poetry](https://python-poetry.org/) installed

#### 1. Clone and Install

```bash
git clone https://github.com/kevinflint-cs2/sentinel-threat-hunting.git
cd sentinel-threat-hunting
poetry install
```

#### 2. Create a New Investigation

```bash
mkdir investigations/newinvestigation
cp investigations/example-case/config.yaml investigations/newinvestigation/config.yaml
# Edit config.yaml with investigation parameters
```

#### 3. Set Environment Variables

Create a `.env` file or set variables in your shell for investigation context.

#### 4. Use Prompts for Query Creation

- Review and use `.github/prompts` for AI-assisted KQL query design.
- Generate or refine queries in `queries/` using your config.

#### 5. Test Queries

```bash
poetry run python utils/test_query_file.py queries/analysis/xdr/process_chain_analysis.yaml investigations/newinvestigation/config.yaml
```

#### 6. Batch Test All Queries

```bash
poetry run python utils/hailmary_runner.py investigations/newinvestigation/config.yaml
```

### Example Workflow

1. Create a new investigation folder and config file.
2. Set environment variables for your investigation.
3. Use AI prompts to assist in KQL query creation.
4. Test individual queries with `test_query_file.py`.
5. Run all tests with `hailmary_runner.py` for comprehensive validation.

### Best Practices

- Use dedicated investigation folders for each case.
- Keep config files up to date with relevant parameters.
- Leverage AI prompts for efficient query development.
- Validate all queries before use in Sentinel.

### Additional Resources

- [Poetry Documentation](https://python-poetry.org/docs/)
- [Microsoft Sentinel Documentation](https://docs.microsoft.com/azure/sentinel/)
- [KQL Language Reference](https://docs.microsoft.com/azure/data-explorer/kusto/query/)

