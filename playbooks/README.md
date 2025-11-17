# Azure Sentinel Playbooks

This directory contains automated response playbooks for Microsoft Sentinel incidents.

## Available Playbooks

### 1. IP Enrichment Playbook (`ip-enrichment-playbook.json`)
**Purpose**: Automatically enriches IP addresses in incidents with threat intelligence data.

**Features**:
- Extracts IP addresses from Sentinel incidents
- Queries VirusTotal for reputation data
- Adds enrichment comments to incidents
- Provides geolocation and ASN information

**Deployment**:
```bash
az deployment group create \
  --resource-group <your-resource-group> \
  --template-file ip-enrichment-playbook.json \
  --parameters PlaybookName=<playbook-name> SentinelWorkspaceId=<workspace-id>
```

**Configuration**:
- Replace `YOUR_API_KEY` with your VirusTotal API key
- Grant the playbook's managed identity "Microsoft Sentinel Responder" role

### 2. Host Isolation Playbook (`host-isolation-playbook.json`)
**Purpose**: Automatically isolates compromised hosts using Microsoft Defender for Endpoint.

**Features**:
- Triggers on high-severity incidents
- Extracts host entities from incidents
- Isolates machines via Defender API
- Adds isolation status to incident comments

**Deployment**:
```bash
az deployment group create \
  --resource-group <your-resource-group> \
  --template-file host-isolation-playbook.json \
  --parameters PlaybookName=<playbook-name> DefenderEndpointResourceId=<defender-resource-id>
```

**Configuration**:
- Grant the playbook's managed identity API permissions for Microsoft Defender
- Permissions required: `Machine.Isolate`, `Machine.Read.All`

## General Setup

### Prerequisites
1. Azure Sentinel workspace deployed
2. Logic Apps enabled in your subscription
3. Appropriate API connections configured

### Post-Deployment Steps
1. Configure API connections with proper authentication
2. Assign managed identity permissions:
   ```bash
   # For Sentinel access
   az role assignment create \
     --assignee <managed-identity-id> \
     --role "Microsoft Sentinel Responder" \
     --scope <sentinel-workspace-resource-id>
   ```
3. Test playbooks manually before enabling automated triggers
4. Monitor playbook run history for errors

## Customization

Each playbook can be customized by:
- Modifying trigger conditions
- Adding additional enrichment sources
- Implementing custom logic for specific use cases
- Integrating with ITSM systems (ServiceNow, Jira)

## Best Practices

1. **Testing**: Always test in a non-production environment first
2. **Monitoring**: Enable diagnostic logging for Logic Apps
3. **Error Handling**: Implement retry policies and error notifications
4. **Documentation**: Document any customizations made to playbooks
5. **Version Control**: Keep playbook templates in source control

## Troubleshooting

Common issues:
- **Authentication failures**: Verify managed identity permissions
- **API limits**: Implement rate limiting and backoff strategies
- **Connection errors**: Check API connection configurations
- **Missing data**: Verify incident entities are properly populated

For more information, see the [Azure Logic Apps documentation](https://docs.microsoft.com/azure/logic-apps/).
