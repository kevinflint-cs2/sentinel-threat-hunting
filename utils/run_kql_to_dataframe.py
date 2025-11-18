import os

import pandas as pd
from azure.identity import DeviceCodeCredential
from azure.monitor.query import LogsQueryClient, LogsQueryStatus

# Use device code flow for Codespaces/remote environments
cred = DeviceCodeCredential()  # Will prompt with a code to enter in browser
workspace_id = os.getenv("SENTINEL_WORKSPACE_ID", "your-workspace-id-here")
client = LogsQueryClient(credential=cred)  # Get LA Query Client

kql = """
shodan_scan_CL
| sample 10
"""

resp = client.query_workspace(workspace_id, kql, timespan=None)

if resp.status == LogsQueryStatus.PARTIAL:
    table = resp.partial_data[0]
elif resp.status == LogsQueryStatus.SUCCESS:
    table = resp.tables[0]
else:
    raise RuntimeError("Query failed")

df = pd.DataFrame(table.rows, columns=table.columns)
print(df.head())