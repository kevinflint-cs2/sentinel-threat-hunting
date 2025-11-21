# Microsoft Sentinel Threat Hunting Repository

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![KQL](https://img.shields.io/badge/KQL-Queries-orange.svg)
![Sentinel](https://img.shields.io/badge/Microsoft-Sentinel-blue.svg)

A comprehensive collection of reusable Microsoft Sentinel threat hunting KQL queries, automation playbooks, and detection rules. Focused on high-signal detections, pivot queries, enrichment joins, and repeatable hunting patterns to help security analysts investigate faster, document hunts, and standardize advanced detections across environments and teams.

## 🎯 Purpose

This repository provides:
- **Production-Ready KQL Queries**: Tested hunting queries for common attack patterns
- **Automated Response Playbooks**: Logic Apps for incident enrichment and response
- **Testing Framework**: Validation tools for query quality assurance
- **Documentation**: Comprehensive guides for deployment and customization

## 📁 Repository Structure

```
sentinel-threat-hunting/
├── queries/                    # KQL hunting queries organized by MITRE ATT&CK
│   ├── analysis/              # Analysis queries for threat hunting
│   │   └── xdr/              # XDR-specific queries
│   ├── mitre/                # MITRE ATT&CK organized queries
│   ├── untested/             # Queries pending validation
│   └── README.md
├── playbooks/                  # Logic App automation playbooks
│   ├── ip-enrichment-playbook.json
│   ├── host-isolation-playbook.json
│   └── README.md
├── investigations/             # Investigation case files
│   ├── example-case/         # Example investigation configuration
│   │   └── config.yaml       # Investigation variables and parameters
│   └── README.md
├── detections/                 # Scheduled analytics rules
├── tests/                      # Testing and validation tools
│   ├── validate_kql.py
│   ├── test_queries.py
│   └── README.md
├── utils/                      # Helper scripts and utilities
│   ├── config_loader.py      # YAML configuration loader
│   ├── query_template.py     # KQL template renderer
│   ├── render_query.py       # CLI tool for rendering queries
│   └── kql_query.py          # KQL query execution
└── README.md
```

## 🚀 Quick Start

### Prerequisites
- Azure Subscription with Microsoft Sentinel enabled
- Log Analytics workspace configured
- Appropriate data connectors enabled (SecurityEvent, CommonSecurityLog, etc.)
- Python 3.12+ (for query rendering and utilities)
- Poetry (Python dependency management)

### 1. Setup Environment

```bash
# Clone repository
git clone https://github.com/kevinflint-cs2/sentinel-threat-hunting.git
cd sentinel-threat-hunting

# Install Python dependencies
poetry install
```

### 2. Configure Investigation Variables

Create an investigation configuration file with your search parameters:

```yaml
# investigations/my-case/config.yaml
investigation_name: "Suspicious Activity Investigation"
investigator: "Security Analyst"
created_date: "2025-11-19"

# Time range for queries
start_time: "2025-11-17T00:00:00Z"
end_time: "2025-11-19T23:59:59Z"

# Entity identifiers
device_name: "LAPTOP-ABC123"
user_name: "john.doe"
ip_address: "192.168.1.100"
domain: "contoso.com"

# Process information
process_name: "powershell.exe"
parent_process: "cmd.exe"
file_path: "C:\\Users\\john.doe\\suspicious.exe"

# Threat indicators
suspicious_hash: "abc123def456..."
known_bad_ip: "10.0.0.1"
```

### 3. Render Queries with Investigation Variables

Use the query rendering tool to substitute your investigation parameters into query templates:

```bash
# Render a query with your investigation config
poetry run poe render queries/analysis/xdr/process_chain_analysis.yaml -c investigations/my-case/config.yaml

# Show required variables for a query
poetry run poe render queries/analysis/xdr/process_chain_analysis.yaml --show-variables

# Or use Python directly
poetry run python utils/render_query.py queries/analysis/xdr/process_chain_analysis.yaml -c investigations/my-case/config.yaml
```

**Example Output:**
```
======================================================================
QUERY METADATA:
======================================================================
Title: Process Chain Analysis
ID: 69e64f51-d680-4870-9b0a-d32ddf242c87
Author: Kevin Flint
Status: test
Level: low
Tags: attack.execution, attack.defense-evasion, attack.t1055

Description:
  Analyzes process execution chains for a specific user and/or device...

Log Source:
  Product: windows
  Table: DeviceProcessEvents
  Category: process_creation
======================================================================

RENDERED KQL QUERY:
======================================================================
DeviceProcessEvents
| where TimeGenerated between (2025-11-17T00:00:00Z .. 2025-11-19T23:59:59Z)
| where DeviceName contains "LAPTOP-ABC123"
| where AccountName contains "john.doe"
| extend Combined = strcat_delim(":", AccountName, InitiatingProcessParentFileName, ...)
| summarize Count=count(), LastExecutionTime=max(Timestamp) by AccountName, ...
| sort by Count desc
======================================================================
```

### 4. Deploy Queries

**Option A: Manual Import**
```bash
# Clone repository
git clone https://github.com/kevinflint-cs2/sentinel-threat-hunting.git
cd sentinel-threat-hunting

# Import queries to Sentinel
# Navigate to Sentinel → Hunting → Queries → Import
```

**Option B: Automated Deployment**
```bash
# Deploy all queries using Azure CLI
az monitor log-analytics query pack create \
  --resource-group <resource-group> \
  --query-pack-name "ThreatHuntingQueries" \
  --location <location>

# Import queries from directory
for file in queries/*.kql; do
  az monitor log-analytics query pack query create \
    --query-pack-name "ThreatHuntingQueries" \
    --query-name $(basename $file .kql) \
    --query-body "$(cat $file)"
done
```

### 2. Deploy Playbooks

```bash
# Deploy IP enrichment playbook
az deployment group create \
  --resource-group <resource-group> \
  --template-file playbooks/ip-enrichment-playbook.json \
  --parameters PlaybookName=EnrichIPWithThreatIntel \
               SentinelWorkspaceId=<workspace-id>

# Deploy host isolation playbook
az deployment group create \
  --resource-group <resource-group> \
  --template-file playbooks/host-isolation-playbook.json \
  --parameters PlaybookName=IsolateCompromisedHost \
               DefenderEndpointResourceId=<defender-resource-id>
```

### 3. Validate Queries

```bash
# Install Python dependencies
pip install requests

# Run validation
python tests/validate_kql.py

# Run tests
python tests/test_queries.py
```

## 📊 Query Template System

### YAML Query Format

Queries are stored as YAML files with metadata and parameterized KQL templates:

```yaml
title: Process Chain Analysis
id: 69e64f51-d680-4870-9b0a-d32ddf242c87
status: test
description: Analyzes process execution chains for a specific user and/or device
author: Security Analyst
date: '2025-11-19'
modified: '2025-11-19'
tags:
  - attack.execution
  - attack.defense-evasion
  - attack.t1055
logsource:
  product: windows
  table: DeviceProcessEvents
  category: process_creation
kql: |
  DeviceProcessEvents
  | where TimeGenerated between ({{ start_time }} .. {{ end_time }})
  {% if device_name %}| where DeviceName contains "{{ device_name }}"
  {% endif %}{% if user_name %}| where AccountName contains "{{ user_name }}"
  {% endif %}| project Timestamp, DeviceName, AccountName, FileName
falsepositives:
  - Legitimate administrative activity
  - Software installations
level: medium
```

### Variable Templating

Queries support Jinja2 template variables for dynamic parameter substitution:

**Available Variables:**
- `device_name`: Target device/hostname
- `user_name`: User account name
- `ip_address`: IP address for filtering
- `domain`: Domain name
- `start_time`: Query start time (ISO format)
- `end_time`: Query end time (ISO format)
- `process_name`: Process executable name
- `parent_process`: Parent process name
- `file_path`: File path for filtering
- `suspicious_hash`: File hash indicator
- `known_bad_ip`: Known malicious IP

**Template Features:**
```jinja2
{# Simple variable substitution #}
| where DeviceName == "{{ device_name }}"

{# Conditional filtering (optional parameters) #}
{% if user_name %}| where AccountName contains "{{ user_name }}"
{% endif %}

{# Time range filtering #}
| where TimeGenerated between ({{ start_time }} .. {{ end_time }})
```

### CLI Usage

**Render a query:**
```bash
poe render <query_file.yaml> -c <config.yaml>
```

**Show required variables:**
```bash
poe render <query_file.yaml> --show-variables
```

**Examples:**
```bash
# Render process chain analysis
poe render queries/analysis/xdr/process_chain_analysis.yaml -c investigations/my-case/config.yaml

# Check what variables a query needs
poe render queries/analysis/xdr/process_chain_analysis.yaml --show-variables
```

## 📊 Query Categories

### Lateral Movement Detection
**File**: `queries/lateral-movement.kql`

Detects:
- ✅ Suspicious RDP connections from unusual sources
- ✅ SMB lateral movement via admin shares
- ✅ Pass-the-hash attacks
- ✅ PSExec and remote service creation
- ✅ WMI remote execution
- ✅ Brute force followed by successful logon

**Sample Query**:
```kql
// Suspicious RDP Connections from Unusual Sources
let knownAdminSources = dynamic(["10.0.1.10", "10.0.1.11"]);
SecurityEvent
| where TimeGenerated > ago(7d)
| where EventID == 4624
| where LogonType == 10
| where IpAddress !in (knownAdminSources)
| summarize ConnectionCount = count() by Account, IpAddress, Computer
| where ConnectionCount > 2
| order by ConnectionCount desc
```

### Privilege Escalation Detection
**File**: `queries/privilege-escalation.kql`

Detects:
- ✅ User additions to privileged groups
- ✅ Suspicious service creation with SYSTEM privileges
- ✅ UAC bypass attempts
- ✅ Scheduled task creation by non-admin users
- ✅ SeDebugPrivilege usage
- ✅ Token manipulation

### Persistence Detection
**File**: `queries/persistence.kql`

Detects:
- ✅ Registry run key modifications
- ✅ Scheduled task persistence
- ✅ WMI event subscriptions
- ✅ Startup folder modifications
- ✅ Service creation for persistence
- ✅ DLL hijacking attempts

### Command & Control Detection
**File**: `queries/command-and-control.kql`

Detects:
- ✅ Beaconing patterns (regular network connections)
- ✅ DNS tunneling
- ✅ Connections to rare destinations
- ✅ Non-standard port usage
- ✅ Long connection durations
- ✅ TOR/Proxy usage
- ✅ Domain Generation Algorithm (DGA) patterns

### Credential Access Detection
**File**: `queries/credential-access.kql`

Detects:
- ✅ LSASS memory dumping
- ✅ Credential dumping tool execution (Mimikatz, etc.)
- ✅ SAM/SYSTEM registry hive access
- ✅ Password spray attacks
- ✅ Kerberoasting
- ✅ NTDS.dit access
- ✅ Credential Manager access
- ✅ DCSync attacks

### Data Exfiltration Detection
**File**: `queries/data-exfiltration.kql`

Detects:
- ✅ Large data uploads to external destinations
- ✅ Cloud storage service usage
- ✅ After-hours data transfers
- ✅ Mass file downloads from SharePoint/OneDrive
- ✅ Emails with large attachments
- ✅ Database bulk exports
- ✅ Compressed archive creation before transfer

## 🤖 Automation Playbooks

### IP Enrichment Playbook
Automatically enriches IP addresses in incidents with threat intelligence.

**Features**:
- Queries VirusTotal for IP reputation
- Adds geolocation and ASN data
- Posts enrichment to incident comments

**Configuration**:
1. Deploy playbook template
2. Add VirusTotal API key
3. Grant managed identity permissions
4. Attach to incident creation rule

### Host Isolation Playbook
Automatically isolates compromised hosts using Microsoft Defender for Endpoint.

**Features**:
- Triggers on high-severity incidents
- Isolates machines via Defender API
- Adds status updates to incidents

**Configuration**:
1. Deploy playbook template
2. Configure Defender API permissions
3. Set severity threshold
4. Test before production use

## 🧪 Testing & Validation

### Validate Query Syntax
```bash
python tests/validate_kql.py queries/
```

**Checks**:
- Syntax errors
- Missing time filters
- Performance anti-patterns
- Best practice compliance

### Test Query Execution
```bash
# Set environment variables
export SENTINEL_WORKSPACE_ID="your-workspace-id"
export AZURE_TENANT_ID="your-tenant-id"

# Run tests
python tests/test_queries.py
```

### Review Test Results
```bash
cat tests/test-results.json
```

## 📈 Usage Examples

### Investigation Workflow

**1. Create Investigation Folder**
```bash
mkdir -p investigations/incident-12345
```

**2. Create Configuration File**
```yaml
# investigations/incident-12345/config.yaml
investigation_name: "Incident 12345 - Ransomware Investigation"
investigator: "SOC Analyst"
created_date: "2025-11-19"

start_time: "2025-11-18T14:00:00Z"
end_time: "2025-11-19T02:00:00Z"

device_name: "SRV-FILE-01"
user_name: "compromised.user"
ip_address: "192.168.10.50"
suspicious_hash: "a3b2c1..."
```

**3. Render and Execute Queries**
```bash
# Render process chain analysis
poe render queries/analysis/xdr/process_chain_analysis.yaml \
  -c investigations/incident-12345/config.yaml > output.kql

# Copy rendered KQL to Sentinel
# Execute in Sentinel → Logs
# Document findings in investigation folder
```

**4. Iterate and Refine**
```bash
# Update config with new findings
# Render additional queries as needed
# Build timeline of attacker activity
```

### Running a Hunt

1. **Select Query Category**
   ```kql
   // Example: Hunt for lateral movement
   // Open queries/lateral-movement.kql
   ```

2. **Customize Parameters**
   ```kql
   let timeframe = 7d;  // Adjust time range
   let knownAdminSources = dynamic(["10.0.1.10"]);  // Add your admin IPs
   ```

3. **Execute in Sentinel**
   - Navigate to Sentinel → Logs
   - Paste and run query
   - Review results

4. **Document Findings**
   - Export results
   - Create incident if suspicious activity found
   - Add to threat hunting report

### Creating Custom Queries

```kql
// Template for custom hunting query
let timeRange = 7d;
let threshold = 10;

YourDataSource
| where TimeGenerated > ago(timeRange)
| where <your_conditions>
| summarize 
    EventCount = count(),
    FirstSeen = min(TimeGenerated),
    LastSeen = max(TimeGenerated)
    by <group_by_fields>
| where EventCount > threshold
| project-reorder FirstSeen, LastSeen, EventCount
| order by EventCount desc
```

## 🔧 Customization

### Adapting Queries for Your Environment

1. **Update Known Good Lists**
   ```kql
   let knownAdminSources = dynamic([
       "10.0.1.10",    // Add your admin IPs
       "10.0.1.11"
   ]);
   
   let excludedAccounts = dynamic([
       "svc-backup",   // Add your service accounts
       "svc-monitor"
   ]);
   ```

2. **Adjust Thresholds**
   ```kql
   let failureThreshold = 5;        // Adjust based on baseline
   let accountThreshold = 10;       // Tune to reduce false positives
   let timeWindow = 1h;             // Modify detection window
   ```

3. **Add Custom Logic**
   ```kql
   | extend Severity = case(
       EventCount > 100, "Critical",
       EventCount > 50, "High",
       EventCount > 20, "Medium",
       "Low"
   )
   ```

## 📚 MITRE ATT&CK Mapping

All queries are mapped to MITRE ATT&CK framework:

| Category | Techniques | Query File |
|----------|-----------|------------|
| Lateral Movement | T1021 | lateral-movement.kql |
| Privilege Escalation | T1068, T1078, T1134 | privilege-escalation.kql |
| Persistence | T1547, T1053, T1098 | persistence.kql |
| Command & Control | T1071, T1090, T1095 | command-and-control.kql |
| Credential Access | T1003, T1110, T1555 | credential-access.kql |
| Exfiltration | T1020, T1030, T1048 | data-exfiltration.kql |

## 🛡️ Best Practices

### Query Performance
1. Always include time range filters
2. Filter early in query pipeline
3. Use `has` instead of `contains` when possible
4. Limit result sets appropriately
5. Monitor query execution time

### False Positive Reduction
1. Maintain allowlists for known good activity
2. Baseline normal behavior before alerting
3. Adjust thresholds based on environment
4. Document exclusions and reasoning
5. Regularly review and tune queries

### Operational Workflow
1. Start with short time ranges for testing
2. Validate results before creating alerts
3. Document hunt hypothesis and findings
4. Share relevant queries with team
5. Convert successful hunts to scheduled rules

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Add/modify queries with documentation
4. Run validation tests
5. Submit pull request

### Contribution Guidelines
- Follow KQL best practices
- Include MITRE ATT&CK mappings
- Add inline comments for complex logic
- Test queries before submission
- Update README with new queries

## 📖 Additional Resources

- [Microsoft Sentinel Documentation](https://docs.microsoft.com/azure/sentinel/)
- [KQL Quick Reference](https://docs.microsoft.com/azure/data-explorer/kusto/query/)
- [MITRE ATT&CK Framework](https://attack.mitre.org/)
- [Threat Hunting Best Practices](https://www.sans.org/white-papers/threat-hunting/)
- [Azure Logic Apps Documentation](https://docs.microsoft.com/azure/logic-apps/)

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

These queries and playbooks are provided as-is for educational and operational purposes. Always test in a non-production environment before deploying to production. Customize queries based on your specific environment and requirements.

## 🙋 Support

For issues, questions, or suggestions:
- Open an issue in this repository
- Review existing queries and documentation
- Contribute improvements via pull requests

## 🔄 Version History

- **v2.0.0** (2025-11-19): YAML Query Template System
  - Added YAML-based query format with metadata
  - Implemented Jinja2 template variable system
  - Created investigation config framework
  - Added CLI query rendering tool
  - Standardized variable naming (snake_case)
  - Comprehensive testing (38 unit tests)
  - Type checking and linting compliance

- **v1.0.0** (2025-11-17): Initial release
  - 6 query categories with 40+ hunting queries
  - 2 automation playbooks
  - Complete testing framework
  - Comprehensive documentation

---

**Made with 🛡️ for the security community**
