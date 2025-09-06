#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Auto-refresh documentation dashboard every 5 minutes
"""

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
            print("\nStopping auto-refresh...")
            break
        except Exception as e:
            print(f"Error updating dashboard: {e}")
            time.sleep(300)

if __name__ == '__main__':
    main()
