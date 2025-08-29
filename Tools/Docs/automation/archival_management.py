"""
Terminal Grounds Documentation Automation Framework
Phase 4.1.1.3: Archival Management System

Intelligent content archival, retirement processes, and historical preservation
for comprehensive document lifecycle management.
"""

import os
import shutil
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import logging
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ArchivalStatus(Enum):
    """Status of document archival"""
    ACTIVE = "active"
    PENDING_ARCHIVAL = "pending_archival"
    ARCHIVED = "archived"
    RETIRED = "retired"
    DELETED = "deleted"

class RetentionPolicy(Enum):
    """Document retention policies"""
    PERMANENT = "permanent"  # Never delete
    LONG_TERM = "long_term"  # Keep for extended period
    STANDARD = "standard"   # Standard retention period
    SHORT_TERM = "short_term"  # Keep for limited time
    TEMPORARY = "temporary"   # Delete after use

@dataclass
class ArchivalRecord:
    """Record of a document's archival information"""
    document_path: str
    original_path: str
    archival_path: str
    status: ArchivalStatus
    archived_at: datetime
    archived_by: str
    retention_policy: RetentionPolicy
    retention_until: Optional[datetime]
    file_hash: str
    metadata: Dict[str, Any]
    access_log: List[Dict[str, Any]] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)

@dataclass
class ArchivalPolicy:
    """Archival policy for a document type"""
    document_type: str
    retention_policy: RetentionPolicy
    retention_period_days: int
    archival_triggers: List[str]
    review_required: bool
    auto_archive: bool
    notification_recipients: List[str]

@dataclass
class ArchivalAnalytics:
    """Analytics for archival operations"""
    total_documents: int = 0
    archived_documents: int = 0
    retired_documents: int = 0
    deleted_documents: int = 0
    storage_saved_mb: float = 0.0
    average_retention_days: float = 0.0
    policy_compliance_rate: float = 0.0

