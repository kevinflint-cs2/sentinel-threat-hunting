# Detection Rules

This directory will contain analytics rules for automated detection in Microsoft Sentinel.

## Structure

Detection rules should be organized by:
- **Severity**: Critical, High, Medium, Low
- **Data Source**: SecurityEvent, CommonSecurityLog, etc.
- **Tactics**: Based on MITRE ATT&CK framework

## Rule Template

```json
{
  "displayName": "Suspicious Activity Detection",
  "description": "Detects suspicious activity pattern",
  "severity": "High",
  "enabled": true,
  "query": "SecurityEvent | where ...",
  "queryFrequency": "PT5M",
  "queryPeriod": "PT1H",
  "triggerOperator": "GreaterThan",
  "triggerThreshold": 0,
  "suppressionDuration": "PT1H",
  "suppressionEnabled": false,
  "tactics": ["LateralMovement", "PrivilegeEscalation"],
  "techniques": ["T1021", "T1068"]
}
```

## Deployment

Analytics rules can be deployed via:
- Azure Portal (Sentinel → Analytics)
- ARM Templates
- Azure CLI
- PowerShell

## Best Practices

1. Test queries thoroughly before enabling
2. Set appropriate frequency and look-back period
3. Configure alert grouping to reduce noise
4. Map to MITRE ATT&CK framework
5. Document expected false positives
6. Regularly review and tune rules

## Converting Hunts to Rules

When a hunting query proves valuable:
1. Optimize query performance
2. Add appropriate thresholds
3. Configure alert metadata
4. Set up incident automation
5. Document in playbook

## Coming Soon

Pre-built detection rules converted from hunting queries will be added to this directory.
