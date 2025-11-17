# Development Setup Guide

This guide covers the complete development environment setup for the Sentinel Threat Hunting project.

## Prerequisites

- Git
- Python 3.12+
- Visual Studio Code with Dev Containers extension

## Quick Start

### 1. Clone and Open in Dev Container

```bash
git clone https://github.com/kevinflint-cs2/sentinel-threat-hunting.git
cd sentinel-threat-hunting
code .
```

When prompted, click "Reopen in Container" to use the devcontainer configuration.

### 2. Verify Installation

The devcontainer automatically installs Poetry and all dependencies. Verify:

```bash
poetry --version
poetry show
```

### 3. Available Commands

Using Poe the Poet task runner:

```bash
# Validate KQL queries
poe validate

# Run query tests
poe test

# Format code with ruff
poe format

# Lint code
poe lint

# Auto-fix lint issues
poe lint-fix

# Type checking with mypy
poe type-check

# Scan for secrets
poe secrets

# Audit detected secrets
poe secrets-audit

# Start Jupyter Lab
poe notebook

# Run all checks
poe all
```

## Manual Setup (Without Dev Container)

If not using the devcontainer:

### 1. Install Poetry

```bash
curl -sSL https://install.python-poetry.org | python3 -
export PATH="$HOME/.local/bin:$PATH"
```

### 2. Install Dependencies

```bash
poetry install
```

### 3. Activate Virtual Environment

```bash
poetry shell
```

## Project Structure

```
sentinel-threat-hunting/
├── .devcontainer/          # VS Code dev container config
│   └── devcontainer.json
├── .vscode/                # VS Code workspace settings
│   └── settings.json
├── queries/                # KQL hunting queries
├── playbooks/              # Logic App playbooks
├── notebooks/              # Jupyter notebooks
├── tests/                  # Test scripts
├── utils/                  # Helper utilities
├── pyproject.toml          # Poetry configuration
├── .secrets.baseline       # detect-secrets baseline
└── .gitignore
```

## Tools and Configuration

### Poetry (Dependency Management)

**pyproject.toml** contains all dependency and tool configurations:

- **Dependencies**: azure-identity, azure-monitor-query, requests, pandas, matplotlib, plotly
- **Dev Dependencies**: pytest, ruff, mypy, detect-secrets, jupyterlab, poethepoet

Add new dependencies:
```bash
poetry add package-name
poetry add --group dev dev-package-name
```

### Ruff (Linting & Formatting)

Configured in `pyproject.toml`:
- Line length: 100
- Target: Python 3.12
- Auto-format on save (in VS Code)

Manual usage:
```bash
poe format              # Format all files
poe lint                # Check for issues
poe lint-fix            # Auto-fix issues
```

### Mypy (Type Checking)

Configured in `pyproject.toml` with:
- Python version: 3.12
- Check untyped definitions
- Ignore missing imports (for Azure SDK)

Run:
```bash
poe type-check
```

### detect-secrets (Secret Scanning)

Prevents committing sensitive data:
```bash
poe secrets             # Scan for secrets
poe secrets-audit       # Review detected secrets
```

Pre-commit hook (recommended):
```bash
# Add to .git/hooks/pre-commit
#!/bin/bash
poetry run detect-secrets-hook --baseline .secrets.baseline
```

## Jupyter Notebooks

### Start Jupyter Lab

```bash
poe notebook
```

Access at: http://localhost:8888

### Available Notebooks

- **threat-hunting-starter.ipynb**: Interactive threat hunting examples

### Creating New Notebooks

1. Start Jupyter Lab
2. Create new notebook
3. Use Python 3.12 kernel (automatically configured by Poetry)
4. Import Azure SDK packages as needed

## Azure Authentication

### For Local Development

1. Install Azure CLI:
   ```bash
   curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash
   ```

2. Login:
   ```bash
   az login
   ```

3. Set workspace ID:
   ```bash
   export SENTINEL_WORKSPACE_ID="your-workspace-id"
   export AZURE_TENANT_ID="your-tenant-id"
   ```

### In Python/Notebooks

```python
from azure.identity import DefaultAzureCredential, AzureCliCredential
from azure.monitor.query import LogsQueryClient

# Use Azure CLI credentials
credential = AzureCliCredential()
client = LogsQueryClient(credential)
```

## Testing

### Run All Tests

```bash
poe test
```

### Run Specific Test

```bash
poetry run python tests/test_queries.py
poetry run python tests/validate_kql.py
```

### Run with pytest

```bash
poetry run pytest tests/ -v
poetry run pytest tests/ --cov=tests
```

## VS Code Extensions

The devcontainer automatically installs:

- **ms-python.python**: Python support
- **ms-python.vscode-pylance**: Python language server
- **ms-toolsai.jupyter**: Jupyter notebook support
- **charliermarsh.ruff**: Ruff linter/formatter
- **Yelp.detect-secrets**: Secret detection
- **ms-azuretools.vscode-azureresourcegroups**: Azure resources
- **ms-azuretools.vscode-azurelogicapps**: Logic Apps support

## Common Workflows

### Adding a New Query

1. Create query in `queries/new-query.kql`
2. Validate syntax: `poe validate`
3. Test execution: `poe test`
4. Commit changes

### Creating a Detection Rule

1. Develop query in notebook
2. Test against workspace
3. Convert to query file
4. Document in `detections/README.md`

### Running a Threat Hunt

1. Open `notebooks/threat-hunting-starter.ipynb`
2. Configure workspace ID
3. Run hunt queries
4. Export findings to `docs/hunt-results/`
5. Document in hunt report

## Troubleshooting

### Poetry Issues

**"No module named 'poetry'"**
```bash
export PATH="$HOME/.local/bin:$PATH"
```

**"Lock file out of sync"**
```bash
poetry lock --no-update
poetry install
```

### Azure Authentication

**"No credentials available"**
```bash
az login
az account set --subscription "your-subscription-id"
```

**"Workspace not found"**
- Verify workspace ID is correct
- Ensure you have Reader role on workspace

### Jupyter Issues

**"Kernel not found"**
```bash
poetry run python -m ipykernel install --user --name sentinel-hunting
```

**"Port already in use"**
```bash
# Use different port
poetry run jupyter lab --port 8889
```

## Best Practices

### Code Quality

- Always run `poe all` before committing
- Fix linting issues before pushing
- Add type hints to functions
- Document complex logic

### Security

- Never commit credentials or secrets
- Use environment variables for sensitive data
- Run `poe secrets` regularly
- Audit baseline periodically

### Query Development

- Start with small time ranges for testing
- Document hunt hypothesis and findings
- Include MITRE ATT&CK mappings
- Test queries before creating rules

### Version Control

- Clear notebook outputs before committing
- Use descriptive commit messages
- Reference issue numbers in commits
- Keep commits focused and atomic

## Additional Resources

- [Poetry Documentation](https://python-poetry.org/docs/)
- [Ruff Documentation](https://docs.astral.sh/ruff/)
- [Mypy Documentation](https://mypy.readthedocs.io/)
- [Azure Monitor Query SDK](https://docs.microsoft.com/python/api/azure-monitor-query/)
- [Jupyter Lab Documentation](https://jupyterlab.readthedocs.io/)

## Support

For issues or questions:
1. Check this guide
2. Review project README
3. Open GitHub issue
4. Contact project maintainer
