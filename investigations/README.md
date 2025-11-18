# Investigation Configurations

This directory contains investigation-specific configuration files and data. Each investigation should be organized in its own subdirectory.

## Overview

The investigation system uses YAML configuration files to define variables that are automatically substituted into KQL query templates. This allows you to run the same queries across different investigations by simply changing the configuration.

## Directory Structure

```
investigations/
├── README.md                 # This file
├── example-case/             # Example investigation
│   └── config.yaml           # Configuration for example case
└── your-investigation/       # Your investigation folder
    └── config.yaml           # Your configuration
```

## Creating a New Investigation

1. **Create a new folder** for your investigation:
   ```powershell
   mkdir investigations/case-2025-001
   ```

2. **Copy the example config** as a template:
   ```powershell
   Copy-Item investigations/example-case/config.yaml investigations/case-2025-001/config.yaml
   ```

3. **Edit the config** with your investigation-specific values:
   - Update device names, usernames, IP addresses, etc.
   - Set the appropriate time range for your investigation
   - Fill in any threat indicators or IOCs

4. **Use the config** in your Python scripts or notebooks:
   ```python
   from utils.config_loader import load_config
   from utils.query_template import render_kql_file
   
   # Load your investigation config
   config = load_config("investigations/case-2025-001/config.yaml")
   
   # Render a query with your variables
   query = render_kql_file("queries/lateral-movement.kql", config)
   ```

## Configuration File Format

Configuration files are written in YAML format with the following structure:

```yaml
# Investigation metadata (optional - for documentation)
investigation_name: "Lateral Movement Investigation"
investigator: "Security Analyst Name"
created_date: "2025-11-17"

# Time range for queries
start_time: "2025-11-01T00:00:00Z"
end_time: "2025-11-17T23:59:59Z"

# Entity identifiers
devicename: "DESKTOP-ABC123"
username: "john.doe"
ip_address: "192.168.1.100"
domain: "contoso.com"

# Process information
process_name: "powershell.exe"
parent_process: "cmd.exe"
file_path: "C:\\Windows\\System32\\suspicious.exe"

# Threat indicators
suspicious_hash: "abc123def456..."
known_bad_ip: "10.0.0.1"
```

## Variable Naming Conventions

- Use lowercase with underscores: `device_name`, `start_time`
- Be descriptive: `suspicious_hash` not just `hash`
- Keep names consistent across investigations
- Use empty string `""` for optional variables you don't need

## Available Variables

Current supported variables include:

| Variable | Description | Example |
|----------|-------------|---------|
| `devicename` | Device/computer name | `"DESKTOP-ABC123"` |
| `username` | User account name | `"john.doe"` |
| `ip_address` | IP address | `"192.168.1.100"` |
| `domain` | Domain name | `"contoso.com"` |
| `start_time` | Investigation start time (ISO 8601) | `"2025-11-01T00:00:00Z"` |
| `end_time` | Investigation end time (ISO 8601) | `"2025-11-17T23:59:59Z"` |
| `process_name` | Process/executable name | `"powershell.exe"` |
| `parent_process` | Parent process name | `"cmd.exe"` |
| `file_path` | File path | `"C:\\Windows\\System32\\file.exe"` |
| `suspicious_hash` | File hash (MD5/SHA1/SHA256) | `"abc123def456..."` |
| `known_bad_ip` | Known malicious IP | `"10.0.0.1"` |

## Using Configs in KQL Queries

KQL query files can reference config variables using Jinja2 syntax:

```kql
DeviceNetworkEvents
| where DeviceName == "{{ devicename }}"
| where InitiatingProcessAccountName == "{{ username }}"
| where Timestamp between (datetime({{ start_time }}) .. datetime({{ end_time }}))
```

## Complete Workflow Example

```python
# Import required modules
from utils.config_loader import load_config
from utils.query_template import render_kql_file
from utils.kql_query import execute_kql_query
from azure.identity import DefaultAzureCredential
from azure.monitor.query import LogsQueryClient
import os

# 1. Load investigation config
config = load_config("investigations/case-2025-001/config.yaml")

# 2. Render KQL query with variables
query = render_kql_file("queries/lateral-movement.kql", config)

# 3. Setup Azure connection
credential = DefaultAzureCredential()
client = LogsQueryClient(credential=credential)
workspace_id = os.getenv("SENTINEL_WORKSPACE_ID")

# 4. Execute query and get results
df = execute_kql_query(client, workspace_id, query)

# 5. Analyze results
print(f"Found {len(df)} events")
df.head()
```

## Best Practices

1. **One config per investigation** - Keep each investigation isolated
2. **Document your variables** - Add comments in your config explaining values
3. **Use version control** - Configs are automatically excluded from git
4. **Validate configs** - Test with small queries before running large ones
5. **Keep metadata** - Include investigator name, date, and case description

## Troubleshooting

### Missing Variables Error
```
jinja2.UndefinedError: 'devicename' is undefined
```
**Solution:** Add the missing variable to your config.yaml file.

### Config File Not Found
```
FileNotFoundError: Configuration file not found
```
**Solution:** Check the path to your config file is correct.

### Invalid YAML Syntax
```
yaml.YAMLError: Invalid YAML in configuration file
```
**Solution:** Validate your YAML syntax. Common issues:
- Inconsistent indentation
- Missing quotes around special characters
- Incorrect structure

## Privacy and Security

**Important:** Investigation config files are automatically excluded from git by `.gitignore`. They contain sensitive investigation data and should never be committed to version control.

The `.gitignore` rule `investigations/*/` ensures all subdirectories in investigations are ignored while allowing this README to be tracked.

## Adding New Variables

When you need a new variable:

1. Add it to your `config.yaml`
2. Use it in your KQL queries with `{{ variable_name }}`
3. Consider updating `tests/fixtures/test_config.yaml` if contributing to the project
4. Document it in this README's Available Variables table

## Support

For questions or issues with the configuration system:
- Check the test files in `tests/` for examples
- Review the Python modules in `utils/`
- Examine the example config in `investigations/example-case/`
