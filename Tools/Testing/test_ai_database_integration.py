# -*- coding: utf-8 -*-
"""
AI Database Integration Test
Tests AI territorial decision-making with CTO's SQLite database
"""

import sqlite3
import json
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

class MockAITerritorialBehavior:
    """Mock AI behavior for testing database integration"""
    
    def __init__(self, faction_id, faction_name):
        self.faction_id = faction_id
        self.faction_name = faction_name
        self.aggression_level = 0.5
        self.preferred_territories = []
        
    def evaluate_territorial_opportunity(self, territory_data):
        """Evaluate if territory is worth pursuing"""
        # Simple scoring based on strategic value and current controller
        base_score = territory_data.get('strategic_value', 50)
        
        # Higher aggression = more likely to contest
        aggression_bonus = self.aggression_level * 20
        
        # Avoid territories we already control
        if territory_data.get('controller_faction_id') == self.faction_id:
            return 0
        
        total_score = base_score + aggression_bonus
        return min(total_score, 100)
    
    def decide_territorial_action(self, territory_data):
        """Decide what action to take on a territory"""
        opportunity_score = self.evaluate_territorial_opportunity(territory_data)
        
        if opportunity_score > 70:
            return {
                'action_type': 'aggressive_expansion',
                'influence_change': 15,
                'priority': 'high',
                'reasoning': f'High-value target for {self.faction_name}'
            }
        elif opportunity_score > 40:
            return {
                'action_type': 'gradual_influence',
                'influence_change': 8,
                'priority': 'medium', 
                'reasoning': f'Moderate expansion opportunity for {self.faction_name}'
            }
        else:
            return {
                'action_type': 'maintain_position',
                'influence_change': 0,
                'priority': 'low',
                'reasoning': f'No immediate interest for {self.faction_name}'
            }

