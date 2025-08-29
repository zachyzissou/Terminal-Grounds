"""
Terminal Grounds Documentation Monitoring Framework
Phase 3: Advanced Governance & Automation

Real-time monitoring and alerting for documentation quality and compliance.
"""

import os
import time
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass
import logging
import json
import schedule

# Import our validation framework functions
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class ValidationResult:
    """Result of a validation check"""
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    suggestions: List[str]

def get_all_markdown_files(docs_root: str = "../../docs") -> List[Path]:
    """Get all markdown files in the docs directory"""
    docs_path = Path(docs_root)
    return list(docs_path.rglob("*.md"))

def validate_all_documents(docs_root: str = "../../docs") -> Dict[str, ValidationResult]:
    """Validate all documents - simplified version for monitoring"""
    results = {}

    for md_file in get_all_markdown_files(docs_root):
        if md_file.name.lower() == "readme.md":
            continue

        # Simple validation - check if frontmatter exists
        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()

            has_frontmatter = content.startswith('---')
            is_valid = has_frontmatter

            if is_valid:
                results[str(md_file.relative_to(docs_root))] = ValidationResult(True, [], [], [])
            else:
                results[str(md_file.relative_to(docs_root))] = ValidationResult(False, ["Missing frontmatter"], [], [])

        except Exception as e:
            results[str(md_file.relative_to(docs_root))] = ValidationResult(False, [f"Error reading file: {e}"], [], [])

    return results

@dataclass
class MonitoringConfig:
    """Configuration for monitoring system"""
    check_interval_minutes: int = 60
    alert_threshold: float = 0.8  # Alert if quality drops below 80%
    enable_email_alerts: bool = False
    email_recipients: List[str] = None
    log_file: str = "monitoring.log"
    history_file: str = "quality_history.json"

@dataclass
class QualityMetrics:
    """Quality metrics for documentation"""
    timestamp: datetime
    total_docs: int
    valid_docs: int
    invalid_docs: int
    success_rate: float
    issues_by_type: Dict[str, int]

