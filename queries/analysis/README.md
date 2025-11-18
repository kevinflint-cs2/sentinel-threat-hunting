# Analysis Queries

This directory contains non-MITRE queries focused on baseline analysis, noise reduction, anomaly detection, and general threat hunting across different platforms.

## Purpose

Analysis queries are designed for:
- **Baseline establishment** - Understanding normal behavior in your environment
- **Noise reduction** - Filtering out known-good activity
- **Anomaly detection** - Finding statistical outliers and unusual patterns
- **General hunting** - Exploratory analysis without specific MITRE mapping

## Organization

Queries are organized by platform:
- `azure/` - Azure and Microsoft 365 analysis
- `aws/` - AWS CloudTrail and service analysis
- `xdr/` - Microsoft Defender XDR analysis

## Query Types

### Baseline Queries
Establish normal patterns of behavior:
- User signin patterns and locations
- Process execution baselines
- Network communication patterns
- API call frequency and timing

### Noise Reduction
Filter known-good activity:
- Approved service accounts
- Scheduled tasks and automation
- Known administrative actions
- Legitimate third-party tools

### Anomaly Detection
Statistical outliers and unusual behavior:
- Rare process executions
- Unusual signin times or locations
- Abnormal data volumes
- First-time observations

## Using Analysis Queries

These queries often need customization for your environment:

1. **Run the query** to see raw data
2. **Identify baselines** specific to your organization
3. **Update filters** with your known-good values
4. **Save customized versions** in your investigation folders

Example workflow:
```python
# Run baseline query
config = load_config("investigations/baseline/config.yaml")
query = render_kql_file("queries/analysis/azure/baseline-activity.kql", config)
df = execute_kql_query(client, workspace_id, query)

# Analyze results
common_ips = df['IPAddress'].value_counts().head(20)
# Add these to your config as known-good
```

## Best Practices

- **Document assumptions** about what's normal in your environment
- **Version control custom filters** in investigation configs
- **Regularly update baselines** as your environment evolves
- **Share findings** with your team to improve collective knowledge