class TerritorialAIIntegrationTest:
    """Test AI integration with CTO territorial database"""
    
    def __init__(self):
        self.db_path = Path("C:/Users/Zachg/Terminal-Grounds/Database/territorial_system.db")
        self.faction_ais = {}
        self.initialize_faction_ais()
    
    def initialize_faction_ais(self):
        """Initialize mock AI for each faction"""
        # Create AI for first 3 factions as specified in Week 2 plan
        factions = [
            (1, "Directorate", 0.4),      # Corporate efficiency - moderate aggression
            (2, "Free77", 0.8),           # Guerrilla warfare - high aggression  
            (3, "Nomad Clans", 0.3)       # Environmental mastery - low aggression
        ]
        
        for faction_id, name, aggression in factions:
            ai = MockAITerritorialBehavior(faction_id, name)
            ai.aggression_level = aggression
            self.faction_ais[faction_id] = ai
            
        print(f"AI INITIALIZED: {len(self.faction_ais)} faction AIs ready")
    
    def test_database_connection(self):
        """Test connection to CTO territorial database"""
        print("DATABASE CONNECTION TEST")
        print("-" * 40)
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Test basic queries
            cursor.execute("SELECT COUNT(*) FROM factions")
            faction_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM territories")  
            territory_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM territorial_influence")
            influence_count = cursor.fetchone()[0]
            
            print(f"SUCCESS: Database connection established")
            print(f"  -> Factions: {faction_count}")
            print(f"  -> Territories: {territory_count}")
            print(f"  -> Influence relationships: {influence_count}")
            
            conn.close()
            return True
            
        except Exception as e:
            print(f"ERROR: Database connection failed - {e}")
            return False
    
    def test_territorial_queries(self):
        """Test territorial state queries for AI decision-making"""
        print("\nTERRITORIAL QUERY TEST")
        print("-" * 40)
        
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row  # Enable column access by name
            cursor = conn.cursor()
            
            # Query territorial state - what AI needs for decisions
            query = """
            SELECT 
                t.id,
                t.name,
                t.strategic_value,
                t.controller_faction_id,
                f.name as controller_name,
                COALESCE(SUM(CASE WHEN ti.influence_value > 0 THEN 1 ELSE 0 END), 0) as active_factions
            FROM territories t
            LEFT JOIN factions f ON t.controller_faction_id = f.id
            LEFT JOIN territorial_influence ti ON t.id = ti.territory_id
            GROUP BY t.id, t.name, t.strategic_value, t.controller_faction_id, f.name
            ORDER BY t.strategic_value DESC
            """
            
            cursor.execute(query)
            territories = cursor.fetchall()
            
            print(f"TERRITORIAL STATE QUERY: {len(territories)} territories")
            
            for territory in territories:
                print(f"  -> {territory['name']}: "
                      f"Value={territory['strategic_value']}, "
                      f"Controller={territory['controller_name'] or 'None'}, "
                      f"Active factions={territory['active_factions']}")
            
            conn.close()
            return territories
            
        except Exception as e:
            print(f"ERROR: Territorial query failed - {e}")
            return []
    
    def test_ai_decision_making(self, territories):
        """Test AI decision-making with real territorial data"""
        print("\nAI DECISION-MAKING TEST")
        print("-" * 40)
        
        decisions_made = 0
        
        for territory in territories:
            territory_dict = dict(territory)  # Convert Row to dict
            
            print(f"\nTERRITORY: {territory_dict['name']}")
            
            for faction_id, ai in self.faction_ais.items():
                decision = ai.decide_territorial_action(territory_dict)
                
                if decision['action_type'] != 'maintain_position':
                    print(f"  -> {ai.faction_name}: {decision['action_type']} "
                          f"(+{decision['influence_change']} influence) - {decision['reasoning']}")
                    decisions_made += 1
        
        print(f"\nDECISION SUMMARY: {decisions_made} territorial actions decided")
        return decisions_made > 0
    
    def test_influence_simulation(self):
        """Test simulated influence changes based on AI decisions"""
        print("\nINFLUENCE SIMULATION TEST")
        print("-" * 40)
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get current influence state
            cursor.execute("""
                SELECT ti.territory_id, ti.faction_id, ti.influence_value, t.name as territory_name
                FROM territorial_influence ti
                JOIN territories t ON ti.territory_id = t.id
                WHERE ti.influence_value > 0
                ORDER BY ti.territory_id, ti.influence_value DESC
            """)
            
            current_influences = cursor.fetchall()
            
            print("CURRENT INFLUENCE STATE:")
            current_territory = None
            for influence in current_influences:
                territory_id, faction_id, influence_value, territory_name = influence
                
                if current_territory != territory_id:
                    if current_territory is not None:
                        print()  # Add spacing between territories
                    print(f"  {territory_name}:")
                    current_territory = territory_id
                
                print(f"    -> Faction {faction_id}: {influence_value}%")
            
            # Simulate AI influence changes
            print(f"\nSIMULATING: AI influence changes...")
            
            # Test influence update (read-only simulation)
            test_changes = [
                (1, 1, 5, "Directorate expansion"),    # Territory 1, Faction 1, +5 influence
                (2, 2, 8, "Free77 guerrilla action"), # Territory 2, Faction 2, +8 influence  
                (3, 3, 3, "Nomad defensive action")    # Territory 3, Faction 3, +3 influence
            ]
            
            for territory_id, faction_id, change, reason in test_changes:
                # Get current influence
                cursor.execute("""
                    SELECT influence_value FROM territorial_influence 
                    WHERE territory_id = ? AND faction_id = ?
                """, (territory_id, faction_id))
                
                result = cursor.fetchone()
                current_value = result[0] if result else 0
                new_value = min(current_value + change, 100)  # Cap at 100%
                
                print(f"  -> Territory {territory_id}, Faction {faction_id}: "
                      f"{current_value}% -> {new_value}% ({reason})")
            
            conn.close()
            print(f"SIMULATION: Successful (read-only test)")
            return True
            
        except Exception as e:
            print(f"ERROR: Influence simulation failed - {e}")
            return False
    
    def test_performance_benchmark(self):
        """Test query performance for AI decision-making"""
        print("\nPERFORMACE BENCHMARK TEST")
        print("-" * 40)
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Benchmark territorial state query (what AI needs frequently)
            query = """
            SELECT t.id, t.name, t.strategic_value, t.controller_faction_id,
                   COUNT(ti.faction_id) as competing_factions,
                   AVG(ti.influence_value) as avg_influence
            FROM territories t
            LEFT JOIN territorial_influence ti ON t.id = ti.territory_id AND ti.influence_value > 0
            GROUP BY t.id, t.name, t.strategic_value, t.controller_faction_id
            """
            
            # Run query multiple times to get average performance
            times = []
            iterations = 10
            
            for i in range(iterations):
                start_time = time.time()
                cursor.execute(query)
                results = cursor.fetchall()
                end_time = time.time()
                
                query_time = (end_time - start_time) * 1000  # Convert to milliseconds
                times.append(query_time)
            
            avg_time = sum(times) / len(times)
            min_time = min(times)
            max_time = max(times)
            
            print(f"QUERY PERFORMANCE ({iterations} iterations):")
            print(f"  -> Average: {avg_time:.2f}ms")
            print(f"  -> Best: {min_time:.2f}ms")
            print(f"  -> Worst: {max_time:.2f}ms")
            print(f"  -> Records: {len(results)}")
            
            # Check if meets CTO's performance target
            cto_target = 50.0  # 50ms target
            cto_achievement = 0.04  # CTO's 0.04ms achievement
            
            if avg_time < cto_target:
                print(f"SUCCESS: Performance target met ({avg_time:.2f}ms < {cto_target}ms)")
                if avg_time < 1.0:
                    print(f"EXCELLENT: Performance within CTO range ({cto_achievement}ms)")
            else:
                print(f"WARNING: Performance below target ({avg_time:.2f}ms >= {cto_target}ms)")
            
            conn.close()
            return avg_time < cto_target
            
        except Exception as e:
            print(f"ERROR: Performance benchmark failed - {e}")
            return False

