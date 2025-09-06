#!/usr/bin/env python3
"""
Performance Validation Suite for Adaptive AI Territorial System
Performance Engineer Implementation - Comprehensive testing for 100+ concurrent players

Validates adaptive AI faction behavior performance under realistic multiplayer load
with comprehensive benchmarking, stress testing, and optimization validation.
"""

import asyncio
import json
import time
import random
import statistics
import psutil
import threading
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from pathlib import Path
from collections import defaultdict, deque
import concurrent.futures
import websockets
import sqlite3

# Import our adaptive AI systems
from adaptive_ai_faction_behavior import AdaptiveAIFactionBehaviorSystem
from ai_performance_optimizer import AIPerformanceOptimizer, integrate_ai_performance_optimization
from faction_adaptive_specializations import FactionAdaptiveBehaviorEngine
from advanced_ai_features import AdvancedAIFeaturesEngine
from adaptive_ai_integration import AdaptiveAIIntegrationSystem, SystemIntegrationConfig

@dataclass
class PerformanceTarget:
    """Performance targets for validation"""
    max_ai_processing_time_ms: float = 16.0  # 16ms per frame (60 FPS)
    max_database_query_time_ms: float = 1.0  # <1ms database queries
    target_websocket_latency_ms: float = 50.0  # <50ms WebSocket latency
    min_ai_decisions_per_second: float = 7.0  # At least 7 AI decisions per second
    max_memory_usage_mb: float = 2048.0  # Max 2GB memory usage
    target_cache_hit_ratio: float = 0.85  # 85% cache hit ratio
    max_concurrent_connections: int = 100  # 100+ concurrent connections

@dataclass
class TestScenario:
    """Test scenario definition"""
    name: str
    description: str
    concurrent_connections: int
    test_duration_seconds: int
    ai_processing_load: float  # 0.0 to 1.0
    database_operations_per_second: int
    expected_results: Dict[str, Any]

@dataclass
class PerformanceTestResult:
    """Results from performance test"""
    scenario_name: str
    test_duration: float
    success: bool
    performance_metrics: Dict[str, float]
    violations: List[str]
    recommendations: List[str]
    detailed_stats: Dict[str, Any]

class PerformanceMonitor:
    """Real-time performance monitoring during tests"""
    
    def __init__(self):
        self.monitoring_active = False
        self.metrics_history = deque(maxlen=10000)
        self.violation_count = defaultdict(int)
        self.start_time = 0.0
        
    async def start_monitoring(self):
        """Start performance monitoring"""
        self.monitoring_active = True
        self.start_time = time.time()
        asyncio.create_task(self._monitoring_loop())
        
    def stop_monitoring(self):
        """Stop performance monitoring"""
        self.monitoring_active = False
        
    async def _monitoring_loop(self):
        """Main monitoring loop"""
        while self.monitoring_active:
            try:
                # Collect system metrics
                cpu_usage = psutil.cpu_percent(interval=0.1)
                memory_info = psutil.Process().memory_info()
                memory_usage_mb = memory_info.rss / 1024 / 1024
                
                metrics = {
                    'timestamp': time.time() - self.start_time,
                    'cpu_usage_percent': cpu_usage,
                    'memory_usage_mb': memory_usage_mb,
                    'threads_active': threading.active_count()
                }
                
                self.metrics_history.append(metrics)
                
                # Check for violations
                if cpu_usage > 90:
                    self.violation_count['high_cpu'] += 1
                if memory_usage_mb > 2048:
                    self.violation_count['high_memory'] += 1
                    
                await asyncio.sleep(0.1)  # 10 samples per second
                
            except Exception as e:
                print(f"Error in performance monitoring: {e}")
                await asyncio.sleep(1.0)
                
    def get_summary_stats(self) -> Dict[str, Any]:
        """Get summary statistics"""
        if not self.metrics_history:
            return {}
            
        cpu_values = [m['cpu_usage_percent'] for m in self.metrics_history]
        memory_values = [m['memory_usage_mb'] for m in self.metrics_history]
        
        return {
            'cpu_stats': {
                'mean': statistics.mean(cpu_values),
                'max': max(cpu_values),
                'p95': sorted(cpu_values)[int(len(cpu_values) * 0.95)],
                'p99': sorted(cpu_values)[int(len(cpu_values) * 0.99)]
            },
            'memory_stats': {
                'mean': statistics.mean(memory_values),
                'max': max(memory_values),
                'p95': sorted(memory_values)[int(len(memory_values) * 0.95)],
                'p99': sorted(memory_values)[int(len(memory_values) * 0.99)]
            },
            'violations': dict(self.violation_count),
            'samples_collected': len(self.metrics_history)
        }

