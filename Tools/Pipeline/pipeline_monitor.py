#!/usr/bin/env python3
"""
Terminal Grounds Pipeline Monitor & Control Dashboard
Real-time monitoring and management interface for procedural generation pipeline

Author: DevOps Engineer
Version: 1.0.0
"""

import asyncio
import json
import sqlite3
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
import urllib.request
import argparse
import sys

# Rich console for better terminal output
try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.layout import Layout
    from rich.live import Live
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    print("Warning: 'rich' library not installed. Using basic output.")
    print("Install with: pip install rich")

class PipelineMonitor:
    """Monitor and control the procedural generation pipeline"""
    
    def __init__(self):
        self.console = Console() if RICH_AVAILABLE else None
        self.comfyui_url = "http://127.0.0.1:8188"
        self.websocket_url = "ws://127.0.0.1:8765"
        self.pipeline_db = Path("C:/Users/Zachg/Terminal-Grounds/Database/pipeline_state.db")
        self.territorial_db = Path("C:/Users/Zachg/Terminal-Grounds/Database/territorial_system.db")
        
    def check_service_health(self) -> Dict:
        """Check health of all services"""
        health = {
            "comfyui": self._check_comfyui(),
            "websocket": self._check_websocket(),
            "pipeline_db": self.pipeline_db.exists(),
            "territorial_db": self.territorial_db.exists()
        }
        
        health["overall"] = all(health.values())
        return health
    
    def _check_comfyui(self) -> bool:
        """Check if ComfyUI is running"""
        try:
            req = urllib.request.Request(f"{self.comfyui_url}/system_stats")
            with urllib.request.urlopen(req, timeout=2) as response:
                return response.status == 200
        except:
            return False
    
    def _check_websocket(self) -> bool:
        """Check if WebSocket server is running"""
        # Simple check - actual WebSocket connection would require asyncio
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('127.0.0.1', 8765))
        sock.close()
        return result == 0
    
    def get_pipeline_stats(self) -> Dict:
        """Get pipeline statistics from database"""
        if not self.pipeline_db.exists():
            return {}
        
        conn = sqlite3.connect(str(self.pipeline_db))
        cursor = conn.cursor()
        
        try:
            cursor.execute("SELECT * FROM pipeline_stats")
            stats = {row[0]: row[1] for row in cursor.fetchall()}
        except:
            stats = {}
        
        conn.close()
        return stats
    
    def get_recent_generations(self, limit: int = 10) -> List[Dict]:
        """Get recent generation requests"""
        if not self.pipeline_db.exists():
            return []
        
        conn = sqlite3.connect(str(self.pipeline_db))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT * FROM generation_requests 
                ORDER BY created_at DESC 
                LIMIT ?
            """, (limit,))
            
            generations = [dict(row) for row in cursor.fetchall()]
        except:
            generations = []
        
        conn.close()
        return generations
    
    def get_generation_metrics(self) -> Dict:
        """Calculate generation metrics"""
        if not self.pipeline_db.exists():
            return {
                "total": 0,
                "completed": 0,
                "failed": 0,
                "pending": 0,
                "success_rate": 0,
                "avg_time": 0
            }
        
        conn = sqlite3.connect(str(self.pipeline_db))
        cursor = conn.cursor()
        
        metrics = {}
        
        try:
            # Total requests
            cursor.execute("SELECT COUNT(*) FROM generation_requests")
            metrics["total"] = cursor.fetchone()[0]
            
            # By status
            cursor.execute("""
                SELECT status, COUNT(*) FROM generation_requests 
                GROUP BY status
            """)
            status_counts = dict(cursor.fetchall())
            
            metrics["completed"] = status_counts.get("completed", 0)
            metrics["failed"] = status_counts.get("failed", 0)
            metrics["pending"] = status_counts.get("pending", 0) + status_counts.get("queued", 0)
            
            # Success rate
            if metrics["total"] > 0:
                metrics["success_rate"] = (metrics["completed"] / metrics["total"]) * 100
            else:
                metrics["success_rate"] = 0
            
            # Average generation time
            cursor.execute("""
                SELECT AVG(
                    CAST((julianday(completed_at) - julianday(created_at)) * 86400 AS REAL)
                ) 
                FROM generation_requests 
                WHERE status = 'completed' 
                AND completed_at IS NOT NULL
            """)
            avg_time = cursor.fetchone()[0]
            metrics["avg_time"] = avg_time if avg_time else 0
            
        except Exception as e:
            print(f"Error calculating metrics: {e}")
            metrics = {
                "total": 0,
                "completed": 0,
                "failed": 0,
                "pending": 0,
                "success_rate": 0,
                "avg_time": 0
            }
        
        conn.close()
        return metrics
    
    def get_comfyui_queue(self) -> Dict:
        """Get ComfyUI queue status"""
        try:
            req = urllib.request.Request(f"{self.comfyui_url}/queue")
            with urllib.request.urlopen(req, timeout=2) as response:
                if response.status == 200:
                    return json.loads(response.read())
        except:
            pass
        
        return {"queue_running": [], "queue_pending": []}
    
    def display_dashboard(self):
        """Display monitoring dashboard"""
        if not RICH_AVAILABLE:
            self.display_basic_dashboard()
            return
        
        # Get data
        health = self.check_service_health()
        stats = self.get_pipeline_stats()
        metrics = self.get_generation_metrics()
        recent = self.get_recent_generations(5)
        queue = self.get_comfyui_queue()
        
        # Create layout
        layout = Layout()
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="main"),
            Layout(name="footer", size=3)
        )
        
        layout["main"].split_row(
            Layout(name="left"),
            Layout(name="right")
        )
        
        # Header
        header = Panel(
            "[bold cyan]Terminal Grounds Pipeline Monitor[/bold cyan]\n"
            f"Status: {'[green]HEALTHY' if health['overall'] else '[red]DEGRADED'}[/]",
            style="bold white on blue"
        )
        layout["header"].update(header)
        
        # Service Health Table
        health_table = Table(title="Service Health", box=None)
        health_table.add_column("Service", style="cyan")
        health_table.add_column("Status", style="green")
        
        for service, status in health.items():
            if service != "overall":
                status_text = "[green]OK[/]" if status else "[red]DOWN[/]"
                health_table.add_row(service.upper(), status_text)
        
        # Metrics Table
        metrics_table = Table(title="Generation Metrics", box=None)
        metrics_table.add_column("Metric", style="cyan")
        metrics_table.add_column("Value", style="yellow")
        
        metrics_table.add_row("Total Requests", str(metrics["total"]))
        metrics_table.add_row("Completed", str(metrics["completed"]))
        metrics_table.add_row("Failed", str(metrics["failed"]))
        metrics_table.add_row("Pending", str(metrics["pending"]))
        metrics_table.add_row("Success Rate", f"{metrics['success_rate']:.1f}%")
        metrics_table.add_row("Avg Time", f"{metrics['avg_time']:.1f}s")
        
        # ComfyUI Queue
        queue_table = Table(title="ComfyUI Queue", box=None)
        queue_table.add_column("Status", style="cyan")
        queue_table.add_column("Count", style="yellow")
        
        queue_table.add_row("Running", str(len(queue.get("queue_running", []))))
        queue_table.add_row("Pending", str(len(queue.get("queue_pending", []))))
        
        # Recent Generations
        recent_table = Table(title="Recent Generations", box=None)
        recent_table.add_column("ID", style="cyan", max_width=20)
        recent_table.add_column("Type", style="yellow")
        recent_table.add_column("Status", style="green")
        recent_table.add_column("Created", style="white")
        
        for gen in recent[:5]:
            status_color = {
                "completed": "green",
                "failed": "red",
                "pending": "yellow",
                "processing": "blue"
            }.get(gen.get("status", ""), "white")
            
            recent_table.add_row(
                gen.get("request_id", "")[:20],
                gen.get("generation_type", ""),
                f"[{status_color}]{gen.get('status', '')}[/]",
                gen.get("created_at", "")[:19]
            )
        
        # Update layout
        layout["left"].update(
            Panel.fit(
                f"{health_table}\n\n{metrics_table}\n\n{queue_table}",
                title="System Status"
            )
        )
        
        layout["right"].update(
            Panel.fit(recent_table, title="Activity")
        )
        
        # Footer
        footer = Panel(
            f"Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | "
            "Press Ctrl+C to exit | [yellow]R[/] to refresh",
            style="white on grey23"
        )
        layout["footer"].update(footer)
        
        # Display
        self.console.clear()
        self.console.print(layout)
    
    def display_basic_dashboard(self):
        """Display basic dashboard without rich library"""
        health = self.check_service_health()
        metrics = self.get_generation_metrics()
        
        print("\n" + "="*60)
        print("TERMINAL GROUNDS PIPELINE MONITOR")
        print("="*60)
        
        print("\nSERVICE HEALTH:")
        for service, status in health.items():
            if service != "overall":
                status_text = "OK" if status else "DOWN"
                print(f"  {service.upper()}: {status_text}")
        
        print(f"\nOVERALL STATUS: {'HEALTHY' if health['overall'] else 'DEGRADED'}")
        
        print("\nGENERATION METRICS:")
        print(f"  Total Requests: {metrics['total']}")
        print(f"  Completed: {metrics['completed']}")
        print(f"  Failed: {metrics['failed']}")
        print(f"  Pending: {metrics['pending']}")
        print(f"  Success Rate: {metrics['success_rate']:.1f}%")
        print(f"  Average Time: {metrics['avg_time']:.1f}s")
        
        print("\n" + "="*60)
        print(f"Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    def monitor_loop(self, refresh_interval: int = 5):
        """Continuous monitoring loop"""
        try:
            while True:
                self.display_dashboard()
                time.sleep(refresh_interval)
        except KeyboardInterrupt:
            print("\nMonitoring stopped.")
    
    def get_failed_generations(self) -> List[Dict]:
        """Get all failed generations for retry"""
        if not self.pipeline_db.exists():
            return []
        
        conn = sqlite3.connect(str(self.pipeline_db))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM generation_requests 
            WHERE status = 'failed'
            ORDER BY created_at DESC
        """)
        
        failed = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return failed
    
    def retry_failed_generations(self):
        """Retry all failed generations"""
        failed = self.get_failed_generations()
        
        if not failed:
            print("No failed generations to retry.")
            return
        
        print(f"Found {len(failed)} failed generations.")
        
        # Update status to pending for retry
        conn = sqlite3.connect(str(self.pipeline_db))
        cursor = conn.cursor()
        
        for gen in failed:
            cursor.execute("""
                UPDATE generation_requests 
                SET status = 'pending', attempts = 0 
                WHERE request_id = ?
            """, (gen['request_id'],))
        
        conn.commit()
        conn.close()
        
        print(f"Reset {len(failed)} generations for retry.")
    
    def export_metrics(self, output_file: str = "pipeline_metrics.json"):
        """Export pipeline metrics to JSON"""
        data = {
            "timestamp": datetime.now().isoformat(),
            "health": self.check_service_health(),
            "metrics": self.get_generation_metrics(),
            "stats": self.get_pipeline_stats(),
            "recent_generations": self.get_recent_generations(100)
        }
        
        with open(output_file, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"Metrics exported to {output_file}")