def main():
    """Run complete AI database integration test"""
    print("AI DATABASE INTEGRATION TEST")
    print("=" * 60)
    print("Testing AI territorial decision-making with CTO database")
    print()
    
    tester = TerritorialAIIntegrationTest()
    
    # Run test sequence
    tests = [
        ("Database Connection", tester.test_database_connection),
        ("Territorial Queries", tester.test_territorial_queries),
        ("Performance Benchmark", tester.test_performance_benchmark),
        ("Influence Simulation", tester.test_influence_simulation)
    ]
    
    results = []
    territories = []
    
    for test_name, test_func in tests:
        print(f"\nRunning: {test_name}")
        try:
            if test_name == "Territorial Queries":
                result = test_func()
                territories = result if isinstance(result, list) else []
                results.append((test_name, len(territories) > 0))
            else:
                result = test_func()
                results.append((test_name, result))
        except Exception as e:
            print(f"ERROR in {test_name}: {e}")
            results.append((test_name, False))
    
    # Test AI decision-making with territorial data
    if territories:
        print(f"\nRunning: AI Decision Making")
        try:
            ai_result = tester.test_ai_decision_making(territories)
            results.append(("AI Decision Making", ai_result))
        except Exception as e:
            print(f"ERROR in AI Decision Making: {e}")
            results.append(("AI Decision Making", False))
    
    # Summary
    print("\n" + "=" * 60)
    print("AI DATABASE INTEGRATION TEST SUMMARY")
    print("=" * 60)
    
    passed_tests = sum(1 for _, result in results if result)
    total_tests = len(results)
    
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nResults: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("\nSUCCESS: AI database integration fully operational")
        print("READY: For real-time territorial AI decision-making")
    else:
        print(f"\nISSUES: {total_tests - passed_tests} tests failed")
        print("REVIEW: Check database connection and query implementation")
    
    return passed_tests == total_tests

if __name__ == "__main__":
    main()