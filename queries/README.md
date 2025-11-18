# Threat Hunting Queries

KQL queries for threat hunting across multiple platforms, organized by MITRE ATT&CK framework and analysis categories. All queries support template variables for investigation-specific customization.

## Key Features

- **MITRE ATT&CK Organized** - Queries structured by tactic and technique for comprehensive coverage tracking
- **Multi-Platform Support** - Detections for XDR, Azure, AWS, GCP, and cross-platform scenarios
- **Template Variables** - All queries use YAML config files for investigation-specific customization
- **Standardized Format** - Consistent headers, documentation, and naming conventions
- **Analysis Queries** - Baseline, noise reduction, and anomaly detection queries separate from MITRE detections

## Directory Structure

```
queries/
├── mitre/                      # MITRE ATT&CK organized queries
│   ├── initial-access/
│   ├── execution/
│   ├── persistence/
│   ├── privilege-escalation/
│   ├── defense-evasion/
│   ├── credential-access/
│   ├── discovery/
│   ├── lateral-movement/
│   ├── collection/
│   ├── command-and-control/
│   ├── exfiltration/
│   └── impact/
├── analysis/                   # Non-MITRE analysis queries
│   ├── azure/
│   ├── aws/
│   └── xdr/
├── cross-platform/             # Multi-platform correlation queries
└── _templates/                 # Query templates for new detections
```

## Naming Conventions

### MITRE Query Pattern
```
queries/mitre/<tactic>/<technique-id>/<platform>-<descriptive-name>.kql
```

**Examples:**
- `queries/mitre/lateral-movement/T1021/xdr-remote-services.kql`
- `queries/mitre/initial-access/T1078/azure-valid-accounts-mfa-bypass.kql`
- `queries/mitre/persistence/T1053/aws-scheduled-tasks.kql`

### Analysis Query Pattern
```
queries/analysis/<platform>/<descriptive-name>.kql
```

**Examples:**
- `queries/analysis/azure/baseline-signin-activity.kql`
- `queries/analysis/xdr/process-baseline.kql`
- `queries/analysis/aws/cloudtrail-noise-reduction.kql`

### Platform Prefixes
- `xdr-` - Microsoft Defender XDR tables (DeviceEvents, DeviceNetworkEvents, etc.)
- `azure-` - Azure/Microsoft 365 logs (SigninLogs, AuditLogs, etc.)
- `aws-` - AWS CloudTrail and related services
- `gcp-` - Google Cloud Platform logs
- `multi-` - Cross-platform correlation queries

## Query Template Variables

All queries support template variables via YAML configuration files. Variables are substituted using Jinja2 syntax.

### Common Variables
- `devicename` - Target device/computer name
- `username` - User account name
- `start_time` - Investigation start time (ISO 8601 format)
- `end_time` - Investigation end time (ISO 8601 format)
- `ip_address` - IP address of interest
- `domain` - Domain name
- `process_name` - Process/executable name
- `file_path` - File system path
- `suspicious_hash` - File hash (MD5/SHA1/SHA256)

### Using Variables in Queries
```kql
SecurityEvent
| where TimeGenerated between (datetime({{ start_time }}) .. datetime({{ end_time }}))
| where Computer has "{{ devicename }}"
| where Account has "{{ username }}"
```

## Using Queries

### Quick Start

**Render a query with default config:**
```powershell
poe render queries/mitre/lateral-movement/T1021/xdr-remote-services.kql
```

**Render with custom investigation config:**
```powershell
poe render queries/mitre/lateral-movement/T1021/xdr-remote-services.kql -c investigations/my-case/config.yaml
```

**Show required variables:**
```powershell
poe render queries/mitre/lateral-movement/T1021/xdr-remote-services.kql --show-variables
```

### Programmatic Usage

```python
from utils.config_loader import load_config
from utils.query_template import render_kql_file
from utils.kql_query import execute_kql_query
from azure.identity import DefaultAzureCredential
from azure.monitor.query import LogsQueryClient
import os

# Load investigation config
config = load_config("investigations/case-001/config.yaml")

# Render query with variables
query = render_kql_file("queries/mitre/lateral-movement/T1021/xdr-remote-services.kql", config)

# Execute against Sentinel workspace
credential = DefaultAzureCredential()
client = LogsQueryClient(credential=credential)
workspace_id = os.getenv("SENTINEL_WORKSPACE_ID")

df = execute_kql_query(client, workspace_id, query)
```

## MITRE ATT&CK Coverage

### TA0001 - Initial Access
| Technique | Description | Queries |
|-----------|-------------|---------|
| Coming soon | | |

### TA0002 - Execution
| Technique | Description | Queries |
|-----------|-------------|---------|
| Coming soon | | |

### TA0003 - Persistence
| Technique | Description | Queries |
|-----------|-------------|---------|
| Multiple | Various persistence techniques | `persistence.kql` |

### TA0004 - Privilege Escalation
| Technique | Description | Queries |
|-----------|-------------|---------|
| Multiple | Various privilege escalation techniques | `privilege-escalation.kql` |

### TA0005 - Defense Evasion
| Technique | Description | Queries |
|-----------|-------------|---------|
| Coming soon | | |

### TA0006 - Credential Access
| Technique | Description | Queries |
|-----------|-------------|---------|
| Multiple | Credential dumping, brute force | `credential-access.kql` |

