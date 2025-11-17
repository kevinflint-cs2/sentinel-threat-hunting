#!/usr/bin/env python3
"""
KQL Query Validator for Microsoft Sentinel
Validates KQL queries for syntax and best practices
"""

import re
import sys
from pathlib import Path
from typing import List, Tuple, Dict

class KQLValidator:
    def __init__(self):
        self.errors = []
        self.warnings = []
        
    def validate_file(self, filepath: Path) -> Tuple[bool, List[str], List[str]]:
        """Validate a KQL file"""
        self.errors = []
        self.warnings = []
        
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Split into individual queries
        queries = self._extract_queries(content)
        
        for idx, query in enumerate(queries, 1):
            self._validate_query(query, idx)
        
        return len(self.errors) == 0, self.errors, self.warnings
    
    def _extract_queries(self, content: str) -> List[str]:
        """Extract individual KQL queries from file"""
        # Remove comments
        content = re.sub(r'//.*$', '', content, flags=re.MULTILINE)
        
        # Split by common query patterns
        queries = []
        current_query = []
        
        for line in content.split('\n'):
            line = line.strip()
            if line:
                current_query.append(line)
            elif current_query:
                queries.append(' '.join(current_query))
                current_query = []
        
        if current_query:
            queries.append(' '.join(current_query))
        
        return [q for q in queries if self._is_kql_query(q)]
    
    def _is_kql_query(self, text: str) -> bool:
        """Check if text appears to be a KQL query"""
        kql_keywords = ['where', 'summarize', 'project', 'extend', 'join', 'union', 'let']
        return any(keyword in text.lower() for keyword in kql_keywords)
    
    def _validate_query(self, query: str, query_num: int):
        """Validate an individual query"""
        query_lower = query.lower()
        
        # Check for required elements
        if not any(table in query for table in ['SecurityEvent', 'CommonSecurityLog', 'DnsEvents', 
                                                   'OfficeActivity', 'AuditLogs', 'SigninLogs']):
            self.warnings.append(f"Query {query_num}: No recognized data source table found")
        
        # Check for time filter
        if 'timegenerated' not in query_lower:
            self.errors.append(f"Query {query_num}: Missing TimeGenerated filter")
        
        if 'ago(' not in query_lower:
            self.errors.append(f"Query {query_num}: Missing time range (ago() function)")
        
        # Check for best practices
        if 'summarize' in query_lower:
            if 'bin(timegenerated' not in query_lower and 'bin (timegenerated' not in query_lower:
                self.warnings.append(f"Query {query_num}: Consider using bin() for time-based summarization")
        
        # Check for wildcards at beginning of strings (inefficient)
        if re.search(r'has\s+"[\*]', query) or re.search(r'contains\s+"[\*]', query):
            self.warnings.append(f"Query {query_num}: Avoid wildcards at beginning of search strings")
        
        # Check for case-sensitive operators where case-insensitive might be better
        if ' == ' in query and 'where' in query_lower:
            self.warnings.append(f"Query {query_num}: Consider using =~ for case-insensitive comparison")
        
        # Check for proper use of dynamic objects
        if 'dynamic(' in query_lower and 'let' not in query_lower[:50]:
            self.warnings.append(f"Query {query_num}: Consider defining dynamic objects in let statements")
        
        # Check for summarize without project or project-reorder
        if 'summarize' in query_lower and 'project' not in query_lower:
            self.warnings.append(f"Query {query_num}: Consider using project-reorder after summarize for better readability")
        
        # Check for potential performance issues
        if query_lower.count('join') > 2:
            self.warnings.append(f"Query {query_num}: Multiple joins may impact performance, consider optimization")
        
        # Check for proper use of make_set limits
        make_set_matches = re.findall(r'make_set\([^,]+,\s*(\d+)\)', query)
        for limit in make_set_matches:
            if int(limit) > 100:
                self.warnings.append(f"Query {query_num}: make_set limit of {limit} may be excessive")

def main():
    """Main validation function"""
    if len(sys.argv) > 1:
        query_dir = Path(sys.argv[1])
    else:
        query_dir = Path(__file__).parent.parent / 'queries'
    
    if not query_dir.exists():
        print(f"Error: Directory {query_dir} does not exist")
        sys.exit(1)
    
    print("=" * 80)
    print("KQL Query Validator for Microsoft Sentinel")
    print("=" * 80)
    print()
    
    validator = KQLValidator()
    total_files = 0
    passed_files = 0
    
    for kql_file in query_dir.glob('*.kql'):
        total_files += 1
        print(f"Validating: {kql_file.name}")
        print("-" * 80)
        
        success, errors, warnings = validator.validate_file(kql_file)
        
        if errors:
            print("❌ ERRORS:")
            for error in errors:
                print(f"  - {error}")
        
        if warnings:
            print("⚠️  WARNINGS:")
            for warning in warnings:
                print(f"  - {warning}")
        
        if not errors and not warnings:
            print("✅ No issues found")
        
        if success:
            passed_files += 1
        
        print()
    
    print("=" * 80)
    print(f"Validation Complete: {passed_files}/{total_files} files passed")
    print("=" * 80)
    
    sys.exit(0 if passed_files == total_files else 1)

if __name__ == '__main__':
    main()
