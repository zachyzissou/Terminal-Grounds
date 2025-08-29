"""
Terminal Grounds Documentation Automation Framework
Phase 4.1.1.3: Collaborative Features System

Multi-author editing support, change tracking, and review workflows
for collaborative document creation and maintenance.
"""

import os
import uuid
import json
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import logging
import difflib

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class CollaborationRole(Enum):
    """Roles in collaborative document editing"""
    OWNER = "owner"
    EDITOR = "editor"
    REVIEWER = "reviewer"
    VIEWER = "viewer"

class ChangeType(Enum):
    """Types of document changes"""
    CONTENT_ADDITION = "content_addition"
    CONTENT_DELETION = "content_deletion"
    CONTENT_MODIFICATION = "content_modification"
    METADATA_CHANGE = "metadata_change"
    STRUCTURE_CHANGE = "structure_change"

class ReviewStatus(Enum):
    """Status of document review"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    APPROVED = "approved"
    REJECTED = "rejected"
    REQUIRES_CHANGES = "requires_changes"

@dataclass
class DocumentVersion:
    """A version of the document"""
    id: str
    document_path: str
    version_number: int
    created_at: datetime
    created_by: str
    commit_message: str
    content_hash: str
    metadata_hash: str
    parent_version: Optional[str] = None
    changes_summary: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ChangeRecord:
    """Record of a specific change"""
    id: str
    document_path: str
    version_id: str
    change_type: ChangeType
    author: str
    timestamp: datetime
    line_number: Optional[int]
    old_content: Optional[str]
    new_content: Optional[str]
    description: str
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ReviewComment:
    """A review comment on the document"""
    id: str
    document_path: str
    version_id: str
    reviewer: str
    line_number: Optional[int]
    comment: str
    severity: str  # "minor", "major", "critical"
    status: str  # "open", "resolved", "dismissed"
    created_at: datetime
    resolved_at: Optional[datetime] = None
    resolved_by: Optional[str] = None

@dataclass
class CollaborationSession:
    """Active collaboration session"""
    id: str
    document_path: str
    participants: Dict[str, CollaborationRole]
    current_version: str
    is_active: bool
    created_at: datetime
    last_activity: datetime
    lock_holder: Optional[str] = None
    lock_expires: Optional[datetime] = None

@dataclass
class ReviewWorkflow:
    """Review workflow configuration"""
    document_path: str
    required_reviewers: List[str]
    approval_threshold: int  # Number of approvals needed
    auto_assign: bool
    deadline_days: int
    review_stages: List[Dict[str, Any]]

class CollaborativeEditor:
    """
    Multi-author editing support with change tracking and review workflows
    """

    def __init__(self, docs_root: str = "docs"):
        self.docs_root = Path(docs_root)
        self.versions: Dict[str, List[DocumentVersion]] = {}
        self.change_history: Dict[str, List[ChangeRecord]] = {}
        self.review_comments: Dict[str, List[ReviewComment]] = {}
        self.active_sessions: Dict[str, CollaborationSession] = {}
        self.review_workflows: Dict[str, ReviewWorkflow] = {}

        # Load collaboration data
        self._load_collaboration_data()

    def _load_collaboration_data(self):
        """Load collaboration data from storage"""
        collab_dir = self.docs_root / ".." / "Tools" / "Docs" / "automation" / "collaboration"

        if collab_dir.exists():
            # Load versions
            versions_file = collab_dir / "versions.json"
            if versions_file.exists():
                try:
                    with open(versions_file, 'r', encoding='utf-8') as f:
                        versions_data = json.load(f)
                        for doc_path, versions_list in versions_data.items():
                            self.versions[doc_path] = [
                                DocumentVersion(**version) for version in versions_list
                            ]
                except Exception as e:
                    logger.error(f"Error loading versions: {e}")

            # Load change history
            changes_file = collab_dir / "changes.json"
            if changes_file.exists():
                try:
                    with open(changes_file, 'r', encoding='utf-8') as f:
                        changes_data = json.load(f)
                        for doc_path, changes_list in changes_data.items():
                            self.change_history[doc_path] = [
                                ChangeRecord(**change) for change in changes_list
                            ]
                except Exception as e:
                    logger.error(f"Error loading changes: {e}")

            # Load review comments
            reviews_file = collab_dir / "reviews.json"
            if reviews_file.exists():
                try:
                    with open(reviews_file, 'r', encoding='utf-8') as f:
                        reviews_data = json.load(f)
                        for doc_path, reviews_list in reviews_data.items():
                            self.review_comments[doc_path] = [
                                ReviewComment(**review) for review in reviews_list
                            ]
                except Exception as e:
                    logger.error(f"Error loading reviews: {e}")

    def _save_collaboration_data(self):
        """Save collaboration data to storage"""
        collab_dir = self.docs_root / ".." / "Tools" / "Docs" / "automation" / "collaboration"
        collab_dir.mkdir(parents=True, exist_ok=True)

        # Save versions
        versions_data = {}
        for doc_path, versions in self.versions.items():
            versions_data[doc_path] = [
                {
                    "id": v.id,
                    "document_path": v.document_path,
                    "version_number": v.version_number,
                    "created_at": v.created_at.isoformat(),
                    "created_by": v.created_by,
                    "commit_message": v.commit_message,
                    "content_hash": v.content_hash,
                    "metadata_hash": v.metadata_hash,
                    "parent_version": v.parent_version,
                    "changes_summary": v.changes_summary
                }
                for v in versions
            ]

        with open(collab_dir / "versions.json", 'w', encoding='utf-8') as f:
            json.dump(versions_data, f, indent=2, ensure_ascii=False)

        # Save changes
        changes_data = {}
        for doc_path, changes in self.change_history.items():
            changes_data[doc_path] = [
                {
                    "id": c.id,
                    "document_path": c.document_path,
                    "version_id": c.version_id,
                    "change_type": c.change_type.value,
                    "author": c.author,
                    "timestamp": c.timestamp.isoformat(),
                    "line_number": c.line_number,
                    "old_content": c.old_content,
                    "new_content": c.new_content,
                    "description": c.description,
                    "metadata": c.metadata
                }
                for c in changes
            ]

        with open(collab_dir / "changes.json", 'w', encoding='utf-8') as f:
            json.dump(changes_data, f, indent=2, ensure_ascii=False)

        # Save reviews
        reviews_data = {}
        for doc_path, reviews in self.review_comments.items():
            reviews_data[doc_path] = [
                {
                    "id": r.id,
                    "document_path": r.document_path,
                    "version_id": r.version_id,
                    "reviewer": r.reviewer,
                    "line_number": r.line_number,
                    "comment": r.comment,
                    "severity": r.severity,
                    "status": r.status,
                    "created_at": r.created_at.isoformat(),
                    "resolved_at": r.resolved_at.isoformat() if r.resolved_at else None,
                    "resolved_by": r.resolved_by
                }
                for r in reviews
            ]

        with open(collab_dir / "reviews.json", 'w', encoding='utf-8') as f:
            json.dump(reviews_data, f, indent=2, ensure_ascii=False)

    def start_collaboration_session(self, document_path: str,
                                  participants: Dict[str, CollaborationRole],
                                  creator: str) -> str:
        """
        Start a new collaboration session for a document
        """
        session_id = str(uuid.uuid4())

        # Get current version
        current_version = self._get_current_version(document_path)

        session = CollaborationSession(
            id=session_id,
            document_path=document_path,
            participants=participants,
            current_version=current_version.id if current_version else None,
            is_active=True,
            created_at=datetime.now(),
            last_activity=datetime.now()
        )

        self.active_sessions[session_id] = session

        # Log session creation
        self._log_collaboration_event(session_id, "session_started", {
            "creator": creator,
            "participants": list(participants.keys())
        })

        return session_id

    def _get_current_version(self, document_path: str) -> Optional[DocumentVersion]:
        """Get the current version of a document"""
        if document_path not in self.versions:
            return None

        versions = self.versions[document_path]
        return max(versions, key=lambda v: v.version_number) if versions else None

    def create_version(self, document_path: str, content: str,
                      metadata: Dict[str, Any], author: str,
                      commit_message: str) -> str:
        """
        Create a new version of the document
        """
        # Calculate content and metadata hashes
        content_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()
        metadata_hash = hashlib.sha256(json.dumps(metadata, sort_keys=True).encode('utf-8')).hexdigest()

        # Get current version
        current_version = self._get_current_version(document_path)
        version_number = (current_version.version_number + 1) if current_version else 1

        # Create new version
        version_id = str(uuid.uuid4())
        version = DocumentVersion(
            id=version_id,
            document_path=document_path,
            version_number=version_number,
            created_at=datetime.now(),
            created_by=author,
            commit_message=commit_message,
            content_hash=content_hash,
            metadata_hash=metadata_hash,
            parent_version=current_version.id if current_version else None
        )

        # Analyze changes if there's a previous version
        if current_version:
            changes = self._analyze_changes(document_path, current_version, version, author)
            version.changes_summary = self._summarize_changes(changes)

        # Store version
        if document_path not in self.versions:
            self.versions[document_path] = []
        self.versions[document_path].append(version)

        # Update collaboration sessions
        self._update_sessions_with_new_version(document_path, version_id)

        # Save data
        self._save_collaboration_data()

        return version_id

    def _analyze_changes(self, document_path: str, old_version: DocumentVersion,
                        new_version: DocumentVersion, author: str) -> List[ChangeRecord]:
        """Analyze changes between versions"""
        changes = []

        # Read old and new content (would need actual content storage)
        # For now, create placeholder changes
        change_record = ChangeRecord(
            id=str(uuid.uuid4()),
            document_path=document_path,
            version_id=new_version.id,
            change_type=ChangeType.CONTENT_MODIFICATION,
            author=author,
            timestamp=datetime.now(),
            line_number=None,
            old_content=None,
            new_content=None,
            description="Content updated",
            metadata={"version_diff": f"{old_version.version_number} -> {new_version.version_number}"}
        )

        changes.append(change_record)

        # Store in change history
        if document_path not in self.change_history:
            self.change_history[document_path] = []
        self.change_history[document_path].append(change_record)

        return changes

    def _summarize_changes(self, changes: List[ChangeRecord]) -> Dict[str, Any]:
        """Summarize changes for version"""
        summary = {
            "total_changes": len(changes),
            "change_types": {},
            "authors": set(),
            "lines_affected": 0
        }

        for change in changes:
            summary["change_types"][change.change_type.value] = \
                summary["change_types"].get(change.change_type.value, 0) + 1
            summary["authors"].add(change.author)

        summary["authors"] = list(summary["authors"])
        return summary

    def _update_sessions_with_new_version(self, document_path: str, version_id: str):
        """Update active sessions with new version"""
        for session in self.active_sessions.values():
            if session.document_path == document_path and session.is_active:
                session.current_version = version_id
                session.last_activity = datetime.now()

    def add_review_comment(self, document_path: str, version_id: str,
                          reviewer: str, comment: str, line_number: int = None,
                          severity: str = "minor") -> str:
        """
        Add a review comment to a document version
        """
        comment_id = str(uuid.uuid4())

        review_comment = ReviewComment(
            id=comment_id,
            document_path=document_path,
            version_id=version_id,
            reviewer=reviewer,
            line_number=line_number,
            comment=comment,
            severity=severity,
            status="open",
            created_at=datetime.now()
        )

        # Store comment
        if document_path not in self.review_comments:
            self.review_comments[document_path] = []
        self.review_comments[document_path].append(review_comment)

        # Save data
        self._save_collaboration_data()

        # Log comment
        self._log_collaboration_event(None, "review_comment_added", {
            "comment_id": comment_id,
            "reviewer": reviewer,
            "severity": severity
        })

        return comment_id

    def resolve_review_comment(self, comment_id: str, resolver: str) -> bool:
        """Resolve a review comment"""
        for doc_path, comments in self.review_comments.items():
            for comment in comments:
                if comment.id == comment_id and comment.status == "open":
                    comment.status = "resolved"
                    comment.resolved_at = datetime.now()
                    comment.resolved_by = resolver

                    # Save data
                    self._save_collaboration_data()

                    # Log resolution
                    self._log_collaboration_event(None, "review_comment_resolved", {
                        "comment_id": comment_id,
                        "resolver": resolver
                    })

                    return True

        return False

    def get_document_history(self, document_path: str) -> List[Dict[str, Any]]:
        """Get complete history of a document"""
        if document_path not in self.versions:
            return []

        versions = sorted(self.versions[document_path], key=lambda v: v.version_number)

        history = []
        for version in versions:
            version_info = {
                "version_id": version.id,
                "version_number": version.version_number,
                "created_at": version.created_at.isoformat(),
                "created_by": version.created_by,
                "commit_message": version.commit_message,
                "changes_summary": version.changes_summary,
                "review_comments": self._get_version_comments(document_path, version.id)
            }
            history.append(version_info)

        return history

    def _get_version_comments(self, document_path: str, version_id: str) -> List[Dict[str, Any]]:
        """Get review comments for a specific version"""
        if document_path not in self.review_comments:
            return []

        comments = []
        for comment in self.review_comments[document_path]:
            if comment.version_id == version_id:
                comments.append({
                    "id": comment.id,
                    "reviewer": comment.reviewer,
                    "comment": comment.comment,
                    "severity": comment.severity,
                    "status": comment.status,
                    "created_at": comment.created_at.isoformat(),
                    "line_number": comment.line_number
                })

        return comments

    def get_collaboration_status(self, document_path: str) -> Dict[str, Any]:
        """Get comprehensive collaboration status for a document"""
        status = {
            "document_path": document_path,
            "total_versions": 0,
            "current_version": None,
            "active_sessions": [],
            "pending_reviews": 0,
            "open_comments": 0,
            "contributors": set(),
            "last_activity": None
        }

        # Version information
        if document_path in self.versions:
            versions = self.versions[document_path]
            status["total_versions"] = len(versions)

            if versions:
                current_version = max(versions, key=lambda v: v.version_number)
                status["current_version"] = {
                    "id": current_version.id,
                    "number": current_version.version_number,
                    "created_by": current_version.created_by,
                    "created_at": current_version.created_at.isoformat()
                }

                # Collect contributors
                for version in versions:
                    status["contributors"].add(version.created_by)

                # Last activity
                status["last_activity"] = current_version.created_at.isoformat()

        # Active sessions
        for session_id, session in self.active_sessions.items():
            if session.document_path == document_path and session.is_active:
                status["active_sessions"].append({
                    "id": session_id,
                    "participants": list(session.participants.keys()),
                    "created_at": session.created_at.isoformat()
                })

        # Review comments
        if document_path in self.review_comments:
            comments = self.review_comments[document_path]
            status["open_comments"] = sum(1 for c in comments if c.status == "open")

        # Convert contributors set to list
        status["contributors"] = list(status["contributors"])

        return status

    def compare_versions(self, document_path: str, version_id_1: str,
                        version_id_2: str) -> Dict[str, Any]:
        """Compare two versions of a document"""
        # Find versions
        version_1 = None
        version_2 = None

        if document_path in self.versions:
            for version in self.versions[document_path]:
                if version.id == version_id_1:
                    version_1 = version
                elif version.id == version_id_2:
                    version_2 = version

        if not version_1 or not version_2:
            return {"error": "One or both versions not found"}

        # Compare versions (simplified - would need actual content)
        comparison = {
            "version_1": {
                "id": version_1.id,
                "number": version_1.version_number,
                "created_by": version_1.created_by,
                "created_at": version_1.created_at.isoformat()
            },
            "version_2": {
                "id": version_2.id,
                "number": version_2.version_number,
                "created_by": version_2.created_by,
                "created_at": version_2.created_at.isoformat()
            },
            "differences": {
                "content_changed": version_1.content_hash != version_2.content_hash,
                "metadata_changed": version_1.metadata_hash != version_2.metadata_hash,
                "changes": self._get_changes_between_versions(document_path, version_id_1, version_id_2)
            }
        }

        return comparison

    def _get_changes_between_versions(self, document_path: str,
                                    version_id_1: str, version_id_2: str) -> List[Dict[str, Any]]:
        """Get changes between two versions"""
        if document_path not in self.change_history:
            return []

        changes = []
        for change in self.change_history[document_path]:
            if change.version_id in [version_id_1, version_id_2]:
                changes.append({
                    "type": change.change_type.value,
                    "author": change.author,
                    "timestamp": change.timestamp.isoformat(),
                    "description": change.description,
                    "line_number": change.line_number
                })

        return changes

    def _log_collaboration_event(self, session_id: Optional[str], event_type: str,
                               details: Dict[str, Any]):
        """Log collaboration event"""
        event = {
            "timestamp": datetime.now().isoformat(),
            "session_id": session_id,
            "event_type": event_type,
            "details": details
        }

        logger.info(f"Collaboration Event: {event_type} - {details}")

    def lock_document(self, document_path: str, user: str,
                     duration_minutes: int = 30) -> bool:
        """Lock document for exclusive editing"""
        # Check if document is already locked
        for session in self.active_sessions.values():
            if (session.document_path == document_path and
                session.lock_holder and
                session.lock_expires and
                session.lock_expires > datetime.now()):
                if session.lock_holder != user:
                    return False  # Already locked by someone else

        # Find or create session for locking
        session = None
        for s in self.active_sessions.values():
            if s.document_path == document_path and s.is_active:
                session = s
                break

        if session:
            session.lock_holder = user
            session.lock_expires = datetime.now() + timedelta(minutes=duration_minutes)
            return True

        return False

    def unlock_document(self, document_path: str, user: str) -> bool:
        """Unlock document"""
        for session in self.active_sessions.values():
            if (session.document_path == document_path and
                session.lock_holder == user):
                session.lock_holder = None
                session.lock_expires = None
                return True

        return False

# Global collaborative editor instance
collaborative_editor = CollaborativeEditor()

def get_collaborative_editor() -> CollaborativeEditor:
    """Get the global collaborative editor instance"""
    return collaborative_editor

if __name__ == "__main__":
    # Test the collaborative features system
    print("Testing Terminal Grounds Collaborative Features System")
    print("=" * 60)

    editor = get_collaborative_editor()

    # Test collaboration session
    print("Creating collaboration session...")
    session_id = editor.start_collaboration_session(
        document_path="docs/test_document.md",
        participants={
            "alice": CollaborationRole.OWNER,
            "bob": CollaborationRole.EDITOR,
            "charlie": CollaborationRole.REVIEWER
        },
        creator="alice"
    )

    print(f"Created session: {session_id}")

    # Test version creation
    print("\nCreating document version...")
    version_id = editor.create_version(
        document_path="docs/test_document.md",
        content="# Test Document\nThis is a test document.",
        metadata={"title": "Test Document", "status": "draft"},
        author="alice",
        commit_message="Initial version"
    )

    print(f"Created version: {version_id}")

    # Test review comment
    print("\nAdding review comment...")
    comment_id = editor.add_review_comment(
        document_path="docs/test_document.md",
        version_id=version_id,
        reviewer="charlie",
        comment="Please add more details to the introduction",
        line_number=2,
        severity="minor"
    )

    print(f"Added comment: {comment_id}")

    # Get collaboration status
    status = editor.get_collaboration_status("docs/test_document.md")
    print(f"\nCollaboration Status:")
    print(f"  Total versions: {status['total_versions']}")
    print(f"  Open comments: {status['open_comments']}")
    print(f"  Contributors: {status['contributors']}")

    print("\nCollaborative features system operational!")
    print("Phase 4.1.1.3 Collaborative Features System ready for implementation.")
