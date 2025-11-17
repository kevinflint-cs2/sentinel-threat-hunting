# Testing Framework for Sentinel Threat Hunting Queries

This directory contains tools for validating and testing KQL queries.

## Tools

### 1. KQL Validator (`validate_kql.py`)
Validates KQL queries for syntax and best practices.

**Usage**:
```bash
python tests/validate_kql.py [query_directory]
```

**Checks**:
- ✅ Syntax validation
- ✅ Required time filters (TimeGenerated, ago())
- ✅ Performance best practices
- ✅ Proper use of operators
- ✅ Efficient query patterns

**Example Output**:
```
Validating: lateral-movement.kql
❌ ERRORS:
  - Query 3: Missing TimeGenerated filter
⚠️  WARNINGS:
  - Query 1: Consider using =~ for case-insensitive comparison
  - Query 5: Multiple joins may impact performance
```

### 2. Query Tester (`test_queries.py`)
Tests query execution and validates results.

**Usage**:
```bash
# Syntax testing only
python tests/test_queries.py

# With Sentinel workspace
export SENTINEL_WORKSPACE_ID="your-workspace-id"
export AZURE_TENANT_ID="your-tenant-id"
python tests/test_queries.py
```

**Features**:
- Syntax validation
- Query structure analysis
- Optional execution against live workspace
- Performance metrics
- Results saved to JSON

## Testing Workflow

### Local Development
```bash
# 1. Validate all queries
python tests/validate_kql.py

# 2. Run syntax tests
python tests/test_queries.py

# 3. Review results
cat tests/test-results.json
```

### CI/CD Integration
```yaml
# Example GitHub Actions workflow
- name: Validate KQL Queries
  run: |
    python tests/validate_kql.py queries/
    python tests/test_queries.py
```

## Best Practices for Query Testing

### 1. Time Filters
Always include time range filters:
```kql
SecurityEvent
| where TimeGenerated > ago(24h)
```

### 2. Performance Optimization
- Use specific time ranges
- Filter early in the query pipeline
- Limit result sets with `take` or `top`
- Use `summarize` efficiently

### 3. Test Data
Create test scenarios:
```kql
// Test with small time window first
| where TimeGenerated > ago(1h)
| take 100
```

### 4. Documentation
Document expected results:
```kql
// Expected: 0-5 results under normal conditions
// Alert if: > 10 results in 24h
```

## Query Performance Guidelines

### Efficient Queries
✅ Filter on TimeGenerated first
✅ Use has/contains instead of wildcards
✅ Limit summarize cardinality
✅ Use project to reduce columns early

### Inefficient Patterns
❌ No time filter
❌ Leading wildcards in searches
❌ Multiple complex joins
❌ Unbounded result sets

## Troubleshooting

### Common Issues

**"Missing TimeGenerated filter"**
- Add `| where TimeGenerated > ago(Xd)` to query

**"Unmatched parentheses"**
- Check all function calls and expressions for balanced parentheses

**"No recognized data source"**
- Ensure query starts with a valid table name

## Sample Test Cases

### Test Case 1: Lateral Movement Detection
```python
test_case = {
    'name': 'RDP from unusual source',
    'query': 'lateral-movement.kql',
    'expected_fields': ['Account', 'IpAddress', 'Computer'],
    'expected_max_results': 100
}
```

### Test Case 2: Privilege Escalation
```python
test_case = {
    'name': 'Admin group additions',
    'query': 'privilege-escalation.kql',
    'alert_threshold': 1,
    'severity': 'High'
}
```

## Contributing Tests

When adding new queries:
1. Run validator before committing
2. Add test cases for edge conditions
3. Document expected behavior
4. Include performance considerations

## Resources

- [KQL Documentation](https://docs.microsoft.com/azure/data-explorer/kusto/query/)
- [Sentinel Best Practices](https://docs.microsoft.com/azure/sentinel/best-practices)
- [Query Performance](https://docs.microsoft.com/azure/azure-monitor/logs/query-optimization)
