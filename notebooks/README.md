# Threat Hunting Notebooks

Interactive Jupyter notebooks for threat hunting analysis, query development, and incident investigation.

## Available Notebooks

### 1. `threat-hunting-starter.ipynb`
Starter notebook demonstrating:
- Connecting to Azure Sentinel workspace
- Running KQL queries programmatically
- Data analysis and visualization
- Common threat hunting patterns

## Getting Started

### Start Jupyter Lab
```bash
poe notebook
```

Access at: http://localhost:8888

### Install Additional Packages
If you need additional data science libraries:
```bash
poetry add scikit-learn seaborn
```

## Usage Patterns

### Authentication
Notebooks support multiple authentication methods:
- Azure CLI authentication (recommended for local dev)
- Managed Identity (for Azure-hosted notebooks)
- Service Principal with environment variables

### Query Execution
```python
from azure.monitor.query import LogsQueryClient
from azure.identity import DefaultAzureCredential

credential = DefaultAzureCredential()
client = LogsQueryClient(credential)

query = """
SecurityEvent
| where TimeGenerated > ago(24h)
| where EventID == 4624
| summarize count() by Account
"""

response = client.query_workspace(workspace_id, query, timespan=None)
```

### Data Analysis
Use pandas for analysis:
```python
import pandas as pd

df = pd.DataFrame(response.tables[0].rows, columns=[col.name for col in response.tables[0].columns])
df.head()
```

### Visualization
Create charts with plotly or matplotlib:
```python
import plotly.express as px

fig = px.bar(df, x='Account', y='count_', title='Logon Events by Account')
fig.show()
```

## Best Practices

1. **Use parameters** - Don't hardcode workspace IDs or time ranges
2. **Save outputs** - Export results to CSV for documentation
3. **Version control** - Clear outputs before committing notebooks
4. **Document findings** - Use markdown cells to explain discoveries
5. **Modular queries** - Break complex hunts into logical steps

## Notebook Structure

Recommended structure for hunt notebooks:
1. **Overview** - Hypothesis and hunt objectives
2. **Setup** - Imports and authentication
3. **Data Collection** - Run queries and gather data
4. **Analysis** - Process and analyze results
5. **Visualization** - Create charts and graphs
6. **Findings** - Document discoveries and next steps
7. **Artifacts** - Export IOCs, queries, and evidence

## Tips

- Use `%%time` magic to measure query execution time
- Use `display()` for better DataFrame rendering
- Save reusable functions in `utils/` directory
- Clear outputs with: `jupyter nbconvert --clear-output notebook.ipynb`

## Resources

- [Azure Monitor Query Documentation](https://docs.microsoft.com/python/api/azure-monitor-query/)
- [Pandas Documentation](https://pandas.pydata.org/docs/)
- [Plotly Python](https://plotly.com/python/)
- [Jupyter Lab Documentation](https://jupyterlab.readthedocs.io/)