class PipelineController:
    """Control the pipeline operations"""
    
    def __init__(self):
        self.comfyui_url = "http://127.0.0.1:8188"
        self.pipeline_db = Path("C:/Users/Zachg/Terminal-Grounds/Database/pipeline_state.db")
    
    def clear_queue(self):
        """Clear ComfyUI queue"""
        try:
            req = urllib.request.Request(
                f"{self.comfyui_url}/queue",
                method='DELETE'
            )
            with urllib.request.urlopen(req) as response:
                if response.status == 200:
                    print("ComfyUI queue cleared.")
                    return True
        except Exception as e:
            print(f"Failed to clear queue: {e}")
        return False
    
    def pause_pipeline(self):
        """Pause pipeline processing (sets all pending to paused)"""
        if not self.pipeline_db.exists():
            print("Pipeline database not found.")
            return
        
        conn = sqlite3.connect(str(self.pipeline_db))
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE generation_requests 
            SET status = 'paused' 
            WHERE status IN ('pending', 'queued')
        """)
        
        affected = cursor.rowcount
        conn.commit()
        conn.close()
        
        print(f"Paused {affected} pending generations.")
    
    def resume_pipeline(self):
        """Resume pipeline processing"""
        if not self.pipeline_db.exists():
            print("Pipeline database not found.")
            return
        
        conn = sqlite3.connect(str(self.pipeline_db))
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE generation_requests 
            SET status = 'pending' 
            WHERE status = 'paused'
        """)
        
        affected = cursor.rowcount
        conn.commit()
        conn.close()
        
        print(f"Resumed {affected} paused generations.")
    
    def reset_failed(self):
        """Reset all failed generations for retry"""
        monitor = PipelineMonitor()
        monitor.retry_failed_generations()

