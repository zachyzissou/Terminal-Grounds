# -*- coding: utf-8 -*-
"""
Inspect CTO Database Schema
Understand the actual table structure for proper AI integration
"""

import sqlite3
from pathlib import Path

def inspect_database():
    """Inspect CTO territorial database structure"""
    db_path = Path("C:/Users/Zachg/Terminal-Grounds/Database/territorial_system.db")
    
    print("CTO DATABASE SCHEMA INSPECTION")
    print("=" * 50)
    
    if not db_path.exists():
        print(f"ERROR: Database not found at {db_path}")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        print(f"TABLES FOUND: {len(tables)}")
        
        for (table_name,) in tables:
            print(f"\nTABLE: {table_name}")
            print("-" * 30)
            
            # Get table schema
            cursor.execute(f"PRAGMA table_info({table_name});")
            columns = cursor.fetchall()
            
            for column in columns:
                cid, name, data_type, notnull, default, pk = column
                pk_indicator = " (PRIMARY KEY)" if pk else ""
                null_indicator = " NOT NULL" if notnull else ""
                default_indicator = f" DEFAULT {default}" if default else ""
                
                print(f"  {name}: {data_type}{pk_indicator}{null_indicator}{default_indicator}")
            
            # Get row count
            cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
            count = cursor.fetchone()[0]
            print(f"  Rows: {count}")
            
            # Show sample data if table has rows
            if count > 0 and count <= 10:
                cursor.execute(f"SELECT * FROM {table_name} LIMIT 3;")
                samples = cursor.fetchall()
                
                if samples:
                    print("  Sample data:")
                    for i, row in enumerate(samples):
                        print(f"    Row {i+1}: {row}")
        
        conn.close()
        
    except Exception as e:
        print(f"ERROR: Database inspection failed - {e}")

if __name__ == "__main__":
    inspect_database()