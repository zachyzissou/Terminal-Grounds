#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Terminal Grounds AI Documentation Assistant
Intelligent documentation management with automated consolidation and quality control
"""

import os
import json
import sqlite3
import hashlib
import shutil
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from doc_graph_database import DocumentGraphDatabase
import re

class DocumentAssistant:
    """AI-powered documentation consolidation and management assistant"""
    
    def __init__(self, project_root: str = "C:/Users/Zachg/Terminal-Grounds"):
        self.project_root = Path(project_root)
        self.doc_db = DocumentGraphDatabase(project_root)
        self.archive_dir = self.project_root / "Docs/Archive"
        self.consolidated_dir = self.project_root / "Docs/Consolidated"
        self.governance_rules = self.load_governance_rules()
        
    def load_governance_rules(self) -> Dict:
        """Load documentation governance rules"""
        return {
            'min_quality_score': 50,
            'min_word_count': 20,
            'max_duplicate_similarity': 0.85,
            'required_metadata': ['title', 'category', 'owner', 'last_updated'],
            'review_cycle_days': 90,
            'auto_archive_days': 180,
            'priority_categories': ['design', 'technical', 'lore']
        }
        
    def execute_consolidation_plan(self) -> Dict[str, int]:
        """Execute the full consolidation plan"""
        print("\n=== EXECUTING DOCUMENTATION CONSOLIDATION PLAN ===\n")
        
        stats = {
            'merged': 0,
            'archived': 0,
            'updated': 0,
            'errors': 0
        }
        
        # Get consolidation plan from database
        plan = self.doc_db.generate_consolidation_plan()
        
        # 1. Process immediate merges (identical content)
        print(f"Processing {len(plan['immediate_actions'])} identical document merges...")
        for action in plan['immediate_actions'][:10]:  # Process first 10 for safety
            try:
                if self.merge_identical_documents(action['files']):
                    stats['merged'] += 1
            except Exception as e:
                print(f"  Error merging {action['files'][0]}: {e}")
                stats['errors'] += 1
                
        # 2. Archive low-quality documents
        print(f"\nArchiving {len(plan['archive_candidates'])} low-quality documents...")
        for candidate in plan['archive_candidates']:
            try:
                if self.archive_document(candidate['file'], candidate['reason']):
                    stats['archived'] += 1
            except Exception as e:
                print(f"  Error archiving {candidate['file']}: {e}")
                stats['errors'] += 1
                
        # 3. Consolidate roadmaps
        print("\nConsolidating roadmap documents...")
        roadmap_count = self.consolidate_roadmaps()
        stats['updated'] += roadmap_count
        
        # 4. Clean up MCP directories
        print("\nCleaning up MCP integration directories...")
        mcp_count = self.consolidate_mcp_docs()
        stats['updated'] += mcp_count
        
        return stats
        
    def merge_identical_documents(self, file_paths: List[str]) -> bool:
        """Merge identical documents, keeping the most canonical location"""
        if len(file_paths) < 2:
            return False
            
        # Determine canonical file (prefer Docs/ over other locations)
        canonical = None
        for path in file_paths:
            if 'Docs/' in path or 'docs/' in path:
                canonical = path
                break
        if not canonical:
            canonical = file_paths[0]  # Use first if no docs folder
            
        canonical_path = self.project_root / canonical
        if not canonical_path.exists():
            return False
            
        # Archive and remove duplicates
        for path in file_paths:
            if path != canonical:
                duplicate_path = self.project_root / path
                if duplicate_path.exists():
                    # Create reference file pointing to canonical
                    ref_content = f"# Document Moved\n\nThis document has been consolidated.\n\nCanonical location: [{canonical}](/{canonical})\n"
                    duplicate_path.write_text(ref_content, encoding='utf-8')
                    print(f"  Merged: {path} -> {canonical}")
                    
        return True
        
    def archive_document(self, file_path: str, reason: str) -> bool:
        """Archive a low-quality or obsolete document"""
        source_path = self.project_root / file_path
        if not source_path.exists():
            return False
            
        # Create archive directory structure
        archive_subdir = self.archive_dir / datetime.now().strftime("%Y-%m-%d")
        archive_subdir.mkdir(parents=True, exist_ok=True)
        
        # Move to archive with metadata
        archive_path = archive_subdir / source_path.name
        shutil.move(str(source_path), str(archive_path))
        
        # Create archive metadata
        metadata = {
            'original_path': file_path,
            'archived_date': datetime.now().isoformat(),
            'reason': reason
        }
        metadata_path = archive_path.with_suffix('.meta.json')
        metadata_path.write_text(json.dumps(metadata, indent=2))
        
        print(f"  Archived: {file_path} ({reason})")
        return True
        
    def consolidate_roadmaps(self) -> int:
        """Consolidate multiple roadmap documents into master roadmap"""
        # Find all roadmap documents
        conn = sqlite3.connect(self.doc_db.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT path, title, last_updated 
            FROM documents 
            WHERE LOWER(path) LIKE '%roadmap%' 
            ORDER BY last_updated DESC
        """)
        roadmaps = cursor.fetchall()
        conn.close()
        
        if len(roadmaps) <= 1:
            print("  No roadmap consolidation needed")
            return 0
            
        print(f"  Found {len(roadmaps)} roadmap documents to consolidate")
        
        # Create master roadmap
        master_content = [
            "# Terminal Grounds Master Development Roadmap",
            f"\n*Consolidated from {len(roadmaps)} roadmap documents on {datetime.now().strftime('%Y-%m-%d')}*\n",
            "## Roadmap Sources\n"
        ]
        
        # Add source references
        for path, title, updated in roadmaps:
            master_content.append(f"- [{title or Path(path).stem}]({path}) (Updated: {updated})")
            
        master_content.append("\n## Consolidated Development Phases\n")
        
        # Extract and merge content from each roadmap
        phase_content = {}
        for path, _, _ in roadmaps:
            full_path = self.project_root / path
            if full_path.exists():
                content = full_path.read_text(encoding='utf-8')
                # Extract phase information
                phases = re.findall(r'##\s+(Phase \d+[^#]*)', content, re.MULTILINE | re.DOTALL)
                for phase in phases:
                    phase_title = phase.split('\n')[0].strip()
                    if phase_title not in phase_content:
                        phase_content[phase_title] = []
                    phase_content[phase_title].append(phase)
                    
        # Add consolidated phases
        for phase_title, contents in sorted(phase_content.items()):
            master_content.append(f"\n### {phase_title}\n")
            # Merge similar content
            merged = contents[0] if contents else ""
            master_content.append(merged[:500] + "...")  # Truncate for brevity
            
        # Write master roadmap
        master_path = self.project_root / "Docs" / "MASTER_ROADMAP.md"
        master_path.write_text('\n'.join(master_content), encoding='utf-8')
        print(f"  Created: {master_path}")
        
        # Update individual roadmaps with reference
        for path, _, _ in roadmaps[1:]:  # Skip the newest one
            ref_path = self.project_root / path
            if ref_path.exists() and 'MASTER_ROADMAP' not in str(ref_path):
                ref_content = ref_path.read_text(encoding='utf-8')
                if '# Document Consolidated' not in ref_content:
                    header = "# Document Consolidated\n\n> **Note**: This roadmap has been consolidated into the [Master Roadmap](/Docs/MASTER_ROADMAP.md)\n\n---\n\n"
                    ref_path.write_text(header + ref_content, encoding='utf-8')
                    
        return len(roadmaps)
        
    def consolidate_mcp_docs(self) -> int:
        """Consolidate duplicate MCP documentation"""
        # Find all MCP-related directories
        mcp_dirs = []
        for pattern in ['*mcp*', '*MCP*', 'unreal-*-mcp', 'binary-reader-mcp']:
            mcp_dirs.extend(self.project_root.glob(pattern))
            
        consolidated_count = 0
        
        # Create consolidated MCP directory
        mcp_master = self.project_root / "Docs" / "MCP_Integration"
        mcp_master.mkdir(parents=True, exist_ok=True)
        
        # Consolidate README files
        for mcp_dir in mcp_dirs:
            if mcp_dir.is_dir():
                readme = mcp_dir / "README.md"
                if readme.exists():
                    # Copy to consolidated location with source prefix
                    dest_name = f"{mcp_dir.name}_README.md"
                    dest_path = mcp_master / dest_name
                    shutil.copy2(readme, dest_path)
                    consolidated_count += 1
                    print(f"  Consolidated: {readme} -> {dest_path}")
                    
        # Create index file
        index_content = [
            "# MCP Integration Documentation",
            f"\n*Consolidated from {len(mcp_dirs)} MCP directories on {datetime.now().strftime('%Y-%m-%d')}*\n",
            "## MCP Components\n"
        ]
        
        for mcp_dir in mcp_dirs:
            if mcp_dir.is_dir():
                index_content.append(f"- **{mcp_dir.name}**: {mcp_dir}")
                
        index_path = mcp_master / "README.md"
        index_path.write_text('\n'.join(index_content), encoding='utf-8')
        
        return consolidated_count
        
    def generate_quality_report(self) -> str:
        """Generate comprehensive quality report"""
        stats = self.doc_db.get_documentation_stats()
        conflicts = self.doc_db.find_conflicting_documents()
        
        report = [
            "# Documentation Quality Report",
            f"\n*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}*\n",
            "## Summary Statistics\n",
            f"- **Total Documents**: {sum(stats['by_category'].values())}",
            f"- **Average Quality Score**: {stats['average_scores']['quality']:.1f}/100",
            f"- **Duplicate Pairs**: {stats['duplicate_pairs']}",
            f"- **Cross-references**: {stats['relationships']}\n",
            "## Quality Distribution\n"
        ]
        
        for level, count in stats['quality_distribution'].items():
            report.append(f"- **{level.title()}**: {count} documents")
            
        report.append("\n## Categories\n")
        for category, count in sorted(stats['by_category'].items(), key=lambda x: x[1], reverse=True):
            report.append(f"- **{category.title()}**: {count} documents")
            
        if conflicts:
            report.append(f"\n## Conflicts Found ({len(conflicts)})\n")
            for path1, path2, conflict_type in conflicts[:10]:  # Show first 10
                report.append(f"- {conflict_type}: `{path1}` vs `{path2}`")
                
        return '\n'.join(report)
        
    def implement_governance(self) -> None:
        """Implement automated governance rules"""
        print("\n=== IMPLEMENTING DOCUMENTATION GOVERNANCE ===\n")
        
        # Create governance structure
        gov_dir = self.project_root / "Docs" / "Governance"
        gov_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate quality report
        report = self.generate_quality_report()
        report_path = gov_dir / f"Quality_Report_{datetime.now().strftime('%Y%m%d')}.md"
        report_path.write_text(report, encoding='utf-8')
        print(f"Generated quality report: {report_path}")
        
        # Create documentation template
        template = """# [Document Title]

## Metadata
- **Category**: [design|technical|lore|guide|tooling|content]
- **Owner**: [Team/Person]
- **Priority**: [1-5]
- **Last Updated**: [YYYY-MM-DD]
- **Status**: [draft|review|approved|deprecated]

## Overview
[Brief description of this document's purpose]

## Content
[Main content goes here]

## References
- [Related Document 1](link)
- [Related Document 2](link)

## Change Log
- [YYYY-MM-DD]: Initial creation
"""
        
        template_path = gov_dir / "TEMPLATE.md"
        template_path.write_text(template, encoding='utf-8')
        print(f"Created documentation template: {template_path}")
        
        # Create governance rules document
        rules = """# Documentation Governance Rules

## Quality Standards
- Minimum quality score: 50/100
- Minimum word count: 20 words
- Required metadata fields: title, category, owner, last_updated

## Review Cycles
- Priority 1-2: Review every 30 days
- Priority 3-4: Review every 90 days
- Priority 5: Review every 180 days

## Automatic Actions
- Archive documents unchanged for 180+ days
- Merge identical documents automatically
- Flag conflicts for manual review

## Categories
1. **Design**: Game design documents, feature specs
2. **Technical**: Architecture, API docs, implementation guides
3. **Lore**: World building, story, character backgrounds
4. **Guide**: How-to guides, tutorials, walkthroughs
5. **Tooling**: Tool documentation, scripts, automation
6. **Content**: Asset lists, content specifications

## Naming Conventions
- Use descriptive names with underscores: `Feature_Name_Type.md`
- Include version in filename for specs: `System_Name_v1.2.md`
- Prefix with date for time-sensitive docs: `2025_01_31_Meeting_Notes.md`
"""
        
        rules_path = gov_dir / "GOVERNANCE_RULES.md"
        rules_path.write_text(rules, encoding='utf-8')
        print(f"Created governance rules: {rules_path}")
        
if __name__ == '__main__':
    # Initialize the documentation assistant
    print("Initializing Terminal Grounds Documentation Assistant...")
    assistant = DocumentAssistant()
    
    # First, scan the documentation
    print("\nScanning documentation with graph database...")
    scan_stats = assistant.doc_db.scan_documentation()
    print(f"Scanned {scan_stats['total_files']} documents")
    
    # Execute consolidation plan
    consolidation_stats = assistant.execute_consolidation_plan()
    print("\n=== CONSOLIDATION COMPLETE ===")
    print(f"  Documents Merged: {consolidation_stats['merged']}")
    print(f"  Documents Archived: {consolidation_stats['archived']}")
    print(f"  Documents Updated: {consolidation_stats['updated']}")
    print(f"  Errors: {consolidation_stats['errors']}")
    
    # Implement governance
    assistant.implement_governance()
    
    print("\n=== DOCUMENTATION ASSISTANT COMPLETE ===")