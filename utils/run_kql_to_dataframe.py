from dotenv import load_dotenv
import os
from azure.identity import ManagedIdentityCredential
from azure.monitor.query import LogsQueryClient
import pandas as pd


load_dotenv()  # loads variables from .env into the process
cred = ManagedIdentityCredential()  # no args if system-assigned; or pass client_id for UAMI
workspace_id = os.getenv("SENTINEL_WORKSPACE_ID", "your-workspace-id-here-though-not-recommended")
client = LogsQueryClient(credential=cred) # Get LA Query Client

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