class MockWebSocketClient:
    """Mock WebSocket client for load testing"""
    
    def __init__(self, client_id: int, server_uri: str):
        self.client_id = client_id
        self.server_uri = server_uri
        self.websocket = None
        self.messages_received = 0
        self.messages_sent = 0
        self.latency_measurements = deque(maxlen=100)
        self.connected = False
        
    async def connect_and_simulate(self, duration: float):
        """Connect and simulate client activity"""
        try:
            self.websocket = await websockets.connect(self.server_uri)
            self.connected = True
            
            # Send initial ping
            await self.websocket.send(json.dumps({"type": "ping", "timestamp": time.time()}))
            
            # Simulate client activity
            end_time = time.time() + duration
            
            while time.time() < end_time and self.connected:
                # Simulate periodic client actions
                if random.random() < 0.1:  # 10% chance per cycle
                    await self._simulate_client_action()
                    
                # Listen for server messages
                try:
                    message = await asyncio.wait_for(self.websocket.recv(), timeout=0.1)
                    self._process_server_message(message)
                except asyncio.TimeoutError:
                    pass
                    
                await asyncio.sleep(0.1)
                
        except Exception as e:
            print(f"Client {self.client_id} error: {e}")
        finally:
            if self.websocket:
                await self.websocket.close()
            self.connected = False
            
    async def _simulate_client_action(self):
        """Simulate client territorial action"""
        actions = [
            {"type": "request_update", "territory_id": random.randint(1, 10)},
            {"type": "influence_action", "territory_id": random.randint(1, 10), 
             "faction_id": random.randint(1, 7), "influence_change": random.randint(-10, 10)}
        ]
        
        action = random.choice(actions)
        action["timestamp"] = time.time()
        action["client_id"] = self.client_id
        
        await self.websocket.send(json.dumps(action))
        self.messages_sent += 1
        
    def _process_server_message(self, message: str):
        """Process message from server"""
        try:
            data = json.loads(message)
            self.messages_received += 1
            
            # Calculate latency for pong responses
            if data.get("type") == "pong":
                sent_time = data.get("timestamp", 0)
                if sent_time > 0:
                    latency = (time.time() - sent_time) * 1000  # ms
                    self.latency_measurements.append(latency)
                    
        except json.JSONDecodeError:
            pass
            
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get client performance statistics"""
        avg_latency = statistics.mean(self.latency_measurements) if self.latency_measurements else 0
        
        return {
            'messages_sent': self.messages_sent,
            'messages_received': self.messages_received,
            'avg_latency_ms': avg_latency,
            'max_latency_ms': max(self.latency_measurements) if self.latency_measurements else 0,
            'connected': self.connected
        }

class DatabaseStressTest:
    """Database performance stress testing"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.query_times = deque(maxlen=10000)
        self.queries_executed = 0
        self.query_failures = 0
        
    async def run_stress_test(self, duration: float, queries_per_second: int):
        """Run database stress test"""
        print(f"Starting database stress test: {queries_per_second} queries/sec for {duration}s")
        
        end_time = time.time() + duration
        interval = 1.0 / queries_per_second
        
        while time.time() < end_time:
            start_time = time.time()
            
            try:
                await self._execute_test_query()
                query_time = (time.time() - start_time) * 1000  # ms
                self.query_times.append(query_time)
                self.queries_executed += 1
                
            except Exception as e:
                self.query_failures += 1
                print(f"Database query failed: {e}")
                
            # Maintain query rate
            elapsed = time.time() - start_time
            if elapsed < interval:
                await asyncio.sleep(interval - elapsed)
                
    async def _execute_test_query(self):
        """Execute a test database query"""
        connection = sqlite3.connect(self.db_path)
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()
        
        # Random query selection
        queries = [
            "SELECT * FROM territories WHERE strategic_value > ?",
            "SELECT COUNT(*) FROM faction_territorial_influence WHERE influence_level > ?",
            "SELECT t.*, f.faction_name FROM territories t LEFT JOIN factions f ON t.current_controller_faction_id = f.id",
            "SELECT * FROM territorial_events WHERE started_at > datetime('now', '-1 hour')"
        ]
        
        query = random.choice(queries)
        
        if '?' in query:
            param = random.randint(1, 10)
            cursor.execute(query, (param,))
        else:
            cursor.execute(query)
            
        results = cursor.fetchall()
        connection.close()
        
        return len(results)
        
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get database performance statistics"""
        if not self.query_times:
            return {}
            
        query_times_list = list(self.query_times)
        
        return {
            'queries_executed': self.queries_executed,
            'query_failures': self.query_failures,
            'success_rate': self.queries_executed / max(self.queries_executed + self.query_failures, 1),
            'avg_query_time_ms': statistics.mean(query_times_list),
            'max_query_time_ms': max(query_times_list),
            'p95_query_time_ms': sorted(query_times_list)[int(len(query_times_list) * 0.95)],
            'p99_query_time_ms': sorted(query_times_list)[int(len(query_times_list) * 0.99)]
        }

class AdaptiveAIPerformanceValidator:
    """
    Comprehensive performance validation suite for adaptive AI territorial system
    Tests all components under realistic 100+ player load conditions
    """
    
    def __init__(self):
        self.performance_targets = PerformanceTarget()
        self.test_scenarios = self._create_test_scenarios()
        self.test_results: List[PerformanceTestResult] = []
        
        print("Adaptive AI Performance Validator initialized")
        print(f"Configured for testing up to {self.performance_targets.max_concurrent_connections} concurrent connections")
        
    def _create_test_scenarios(self) -> List[TestScenario]:
        """Create comprehensive test scenarios"""
        return [
            TestScenario(
                name="baseline_performance",
                description="Baseline single-player performance validation",
                concurrent_connections=1,
                test_duration_seconds=60,
                ai_processing_load=0.5,
                database_operations_per_second=10,
                expected_results={'ai_processing_time_ms': 8.0, 'memory_usage_mb': 500.0}
            ),
            
            TestScenario(
                name="medium_multiplayer_load",
                description="Medium multiplayer load testing (25 concurrent players)",
                concurrent_connections=25,
                test_duration_seconds=120,
                ai_processing_load=0.7,
                database_operations_per_second=50,
                expected_results={'ai_processing_time_ms': 12.0, 'memory_usage_mb': 800.0}
            ),
            
            TestScenario(
                name="high_multiplayer_load",
                description="High multiplayer load testing (50 concurrent players)",
                concurrent_connections=50,
                test_duration_seconds=180,
                ai_processing_load=0.8,
                database_operations_per_second=100,
                expected_results={'ai_processing_time_ms': 14.0, 'memory_usage_mb': 1200.0}
            ),
            
            TestScenario(
                name="maximum_capacity_test",
                description="Maximum capacity testing (100+ concurrent players)",
                concurrent_connections=100,
                test_duration_seconds=300,
                ai_processing_load=1.0,
                database_operations_per_second=200,
                expected_results={'ai_processing_time_ms': 16.0, 'memory_usage_mb': 2000.0}
            ),
            
            TestScenario(
                name="stress_overload_test",
                description="Stress testing beyond normal capacity (150 connections)",
                concurrent_connections=150,
                test_duration_seconds=120,
                ai_processing_load=1.0,
                database_operations_per_second=300,
                expected_results={'connection_rejections': True, 'graceful_degradation': True}
            ),
            
            TestScenario(
                name="ai_adaptation_performance",
                description="AI adaptation and learning performance under load",
                concurrent_connections=75,
                test_duration_seconds=240,
                ai_processing_load=0.9,
                database_operations_per_second=150,
                expected_results={'adaptation_cycles': 10, 'learning_convergence': True}
            )
        ]
        
    async def run_comprehensive_validation(self) -> Dict[str, Any]:
        """Run complete performance validation suite"""
        print("STARTING COMPREHENSIVE ADAPTIVE AI PERFORMANCE VALIDATION")
        print("=" * 70)
        
        validation_start_time = time.time()
        overall_success = True
        
        # Initialize systems for testing
        integration_system = await self._initialize_test_systems()
        
        try:
            # Run each test scenario
            for scenario in self.test_scenarios:
                print(f"\n--- Running Test Scenario: {scenario.name} ---")
                print(f"Description: {scenario.description}")
                print(f"Load: {scenario.concurrent_connections} connections, {scenario.test_duration_seconds}s duration")
                
                result = await self._run_test_scenario(scenario, integration_system)
                self.test_results.append(result)
                
                if not result.success:
                    overall_success = False
                    print(f"❌ FAILED: {scenario.name}")
                    for violation in result.violations:
                        print(f"   - {violation}")
                else:
                    print(f"✅ PASSED: {scenario.name}")
                    
                # Brief pause between tests
                await asyncio.sleep(5)
                
            # Generate comprehensive report
            validation_report = await self._generate_validation_report(
                overall_success, time.time() - validation_start_time
            )
            
            return validation_report
            
        finally:
            # Cleanup test systems
            if integration_system:
                integration_system.shutdown_integration()
                
    async def _initialize_test_systems(self):
        """Initialize all systems for performance testing"""
        print("Initializing adaptive AI systems for testing...")
        
        # Create test configuration
        config = SystemIntegrationConfig(
            websocket_host="127.0.0.1",
            websocket_port=8766,  # Different port for testing
            ai_processing_interval=1.0,
            max_concurrent_connections=150,  # Higher than normal for stress testing
            performance_monitoring_enabled=True
        )
        
        # Initialize integration system
        integration_system = AdaptiveAIIntegrationSystem(config)
        await integration_system.initialize_integration()
        
        # Start WebSocket server in background
        server_task = asyncio.create_task(integration_system.start_integrated_websocket_server())
        
        # Wait for server to start
        await asyncio.sleep(2)
        
        print("Test systems initialized successfully")
        return integration_system
        
    async def _run_test_scenario(self, scenario: TestScenario, 
                                integration_system) -> PerformanceTestResult:
        """Run a single test scenario"""
        # Initialize monitoring
        monitor = PerformanceMonitor()
        await monitor.start_monitoring()
        
        # Initialize database stress test
        db_stress = DatabaseStressTest(str(integration_system.adaptive_ai.db_path))
        
        test_start_time = time.time()
        violations = []
        performance_metrics = {}
        
        try:
            # Start concurrent components
            tasks = []
            
            # Database stress testing
            tasks.append(asyncio.create_task(
                db_stress.run_stress_test(scenario.test_duration_seconds, 
                                        scenario.database_operations_per_second)
            ))
            
            # WebSocket client simulation
            if scenario.concurrent_connections > 0:
                client_tasks = []
                for client_id in range(scenario.concurrent_connections):
                    client = MockWebSocketClient(client_id, "ws://127.0.0.1:8766")
                    client_task = asyncio.create_task(
                        client.connect_and_simulate(scenario.test_duration_seconds)
                    )
                    client_tasks.append((client, client_task))
                    
                tasks.extend([task for _, task in client_tasks])
            
            # Wait for all tasks to complete
            await asyncio.gather(*tasks, return_exceptions=True)
            
            # Collect performance metrics
            test_duration = time.time() - test_start_time
            monitor.stop_monitoring()
            
            # System performance metrics
            system_stats = monitor.get_summary_stats()
            db_stats = db_stress.get_performance_stats()
            
            # WebSocket client metrics
            if scenario.concurrent_connections > 0:
                client_stats = []
                for client, _ in client_tasks:
                    client_stats.append(client.get_performance_stats())
                    
                # Aggregate client metrics
                total_messages_sent = sum(stats['messages_sent'] for stats in client_stats)
                total_messages_received = sum(stats['messages_received'] for stats in client_stats)
                avg_client_latency = statistics.mean([stats['avg_latency_ms'] for stats in client_stats 
                                                     if stats['avg_latency_ms'] > 0]) if client_stats else 0
                successful_connections = sum(1 for stats in client_stats if stats['connected'])
                
                performance_metrics.update({
                    'websocket_messages_sent': total_messages_sent,
                    'websocket_messages_received': total_messages_received,
                    'websocket_avg_latency_ms': avg_client_latency,
                    'successful_connections': successful_connections,
                    'connection_success_rate': successful_connections / scenario.concurrent_connections
                })
            
            # AI system metrics
            ai_status = integration_system.get_integration_status()
            performance_metrics.update({
                'ai_decisions_processed': ai_status['metrics']['ai_decisions_processed'],
                'economic_syncs_completed': ai_status['metrics']['economic_syncs_completed'],
                'websocket_broadcasts': ai_status['metrics']['websocket_broadcasts'],
                'avg_integration_loop_time': ai_status['metrics']['avg_integration_loop_time']
            })
            
            # Combine all performance metrics
            performance_metrics.update({
                'test_duration_seconds': test_duration,
                'cpu_usage_mean': system_stats['cpu_stats']['mean'],
                'cpu_usage_max': system_stats['cpu_stats']['max'],
                'cpu_usage_p95': system_stats['cpu_stats']['p95'],
                'memory_usage_mean': system_stats['memory_stats']['mean'],
                'memory_usage_max': system_stats['memory_stats']['max'],
                'memory_usage_p95': system_stats['memory_stats']['p95'],
                'database_avg_query_time_ms': db_stats.get('avg_query_time_ms', 0),
                'database_max_query_time_ms': db_stats.get('max_query_time_ms', 0),
                'database_p95_query_time_ms': db_stats.get('p95_query_time_ms', 0),
                'database_success_rate': db_stats.get('success_rate', 0),
                'queries_executed': db_stats.get('queries_executed', 0)
            })
            
            # Validate against performance targets
            violations = self._validate_performance_targets(performance_metrics, scenario)
            
            success = len(violations) == 0
            
        except Exception as e:
            violations.append(f"Test execution error: {str(e)}")
            success = False
            test_duration = time.time() - test_start_time
            monitor.stop_monitoring()
            
        # Generate recommendations
        recommendations = self._generate_recommendations(performance_metrics, violations, scenario)
        
        return PerformanceTestResult(
            scenario_name=scenario.name,
            test_duration=test_duration,
            success=success,
            performance_metrics=performance_metrics,
            violations=violations,
            recommendations=recommendations,
            detailed_stats=system_stats if 'system_stats' in locals() else {}
        )
        
    def _validate_performance_targets(self, metrics: Dict[str, float], 
                                    scenario: TestScenario) -> List[str]:
        """Validate performance metrics against targets"""
        violations = []
        
        # AI processing time validation
        ai_loop_time_ms = metrics.get('avg_integration_loop_time', 0) * 1000
        if ai_loop_time_ms > self.performance_targets.max_ai_processing_time_ms:
            violations.append(f"AI processing time {ai_loop_time_ms:.1f}ms exceeds target {self.performance_targets.max_ai_processing_time_ms}ms")
            
        # Database query time validation
        db_query_time_ms = metrics.get('database_avg_query_time_ms', 0)
        if db_query_time_ms > self.performance_targets.max_database_query_time_ms:
            violations.append(f"Database query time {db_query_time_ms:.2f}ms exceeds target {self.performance_targets.max_database_query_time_ms}ms")
            
        # WebSocket latency validation
        websocket_latency = metrics.get('websocket_avg_latency_ms', 0)
        if websocket_latency > self.performance_targets.target_websocket_latency_ms:
            violations.append(f"WebSocket latency {websocket_latency:.1f}ms exceeds target {self.performance_targets.target_websocket_latency_ms}ms")
            
        # Memory usage validation
        memory_usage = metrics.get('memory_usage_max', 0)
        if memory_usage > self.performance_targets.max_memory_usage_mb:
            violations.append(f"Memory usage {memory_usage:.1f}MB exceeds target {self.performance_targets.max_memory_usage_mb}MB")
            
        # AI decisions per second validation
        ai_decisions = metrics.get('ai_decisions_processed', 0)
        test_duration = metrics.get('test_duration_seconds', 1)
        decisions_per_second = ai_decisions / test_duration
        if decisions_per_second < self.performance_targets.min_ai_decisions_per_second:
            violations.append(f"AI decisions per second {decisions_per_second:.1f} below target {self.performance_targets.min_ai_decisions_per_second}")
            
        # Connection handling validation
        if scenario.concurrent_connections <= self.performance_targets.max_concurrent_connections:
            connection_success_rate = metrics.get('connection_success_rate', 0)
            if connection_success_rate < 0.95:  # 95% success rate expected
                violations.append(f"Connection success rate {connection_success_rate:.1%} below 95% target")
                
        return violations
        
    def _generate_recommendations(self, metrics: Dict[str, float], violations: List[str], 
                                 scenario: TestScenario) -> List[str]:
        """Generate performance optimization recommendations"""
        recommendations = []
        
        # CPU usage recommendations
        cpu_max = metrics.get('cpu_usage_max', 0)
        if cpu_max > 80:
            recommendations.append("Consider increasing AI processing interval to reduce CPU load")
            recommendations.append("Implement CPU-based dynamic scaling")
            
        # Memory usage recommendations
        memory_max = metrics.get('memory_usage_max', 0)
        if memory_max > 1500:  # 1.5GB threshold
            recommendations.append("Implement more aggressive cache cleanup")
            recommendations.append("Consider reducing decision history retention")
            
        # Database performance recommendations
        db_query_time = metrics.get('database_avg_query_time_ms', 0)
        if db_query_time > 0.5:
            recommendations.append("Optimize database queries with better indexing")
            recommendations.append("Implement database connection pooling")
            
        # WebSocket performance recommendations
        websocket_latency = metrics.get('websocket_avg_latency_ms', 0)
        if websocket_latency > 30:
            recommendations.append("Optimize WebSocket message batching")
            recommendations.append("Implement message priority queuing")
            
        # AI performance recommendations
        ai_decisions = metrics.get('ai_decisions_processed', 0)
        if ai_decisions < scenario.test_duration_seconds * 5:  # Expected 5+ per second
            recommendations.append("Optimize AI decision-making algorithms")
            recommendations.append("Implement better AI processing parallelization")
            
        # Connection handling recommendations
        connection_success_rate = metrics.get('connection_success_rate', 1.0)
        if connection_success_rate < 0.95:
            recommendations.append("Implement connection queuing for overload scenarios")
            recommendations.append("Add graceful connection rejection with retry guidance")
            
        return recommendations
        
    async def _generate_validation_report(self, overall_success: bool, 
                                         total_duration: float) -> Dict[str, Any]:
        """Generate comprehensive validation report"""
        print(f"\n{'='*70}")
        print("ADAPTIVE AI PERFORMANCE VALIDATION REPORT")
        print(f"{'='*70}")
        
        report = {
            'validation_summary': {
                'overall_success': overall_success,
                'total_test_duration': total_duration,
                'scenarios_tested': len(self.test_scenarios),
                'scenarios_passed': len([r for r in self.test_results if r.success]),
                'scenarios_failed': len([r for r in self.test_results if not r.success])
            },
            'performance_targets': asdict(self.performance_targets),
            'test_results': [asdict(result) for result in self.test_results],
            'summary_statistics': self._calculate_summary_statistics(),
            'recommendations': self._generate_overall_recommendations(),
            'validation_timestamp': time.time()
        }
        
        # Print summary
        print(f"Overall Result: {'✅ PASSED' if overall_success else '❌ FAILED'}")
        print(f"Total Test Duration: {total_duration:.1f} seconds")
        print(f"Scenarios Tested: {len(self.test_scenarios)}")
        print(f"Scenarios Passed: {report['validation_summary']['scenarios_passed']}")
        print(f"Scenarios Failed: {report['validation_summary']['scenarios_failed']}")
        
        print(f"\n--- Performance Summary ---")
        summary_stats = report['summary_statistics']
        print(f"Peak Memory Usage: {summary_stats['peak_memory_usage_mb']:.1f} MB")
        print(f"Peak CPU Usage: {summary_stats['peak_cpu_usage_percent']:.1f}%")
        print(f"Average Database Query Time: {summary_stats['avg_database_query_time_ms']:.2f} ms")
        print(f"Total AI Decisions Processed: {summary_stats['total_ai_decisions_processed']}")
        print(f"Average WebSocket Latency: {summary_stats['avg_websocket_latency_ms']:.1f} ms")
        
        if report['recommendations']:
            print(f"\n--- Optimization Recommendations ---")
            for i, recommendation in enumerate(report['recommendations'], 1):
                print(f"{i}. {recommendation}")
                
        # Export report to file
        report_path = Path("C:/Users/Zachg/Terminal-Grounds/Tools/TerritorialSystem/performance_validation_report.json")
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, default=str)
            
        print(f"\nDetailed report exported to: {report_path}")
        print(f"{'='*70}")
        
        return report
        
    def _calculate_summary_statistics(self) -> Dict[str, Any]:
        """Calculate summary statistics across all tests"""
        if not self.test_results:
            return {}
            
        all_metrics = [result.performance_metrics for result in self.test_results]
        
        return {
            'peak_memory_usage_mb': max([m.get('memory_usage_max', 0) for m in all_metrics]),
            'peak_cpu_usage_percent': max([m.get('cpu_usage_max', 0) for m in all_metrics]),
            'avg_database_query_time_ms': statistics.mean([m.get('database_avg_query_time_ms', 0) for m in all_metrics if m.get('database_avg_query_time_ms', 0) > 0]),
            'total_ai_decisions_processed': sum([m.get('ai_decisions_processed', 0) for m in all_metrics]),
            'avg_websocket_latency_ms': statistics.mean([m.get('websocket_avg_latency_ms', 0) for m in all_metrics if m.get('websocket_avg_latency_ms', 0) > 0]),
            'total_database_queries': sum([m.get('queries_executed', 0) for m in all_metrics]),
            'overall_connection_success_rate': statistics.mean([m.get('connection_success_rate', 1.0) for m in all_metrics if 'connection_success_rate' in m])
        }
        
    def _generate_overall_recommendations(self) -> List[str]:
        """Generate overall optimization recommendations"""
        recommendations = set()
        
        for result in self.test_results:
            recommendations.update(result.recommendations)
            
        # Add system-wide recommendations based on patterns
        failed_scenarios = [r for r in self.test_results if not r.success]
        if len(failed_scenarios) > len(self.test_results) / 2:
            recommendations.add("Consider fundamental architecture optimization for better scalability")
            
        high_load_failures = [r for r in failed_scenarios if 'high_multiplayer_load' in r.scenario_name or 'maximum_capacity' in r.scenario_name]
        if high_load_failures:
            recommendations.add("Implement advanced load balancing and horizontal scaling")
            
        return sorted(list(recommendations))

async def main():
    """Main performance validation execution"""
    print("ADAPTIVE AI TERRITORIAL SYSTEM PERFORMANCE VALIDATION")
    print("Performance Engineer Implementation - 100+ Concurrent Player Testing")
    print("=" * 70)
    
    validator = AdaptiveAIPerformanceValidator()
    
    try:
        # Run comprehensive validation
        validation_report = await validator.run_comprehensive_validation()
        
        # Final assessment
        print("\n" + "=" * 70)
        print("PERFORMANCE ENGINEER FINAL ASSESSMENT")
        print("=" * 70)
        
        if validation_report['validation_summary']['overall_success']:
            print("✅ VALIDATION PASSED: Adaptive AI system ready for 100+ concurrent players")
            print("All performance targets met under realistic multiplayer load")
            print("System demonstrates enterprise-grade scalability and responsiveness")
        else:
            print("❌ VALIDATION FAILED: Performance optimization required")
            print("System requires additional optimization before production deployment")
            
        print(f"Comprehensive testing completed in {validation_report['validation_summary']['total_test_duration']:.1f} seconds")
        print("Detailed performance analysis and recommendations available in validation report")
        
    except KeyboardInterrupt:
        print("\nValidation interrupted by user")
    except Exception as e:
        print(f"Validation error: {e}")
        
if __name__ == "__main__":
    asyncio.run(main())