#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Terminal Grounds Documentation Review Scheduler
Automated review cycles and maintenance tasks
"""

import os
import json
import sqlite3
import schedule
import time
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from doc_graph_database import DocumentGraphDatabase
from doc_assistant import DocumentAssistant
from doc_dashboard import DocumentationDashboard

class DocumentationScheduler:
    """Automated documentation review and maintenance scheduler"""
    
    def __init__(self, project_root: str = "C:/Users/Zachg/Terminal-Grounds"):
        self.project_root = Path(project_root)
        self.doc_db = DocumentGraphDatabase(project_root)
        self.assistant = DocumentAssistant(project_root)
        self.dashboard = DocumentationDashboard(project_root)
        self.schedule_log = self.project_root / "Docs" / "Governance" / "schedule.log"
        
    def log_activity(self, message: str):
        """Log scheduled activity"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(self.schedule_log, 'a', encoding='utf-8') as f:
            f.write(f"[{timestamp}] {message}\\n")
        print(f"[{timestamp}] {message}")
        
    def daily_quality_scan(self):
        """Daily documentation quality scan"""
        self.log_activity("Starting daily quality scan...")
        
        stats = self.doc_db.scan_documentation()
        self.log_activity(f"Scanned {stats['total_files']} files, {stats['new_files']} new, {stats['updated_files']} updated")
        
        # Update dashboard
        self.dashboard.create_dashboard()
        self.log_activity("Dashboard updated")
        
        # Check for critical issues
        doc_stats = self.doc_db.get_documentation_stats()
        if doc_stats['quality_distribution']['poor'] > 10:
            self.log_activity(f"WARNING: {doc_stats['quality_distribution']['poor']} poor quality documents detected")
            
        if doc_stats['duplicate_pairs'] > 1000:
            self.log_activity(f"WARNING: {doc_stats['duplicate_pairs']} duplicate pairs require attention")
            
    def weekly_consolidation(self):
        """Weekly automated consolidation"""
        self.log_activity("Starting weekly consolidation...")
        
        # Execute consolidation plan
        stats = self.assistant.execute_consolidation_plan()
        self.log_activity(f"Consolidation complete: {stats['merged']} merged, {stats['archived']} archived")
        
        # Generate quality report
        report = self.assistant.generate_quality_report()
        report_path = self.project_root / "Docs" / "Governance" / f"Weekly_Report_{datetime.now().strftime('%Y%m%d')}.md"
        report_path.write_text(report, encoding='utf-8')
        self.log_activity(f"Quality report generated: {report_path}")
        
    def monthly_deep_analysis(self):
        """Monthly comprehensive analysis"""
        self.log_activity("Starting monthly deep analysis...")
        
        # Full documentation rescan
        stats = self.doc_db.scan_documentation()
        
        # Analyze trends
        conn = sqlite3.connect(self.doc_db.db_path)
        cursor = conn.cursor()
        
        # Find stale documents
        cutoff_date = datetime.now() - timedelta(days=90)
        cursor.execute("""
            SELECT path, title, last_updated, category
            FROM documents 
            WHERE last_updated < ? AND category IN ('design', 'technical')
            ORDER BY last_updated ASC
            LIMIT 20
        """, (cutoff_date,))
        stale_docs = cursor.fetchall()
        
        # Find orphaned documents (no references)
        cursor.execute("""
            SELECT d.path, d.title, d.category
            FROM documents d
            LEFT JOIN relationships r ON d.id = r.source_doc_id OR d.id = r.target_doc_id
            WHERE r.id IS NULL AND d.category != 'general'
            LIMIT 10
        """)
        orphaned_docs = cursor.fetchall()
        conn.close()
        
        # Generate comprehensive analysis
        analysis = [
            f"# Monthly Documentation Analysis - {datetime.now().strftime('%B %Y')}\\n",
            f"**Total Documents**: {sum(self.doc_db.get_documentation_stats()['by_category'].values())}",
            f"**New This Month**: {stats['new_files']}",
            f"**Updated This Month**: {stats['updated_files']}\\n",
            "## Stale Documents (90+ days old)\\n"
        ]
        
        if stale_docs:
            for path, title, updated, category in stale_docs:
                analysis.append(f"- **{title or Path(path).stem}** ({category}) - Last updated: {updated}")
        else:
            analysis.append("No stale critical documents found.")
            
        analysis.append("\\n## Orphaned Documents (No References)\\n")
        
        if orphaned_docs:
            for path, title, category in orphaned_docs:
                analysis.append(f"- **{title or Path(path).stem}** ({category})")
        else:
            analysis.append("No orphaned documents found.")
            
        analysis.append("\\n## Recommendations\\n")
        analysis.append("1. Review and update stale critical documents")
        analysis.append("2. Add cross-references to orphaned documents")
        analysis.append("3. Continue regular consolidation efforts")
        
        # Save analysis
        analysis_path = self.project_root / "Docs" / "Governance" / f"Monthly_Analysis_{datetime.now().strftime('%Y%m')}.md"
        analysis_path.write_text('\\n'.join(analysis), encoding='utf-8')
        
        self.log_activity(f"Monthly analysis complete: {analysis_path}")
        if stale_docs:
            self.log_activity(f"Found {len(stale_docs)} stale critical documents")
        if orphaned_docs:
            self.log_activity(f"Found {len(orphaned_docs)} orphaned documents")
            
    def setup_schedule(self):
        """Setup automated schedule"""
        # Daily tasks at 9 AM
        schedule.every().day.at("09:00").do(self.daily_quality_scan)
        
        # Weekly tasks on Monday at 10 AM
        schedule.every().monday.at("10:00").do(self.weekly_consolidation)
        
        # Monthly tasks on the 1st at 11 AM
        schedule.every().month.do(self.monthly_deep_analysis)
        
        self.log_activity("Schedule configured:")
        self.log_activity("- Daily quality scan at 9:00 AM")
        self.log_activity("- Weekly consolidation on Monday at 10:00 AM")
        self.log_activity("- Monthly analysis on 1st at 11:00 AM")
        
    def run_scheduler(self):
        """Run the scheduler continuously"""
        self.log_activity("Documentation scheduler started")
        
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
            
    def run_immediate_tasks(self):
        """Run all tasks immediately for testing"""
        self.log_activity("Running immediate test of all scheduled tasks...")
        
        self.daily_quality_scan()
        self.weekly_consolidation()
        self.monthly_deep_analysis()
        
        self.log_activity("All scheduled tasks completed successfully")
        
def main():
    import sys
    
    scheduler = DocumentationScheduler()
    
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        # Run all tasks immediately for testing
        scheduler.run_immediate_tasks()
    elif len(sys.argv) > 1 and sys.argv[1] == "--setup":
        # Just setup schedule and exit
        scheduler.setup_schedule()
        print("Schedule configured. Use --run to start scheduler.")
    elif len(sys.argv) > 1 and sys.argv[1] == "--run":
        # Run scheduler continuously
        scheduler.setup_schedule()
        try:
            scheduler.run_scheduler()
        except KeyboardInterrupt:
            scheduler.log_activity("Scheduler stopped by user")
    else:
        print("Usage: python doc_scheduler.py [--test|--setup|--run]")
        print("  --test   Run all tasks immediately")
        print("  --setup  Configure schedule")
        print("  --run    Start continuous scheduler")

if __name__ == '__main__':
    main()