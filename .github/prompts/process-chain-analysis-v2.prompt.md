# Process Chain Analysis Prompt (Version 2)

## Objective
Perform a comprehensive process chain analysis on the provided CSV, focusing on:
- Evidence-driven severity scoring (with explicit rationale for each score)
- Complete timeline export (all records, not just highlights)
- Expanded KQL detection coverage (for all relevant MITRE ATT&CK techniques observed)
- Explicit audit trail: For each record, indicate if it was evaluated, flagged, or ignored, and why
- Collaborative tuning: Output should be reproducible and allow for iterative improvement

## Workflow
1. **Pre-Analysis Checks**
   - Confirm existence of required folders: `analysis/xdr`, `reports`, `baselines`
   - Confirm presence of main input CSV and baseline CSV
   - Await explicit user approval before proceeding

2. **Analysis Steps**
   - Load the main process chain CSV and baseline CSV
   - For each process event:
     - Compare against baseline to identify anomalies
     - Map to MITRE ATT&CK techniques (cite technique IDs)
     - Propose KQL detection queries for each suspicious pattern
     - Assign a severity score (Critical/High/Medium/Low/Info) with explicit, evidence-based rationale
     - Record audit trail: Was this event flagged? Why or why not?
   - Export a complete timeline table (all records, not just highlights)
   - Summarize findings, detection coverage, and any gaps

3. **Output Requirements**
   - Save the markdown report to the path specified in the prompt (e.g., `investigations/rtbt/reports/process-chain-analysis-v2.md`)
   - Report must include:
     - Executive summary
     - Full timeline table (with audit trail columns)
     - MITRE ATT&CK mapping table
     - KQL detection queries (with coverage notes)
     - Severity rationale for each flagged event
     - Recommendations for detection engineering and tuning

4. **Reproducibility**
   - All steps, logic, and scoring must be explicit and repeatable
   - Output should facilitate collaborative review and iterative improvement

---

**Note:** Strictly follow this prompt. Do not omit any required section. All records must be accounted for in the output timeline and audit trail.