### TA0007 - Discovery
| Technique | Description | Queries |
|-----------|-------------|---------|
| Coming soon | | |

### TA0008 - Lateral Movement
| Technique | Description | Queries |
|-----------|-------------|---------|
| T1021 | Remote Services (RDP, SMB, WMI, PSExec) | `T1021/xdr-remote-services.kql` |

### TA0009 - Collection
| Technique | Description | Queries |
|-----------|-------------|---------|
| Coming soon | | |

### TA0010 - Command and Control
| Technique | Description | Queries |
|-----------|-------------|---------|
| Multiple | C2 communication detection | `command-and-control.kql` |

### TA0011 - Exfiltration
| Technique | Description | Queries |
|-----------|-------------|---------|
| Multiple | Data exfiltration detection | `exfiltration/data-exfiltration.kql` |

### TA0040 - Impact
| Technique | Description | Queries |
|-----------|-------------|---------|
| Coming soon | | |

---

## Query Template Variables

All queries support template variables via YAML configuration files. See `investigations/README.md` for details.

### Common Variables
- `devicename` - Target device/computer name
- `username` - User account name
- `start_time` - Investigation start time (ISO 8601)
- `end_time` - Investigation end time (ISO 8601)
- `ip_address` - IP address of interest
- `domain` - Domain name
- `process_name` - Process/executable name
- `file_path` - File system path
- `suspicious_hash` - File hash (MD5/SHA1/SHA256)

---

## Using Queries

### 1. Direct Execution (after rendering)
```powershell
# Render query with config
poe render queries/mitre/lateral-movement/T1021/xdr-remote-services.kql -c investigations/my-case/config.yaml

# Copy output and paste into Sentinel/Advanced Hunting
```

### 2. Programmatic Execution
```python
from utils.config_loader import load_config
from utils.query_template import render_kql_file
from utils.kql_query import execute_kql_query

# Load config and render
config = load_config("investigations/case-001/config.yaml")
query = render_kql_file("queries/mitre/lateral-movement/T1021/xdr-remote-services.kql", config)

# Execute against workspace
df = execute_kql_query(client, workspace_id, query)
```

## Adding New Queries

### For MITRE ATT&CK Queries

**Step 1:** Identify the MITRE tactic and technique
- Reference: [MITRE ATT&CK Framework](https://attack.mitre.org/)

**Step 2:** Create the directory structure
```powershell
New-Item -ItemType Directory -Path "queries/mitre/<tactic>/<technique-id>" -Force
```

**Step 3:** Copy the template
```powershell
Copy-Item queries/_templates/mitre-technique-template.kql queries/mitre/<tactic>/<technique-id>/<platform>-<name>.kql
```

**Step 4:** Customize the query
- Update header with technique details
- Implement detection logic
- Add template variables using `{{ variable_name }}` syntax
- Document required and optional variables
- Test with example config

**Step 5:** Update coverage matrix in this README

### For Analysis Queries

**Step 1:** Choose the appropriate platform folder
```
queries/analysis/<platform>/
```

**Step 2:** Create descriptive filename
- Examples: `baseline-activity.kql`, `noise-reduction.kql`, `anomaly-detection.kql`

**Step 3:** Document the analysis purpose
- What baseline or pattern are you establishing?
- What noise are you filtering?
- What anomalies are you detecting?

**Step 4:** Use template variables where appropriate
- Makes queries reusable across investigations

## Query Standards
Always include a header with:
```kql
// ============================================================================
// [Query Name]
// ============================================================================
// Description: [What this query detects]
// Data Sources: [Tables used]
// MITRE ATT&CK: [Technique IDs]
// Template Variables:
//   Required: variable1, variable2
//   Optional: variable3, variable4
// ============================================================================
```

### Template Variables
- Always document required vs optional variables
- Use descriptive variable names
- Provide examples in comments
- Test queries with the example config

### Performance
- Use time ranges to limit data scanned
- Filter early in the query pipeline
- Use `has` instead of `contains` when possible
- Comment on expected result sizes

### Testing
- Test with example config before committing
- Verify query syntax with `poe render`
- Run against test data when possible
- Document false positive scenarios

---

## Platform-Specific Notes

### Microsoft Defender XDR (xdr-)
- Primary tables: DeviceEvents, DeviceNetworkEvents, DeviceProcessEvents, DeviceFileEvents
- Time column: `Timestamp`
- Device identifier: `DeviceName`

### Azure/Microsoft 365 (azure-)
- Primary tables: SigninLogs, AuditLogs, AADNonInteractiveUserSignInLogs
- Time column: `TimeGenerated`
- Identity identifier: `UserPrincipalName`

### AWS CloudTrail (aws-)
- Primary tables: AWSCloudTrail
- Time column: `TimeGenerated`
- Identity identifier: `UserIdentityArn`, `UserIdentityUserName`

---

## Resources

- [MITRE ATT&CK Framework](https://attack.mitre.org/)
- [KQL Reference](https://learn.microsoft.com/en-us/azure/data-explorer/kusto/query/)
- [Microsoft Sentinel Documentation](https://learn.microsoft.com/en-us/azure/sentinel/)
- [Project Investigations Guide](../investigations/README.md)