def main():
    parser = argparse.ArgumentParser(description="Terminal Grounds Pipeline Monitor & Control")
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Monitor command
    monitor_parser = subparsers.add_parser('monitor', help='Monitor pipeline status')
    monitor_parser.add_argument('--refresh', type=int, default=5, help='Refresh interval in seconds')
    
    # Status command
    status_parser = subparsers.add_parser('status', help='Show current status')
    
    # Control commands
    control_parser = subparsers.add_parser('control', help='Control pipeline operations')
    control_parser.add_argument('action', choices=['pause', 'resume', 'clear-queue', 'retry-failed'])
    
    # Export command
    export_parser = subparsers.add_parser('export', help='Export metrics')
    export_parser.add_argument('--output', default='pipeline_metrics.json', help='Output file')
    
    args = parser.parse_args()
    
    if args.command == 'monitor':
        monitor = PipelineMonitor()
        monitor.monitor_loop(args.refresh)
    
    elif args.command == 'status':
        monitor = PipelineMonitor()
        monitor.display_dashboard()
    
    elif args.command == 'control':
        controller = PipelineController()
        
        if args.action == 'pause':
            controller.pause_pipeline()
        elif args.action == 'resume':
            controller.resume_pipeline()
        elif args.action == 'clear-queue':
            controller.clear_queue()
        elif args.action == 'retry-failed':
            controller.reset_failed()
    
    elif args.command == 'export':
        monitor = PipelineMonitor()
        monitor.export_metrics(args.output)
    
    else:
        # Default: show status once
        monitor = PipelineMonitor()
        monitor.display_dashboard()

if __name__ == "__main__":
    main()