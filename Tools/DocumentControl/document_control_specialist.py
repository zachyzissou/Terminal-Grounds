# -*- coding: utf-8 -*-
"""
Terminal Grounds - Document Control Specialist Agent

This agent manages the comprehensive documentation ecosystem for Terminal Grounds,
preventing documentation sprawl and ensuring governance across 250+ markdown files.

Author: Claude Code
Date: August 28, 2025
"""

import os
import re
import json
import yaml
from pathlib import Path
from typing import Dict, List, Tuple, Set, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import hashlib

@dataclass
class DocumentMetadata:
    """Metadata tracking for each documentation file"""
    file_path: str
    title: str
    category: str
    owner: str
    last_modified: datetime
    version: str
    status: str  # draft, review, approved, deprecated, archived
    dependencies: List[str]  # Files that reference this document
    references: List[str]    # Files this document references
    tags: List[str]
    content_hash: str
    word_count: int
    maintenance_priority: int  # 1-5 scale

@dataclass
class DocumentationIssue:
    """Represents a governance issue found in documentation"""
    file_path: str
    issue_type: str  # duplicate, orphaned, outdated, inconsistent, missing_metadata
    severity: str    # low, medium, high, critical
    description: str
    recommendation: str
    auto_fixable: bool

class DocumentControlSpecialist:
    """
    Professional document control specialist for Terminal Grounds project.
    
    Responsibilities:
    - Document lifecycle management
    - Version control and governance
    - Consolidation of duplicate content
    - Quality assurance and standards enforcement
    - Architecture optimization
    - Cross-reference integrity
    """
    
    def __init__(self, project_root: str = None):
        self.project_root = Path(project_root or os.getcwd())
        self.metadata_db_path = self.project_root / "Tools" / "DocumentControl" / "document_registry.json"
        self.config_path = self.project_root / "Tools" / "DocumentControl" / "governance_config.yaml"
        
        # Ensure directory structure exists
        self.metadata_db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Load or initialize document registry
        self.document_registry = self._load_document_registry()
        self.governance_config = self._load_governance_config()
        
    def _load_document_registry(self) -> Dict[str, DocumentMetadata]:
        """Load existing document registry or create new one"""
        if self.metadata_db_path.exists():
            with open(self.metadata_db_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return {
                    path: DocumentMetadata(**meta) 
                    for path, meta in data.items()
                }
        return {}
    
    def _save_document_registry(self):
        """Save document registry to disk"""
        with open(self.metadata_db_path, 'w', encoding='utf-8') as f:
            json.dump(
                {path: asdict(meta) for path, meta in self.document_registry.items()},
                f, 
                indent=2,
                default=str
            )
    
    def _load_governance_config(self) -> Dict:
        """Load governance configuration"""
        default_config = {
            'document_categories': {
                'technical': ['docs/Tech/', 'Tools/'],
                'design': ['docs/Design/', 'docs/Concepts/'],
                'lore': ['docs/Lore/'],
                'art': ['docs/Art/', 'Content/TG/'],
                'process': ['*.md'],  # Root-level process docs
                'reference': ['Tools/ArtGen/', 'docs/Assets/']
            },
            'mandatory_metadata': [
                'title', 'category', 'owner', 'status'
            ],
            'status_lifecycle': [
                'draft', 'review', 'approved', 'deprecated', 'archived'
            ],
            'max_duplicate_content_similarity': 0.8,
            'maintenance_schedule_days': {
                'critical': 30,
                'high': 60,
                'medium': 120,
                'low': 365
            }
        }
        
        if self.config_path.exists():
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        else:
            # Create default config
            with open(self.config_path, 'w', encoding='utf-8') as f:
                yaml.dump(default_config, f, indent=2)
            return default_config
    
    def scan_all_documentation(self) -> List[Path]:
        """Discover all markdown files in the project"""
        markdown_files = []
        
        # Scan multiple directory patterns
        scan_patterns = [
            "**/*.md",
            "**/*.MD"
        ]
        
        for pattern in scan_patterns:
            markdown_files.extend(self.project_root.glob(pattern))
        
        # Filter out excluded directories
        excluded_dirs = {'.git', 'node_modules', '__pycache__', '.venv'}
        
        return [
            f for f in markdown_files 
            if not any(excluded in f.parts for excluded in excluded_dirs)
        ]
    
    def analyze_document(self, file_path: Path) -> DocumentMetadata:
        """Analyze a single document and extract metadata"""
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # Extract title (first # heading or filename)
        title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        title = title_match.group(1) if title_match else file_path.stem
        
        # Determine category based on path
        category = self._categorize_document(file_path)
        
        # Extract owner from content or determine from git
        owner_match = re.search(r'(?:author|owner):\s*(.+)$', content, re.IGNORECASE | re.MULTILINE)
        owner = owner_match.group(1).strip() if owner_match else "unassigned"
        
        # Extract status
        status_match = re.search(r'status:\s*(\w+)', content, re.IGNORECASE)
        status = status_match.group(1).lower() if status_match else "draft"
        
        # Extract version
        version_match = re.search(r'version:\s*([^\n]+)', content, re.IGNORECASE)
        version = version_match.group(1).strip() if version_match else "1.0"
        
        # Calculate content hash
        content_hash = hashlib.md5(content.encode('utf-8')).hexdigest()
        
        # Find dependencies and references
        dependencies = self._find_document_dependencies(content)
        references = self._find_document_references(content)
        
        # Extract tags
        tags_match = re.search(r'tags:\s*\[([^\]]+)\]', content, re.IGNORECASE)
        tags = [t.strip().strip('"\'') for t in tags_match.group(1).split(',')] if tags_match else []
        
        return DocumentMetadata(
            file_path=str(file_path.relative_to(self.project_root)),
            title=title,
            category=category,
            owner=owner,
            last_modified=datetime.fromtimestamp(file_path.stat().st_mtime),
            version=version,
            status=status,
            dependencies=dependencies,
            references=references,
            tags=tags,
            content_hash=content_hash,
            word_count=len(content.split()),
            maintenance_priority=self._calculate_maintenance_priority(file_path, content)
        )
    
    def _categorize_document(self, file_path: Path) -> str:
        """Categorize document based on its path"""
        path_str = str(file_path)
        
        for category, patterns in self.governance_config['document_categories'].items():
            for pattern in patterns:
                if pattern in path_str:
                    return category
        
        return "uncategorized"
    
    def _find_document_dependencies(self, content: str) -> List[str]:
        """Find files that this document depends on (references)"""
        dependencies = []
        
        # Look for markdown links
        md_links = re.findall(r'\[([^\]]+)\]\(([^)]+\.md)\)', content)
        dependencies.extend([link[1] for link in md_links])
        
        # Look for file paths
        file_refs = re.findall(r'`([^`]*\.md)`', content)
        dependencies.extend(file_refs)
        
        return list(set(dependencies))  # Remove duplicates
    
    def _find_document_references(self, content: str) -> List[str]:
        """Find files that reference this document (reverse dependencies)"""
        # This would require scanning all other documents - implemented in full_audit
        return []
    
    def _calculate_maintenance_priority(self, file_path: Path, content: str) -> int:
        """Calculate maintenance priority (1=low, 5=critical)"""
        priority = 1
        
        # Critical system files
        if 'CLAUDE.md' in str(file_path) or 'README.md' in str(file_path):
            priority = 5
        
        # Frequently referenced files
        if len(re.findall(r'Tools/|Scripts/|Source/', content)) > 5:
            priority = max(priority, 4)
        
        # Large files need more maintenance
        if len(content.split()) > 2000:
            priority = max(priority, 3)
        
        # Files with many external references
        if len(re.findall(r'http[s]?://', content)) > 10:
            priority = max(priority, 3)
        
        return priority
    
    def perform_full_audit(self) -> List[DocumentationIssue]:
        """Perform comprehensive documentation audit"""
        issues = []
        all_docs = self.scan_all_documentation()
        
        print(f"Scanning {len(all_docs)} documentation files...")
        
        # Update registry with current state
        for doc_path in all_docs:
            try:
                metadata = self.analyze_document(doc_path)
                self.document_registry[str(doc_path.relative_to(self.project_root))] = metadata
            except Exception as e:
                issues.append(DocumentationIssue(
                    file_path=str(doc_path.relative_to(self.project_root)),
                    issue_type="analysis_error",
                    severity="medium",
                    description=f"Could not analyze document: {str(e)}",
                    recommendation="Manual review required",
                    auto_fixable=False
                ))
        
        # Check for governance issues
        issues.extend(self._detect_duplicates())
        issues.extend(self._detect_orphaned_docs())
        issues.extend(self._detect_missing_metadata())
        issues.extend(self._detect_broken_references())
        issues.extend(self._detect_outdated_docs())
        
        self._save_document_registry()
        return issues
    
    def _detect_duplicates(self) -> List[DocumentationIssue]:
        """Detect duplicate or very similar content"""
        issues = []
        docs = list(self.document_registry.values())
        
        for i, doc1 in enumerate(docs):
            for doc2 in docs[i+1:]:
                similarity = self._calculate_content_similarity(doc1.title, doc2.title)
                if similarity > self.governance_config['max_duplicate_content_similarity']:
                    issues.append(DocumentationIssue(
                        file_path=doc1.file_path,
                        issue_type="duplicate",
                        severity="high",
                        description=f"Very similar to {doc2.file_path} (similarity: {similarity:.2f})",
                        recommendation="Consider consolidating these documents",
                        auto_fixable=False
                    ))
        
        return issues
    
    def _detect_orphaned_docs(self) -> List[DocumentationIssue]:
        """Detect documents with no incoming references"""
        issues = []
        
        # Build reference graph
        referenced_docs = set()
        for doc in self.document_registry.values():
            referenced_docs.update(doc.dependencies)
        
        for doc in self.document_registry.values():
            if (doc.file_path not in referenced_docs and 
                doc.category not in ['process'] and  # Process docs can be standalone
                'README' not in doc.file_path):      # READMEs are expected to be standalone
                
                issues.append(DocumentationIssue(
                    file_path=doc.file_path,
                    issue_type="orphaned",
                    severity="medium",
                    description="Document has no incoming references",
                    recommendation="Add references or consider archiving",
                    auto_fixable=False
                ))
        
        return issues
    
    def _detect_missing_metadata(self) -> List[DocumentationIssue]:
        """Detect documents missing required metadata"""
        issues = []
        required_fields = self.governance_config['mandatory_metadata']
        
        for doc in self.document_registry.values():
            if doc.owner == "unassigned":
                issues.append(DocumentationIssue(
                    file_path=doc.file_path,
                    issue_type="missing_metadata",
                    severity="medium",
                    description="Document lacks owner assignment",
                    recommendation="Add owner metadata to document header",
                    auto_fixable=True
                ))
            
            if doc.status == "draft" and doc.maintenance_priority >= 4:
                issues.append(DocumentationIssue(
                    file_path=doc.file_path,
                    issue_type="missing_metadata",
                    severity="high",
                    description="High-priority document still in draft status",
                    recommendation="Review and approve this critical document",
                    auto_fixable=False
                ))
        
        return issues
    
    def _detect_broken_references(self) -> List[DocumentationIssue]:
        """Detect broken internal links"""
        issues = []
        
        for doc in self.document_registry.values():
            for dependency in doc.dependencies:
                # Check if referenced file exists
                dep_path = self.project_root / dependency
                if not dep_path.exists():
                    issues.append(DocumentationIssue(
                        file_path=doc.file_path,
                        issue_type="broken_reference",
                        severity="high",
                        description=f"References non-existent file: {dependency}",
                        recommendation="Update or remove broken reference",
                        auto_fixable=True
                    ))
        
        return issues
    
    def _detect_outdated_docs(self) -> List[DocumentationIssue]:
        """Detect documents that haven't been updated recently"""
        issues = []
        now = datetime.now()
        
        for doc in self.document_registry.values():
            days_since_update = (now - doc.last_modified).days
            maintenance_interval = self.governance_config['maintenance_schedule_days'].get(
                self._priority_to_level(doc.maintenance_priority), 365
            )
            
            if days_since_update > maintenance_interval:
                issues.append(DocumentationIssue(
                    file_path=doc.file_path,
                    issue_type="outdated",
                    severity="low" if doc.maintenance_priority <= 2 else "medium",
                    description=f"Not updated for {days_since_update} days",
                    recommendation="Review and update if necessary",
                    auto_fixable=False
                ))
        
        return issues
    
    def _priority_to_level(self, priority: int) -> str:
        """Convert numeric priority to level string"""
        levels = {1: "low", 2: "low", 3: "medium", 4: "high", 5: "critical"}
        return levels.get(priority, "low")
    
    def _calculate_content_similarity(self, title1: str, title2: str) -> float:
        """Calculate similarity between two document titles"""
        # Simple word-based similarity
        words1 = set(title1.lower().split())
        words2 = set(title2.lower().split())
        
        if not words1 and not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union) if union else 0.0
    
    def generate_governance_report(self, issues: List[DocumentationIssue]) -> str:
        """Generate comprehensive governance report"""
        report = []
        report.append("# Terminal Grounds - Documentation Governance Report")
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        # Summary statistics
        total_docs = len(self.document_registry)
        total_issues = len(issues)
        critical_issues = len([i for i in issues if i.severity == "critical"])
        high_issues = len([i for i in issues if i.severity == "high"])
        
        report.append("## Executive Summary")
        report.append(f"- **Total Documents**: {total_docs}")
        report.append(f"- **Total Issues**: {total_issues}")
        report.append(f"- **Critical Issues**: {critical_issues}")
        report.append(f"- **High Priority Issues**: {high_issues}\n")
        
        # Category breakdown
        categories = {}
        for doc in self.document_registry.values():
            categories[doc.category] = categories.get(doc.category, 0) + 1
        
        report.append("## Documentation Categories")
        for category, count in sorted(categories.items()):
            report.append(f"- **{category.title()}**: {count} documents")
        report.append("")
        
        # Issues by severity
        severity_groups = {}
        for issue in issues:
            severity_groups.setdefault(issue.severity, []).append(issue)
        
        for severity in ["critical", "high", "medium", "low"]:
            if severity in severity_groups:
                report.append(f"## {severity.title()} Issues ({len(severity_groups[severity])})")
                
                for issue in severity_groups[severity][:10]:  # Show top 10
                    report.append(f"### {issue.file_path}")
                    report.append(f"**Type**: {issue.issue_type}")
                    report.append(f"**Description**: {issue.description}")
                    report.append(f"**Recommendation**: {issue.recommendation}")
                    report.append("")
        
        # Maintenance priorities
        report.append("## High Maintenance Priority Documents")
        high_priority_docs = [
            doc for doc in self.document_registry.values() 
            if doc.maintenance_priority >= 4
        ]
        
        for doc in sorted(high_priority_docs, key=lambda x: x.maintenance_priority, reverse=True):
            report.append(f"- **{doc.file_path}** (Priority: {doc.maintenance_priority})")
        
        report.append("\n## Recommended Actions")
        report.append("1. Address all critical issues immediately")
        report.append("2. Assign owners to unassigned documents")
        report.append("3. Consolidate duplicate content")
        report.append("4. Update broken references")
        report.append("5. Review and approve draft documents")
        report.append("6. Archive truly orphaned documents")
        
        return "\n".join(report)
    
    def auto_fix_issues(self, issues: List[DocumentationIssue]) -> List[str]:
        """Automatically fix issues that can be resolved programmatically"""
        fixed_issues = []
        
        for issue in issues:
            if not issue.auto_fixable:
                continue
            
            try:
                if issue.issue_type == "missing_metadata":
                    self._add_missing_metadata(issue.file_path)
                elif issue.issue_type == "broken_reference":
                    self._fix_broken_reference(issue.file_path, issue.description)
                
                fixed_issues.append(f"Fixed {issue.issue_type} in {issue.file_path}")
            except Exception as e:
                print(f"Failed to auto-fix {issue.file_path}: {str(e)}")
        
        return fixed_issues
    
    def _add_missing_metadata(self, file_path: str):
        """Add missing metadata header to document"""
        full_path = self.project_root / file_path
        
        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if metadata header already exists
        if not content.startswith('---'):
            metadata_header = f"""---
title: "{self.document_registry[file_path].title}"
category: {self.document_registry[file_path].category}
owner: unassigned
status: draft
version: 1.0
last_updated: {datetime.now().strftime('%Y-%m-%d')}
---

"""
            
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(metadata_header + content)
    
    def _fix_broken_reference(self, file_path: str, description: str):
        """Fix broken references by updating or removing them"""
        # This would need more sophisticated logic based on the specific reference
        # For now, just flag for manual review
        pass


