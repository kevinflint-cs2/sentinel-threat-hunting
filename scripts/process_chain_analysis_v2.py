"""
Process Chain Analysis Script

This script performs process chain analysis as specified in the process-chain-analysis-v2.prompt.md.
It compares process chain events to a baseline, maps to MITRE ATT&CK, proposes KQL, assigns severity, and generates a markdown report.
"""
from pathlib import Path

import pandas as pd

# Paths
CASE_DIR = Path("investigations/rtbt")
CHAIN_PATH = CASE_DIR / "analysis/xdr/process_chain_analysis.csv"
BASELINE_PATH = CASE_DIR / "baselines/DeviceProcessEvents.csv"
REPORT_PATH = CASE_DIR / "reports/process-chain-analysis-v2.md"

# Load data
chain_df = pd.read_csv(CHAIN_PATH)
baseline_df = pd.read_csv(BASELINE_PATH)

# Helper: Check if a process chain is in baseline
baseline_chains = set(
    baseline_df.apply(
        lambda r: f"{r.get('AccountName','')}:{r.get('InitiatingProcessParentFileName','')}:{r.get('InitiatingProcessFileName','')}:{r.get('FileName','')}",
        axis=1,
    )
)


def map_mitre(process_row):
    # Placeholder: Map to MITRE ATT&CK based on process/file names
    # In real use, this would use a mapping table or logic
    suspicious = ["powershell.exe", "cmd.exe", "rundll32.exe", "wmic.exe", "regsvr32.exe", "sc.exe"]
    for s in suspicious:
        if (
            s in str(process_row["FileName"]).lower()
            or s in str(process_row["InitiatingProcessFileName"]).lower()
        ):
            return "T1059", "Command and Scripting Interpreter"
    return "", ""


def propose_kql(process_row):
    # Placeholder: Propose KQL for suspicious process
    if process_row["FileName"].lower() == "powershell.exe":
        return "DeviceProcessEvents | where FileName == 'powershell.exe'"
    return ""


def assign_severity(process_row, anomaly):
    # Placeholder: Assign severity
    if anomaly:
        if process_row["FileName"].lower() in ["powershell.exe", "cmd.exe", "rundll32.exe"]:
            return "High", "Known LOLBin used in attack chains."
        return "Medium", "Anomalous process chain not seen in baseline."
    return "Info", "Seen in baseline."


# Analysis and report rows
timeline_rows = []
mitre_rows = []
kql_queries = set()
severity_rationales = []

for _, row in chain_df.iterrows():
    combined = row["Combined"]
    anomaly = combined not in baseline_chains
    tech_id, tech_name = map_mitre(row)
    kql = propose_kql(row)
    severity, rationale = assign_severity(row, anomaly)
    audit = f"{'Flagged' if anomaly else 'Ignored'}: {'Not in baseline' if anomaly else 'Seen in baseline'}"
    timeline_rows.append(
        f"| {row['AccountName']} | {row['InitiatingProcessParentFileName']} | {row['InitiatingProcessFileName']} | {row['FileName']} | {combined} | {row['Count']} | {row['LastExecutionTime']} | {anomaly} | {tech_id} | {kql} | {severity} | {rationale} | {audit} |"
    )
    if tech_id:
        mitre_rows.append(f"| {combined} | {tech_id} | {tech_name} | {rationale} |")
    if kql:
        kql_queries.add(f"### {combined}\n{kql}\n")
    if anomaly:
        severity_rationales.append(f"- **{combined}**: {severity} - {rationale}")

# Write to report
with open(REPORT_PATH, encoding="utf-8") as f:
    report = f.read()

report = report.replace(
    "<!-- Timeline rows will be inserted here by the analysis script -->", "\n".join(timeline_rows)
)
report = report.replace(
    "<!-- MITRE mapping rows will be inserted here by the analysis script -->",
    "\n".join(mitre_rows),
)
report = report.replace(
    "<!-- KQL queries and coverage notes will be inserted here by the analysis script -->",
    "\n".join(kql_queries),
)
report = report.replace(
    "<!-- Severity rationale for each flagged event will be inserted here by the analysis script -->",
    "\n".join(severity_rationales),
)

with open(REPORT_PATH, "w", encoding="utf-8") as f:
    f.write(report)

print(f"Process chain analysis complete. Report written to {REPORT_PATH}")
