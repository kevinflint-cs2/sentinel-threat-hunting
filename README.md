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
│   ├── lateral-movement.kql
│   ├── privilege-escalation.kql
│   ├── persistence.kql
│   ├── command-and-control.kql
│   ├── credential-access.kql
│   └── data-exfiltration.kql
├── playbooks/                  # Logic App automation playbooks
│   ├── ip-enrichment-playbook.json
│   ├── host-isolation-playbook.json
│   └── README.md
├── detections/                 # Scheduled analytics rules
├── tests/                      # Testing and validation tools
│   ├── validate_kql.py
│   ├── test_queries.py
│   └── README.md
├── utils/                      # Helper scripts and utilities
└── README.md
```

## 🚀 Quick Start

### Prerequisites
- Azure Subscription with Microsoft Sentinel enabled
- Log Analytics workspace configured
- Appropriate data connectors enabled (SecurityEvent, CommonSecurityLog, etc.)

### 1. Deploy Queries

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

- **v1.0.0** (2025-11-17): Initial release
  - 6 query categories with 40+ hunting queries
  - 2 automation playbooks
  - Complete testing framework
  - Comprehensive documentation

---

**Made with 🛡️ for the security community**