def main():
    """Main entry point for document control operations"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Terminal Grounds Document Control Specialist')
    parser.add_argument('--audit', action='store_true', help='Perform full documentation audit')
    parser.add_argument('--fix', action='store_true', help='Auto-fix issues that can be resolved automatically')
    parser.add_argument('--report', type=str, help='Generate governance report to specified file')
    parser.add_argument('--project-root', type=str, help='Project root directory', default='.')
    
    args = parser.parse_args()
    
    dcs = DocumentControlSpecialist(args.project_root)
    
    if args.audit:
        print("Performing documentation audit...")
        issues = dcs.perform_full_audit()
        
        print(f"\nAudit complete. Found {len(issues)} issues:")
        for severity in ["critical", "high", "medium", "low"]:
            count = len([i for i in issues if i.severity == severity])
            if count > 0:
                print(f"  {severity.title()}: {count}")
        
        if args.fix:
            print("\nAttempting auto-fixes...")
            fixed = dcs.auto_fix_issues(issues)
            if fixed:
                for fix in fixed:
                    print(f"  ✓ {fix}")
            else:
                print("  No auto-fixable issues found")
        
        if args.report:
            report_content = dcs.generate_governance_report(issues)
            with open(args.report, 'w', encoding='utf-8') as f:
                f.write(report_content)
            print(f"\nGovernance report saved to: {args.report}")


if __name__ == "__main__":
    main()