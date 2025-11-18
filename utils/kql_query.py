"""
Azure Monitor KQL Query Utilities.

This module provides functions to execute KQL queries against Azure
Monitor/Sentinel workspaces and return results as pandas DataFrames.
"""

from typing import Optional, Union
from azure.monitor.query import LogsQueryClient, LogsQueryStatus
import pandas as pd


def execute_kql_query(
    client: LogsQueryClient,
    workspace_id: str,
    kql_query: str,
    timespan: Optional[Union[str, tuple]] = None
) -> pd.DataFrame:
    """
    Execute a KQL query using a LogsQueryClient and return results.
    
    This function takes an Azure Monitor LogsQueryClient object and a KQL
    query string, executes the query against the specified workspace, and
    returns the results as a pandas DataFrame.
    
    Parameters:
    -----------
    client : LogsQueryClient
        An initialized Azure Monitor LogsQueryClient instance with valid
        credentials.
    workspace_id : str
        The Log Analytics workspace ID to query against.
    kql_query : str
        The KQL (Kusto Query Language) query string to execute.
    timespan : Optional[Union[str, tuple]], optional
        The timespan for the query. Can be a string like "P1D" for last
        day, or a tuple of (start_time, end_time). Default is None which
        queries all available data.
    
    Returns:
    --------
    pd.DataFrame
        A pandas DataFrame containing the query results with columns
        corresponding to the KQL query output schema.
    
    Raises:
    -------
    ValueError
        If client, workspace_id, or kql_query are empty or None.
    RuntimeError
        If the query fails completely (not partial success).
    
    Examples:
    ---------
    >>> from azure.identity import DefaultAzureCredential
    >>> from azure.monitor.query import LogsQueryClient
    >>> credential = DefaultAzureCredential()
    >>> client = LogsQueryClient(credential=credential)
    >>> workspace_id = "12345678-1234-1234-1234-123456789012"
    >>> query = "SecurityEvent | take 10"
    >>> df = execute_kql_query(client, workspace_id, query)
    >>> print(df.head())
    """
    # Validate inputs to handle edge cases
    if not client:
        raise ValueError("client cannot be None")
    if not workspace_id or not isinstance(workspace_id, str):
        raise ValueError("workspace_id must be a non-empty string")
    if not kql_query or not isinstance(kql_query, str):
        raise ValueError("kql_query must be a non-empty string")
    
    # Execute the KQL query against the workspace
    try:
        response = client.query_workspace(
            workspace_id,
            kql_query,
            timespan=timespan
        )
    except Exception as e:
        raise RuntimeError(f"Failed to execute KQL query: {str(e)}") from e
    
    # Handle different response statuses
    # PARTIAL status means some data was returned but query had issues
    if response.status == LogsQueryStatus.PARTIAL:
        table = response.partial_data[0]
    # SUCCESS status means query completed successfully
    elif response.status == LogsQueryStatus.SUCCESS:
        table = response.tables[0]
    else:
        # Query failed completely with no data
        raise RuntimeError(
            f"Query failed with status: {response.status}"
        )
    
    # Convert the query results to a pandas DataFrame
    # table.rows contains the data, table.columns contains column names
    df = pd.DataFrame(table.rows, columns=table.columns)
    
    return df
