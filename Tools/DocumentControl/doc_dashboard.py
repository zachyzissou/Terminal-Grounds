#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Terminal Grounds Documentation Dashboard
Real-time monitoring and visualization of documentation health
"""

import os
import json
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from doc_graph_database import DocumentGraphDatabase
from doc_assistant import DocumentAssistant
import time

class DocumentationDashboard:
    """Real-time documentation monitoring dashboard"""
    
    def __init__(self, project_root: str = "C:/Users/Zachg/Terminal-Grounds"):
        self.project_root = Path(project_root)
        self.doc_db = DocumentGraphDatabase(project_root)
        self.assistant = DocumentAssistant(project_root)
        self.dashboard_path = self.project_root / "Docs" / "Dashboard"
        self.dashboard_path.mkdir(parents=True, exist_ok=True)
        
    def generate_dashboard_html(self) -> str:
        """Generate HTML dashboard with real-time statistics"""
        stats = self.doc_db.get_documentation_stats()
        total_docs = sum(stats['by_category'].values())
        
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Terminal Grounds Documentation Dashboard</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #0a0e27 0%, #1a1f3a 100%);
            color: #e0e0e0;
            margin: 0;
            padding: 20px;
        }}
        .dashboard {{
            max-width: 1400px;
            margin: 0 auto;
        }}
        .header {{
            text-align: center;
            padding: 30px;
            background: rgba(0,0,0,0.3);
            border-radius: 10px;
            margin-bottom: 30px;
        }}
        h1 {{
            color: #00ffcc;
            font-size: 2.5em;
            margin: 0;
            text-shadow: 0 0 20px rgba(0,255,204,0.5);
        }}
        .timestamp {{
            color: #888;
            margin-top: 10px;
        }}
        .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .card {{
            background: rgba(30,35,60,0.8);
            border: 1px solid rgba(0,255,204,0.3);
            border-radius: 8px;
            padding: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.3);
            transition: transform 0.3s;
        }}
        .card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 8px 12px rgba(0,255,204,0.2);
        }}
        .card h3 {{
            color: #00ffcc;
            margin-top: 0;
            font-size: 1.2em;
        }}
        .metric {{
            font-size: 2em;
            font-weight: bold;
            color: #fff;
            margin: 10px 0;
        }}
        .metric.good {{
            color: #00ff88;
        }}
        .metric.warning {{
            color: #ffaa00;
        }}
        .metric.bad {{
            color: #ff4444;
        }}
        .progress-bar {{
            background: rgba(0,0,0,0.4);
            border-radius: 10px;
            height: 20px;
            overflow: hidden;
            margin: 10px 0;
        }}
        .progress-fill {{
            height: 100%;
            background: linear-gradient(90deg, #00ffcc, #00ff88);
            transition: width 0.5s;
        }}
        .category-list {{
            list-style: none;
            padding: 0;
        }}
        .category-list li {{
            padding: 8px;
            margin: 5px 0;
            background: rgba(0,0,0,0.3);
            border-left: 3px solid #00ffcc;
            display: flex;
            justify-content: space-between;
        }}
        .quality-grid {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 10px;
            margin-top: 15px;
        }}
        .quality-item {{
            padding: 10px;
            background: rgba(0,0,0,0.3);
            border-radius: 5px;
            text-align: center;
        }}
        .alerts {{
            background: rgba(255,68,68,0.1);
            border: 1px solid rgba(255,68,68,0.3);
            border-radius: 8px;
            padding: 20px;
            margin-top: 30px;
        }}
        .alerts h3 {{
            color: #ff4444;
        }}
        .alert-item {{
            padding: 10px;
            margin: 10px 0;
            background: rgba(0,0,0,0.3);
            border-left: 3px solid #ff4444;
        }}
        .refresh-btn {{
            background: linear-gradient(135deg, #00ffcc, #00ff88);
            color: #000;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            font-weight: bold;
            cursor: pointer;
            margin-top: 10px;
        }}
        .refresh-btn:hover {{
            transform: scale(1.05);
        }}
    </style>
    <script>
        function autoRefresh() {{
            setTimeout(function(){{
                location.reload();
            }}, 60000); // Refresh every 60 seconds
        }}
        window.onload = autoRefresh;
    </script>
</head>
<body>
    <div class="dashboard">
        <div class="header">
            <h1>Terminal Grounds Documentation Dashboard</h1>
            <div class="timestamp">Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>
            <button class="refresh-btn" onclick="location.reload()">Refresh Now</button>
        </div>
        
        <div class="grid">
            <div class="card">
                <h3>Total Documents</h3>
                <div class="metric">{total_docs}</div>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: 100%"></div>
                </div>
                <small>Across all categories</small>
            </div>
            
            <div class="card">
                <h3>Average Quality Score</h3>
                <div class="metric {'good' if stats['average_scores']['quality'] >= 80 else 'warning' if stats['average_scores']['quality'] >= 60 else 'bad'}">{stats['average_scores']['quality']:.1f}%</div>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: {stats['average_scores']['quality']}%"></div>
                </div>
                <small>Target: 85%</small>
            </div>
            
            <div class="card">
                <h3>Duplicate Pairs</h3>
                <div class="metric {'good' if stats['duplicate_pairs'] < 100 else 'warning' if stats['duplicate_pairs'] < 500 else 'bad'}">{stats['duplicate_pairs']}</div>
                <small>Documents with similar content</small>
            </div>
            
            <div class="card">
                <h3>Cross-References</h3>
                <div class="metric good">{stats['relationships']}</div>
                <small>Internal documentation links</small>
            </div>
        </div>
        
        <div class="grid">
            <div class="card">
                <h3>Quality Distribution</h3>
                <div class="quality-grid">
                    <div class="quality-item">
                        <div style="color: #00ff88;">Excellent</div>
                        <div class="metric">{stats['quality_distribution']['excellent']}</div>
                    </div>
                    <div class="quality-item">
                        <div style="color: #00ffcc;">Good</div>
                        <div class="metric">{stats['quality_distribution']['good']}</div>
                    </div>
                    <div class="quality-item">
                        <div style="color: #ffaa00;">Fair</div>
                        <div class="metric">{stats['quality_distribution']['fair']}</div>
                    </div>
                    <div class="quality-item">
                        <div style="color: #ff4444;">Poor</div>
                        <div class="metric">{stats['quality_distribution']['poor']}</div>
                    </div>
                </div>
            </div>
            
            <div class="card">
                <h3>Categories</h3>
                <ul class="category-list">
                    {"".join([f'<li><span>{cat.title()}</span><span>{count}</span></li>' for cat, count in sorted(stats['by_category'].items(), key=lambda x: x[1], reverse=True)[:6]])}
                </ul>
            </div>
        </div>
        
        {self._generate_alerts_html()}
        
    </div>
</body>
</html>"""
        return html
        
    def _generate_alerts_html(self) -> str:
        """Generate alerts section for critical issues"""
        alerts = []
        
        # Check for conflicts
        conflicts = self.doc_db.find_conflicting_documents()
        if len(conflicts) > 0:
            alerts.append(f"Found {len(conflicts)} conflicting documents requiring review")
            
        # Check for outdated documents
        conn = sqlite3.connect(self.doc_db.db_path)
        cursor = conn.cursor()
        
        cutoff_date = datetime.now() - timedelta(days=90)
        cursor.execute("""
            SELECT COUNT(*) FROM documents 
            WHERE last_updated < ? AND category IN ('design', 'technical')
        """, (cutoff_date,))
        outdated = cursor.fetchone()[0]
        if outdated > 0:
            alerts.append(f"{outdated} critical documents haven't been updated in 90+ days")
            
        # Check for missing metadata
        cursor.execute("""
            SELECT COUNT(*) FROM documents 
            WHERE title IS NULL OR category = 'general'
        """)
        missing_meta = cursor.fetchone()[0]
        if missing_meta > 50:
            alerts.append(f"{missing_meta} documents missing proper metadata")
            
        conn.close()
        
        if not alerts:
            return ""
            
        alerts_html = '<div class="alerts"><h3>Action Required</h3>'
        for alert in alerts:
            alerts_html += f'<div class="alert-item">{alert}</div>'
        alerts_html += '</div>'
        
        return alerts_html
        
    def generate_markdown_report(self) -> str:
        """Generate markdown report for documentation"""
        stats = self.doc_db.get_documentation_stats()
        plan = self.doc_db.generate_consolidation_plan()
        
        report = f"""# Terminal Grounds Documentation Status

*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}*

## Overview

The Terminal Grounds project currently has **{sum(stats['by_category'].values())} documentation files** with an average quality score of **{stats['average_scores']['quality']:.1f}/100**.

## Key Metrics

| Metric | Value | Status |
|--------|-------|---------|
| Total Documents | {sum(stats['by_category'].values())} | {'🟢' if sum(stats['by_category'].values()) < 500 else '🟡' if sum(stats['by_category'].values()) < 1000 else '🔴'} |
| Average Quality | {stats['average_scores']['quality']:.1f}% | {'🟢' if stats['average_scores']['quality'] >= 80 else '🟡' if stats['average_scores']['quality'] >= 60 else '🔴'} |
| Duplicate Pairs | {stats['duplicate_pairs']} | {'🟢' if stats['duplicate_pairs'] < 100 else '🟡' if stats['duplicate_pairs'] < 500 else '🔴'} |
| Cross-references | {stats['relationships']} | {'🟢' if stats['relationships'] > 20 else '🟡' if stats['relationships'] > 10 else '🔴'} |

## Categories

| Category | Count | Percentage |
|----------|-------|------------|
"""
        
        total = sum(stats['by_category'].values())
        for cat, count in sorted(stats['by_category'].items(), key=lambda x: x[1], reverse=True):
            percentage = (count / total * 100) if total > 0 else 0
            report += f"| {cat.title()} | {count} | {percentage:.1f}% |\n"
            
        report += f"""

## Quality Distribution

- **Excellent (85-100)**: {stats['quality_distribution']['excellent']} documents
- **Good (70-85)**: {stats['quality_distribution']['good']} documents
- **Fair (50-70)**: {stats['quality_distribution']['fair']} documents
- **Poor (<50)**: {stats['quality_distribution']['poor']} documents

## Recommended Actions

1. **Immediate Merges**: {len(plan['immediate_actions'])} identical documents
2. **Review Required**: {len(plan['review_required'])} similar documents
3. **Archive Candidates**: {len(plan['archive_candidates'])} low-quality documents

## Recent Consolidation

- ✅ Merged 10 identical documents
- ✅ Archived 16 low-quality files
- ✅ Consolidated 7 roadmaps into MASTER_ROADMAP.md
- ✅ Organized 11 MCP integrations

## Next Steps

1. Process remaining duplicate merges
2. Review high-similarity document pairs
3. Update metadata for 'general' category documents
4. Establish regular review cycles for critical documentation

---
*Auto-refresh enabled - Updates every 60 seconds*
"""
        return report
        
    def create_dashboard(self):
        """Create and save dashboard files"""
        print("\n=== CREATING DOCUMENTATION DASHBOARD ===\n")
        
        # Generate HTML dashboard
        html = self.generate_dashboard_html()
        html_path = self.dashboard_path / "index.html"
        html_path.write_text(html, encoding='utf-8')
        print(f"Created HTML dashboard: {html_path}")
        
        # Generate markdown report
        report = self.generate_markdown_report()
        report_path = self.dashboard_path / "STATUS_REPORT.md"
        report_path.write_text(report, encoding='utf-8')
        print(f"Created status report: {report_path}")
        
        # Create auto-refresh script
        script = """#!/usr/bin/env python3
# -*- coding: utf-8 -*-
\"\"\"
Auto-refresh documentation dashboard every 5 minutes
\"\"\"

import time
from pathlib import Path
import sys

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from doc_dashboard import DocumentationDashboard

def main():
    dashboard = DocumentationDashboard()
    
    print("Starting documentation dashboard auto-refresh...")
    print("Dashboard will update every 5 minutes")
    print("Press Ctrl+C to stop")
    
    while True:
        try:
            dashboard.create_dashboard()
            print(f"Dashboard updated at {time.strftime('%Y-%m-%d %H:%M:%S')}")
            time.sleep(300)  # 5 minutes
        except KeyboardInterrupt:
            print("\\nStopping auto-refresh...")
            break
        except Exception as e:
            print(f"Error updating dashboard: {e}")
            time.sleep(300)

if __name__ == '__main__':
    main()
"""
        
        script_path = self.dashboard_path / "auto_refresh.py"
        script_path.write_text(script, encoding='utf-8')
        print(f"Created auto-refresh script: {script_path}")
        
        print("\n✅ Dashboard created successfully!")
        print(f"📊 View at: {html_path}")
        print(f"🔄 Auto-refresh: python {script_path}")
        
if __name__ == '__main__':
    dashboard = DocumentationDashboard()
    dashboard.create_dashboard()