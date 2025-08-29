#!/usr/bin/env python3
"""
Terminal Grounds Pipeline Performance Optimizer
Automated performance tuning and optimization for procedural generation pipeline

Author: DevOps Engineer
Version: 1.0.0
"""

import asyncio
import json
import logging
import psutil
import sqlite3
import time
import statistics
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import urllib.request
import GPUtil
import threading
import queue

logger = logging.getLogger("PerformanceOptimizer")

@dataclass
class PerformanceMetrics:
    """Container for performance metrics"""
    timestamp: str
    cpu_percent: float
    memory_percent: float
    disk_io_read: int
    disk_io_write: int
    gpu_utilization: float
    gpu_memory_used: int
    gpu_memory_total: int
    active_generations: int
    queue_size: int
    average_generation_time: float
    success_rate: float
    throughput: float  # generations per hour

@dataclass
class OptimizationRecommendation:
    """Performance optimization recommendation"""
    category: str  # "resource", "configuration", "scaling"
    priority: str  # "low", "medium", "high", "critical"
    description: str
    action: str
    expected_impact: str
    implementation_complexity: str

class SystemResourceMonitor:
    """Monitor system resources and performance"""
    
    def __init__(self):
        self.metrics_history = []
        self.max_history = 1000
        self.monitoring = False
        self.monitor_thread = None
        
    def start_monitoring(self, interval: float = 5.0):
        """Start continuous resource monitoring"""
        if self.monitoring:
            return
        
        self.monitoring = True
        self.monitor_thread = threading.Thread(
            target=self._monitor_loop,
            args=(interval,)
        )
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
        
        logger.info("Resource monitoring started")
    
    def stop_monitoring(self):
        """Stop resource monitoring"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=10)
        logger.info("Resource monitoring stopped")
    
    def _monitor_loop(self, interval: float):
        """Main monitoring loop"""
        while self.monitoring:
            try:
                metrics = self._collect_metrics()
                self.metrics_history.append(metrics)
                
                # Keep history size manageable
                if len(self.metrics_history) > self.max_history:
                    self.metrics_history.pop(0)
                
                time.sleep(interval)
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                time.sleep(interval)
    
    def _collect_metrics(self) -> PerformanceMetrics:
        """Collect current system metrics"""
        # CPU and Memory
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        
        # Disk I/O
        disk_io = psutil.disk_io_counters()
        
        # GPU metrics
        gpu_utilization = 0
        gpu_memory_used = 0
        gpu_memory_total = 0
        
        try:
            gpus = GPUtil.getGPUs()
            if gpus:
                gpu = gpus[0]  # Use first GPU
                gpu_utilization = gpu.load * 100
                gpu_memory_used = gpu.memoryUsed
                gpu_memory_total = gpu.memoryTotal
        except Exception as e:
            logger.debug(f"GPU monitoring failed: {e}")
        
        # Pipeline-specific metrics
        pipeline_metrics = self._get_pipeline_metrics()
        
        return PerformanceMetrics(
            timestamp=datetime.now().isoformat(),
            cpu_percent=cpu_percent,
            memory_percent=memory.percent,
            disk_io_read=disk_io.read_bytes if disk_io else 0,
            disk_io_write=disk_io.write_bytes if disk_io else 0,
            gpu_utilization=gpu_utilization,
            gpu_memory_used=gpu_memory_used,
            gpu_memory_total=gpu_memory_total,
            active_generations=pipeline_metrics.get("active_generations", 0),
            queue_size=pipeline_metrics.get("queue_size", 0),
            average_generation_time=pipeline_metrics.get("average_time", 0),
            success_rate=pipeline_metrics.get("success_rate", 0),
            throughput=pipeline_metrics.get("throughput", 0)
        )
    
    def _get_pipeline_metrics(self) -> Dict:
        """Get pipeline-specific performance metrics"""
        try:
            # Try to get metrics from pipeline monitor
            pipeline_db = Path("C:/Users/Zachg/Terminal-Grounds/Database/pipeline_state.db")
            
            if not pipeline_db.exists():
                return {}
            
            conn = sqlite3.connect(str(pipeline_db))
            cursor = conn.cursor()
            
            metrics = {}
            
            # Active generations (processing status)
            cursor.execute("SELECT COUNT(*) FROM generation_requests WHERE status = 'processing'")
            metrics["active_generations"] = cursor.fetchone()[0]
            
            # Queue size (pending/queued)
            cursor.execute("SELECT COUNT(*) FROM generation_requests WHERE status IN ('pending', 'queued')")
            metrics["queue_size"] = cursor.fetchone()[0]
            
            # Average generation time (completed in last hour)
            cursor.execute("""
                SELECT AVG(
                    CAST((julianday(completed_at) - julianday(created_at)) * 86400 AS REAL)
                ) 
                FROM generation_requests 
                WHERE status = 'completed' 
                AND completed_at > datetime('now', '-1 hour')
            """)
            avg_time = cursor.fetchone()[0]
            metrics["average_time"] = avg_time if avg_time else 0
            
            # Success rate (last 100 requests)
            cursor.execute("""
                SELECT 
                    COUNT(CASE WHEN status = 'completed' THEN 1 END) * 100.0 / COUNT(*) 
                FROM (
                    SELECT status FROM generation_requests 
                    WHERE status IN ('completed', 'failed') 
                    ORDER BY created_at DESC 
                    LIMIT 100
                )
            """)
            success_rate = cursor.fetchone()[0]
            metrics["success_rate"] = success_rate if success_rate else 0
            
            # Throughput (completions per hour)
            cursor.execute("""
                SELECT COUNT(*) 
                FROM generation_requests 
                WHERE status = 'completed' 
                AND completed_at > datetime('now', '-1 hour')
            """)
            completions_per_hour = cursor.fetchone()[0]
            metrics["throughput"] = completions_per_hour
            
            conn.close()
            return metrics
            
        except Exception as e:
            logger.debug(f"Failed to get pipeline metrics: {e}")
            return {}
    
    def get_current_metrics(self) -> Optional[PerformanceMetrics]:
        """Get current performance metrics"""
        if self.metrics_history:
            return self.metrics_history[-1]
        return self._collect_metrics()
    
    def get_metrics_summary(self, duration_minutes: int = 60) -> Dict:
        """Get performance summary for specified duration"""
        cutoff_time = datetime.now() - timedelta(minutes=duration_minutes)
        
        recent_metrics = [
            m for m in self.metrics_history 
            if datetime.fromisoformat(m.timestamp) > cutoff_time
        ]
        
        if not recent_metrics:
            return {}
        
        return {
            "duration_minutes": duration_minutes,
            "sample_count": len(recent_metrics),
            "cpu": {
                "avg": statistics.mean(m.cpu_percent for m in recent_metrics),
                "max": max(m.cpu_percent for m in recent_metrics),
                "min": min(m.cpu_percent for m in recent_metrics)
            },
            "memory": {
                "avg": statistics.mean(m.memory_percent for m in recent_metrics),
                "max": max(m.memory_percent for m in recent_metrics),
                "min": min(m.memory_percent for m in recent_metrics)
            },
            "gpu": {
                "utilization_avg": statistics.mean(m.gpu_utilization for m in recent_metrics),
                "memory_usage_avg": statistics.mean(m.gpu_memory_used for m in recent_metrics)
            },
            "pipeline": {
                "avg_generation_time": statistics.mean(m.average_generation_time for m in recent_metrics),
                "avg_success_rate": statistics.mean(m.success_rate for m in recent_metrics),
                "avg_throughput": statistics.mean(m.throughput for m in recent_metrics)
            }
        }

class PerformanceAnalyzer:
    """Analyze performance data and generate recommendations"""
    
    def __init__(self, monitor: SystemResourceMonitor):
        self.monitor = monitor
        
    def analyze_performance(self) -> List[OptimizationRecommendation]:
        """Analyze current performance and generate recommendations"""
        recommendations = []
        
        # Get recent metrics
        current = self.monitor.get_current_metrics()
        summary = self.monitor.get_metrics_summary(60)  # Last hour
        
        if not current or not summary:
            return recommendations
        
        # CPU Analysis
        recommendations.extend(self._analyze_cpu(current, summary))
        
        # Memory Analysis
        recommendations.extend(self._analyze_memory(current, summary))
        
        # GPU Analysis
        recommendations.extend(self._analyze_gpu(current, summary))
        
        # Pipeline Analysis
        recommendations.extend(self._analyze_pipeline(current, summary))
        
        # Disk I/O Analysis
        recommendations.extend(self._analyze_disk_io(current, summary))
        
        # Sort by priority
        priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        recommendations.sort(key=lambda x: priority_order.get(x.priority, 4))
        
        return recommendations
    
    def _analyze_cpu(self, current: PerformanceMetrics, summary: Dict) -> List[OptimizationRecommendation]:
        """Analyze CPU performance"""
        recommendations = []
        
        cpu_avg = summary.get("cpu", {}).get("avg", 0)
        cpu_max = summary.get("cpu", {}).get("max", 0)
        
        if cpu_avg > 85:
            recommendations.append(OptimizationRecommendation(
                category="resource",
                priority="high",
                description=f"High CPU utilization (avg: {cpu_avg:.1f}%)",
                action="Reduce concurrent generation limit or upgrade CPU",
                expected_impact="Reduce generation bottlenecks and improve throughput",
                implementation_complexity="low"
            ))
        elif cpu_avg > 70:
            recommendations.append(OptimizationRecommendation(
                category="configuration",
                priority="medium",
                description=f"Moderate CPU utilization (avg: {cpu_avg:.1f}%)",
                action="Consider reducing batch size or concurrent processes",
                expected_impact="Prevent CPU bottlenecks during peak load",
                implementation_complexity="low"
            ))
        
        if cpu_max > 95:
            recommendations.append(OptimizationRecommendation(
                category="resource",
                priority="critical",
                description=f"CPU peaks at {cpu_max:.1f}%",
                action="Implement CPU throttling and load balancing",
                expected_impact="Prevent system instability",
                implementation_complexity="medium"
            ))
        
        return recommendations
    
    def _analyze_memory(self, current: PerformanceMetrics, summary: Dict) -> List[OptimizationRecommendation]:
        """Analyze memory performance"""
        recommendations = []
        
        mem_avg = summary.get("memory", {}).get("avg", 0)
        mem_max = summary.get("memory", {}).get("max", 0)
        
        if mem_avg > 85:
            recommendations.append(OptimizationRecommendation(
                category="resource",
                priority="high",
                description=f"High memory usage (avg: {mem_avg:.1f}%)",
                action="Implement memory cleanup between generations or add RAM",
                expected_impact="Prevent OOM errors and improve stability",
                implementation_complexity="medium"
            ))
        elif mem_avg > 70:
            recommendations.append(OptimizationRecommendation(
                category="configuration",
                priority="medium",
                description=f"Moderate memory usage (avg: {mem_avg:.1f}%)",
                action="Monitor for memory leaks and optimize batch processing",
                expected_impact="Maintain stable memory usage",
                implementation_complexity="low"
            ))
        
        return recommendations
    
    def _analyze_gpu(self, current: PerformanceMetrics, summary: Dict) -> List[OptimizationRecommendation]:
        """Analyze GPU performance"""
        recommendations = []
        
        gpu_util = summary.get("gpu", {}).get("utilization_avg", 0)
        gpu_mem = summary.get("gpu", {}).get("memory_usage_avg", 0)
        gpu_total = current.gpu_memory_total
        
        if gpu_total > 0:  # GPU available
            gpu_mem_percent = (gpu_mem / gpu_total) * 100
            
            if gpu_util < 50:
                recommendations.append(OptimizationRecommendation(
                    category="configuration",
                    priority="medium",
                    description=f"Low GPU utilization (avg: {gpu_util:.1f}%)",
                    action="Increase concurrent generations or batch size",
                    expected_impact="Better GPU resource utilization and higher throughput",
                    implementation_complexity="low"
                ))
            
            if gpu_mem_percent > 90:
                recommendations.append(OptimizationRecommendation(
                    category="resource",
                    priority="high",
                    description=f"GPU memory nearly full ({gpu_mem_percent:.1f}%)",
                    action="Implement VRAM cleanup or reduce image resolution",
                    expected_impact="Prevent CUDA OOM errors",
                    implementation_complexity="medium"
                ))
        else:
            recommendations.append(OptimizationRecommendation(
                category="resource",
                priority="high",
                description="No GPU detected or unavailable",
                action="Verify GPU drivers and CUDA installation",
                expected_impact="Enable GPU acceleration for massive performance gains",
                implementation_complexity="medium"
            ))
        
        return recommendations
    
    def _analyze_pipeline(self, current: PerformanceMetrics, summary: Dict) -> List[OptimizationRecommendation]:
        """Analyze pipeline-specific performance"""
        recommendations = []
        
        pipeline = summary.get("pipeline", {})
        success_rate = pipeline.get("avg_success_rate", 0)
        avg_time = pipeline.get("avg_generation_time", 0)
        throughput = pipeline.get("avg_throughput", 0)
        
        # Success rate analysis
        if success_rate < 85:
            recommendations.append(OptimizationRecommendation(
                category="configuration",
                priority="high",
                description=f"Low success rate ({success_rate:.1f}%)",
                action="Review failed generations and adjust parameters",
                expected_impact="Improve reliability and reduce wasted resources",
                implementation_complexity="medium"
            ))
        
        # Generation time analysis
        if avg_time > 300:  # 5 minutes
            recommendations.append(OptimizationRecommendation(
                category="configuration",
                priority="medium",
                description=f"Long generation time (avg: {avg_time:.1f}s)",
                action="Optimize generation parameters or upgrade hardware",
                expected_impact="Faster turnaround and higher throughput",
                implementation_complexity="low"
            ))
        
        # Throughput analysis
        if throughput < 5:  # Less than 5 per hour
            recommendations.append(OptimizationRecommendation(
                category="scaling",
                priority="medium",
                description=f"Low throughput ({throughput:.1f}/hour)",
                action="Increase concurrency or optimize workflow",
                expected_impact="Higher asset production rate",
                implementation_complexity="low"
            ))
        
        # Queue backlog
        if current.queue_size > 50:
            recommendations.append(OptimizationRecommendation(
                category="scaling",
                priority="high",
                description=f"Large queue backlog ({current.queue_size} requests)",
                action="Scale up processing capacity or prioritize requests",
                expected_impact="Reduce wait times and improve responsiveness",
                implementation_complexity="medium"
            ))
        
        return recommendations
    
    def _analyze_disk_io(self, current: PerformanceMetrics, summary: Dict) -> List[OptimizationRecommendation]:
        """Analyze disk I/O performance"""
        recommendations = []
        
        # Check if we're generating a lot of disk activity
        # This is a simplified analysis - real implementation would track I/O rates
        
        # Placeholder for disk I/O analysis
        # Would need to track read/write rates over time
        
        return recommendations

class AutoOptimizer:
    """Automatically apply safe optimizations"""
    
    def __init__(self, analyzer: PerformanceAnalyzer):
        self.analyzer = analyzer
        self.applied_optimizations = []
        
    async def apply_safe_optimizations(self) -> List[str]:
        """Apply safe, low-risk optimizations automatically"""
        applied = []
        recommendations = self.analyzer.analyze_performance()
        
        for rec in recommendations:
            if (rec.implementation_complexity == "low" and 
                rec.priority in ["high", "critical"] and
                rec.category == "configuration"):
                
                success = await self._apply_optimization(rec)
                if success:
                    applied.append(rec.description)
                    self.applied_optimizations.append({
                        "timestamp": datetime.now().isoformat(),
                        "recommendation": rec,
                        "status": "applied"
                    })
        
        return applied
    
    async def _apply_optimization(self, rec: OptimizationRecommendation) -> bool:
        """Apply a specific optimization"""
        try:
            # This is where specific optimizations would be implemented
            # For now, just log what would be done
            
            logger.info(f"Applying optimization: {rec.description}")
            logger.info(f"Action: {rec.action}")
            
            # Placeholder for actual implementation
            # Real implementation would modify configuration files,
            # adjust pipeline parameters, etc.
            
            await asyncio.sleep(1)  # Simulate work
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to apply optimization: {e}")
            return False

class PerformanceReporter:
    """Generate performance reports"""
    
    def __init__(self, monitor: SystemResourceMonitor, analyzer: PerformanceAnalyzer):
        self.monitor = monitor
        self.analyzer = analyzer
    
    def generate_report(self, output_file: Optional[str] = None) -> Dict:
        """Generate comprehensive performance report"""
        report = {
            "generated_at": datetime.now().isoformat(),
            "summary": self.monitor.get_metrics_summary(60),
            "current_metrics": self.monitor.get_current_metrics(),
            "recommendations": [
                {
                    "category": rec.category,
                    "priority": rec.priority,
                    "description": rec.description,
                    "action": rec.action,
                    "expected_impact": rec.expected_impact,
                    "implementation_complexity": rec.implementation_complexity
                }
                for rec in self.analyzer.analyze_performance()
            ],
            "system_info": self._get_system_info()
        }
        
        if output_file:
            with open(output_file, 'w') as f:
                json.dump(report, f, indent=2, default=str)
            logger.info(f"Performance report saved to {output_file}")
        
        return report
    
    def _get_system_info(self) -> Dict:
        """Get basic system information"""
        return {
            "cpu_count": psutil.cpu_count(),
            "memory_total_gb": round(psutil.virtual_memory().total / (1024**3), 2),
            "disk_usage": {
                path.mountpoint: {
                    "total_gb": round(psutil.disk_usage(path.mountpoint).total / (1024**3), 2),
                    "free_gb": round(psutil.disk_usage(path.mountpoint).free / (1024**3), 2)
                }
                for path in psutil.disk_partitions()
            }
        }
    
    def print_summary(self):
        """Print performance summary to console"""
        current = self.monitor.get_current_metrics()
        summary = self.monitor.get_metrics_summary(60)
        recommendations = self.analyzer.analyze_performance()
        
        print("\n=== TERMINAL GROUNDS PIPELINE PERFORMANCE REPORT ===")
        print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        if current:
            print("CURRENT STATUS:")
            print(f"  CPU: {current.cpu_percent:.1f}%")
            print(f"  Memory: {current.memory_percent:.1f}%")
            print(f"  GPU: {current.gpu_utilization:.1f}%")
            print(f"  Active Generations: {current.active_generations}")
            print(f"  Queue Size: {current.queue_size}")
            print(f"  Success Rate: {current.success_rate:.1f}%")
            print()
        
        if summary:
            print("LAST HOUR AVERAGES:")
            cpu = summary.get("cpu", {})
            memory = summary.get("memory", {})
            pipeline = summary.get("pipeline", {})
            
            print(f"  CPU: {cpu.get('avg', 0):.1f}% (max: {cpu.get('max', 0):.1f}%)")
            print(f"  Memory: {memory.get('avg', 0):.1f}% (max: {memory.get('max', 0):.1f}%)")
            print(f"  Throughput: {pipeline.get('avg_throughput', 0):.1f} generations/hour")
            print(f"  Avg Generation Time: {pipeline.get('avg_generation_time', 0):.1f}s")
            print()
        
        if recommendations:
            print("RECOMMENDATIONS:")
            for i, rec in enumerate(recommendations[:5], 1):  # Top 5
                priority_symbol = {
                    "critical": "🔴",
                    "high": "🟡", 
                    "medium": "🔵",
                    "low": "🟢"
                }.get(rec.priority, "⚪")
                
                print(f"  {i}. {priority_symbol} [{rec.priority.upper()}] {rec.description}")
                print(f"     Action: {rec.action}")
                print()
        else:
            print("No recommendations - performance is optimal!")
            print()

async def main():
    """Main performance monitoring and optimization"""
    
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    
    print("Terminal Grounds Pipeline Performance Optimizer")
    print("Starting monitoring and analysis...")
    print()
    
    # Initialize components
    monitor = SystemResourceMonitor()
    analyzer = PerformanceAnalyzer(monitor)
    optimizer = AutoOptimizer(analyzer)
    reporter = PerformanceReporter(monitor, analyzer)
    
    # Start monitoring
    monitor.start_monitoring(interval=5.0)
    
    try:
        # Monitor for a bit to collect initial data
        await asyncio.sleep(30)
        
        # Generate and display report
        reporter.print_summary()
        
        # Apply safe optimizations
        applied = await optimizer.apply_safe_optimizations()
        
        if applied:
            print("APPLIED OPTIMIZATIONS:")
            for opt in applied:
                print(f"  ✓ {opt}")
            print()
        
        # Save detailed report
        report_file = f"performance_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        reporter.generate_report(report_file)
        
        print(f"Detailed report saved: {report_file}")
        print()
        print("Monitoring continues... Press Ctrl+C to stop")
        
        # Continue monitoring
        while True:
            await asyncio.sleep(60)
            
            # Periodic report
            reporter.print_summary()
            
            # Apply optimizations if needed
            applied = await optimizer.apply_safe_optimizations()
            if applied:
                print(f"Applied {len(applied)} optimizations")
    
    except KeyboardInterrupt:
        print("\nStopping performance monitor...")
    
    finally:
        monitor.stop_monitoring()
        
        # Final report
        final_report = f"final_performance_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        reporter.generate_report(final_report)
        print(f"Final report saved: {final_report}")

if __name__ == "__main__":
    asyncio.run(main())