class ArchivalManagementSystem:
    """
    Intelligent archival management for document lifecycle
    """

    def __init__(self, docs_root: str = "docs"):
        self.docs_root = Path(docs_root)
        self.archival_records: Dict[str, ArchivalRecord] = {}
        self.archival_policies: Dict[str, ArchivalPolicy] = {}
        self.analytics = ArchivalAnalytics()

        # Setup archival directories
        self.archive_root = self.docs_root / ".." / "Archive"
        self.retired_root = self.docs_root / ".." / "Retired"
        self.temp_root = self.docs_root / ".." / "Temp"

        self._setup_directories()
        self._load_archival_data()
        self._load_policies()

    def _setup_directories(self):
        """Setup archival directory structure"""
        directories = [
            self.archive_root,
            self.archive_root / "permanent",
            self.archive_root / "long_term",
            self.archive_root / "standard",
            self.retired_root,
            self.temp_root
        ]

        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)

    def _load_archival_data(self):
        """Load archival records from storage"""
        archival_file = self.docs_root / ".." / "Tools" / "Docs" / "automation" / "archival_records.json"

        if archival_file.exists():
            try:
                with open(archival_file, 'r', encoding='utf-8') as f:
                    records_data = json.load(f)

                for doc_path, record_data in records_data.items():
                    record = ArchivalRecord(
                        document_path=record_data["document_path"],
                        original_path=record_data["original_path"],
                        archival_path=record_data["archival_path"],
                        status=ArchivalStatus(record_data["status"]),
                        archived_at=datetime.fromisoformat(record_data["archived_at"]),
                        archived_by=record_data["archived_by"],
                        retention_policy=RetentionPolicy(record_data["retention_policy"]),
                        retention_until=datetime.fromisoformat(record_data["retention_until"]) if record_data.get("retention_until") else None,
                        file_hash=record_data["file_hash"],
                        metadata=record_data["metadata"],
                        access_log=record_data.get("access_log", []),
                        dependencies=record_data.get("dependencies", [])
                    )
                    self.archival_records[doc_path] = record

            except Exception as e:
                logger.error(f"Error loading archival records: {e}")

    def _load_policies(self):
        """Load archival policies"""
        policies_file = self.docs_root / ".." / "Tools" / "Docs" / "automation" / "archival_policies.yaml"

        if policies_file.exists():
            try:
                import yaml
                with open(policies_file, 'r', encoding='utf-8') as f:
                    policies_data = yaml.safe_load(f)

                for policy_data in policies_data.get("policies", []):
                    policy = ArchivalPolicy(
                        document_type=policy_data["document_type"],
                        retention_policy=RetentionPolicy(policy_data["retention_policy"]),
                        retention_period_days=policy_data["retention_period_days"],
                        archival_triggers=policy_data.get("archival_triggers", []),
                        review_required=policy_data.get("review_required", False),
                        auto_archive=policy_data.get("auto_archive", True),
                        notification_recipients=policy_data.get("notification_recipients", [])
                    )
                    self.archival_policies[policy.document_type] = policy

            except Exception as e:
                logger.error(f"Error loading archival policies: {e}")

        # Create default policies if none exist
        if not self.archival_policies:
            self._create_default_policies()

    def _create_default_policies(self):
        """Create default archival policies"""

        policies = [
            ArchivalPolicy(
                document_type="technical",
                retention_policy=RetentionPolicy.LONG_TERM,
                retention_period_days=365 * 5,  # 5 years
                archival_triggers=["last_modified > 2 years", "superseded", "project_completed"],
                review_required=True,
                auto_archive=True,
                notification_recipients=["tech_lead", "architect"]
            ),
            ArchivalPolicy(
                document_type="design",
                retention_policy=RetentionPolicy.STANDARD,
                retention_period_days=365 * 3,  # 3 years
                archival_triggers=["last_modified > 1 year", "design_implemented"],
                review_required=True,
                auto_archive=True,
                notification_recipients=["design_lead", "product_manager"]
            ),
            ArchivalPolicy(
                document_type="process",
                retention_policy=RetentionPolicy.LONG_TERM,
                retention_period_days=365 * 7,  # 7 years
                archival_triggers=["process_deprecated", "regulation_changed"],
                review_required=True,
                auto_archive=False,  # Manual review required
                notification_recipients=["process_owner", "compliance_officer"]
            ),
            ArchivalPolicy(
                document_type="reference",
                retention_policy=RetentionPolicy.PERMANENT,
                retention_period_days=0,  # Never expires
                archival_triggers=[],  # Manual only
                review_required=True,
                auto_archive=False,
                notification_recipients=["documentation_team"]
            ),
            ArchivalPolicy(
                document_type="temporary",
                retention_policy=RetentionPolicy.TEMPORARY,
                retention_period_days=30,  # 30 days
                archival_triggers=["created > 30 days"],
                review_required=False,
                auto_archive=True,
                notification_recipients=[]
            )
        ]

        for policy in policies:
            self.archival_policies[policy.document_type] = policy

    def _save_archival_data(self):
        """Save archival records to storage"""
        archival_file = self.docs_root / ".." / "Tools" / "Docs" / "automation" / "archival_records.json"

        records_data = {}
        for doc_path, record in self.archival_records.items():
            records_data[doc_path] = {
                "document_path": record.document_path,
                "original_path": record.original_path,
                "archival_path": record.archival_path,
                "status": record.status.value,
                "archived_at": record.archived_at.isoformat(),
                "archived_by": record.archived_by,
                "retention_policy": record.retention_policy.value,
                "retention_until": record.retention_until.isoformat() if record.retention_until else None,
                "file_hash": record.file_hash,
                "metadata": record.metadata,
                "access_log": record.access_log,
                "dependencies": record.dependencies
            }

        with open(archival_file, 'w', encoding='utf-8') as f:
            json.dump(records_data, f, indent=2, ensure_ascii=False)

    def analyze_document_for_archival(self, document_path: str) -> Dict[str, Any]:
        """
        Analyze a document to determine if it should be archived
        """
        doc_path = Path(document_path)

        if not doc_path.exists():
            return {"error": "Document not found"}

        # Get document metadata
        metadata = self._get_document_metadata(doc_path)

        # Determine document type
        document_type = self._determine_document_type(document_path)

        # Get applicable policy
        policy = self.archival_policies.get(document_type)
        if not policy:
            policy = self.archival_policies.get("technical")  # Default

        # Check archival triggers
        archival_reasons = []
        should_archive = False

        for trigger in policy.archival_triggers:
            if self._evaluate_trigger(trigger, metadata):
                archival_reasons.append(trigger)
                should_archive = True

        # Calculate retention information
        retention_until = None
        if policy.retention_policy != RetentionPolicy.PERMANENT:
            retention_until = datetime.now() + timedelta(days=policy.retention_period_days)

        return {
            "document_path": str(doc_path),
            "document_type": document_type,
            "should_archive": should_archive,
            "archival_reasons": archival_reasons,
            "retention_policy": policy.retention_policy.value,
            "retention_until": retention_until.isoformat() if retention_until else None,
            "requires_review": policy.review_required,
            "auto_archive": policy.auto_archive,
            "metadata": metadata
        }

    def _get_document_metadata(self, doc_path: Path) -> Dict[str, Any]:
        """Get document metadata"""
        try:
            stat = doc_path.stat()
            return {
                "size_bytes": stat.st_size,
                "created_at": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                "modified_at": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "last_accessed": datetime.fromtimestamp(stat.st_atime).isoformat(),
                "exists": True
            }
        except Exception as e:
            logger.error(f"Error getting metadata for {doc_path}: {e}")
            return {"error": str(e), "exists": False}

    def _determine_document_type(self, document_path: str) -> str:
        """Determine document type from path and content"""
        path_lower = document_path.lower()

        if "design" in path_lower or "ui" in path_lower or "ux" in path_lower:
            return "design"
        elif "process" in path_lower or "procedure" in path_lower or "workflow" in path_lower:
            return "process"
        elif "reference" in path_lower or "guide" in path_lower:
            return "reference"
        elif "temp" in path_lower or "draft" in path_lower:
            return "temporary"
        else:
            return "technical"

    def _evaluate_trigger(self, trigger: str, metadata: Dict[str, Any]) -> bool:
        """Evaluate if an archival trigger condition is met"""
        try:
            if "last_modified >" in trigger:
                # Extract days from trigger
                days_str = trigger.split(">")[1].strip().split()[0]
                if "year" in days_str:
                    days = int(days_str.split("year")[0]) * 365
                elif "month" in days_str:
                    days = int(days_str.split("month")[0]) * 30
                else:
                    days = int(days_str)

                last_modified = datetime.fromisoformat(metadata["modified_at"])
                cutoff_date = datetime.now() - timedelta(days=days)

                return last_modified < cutoff_date

            elif "created >" in trigger:
                days_str = trigger.split(">")[1].strip().split()[0]
                days = int(days_str) if days_str.isdigit() else 30

                created = datetime.fromisoformat(metadata["created_at"])
                cutoff_date = datetime.now() - timedelta(days=days)

                return created < cutoff_date

            elif "superseded" in trigger:
                # Would check if document has been superseded by newer version
                return False  # Placeholder

            elif "project_completed" in trigger:
                # Would check project status
                return False  # Placeholder

            else:
                return False

        except Exception as e:
            logger.error(f"Error evaluating trigger '{trigger}': {e}")
            return False

    def archive_document(self, document_path: str, archived_by: str,
                        reason: str = "", force: bool = False) -> Dict[str, Any]:
        """
        Archive a document
        """
        doc_path = Path(document_path)

        if not doc_path.exists():
            return {"error": "Document not found"}

        # Analyze document
        analysis = self.analyze_document_for_archival(document_path)

        if not analysis.get("should_archive") and not force:
            return {
                "error": "Document does not meet archival criteria",
                "analysis": analysis
            }

        # Determine archival location
        document_type = analysis["document_type"]
        policy = self.archival_policies.get(document_type)

        if policy.retention_policy == RetentionPolicy.PERMANENT:
            archival_dir = self.archive_root / "permanent"
        elif policy.retention_policy == RetentionPolicy.LONG_TERM:
            archival_dir = self.archive_root / "long_term"
        elif policy.retention_policy == RetentionPolicy.TEMPORARY:
            archival_dir = self.temp_root
        else:
            archival_dir = self.archive_root / "standard"

        # Create archival path
        relative_path = doc_path.relative_to(self.docs_root)
        archival_path = archival_dir / relative_path
        archival_path.parent.mkdir(parents=True, exist_ok=True)

        # Calculate file hash
        file_hash = self._calculate_file_hash(doc_path)

        # Move file
        try:
            shutil.move(str(doc_path), str(archival_path))
        except Exception as e:
            return {"error": f"Failed to move file: {e}"}

        # Create archival record
        record = ArchivalRecord(
            document_path=str(archival_path),
            original_path=document_path,
            archival_path=str(archival_path),
            status=ArchivalStatus.ARCHIVED,
            archived_at=datetime.now(),
            archived_by=archived_by,
            retention_policy=policy.retention_policy,
            retention_until=datetime.fromisoformat(analysis["retention_until"]) if analysis.get("retention_until") else None,
            file_hash=file_hash,
            metadata={
                "original_metadata": analysis["metadata"],
                "archival_reason": reason,
                "document_type": document_type,
                "policy_name": policy.retention_policy.value
            }
        )

        self.archival_records[document_path] = record

        # Save data
        self._save_archival_data()

        # Update analytics
        self._update_analytics()

        # Send notifications
        self._send_archival_notification(record, "archived")

        logger.info(f"Document archived: {document_path} -> {archival_path}")

        return {
            "success": True,
            "archival_path": str(archival_path),
            "retention_policy": policy.retention_policy.value,
            "retention_until": analysis.get("retention_until"),
            "record": {
                "status": record.status.value,
                "archived_at": record.archived_at.isoformat(),
                "archived_by": record.archived_by
            }
        }

    def _calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA256 hash of file"""
        try:
            with open(file_path, 'rb') as f:
                return hashlib.sha256(f.read()).hexdigest()
        except Exception as e:
            logger.error(f"Error calculating file hash: {e}")
            return ""

    def retire_document(self, document_path: str, retired_by: str,
                       reason: str = "") -> Dict[str, Any]:
        """
        Retire a document (move to retired storage)
        """
        if document_path not in self.archival_records:
            return {"error": "Document not found in archival records"}

        record = self.archival_records[document_path]

        # Move to retired location
        retired_path = self.retired_root / Path(record.archival_path).relative_to(self.archive_root)
        retired_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            shutil.move(record.archival_path, str(retired_path))
        except Exception as e:
            return {"error": f"Failed to move file: {e}"}

        # Update record
        record.archival_path = str(retired_path)
        record.status = ArchivalStatus.RETIRED
        record.metadata["retirement_reason"] = reason
        record.metadata["retired_at"] = datetime.now().isoformat()
        record.metadata["retired_by"] = retired_by

        # Save data
        self._save_archival_data()

        # Update analytics
        self._update_analytics()

        # Send notifications
        self._send_archival_notification(record, "retired")

        logger.info(f"Document retired: {document_path} -> {retired_path}")

        return {
            "success": True,
            "retired_path": str(retired_path),
            "retirement_date": datetime.now().isoformat()
        }

    def delete_document(self, document_path: str, deleted_by: str,
                       reason: str = "") -> Dict[str, Any]:
        """
        Permanently delete a document
        """
        if document_path not in self.archival_records:
            return {"error": "Document not found in archival records"}

        record = self.archival_records[document_path]

        # Check retention policy
        if record.retention_policy == RetentionPolicy.PERMANENT:
            return {"error": "Cannot delete document with permanent retention policy"}

        # Check if retention period has expired
        if record.retention_until and datetime.now() < record.retention_until:
            return {"error": "Document is still within retention period"}

        # Delete file
        try:
            os.remove(record.archival_path)
        except Exception as e:
            return {"error": f"Failed to delete file: {e}"}

        # Update record
        record.status = ArchivalStatus.DELETED
        record.metadata["deletion_reason"] = reason
        record.metadata["deleted_at"] = datetime.now().isoformat()
        record.metadata["deleted_by"] = deleted_by

        # Save data
        self._save_archival_data()

        # Update analytics
        self._update_analytics()

        logger.info(f"Document deleted: {document_path}")

        return {
            "success": True,
            "deletion_date": datetime.now().isoformat()
        }

    def restore_document(self, document_path: str, restored_by: str,
                        target_path: str = None) -> Dict[str, Any]:
        """
        Restore a document from archive
        """
        if document_path not in self.archival_records:
            return {"error": "Document not found in archival records"}

        record = self.archival_records[document_path]

        # Determine restore location
        if not target_path:
            target_path = record.original_path

        target_file = Path(target_path)
        target_file.parent.mkdir(parents=True, exist_ok=True)

        # Copy file back
        try:
            shutil.copy2(record.archival_path, target_path)
        except Exception as e:
            return {"error": f"Failed to restore file: {e}"}

        # Log access
        access_entry = {
            "timestamp": datetime.now().isoformat(),
            "action": "restored",
            "user": restored_by,
            "target_path": target_path
        }
        record.access_log.append(access_entry)

        # Save data
        self._save_archival_data()

        # Send notifications
        self._send_archival_notification(record, "restored")

        logger.info(f"Document restored: {record.archival_path} -> {target_path}")

        return {
            "success": True,
            "restored_path": target_path,
            "restored_at": datetime.now().isoformat()
        }

    def get_archival_status(self, document_path: str) -> Dict[str, Any]:
        """Get archival status of a document"""
        if document_path in self.archival_records:
            record = self.archival_records[document_path]
            return {
                "status": record.status.value,
                "archived_at": record.archived_at.isoformat(),
                "archived_by": record.archived_by,
                "retention_policy": record.retention_policy.value,
                "retention_until": record.retention_until.isoformat() if record.retention_until else None,
                "archival_path": record.archival_path,
                "days_until_expiry": (record.retention_until - datetime.now()).days if record.retention_until else None,
                "access_count": len(record.access_log)
            }
        else:
            # Check if document exists and analyze
            analysis = self.analyze_document_for_archival(document_path)
            return {
                "status": "active",
                "analysis": analysis
            }

    def find_documents_for_archival(self) -> List[Dict[str, Any]]:
        """Find documents that should be archived"""
        candidates = []

        # Scan docs directory
        for md_file in self.docs_root.rglob("*.md"):
            if md_file.name.lower() == "readme.md":
                continue

            analysis = self.analyze_document_for_archival(str(md_file))
            if analysis.get("should_archive"):
                candidates.append(analysis)

        return candidates

    def process_pending_archivals(self) -> Dict[str, Any]:
        """Process documents pending archival"""
        candidates = self.find_documents_for_archival()
        results = {
            "processed": 0,
            "archived": 0,
            "skipped": 0,
            "errors": []
        }

        for candidate in candidates:
            document_path = candidate["document_path"]

            # Check if auto-archive is enabled
            if candidate.get("auto_archive"):
                try:
                    result = self.archive_document(
                        document_path=document_path,
                        archived_by="system",
                        reason="Automatic archival based on policy"
                    )

                    if result.get("success"):
                        results["archived"] += 1
                    else:
                        results["errors"].append({
                            "document": document_path,
                            "error": result.get("error", "Unknown error")
                        })

                except Exception as e:
                    results["errors"].append({
                        "document": document_path,
                        "error": str(e)
                    })
            else:
                results["skipped"] += 1

            results["processed"] += 1

        logger.info(f"Archival processing complete: {results['archived']} archived, {results['skipped']} skipped, {len(results['errors'])} errors")

        return results

    def _send_archival_notification(self, record: ArchivalRecord, action: str):
        """Send archival notification"""
        # Implementation would send email/Slack notifications
        logger.info(f"Archival notification: {action} for {record.document_path}")

    def _update_analytics(self):
        """Update archival analytics"""
        records = list(self.archival_records.values())

        self.analytics.total_documents = len(records)
        self.analytics.archived_documents = sum(1 for r in records if r.status == ArchivalStatus.ARCHIVED)
        self.analytics.retired_documents = sum(1 for r in records if r.status == ArchivalStatus.RETIRED)
        self.analytics.deleted_documents = sum(1 for r in records if r.status == ArchivalStatus.DELETED)

        # Calculate average retention
        retention_days = []
        for record in records:
            if record.retention_until:
                retention_days.append((record.retention_until - record.archived_at).days)

        if retention_days:
            self.analytics.average_retention_days = sum(retention_days) / len(retention_days)

    def get_archival_analytics(self) -> Dict[str, Any]:
        """Get comprehensive archival analytics"""
        self._update_analytics()

        return {
            "total_documents": self.analytics.total_documents,
            "archived_documents": self.analytics.archived_documents,
            "retired_documents": self.analytics.retired_documents,
            "deleted_documents": self.analytics.deleted_documents,
            "archival_rate": (self.analytics.archived_documents / self.analytics.total_documents * 100) if self.analytics.total_documents > 0 else 0,
            "average_retention_days": self.analytics.average_retention_days,
            "policy_distribution": self._get_policy_distribution(),
            "storage_by_policy": self._get_storage_by_policy()
        }

    def _get_policy_distribution(self) -> Dict[str, int]:
        """Get distribution of documents by retention policy"""
        distribution = {}
        for record in self.archival_records.values():
            policy = record.retention_policy.value
            distribution[policy] = distribution.get(policy, 0) + 1
        return distribution

    def _get_storage_by_policy(self) -> Dict[str, float]:
        """Get storage usage by retention policy"""
        storage = {}
        for record in self.archival_records.values():
            policy = record.retention_policy.value
            # Estimate storage (would need actual file sizes)
            storage[policy] = storage.get(policy, 0) + 1.0  # Placeholder
        return storage

# Global archival management system instance
archival_system = ArchivalManagementSystem()

def get_archival_system() -> ArchivalManagementSystem:
    """Get the global archival management system instance"""
    return archival_system

if __name__ == "__main__":
    # Test the archival management system
    print("Testing Terminal Grounds Archival Management System")
    print("=" * 60)

    system = get_archival_system()

    # Show archival policies
    print("Archival Policies:")
    for doc_type, policy in system.archival_policies.items():
        print(f"  - {doc_type}: {policy.retention_policy.value} ({policy.retention_period_days} days)")

    # Analyze a test document
    test_doc = "docs/test_document.md"
    print(f"\nAnalyzing document: {test_doc}")
    analysis = system.analyze_document_for_archival(test_doc)

    if "error" not in analysis:
        print(f"  - Document Type: {analysis['document_type']}")
        print(f"  - Should Archive: {analysis['should_archive']}")
        print(f"  - Retention Policy: {analysis['retention_policy']}")
        print(f"  - Retention Until: {analysis.get('retention_until', 'N/A')}")
    else:
        print(f"  - Error: {analysis['error']}")

    # Find documents for archival
    candidates = system.find_documents_for_archival()
    print(f"\nDocuments ready for archival: {len(candidates)}")

    for candidate in candidates[:3]:  # Show first 3
        print(f"  - {candidate['document_path']} ({candidate['document_type']})")

    # Get archival analytics
    analytics = system.get_archival_analytics()
    print(f"\nArchival Analytics:")
    print(f"  - Total Documents: {analytics['total_documents']}")
    print(f"  - Archived Documents: {analytics['archived_documents']}")
    print(f"  - Archival Rate: {analytics['archival_rate']:.1f}%")
    print(f"  - Average Retention: {analytics['average_retention_days']:.1f} days")

    print("\nArchival Management System operational!")
    print("Phase 4.1.1.3 Archival Management System ready for implementation.")
