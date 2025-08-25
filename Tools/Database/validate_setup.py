#!/usr/bin/env python3
"""
Database Setup Validation and Initial Data Population
Week 1 Priority Task - CDO Implementation
"""

import psycopg2
import json
from datetime import datetime

def validate_database_setup():
    """Validate database setup and create initial territorial hierarchy"""
    
    # Database connection (adjust as needed for your setup)
    db_config = {
        'host': 'localhost',
        'database': 'terminal_grounds_territorial',
        'user': 'postgres',  # Use postgres for initial setup
        'password': 'your_password',  # Update with actual password
        'port': 5432
    }
    
    try:
        print("🔍 Connecting to Terminal Grounds territorial database...")
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()
        
        # Test basic connection
        cursor.execute("SELECT version()")
        version = cursor.fetchone()
        print(f"✅ Connected to PostgreSQL: {version[0]}")
        
        # Check PostGIS extension
        cursor.execute("SELECT PostGIS_Version()")
        postgis_version = cursor.fetchone()
        print(f"✅ PostGIS extension active: {postgis_version[0]}")
        
        # Validate required tables exist
        print("\n📊 Validating database schema...")
        required_tables = [
            'regions', 'districts', 'control_points', 'factions',
            'faction_influence', 'influence_history', 'ai_decisions'
        ]
        
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
        """)
        existing_tables = [row[0] for row in cursor.fetchall()]
        
        missing_tables = []
        for table in required_tables:
            if table in existing_tables:
                print(f"✅ Table exists: {table}")
            else:
                missing_tables.append(table)
                print(f"❌ Missing table: {table}")
        
        if missing_tables:
            print(f"\n🚨 Database setup incomplete. Missing tables: {missing_tables}")
            print("Please run: Tools/Database/setup_territorial_database.sql")
            return False
        
        # Validate faction data
        print("\n🏛️ Validating faction initialization...")
        cursor.execute("SELECT faction_id, name, influence_modifier FROM factions ORDER BY faction_id")
        factions = cursor.fetchall()
        
        expected_factions = [
            'Directorate', 'Free77', 'Nomad Clans', 'Civic Wardens',
            'Vultures Union', 'Vaulted Archivists', 'Corporate Combine'
        ]
        
        for i, (faction_id, name, modifier) in enumerate(factions):
            if i < len(expected_factions) and name == expected_factions[i]:
                print(f"✅ Faction {faction_id}: {name} (modifier: {modifier})")
            else:
                print(f"⚠️ Faction data mismatch: {name}")
        
        # Test stored procedures
        print("\n🔧 Testing stored procedures...")
        try:
            # Test influence update procedure
            cursor.execute("SELECT update_territory_influence('region', 1, 1, 25, 'validation_test')")
            result = cursor.fetchone()
            if result[0]:
                print("✅ Influence update procedure working")
            else:
                print("❌ Influence update procedure failed")
            
            # Test territorial state query
            cursor.execute("SELECT get_territorial_state('region', 1)")
            state_result = cursor.fetchone()
            if state_result[0]:
                print("✅ Territorial state query working")
            else:
                print("❌ Territorial state query failed")
                
            conn.commit()
            
        except Exception as e:
            print(f"❌ Stored procedure test failed: {e}")
            conn.rollback()
        
        # Create initial district and control point structure
        print("\n🗺️ Creating initial territorial structure...")
        create_initial_territories(cursor, conn)
        
        cursor.close()
        conn.close()
        
        print("\n✅ Database validation completed successfully!")
        print("🎯 Ready for Week 1 development tasks")
        return True
        
    except psycopg2.Error as e:
        print(f"❌ Database connection failed: {e}")
        print("Please ensure PostgreSQL is running and database exists")
        return False

def create_initial_territories(cursor, conn):
    """Create initial district and control point structure for development"""
    
    # Create districts for each region (simplified structure for Phase 1)
    districts_data = [
        # Tech Wastes districts
        (1, "Primary Salvage Yards", "salvage", 85),
        (1, "Alien Tech Repository", "technology", 95),
        (1, "Industrial Maintenance Hub", "strategic", 70),
        
        # Metro Corridors districts
        (2, "Central Transit Hub", "strategic", 90),
        (2, "Maintenance Tunnels", "intelligence", 60),
        (2, "Emergency Bunkers", "military", 80),
        
        # Corporate Zones districts
        (3, "Executive Plaza", "economic", 95),
        (3, "Data Processing Center", "intelligence", 85),
        (3, "Corporate Security HQ", "military", 90),
        
        # Residential Districts
        (4, "Civilian Evacuation Center", "civilian", 75),
        (4, "Community Resource Hub", "salvage", 65),
        
        # Military Compounds districts
        (5, "Forward Operating Base", "military", 100),
        (5, "Weapons Testing Facility", "technology", 90),
        
        # Research Facilities districts
        (6, "Primary Research Lab", "technology", 95),
        (6, "Data Archive Vault", "intelligence", 85),
        
        # Trade Routes districts
        (7, "Central Marketplace", "economic", 80),
        (7, "Transportation Hub", "strategic", 75),
        
        # Neutral Ground districts
        (8, "Diplomatic Quarter", "civilian", 60),
        (8, "International Aid Station", "civilian", 65)
    ]
    
    print("Creating district structure...")
    for region_id, name, resource_type, importance in districts_data:
        try:
            cursor.execute("""
                INSERT INTO districts (region_id, name, tactical_importance, resource_type)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (region_id, name) DO NOTHING
            """, [region_id, name, importance, resource_type])
        except Exception as e:
            print(f"⚠️ District creation warning: {e}")
    
    conn.commit()
    
    # Get created district IDs for control points
    cursor.execute("SELECT district_id, region_id, name FROM districts ORDER BY district_id")
    districts = cursor.fetchall()
    
    # Create 2-3 control points per district
    control_points_data = []
    for district_id, region_id, district_name in districts[:6]:  # First 6 districts for Phase 1
        # Each district gets a command post and supply depot minimum
        control_points_data.extend([
            (district_id, f"{district_name} Command Post", "command_post", 50, 30),
            (district_id, f"{district_name} Supply Depot", "supply_depot", 25, 40),
        ])
        
        # Strategic districts get additional control points
        if "Hub" in district_name or "HQ" in district_name:
            control_points_data.append(
                (district_id, f"{district_name} Checkpoint", "checkpoint", 40, 20)
            )
    
    print("Creating control point structure...")
    for district_id, name, point_type, radius, difficulty in control_points_data:
        try:
            cursor.execute("""
                INSERT INTO control_points (district_id, name, point_type, control_radius, capture_difficulty)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (district_id, name) DO NOTHING
            """, [district_id, name, point_type, radius, difficulty])
        except Exception as e:
            print(f"⚠️ Control point creation warning: {e}")
    
    conn.commit()
    
    # Initialize basic faction influence (neutral state)
    print("Initializing faction influence...")
    cursor.execute("SELECT region_id FROM regions")
    regions = cursor.fetchall()
    
    for (region_id,) in regions:
        for faction_id in range(1, 8):  # All 7 factions
            initial_influence = 15 if faction_id <= 3 else 10  # Slightly favor first 3 factions initially
            try:
                cursor.execute("""
                    INSERT INTO faction_influence (territory_type, territory_id, faction_id, influence_value)
                    VALUES ('region', %s, %s, %s)
                    ON CONFLICT (territory_type, territory_id, faction_id) DO NOTHING
                """, [region_id, faction_id, initial_influence])
            except Exception as e:
                print(f"⚠️ Initial influence setup warning: {e}")
    
    conn.commit()
    print("✅ Initial territorial structure created")

if __name__ == "__main__":
    print("🚀 Terminal Grounds Database Validation")
    print("=" * 50)
    success = validate_database_setup()
    
    if success:
        print("\n🎯 WEEK 1 TASK COMPLETE: Database foundation validated")
        print("Next: UE5 module compilation and integration")
    else:
        print("\n❌ Database setup issues detected")
        print("Please resolve database connection and schema issues before proceeding")