class QualityMonitor:
    """
    Monitors documentation quality over time
    """

    def __init__(self, config: MonitoringConfig = None, docs_root: str = "../../docs"):
        self.config = config or MonitoringConfig()
        self.docs_root = Path(docs_root)
        self.history: List[QualityMetrics] = []
        self.logger = logging.getLogger(__name__)

        # Setup logging
        logging.basicConfig(
            filename=self.config.log_file,
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )

        # Load existing history
        self._load_history()

    def _load_history(self):
        """Load quality history from file"""
        if os.path.exists(self.config.history_file):
            try:
                with open(self.config.history_file, 'r') as f:
                    data = json.load(f)
                    self.history = [
                        QualityMetrics(
                            timestamp=datetime.fromisoformat(item['timestamp']),
                            total_docs=item['total_docs'],
                            valid_docs=item['valid_docs'],
                            invalid_docs=item['invalid_docs'],
                            success_rate=item['success_rate'],
                            issues_by_type=item['issues_by_type']
                        )
                        for item in data
                    ]
            except Exception as e:
                self.logger.error(f"Failed to load history: {e}")

    def _save_history(self):
        """Save quality history to file"""
        try:
            data = [
                {
                    'timestamp': metric.timestamp.isoformat(),
                    'total_docs': metric.total_docs,
                    'valid_docs': metric.valid_docs,
                    'invalid_docs': metric.invalid_docs,
                    'success_rate': metric.success_rate,
                    'issues_by_type': metric.issues_by_type
                }
                for metric in self.history[-100:]  # Keep last 100 entries
            ]

            with open(self.config.history_file, 'w') as f:
                json.dump(data, f, indent=2)

        except Exception as e:
            self.logger.error(f"Failed to save history: {e}")

    def check_quality(self) -> QualityMetrics:
        """
        Perform quality check and return metrics
        """
        self.logger.info("Performing quality check...")

        # Get validation results
        validation_results = validate_all_documents(str(self.docs_root))

        # Calculate metrics
        total_docs = len(validation_results)
        valid_docs = sum(1 for result in validation_results.values() if result.is_valid)
        invalid_docs = total_docs - valid_docs
        success_rate = (valid_docs / total_docs * 100) if total_docs > 0 else 0

        # Categorize issues
        issues_by_type = {
            'missing_frontmatter': 0,
            'invalid_fields': 0,
            'cross_ref_issues': 0,
            'naming_issues': 0,
            'other': 0
        }

        for result in validation_results.values():
            if not result.is_valid:
                for error in result.errors:
                    if 'Missing frontmatter' in error:
                        issues_by_type['missing_frontmatter'] += 1
                    elif 'Invalid' in error:
                        issues_by_type['invalid_fields'] += 1
                    elif 'Related document not found' in error:
                        issues_by_type['cross_ref_issues'] += 1
                    elif 'doesn\'t match' in error and 'pattern' in error:
                        issues_by_type['naming_issues'] += 1
                    else:
                        issues_by_type['other'] += 1

        metrics = QualityMetrics(
            timestamp=datetime.now(),
            total_docs=total_docs,
            valid_docs=valid_docs,
            invalid_docs=invalid_docs,
            success_rate=success_rate,
            issues_by_type=issues_by_type
        )

        # Add to history
        self.history.append(metrics)
        self._save_history()

        self.logger.info(f"Quality check complete: {success_rate:.1f}% valid ({valid_docs}/{total_docs})")

        return metrics

    def get_quality_trend(self, hours: int = 24) -> Dict[str, Any]:
        """
        Get quality trend over the specified time period
        """
        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_metrics = [m for m in self.history if m.timestamp > cutoff_time]

        if not recent_metrics:
            return {"trend": "insufficient_data", "change": 0, "message": "Not enough data points"}

        # Calculate trend
        first_rate = recent_metrics[0].success_rate
        last_rate = recent_metrics[-1].success_rate
        change = last_rate - first_rate

        if change > 5:
            trend = "improving"
        elif change < -5:
            trend = "declining"
        else:
            trend = "stable"

        return {
            "trend": trend,
            "change": change,
            "first_rate": first_rate,
            "last_rate": last_rate,
            "data_points": len(recent_metrics)
        }

    def should_alert(self, metrics: QualityMetrics) -> bool:
        """
        Determine if an alert should be sent
        """
        if metrics.success_rate < self.config.alert_threshold * 100:
            return True

        # Check for significant decline
        trend = self.get_quality_trend()
        if trend["trend"] == "declining" and abs(trend["change"]) > 10:
            return True

        return False

    def send_alert(self, metrics: QualityMetrics):
        """
        Send alert notification
        """
        self.logger.warning(f"Quality alert triggered: {metrics.success_rate:.1f}% valid documents")

        alert_message = f"""
Terminal Grounds Documentation Quality Alert
==========================================

Timestamp: {metrics.timestamp.strftime('%Y-%m-%d %H:%M:%S')}
Success Rate: {metrics.success_rate:.1f}%
Valid Documents: {metrics.valid_docs}/{metrics.total_docs}

Issues by Type:
{json.dumps(metrics.issues_by_type, indent=2)}

Action Required: Review and fix documentation quality issues.
"""

        if self.config.enable_email_alerts and self.config.email_recipients:
            # Email implementation would go here
            self.logger.info(f"Email alert would be sent to: {self.config.email_recipients}")

        # Log alert
        with open("quality_alerts.log", "a") as f:
            f.write(alert_message + "\n")

class ContinuousMonitor:
    """
    Runs continuous monitoring with scheduled checks
    """

    def __init__(self, config: MonitoringConfig = None):
        self.config = config or MonitoringConfig()
        self.monitor = QualityMonitor(self.config)
        self.is_running = False

    def start_monitoring(self):
        """
        Start continuous monitoring
        """
        self.is_running = True
        self.logger = logging.getLogger(__name__)

        # Schedule quality checks
        schedule.every(self.config.check_interval_minutes).minutes.do(self._scheduled_check)

        self.logger.info(f"Started continuous monitoring (interval: {self.config.check_interval_minutes} minutes)")

        # Run initial check
        self._scheduled_check()

        # Keep running
        while self.is_running:
            schedule.run_pending()
            time.sleep(60)  # Check every minute

    def stop_monitoring(self):
        """
        Stop continuous monitoring
        """
        self.is_running = False
        self.logger.info("Stopped continuous monitoring")

    def _scheduled_check(self):
        """
        Perform scheduled quality check
        """
        try:
            metrics = self.monitor.check_quality()

            if self.monitor.should_alert(metrics):
                self.monitor.send_alert(metrics)

        except Exception as e:
            self.logger.error(f"Scheduled check failed: {e}")

class DocumentationWatcher:
    """
    Watches for file changes and triggers validation
    """

    def __init__(self, docs_root: str = "../../docs"):
        self.docs_root = Path(docs_root)
        self.last_check = {}
        self.monitor = QualityMonitor(docs_root=str(self.docs_root))

    def check_for_changes(self) -> List[str]:
        """
        Check for recently modified files
        """
        changed_files = []

        for md_file in get_all_markdown_files(str(self.docs_root)):
            if md_file.name.lower() == "readme.md":
                continue

            try:
                mtime = md_file.stat().st_mtime
                last_mtime = self.last_check.get(str(md_file), 0)

                if mtime > last_mtime:
                    changed_files.append(str(md_file))
                    self.last_check[str(md_file)] = mtime

            except Exception as e:
                logger.error(f"Error checking file {md_file}: {e}")

        return changed_files

    def validate_changed_files(self) -> Dict[str, ValidationResult]:
        """
        Validate only the files that have changed
        """
        changed_files = self.check_for_changes()
        results = {}

        for file_path in changed_files:
            # Simple validation for changed files
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                has_frontmatter = content.startswith('---')
                is_valid = has_frontmatter

                if is_valid:
                    results[file_path] = ValidationResult(True, [], [], [])
                else:
                    results[file_path] = ValidationResult(False, ["Missing frontmatter"], [], [])

            except Exception as e:
                results[file_path] = ValidationResult(False, [f"Error reading file: {e}"], [], [])

        return results

# Utility functions
def run_quality_check() -> QualityMetrics:
    """Run a one-time quality check"""
    monitor = QualityMonitor()
    return monitor.check_quality()

def get_quality_trend(hours: int = 24) -> Dict[str, Any]:
    """Get quality trend"""
    monitor = QualityMonitor()
    return monitor.get_quality_trend(hours)

def start_continuous_monitoring(interval_minutes: int = 60):
    """Start continuous monitoring"""
    config = MonitoringConfig(check_interval_minutes=interval_minutes)
    monitor = ContinuousMonitor(config)

    try:
        monitor.start_monitoring()
    except KeyboardInterrupt:
        monitor.stop_monitoring()

if __name__ == "__main__":
    print("📊 Terminal Grounds Documentation Monitoring System")
    print("=" * 60)

    # Run quality check
    print("🔍 Running quality check...")
    metrics = run_quality_check()

    print(f"📈 Current Quality: {metrics.success_rate:.1f}%")
    print(f"   Valid: {metrics.valid_docs}/{metrics.total_docs}")
    print(f"   Issues: {sum(metrics.issues_by_type.values())}")

    # Get trend
    print("\n📉 Quality Trend (24h):")
    trend = get_quality_trend()
    print(f"   Trend: {trend['trend']}")
    print(f"   Change: {trend['change']:+.1f}%")

    # Check for recent changes
    print("\n📁 Checking for recent file changes...")
    watcher = DocumentationWatcher()
    changed_files = watcher.check_for_changes()
    print(f"   Changed files: {len(changed_files)}")

    if changed_files:
        print("   Recent changes:")
        for file in changed_files[:5]:  # Show first 5
            print(f"     • {Path(file).name}")

    print("\n✅ Monitoring system operational!")
    print("🎯 Phase 3 real-time quality assurance active!")
