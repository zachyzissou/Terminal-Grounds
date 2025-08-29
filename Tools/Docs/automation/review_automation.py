"""
Terminal Grounds Documentation Automation Framework
Phase 4.1.1.2: Review Cycle Automation System

Automated review processes, approval workflows, and review analytics
for enterprise-grade document review and approval cycles.
"""

import os
import uuid
import json
import smtplib
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ReviewStatus(Enum):
    """Status of a document review"""
    PENDING = "pending"
    IN_REVIEW = "in_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    REQUIRES_CHANGES = "requires_changes"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"

class ReviewPriority(Enum):
    """Priority levels for reviews"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ApprovalGate(Enum):
    """Types of approval gates"""
    PEER_REVIEW = "peer_review"
    TECHNICAL_REVIEW = "technical_review"
    LEGAL_REVIEW = "legal_review"
    MANAGEMENT_APPROVAL = "management_approval"
    FINAL_APPROVAL = "final_approval"

@dataclass
class ReviewCycle:
    """A complete review cycle for a document"""
    id: str
    document_path: str
    version_id: str
    initiator: str
    reviewers: List[str]
    status: ReviewStatus
    priority: ReviewPriority
    created_at: datetime
    due_date: datetime
    completed_at: Optional[datetime] = None
    approval_gates: List[ApprovalGate] = field(default_factory=list)
    current_gate: Optional[ApprovalGate] = None
    review_comments: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ReviewAssignment:
    """Assignment of a review to a specific reviewer"""
    id: str
    review_cycle_id: str
    reviewer: str
    assigned_at: datetime
    due_date: datetime
    status: ReviewStatus
    priority: ReviewPriority
    gate: ApprovalGate
    completed_at: Optional[datetime] = None
    comments: List[Dict[str, Any]] = field(default_factory=list)

@dataclass
class ReviewTemplate:
    """Template for review processes"""
    name: str
    document_type: str
    required_gates: List[ApprovalGate]
    default_reviewers: List[str]
    sla_days: int
    checklist_items: List[str]
    automated_checks: List[str]

@dataclass
class ReviewAnalytics:
    """Analytics data for review processes"""
    total_reviews: int = 0
    completed_reviews: int = 0
    average_completion_time: float = 0.0
    overdue_reviews: int = 0
    approval_rate: float = 0.0
    reviewer_workload: Dict[str, int] = field(default_factory=dict)
    gate_performance: Dict[str, Dict[str, Any]] = field(default_factory=dict)

class ReviewAutomationEngine:
    """
    Automated review cycle management and approval workflows
    """

    def __init__(self, docs_root: str = "docs"):
        self.docs_root = Path(docs_root)
        self.active_reviews: Dict[str, ReviewCycle] = {}
        self.review_assignments: Dict[str, List[ReviewAssignment]] = {}
        self.review_templates: Dict[str, ReviewTemplate] = {}
        self.review_history: List[ReviewCycle] = []
        self.analytics = ReviewAnalytics()

        # Email configuration (would be loaded from config)
        self.email_config = {
            "smtp_server": "smtp.gmail.com",
            "smtp_port": 587,
            "sender_email": "noreply@terminalgrounds.com",
            "sender_name": "Terminal Grounds Review System"
        }

        # Load review templates and data
        self._load_review_templates()
        self._load_review_data()

    def _load_review_templates(self):
        """Load review templates from configuration"""
        templates_dir = self.docs_root / ".." / "Tools" / "Docs" / "automation" / "review_templates"

        if templates_dir.exists():
            for template_file in templates_dir.glob("*.yaml"):
                try:
                    import yaml
                    with open(template_file, 'r', encoding='utf-8') as f:
                        template_data = yaml.safe_load(f)

                    template = ReviewTemplate(
                        name=template_data['name'],
                        document_type=template_data['document_type'],
                        required_gates=[ApprovalGate(gate) for gate in template_data.get('required_gates', [])],
                        default_reviewers=template_data.get('default_reviewers', []),
                        sla_days=template_data.get('sla_days', 7),
                        checklist_items=template_data.get('checklist_items', []),
                        automated_checks=template_data.get('automated_checks', [])
                    )

                    self.review_templates[template_data['document_type']] = template

                except Exception as e:
                    logger.error(f"Error loading review template {template_file}: {e}")

        # Create default templates if none exist
        if not self.review_templates:
            self._create_default_templates()

    def _create_default_templates(self):
        """Create default review templates"""

        # Technical Document Review Template
        technical_template = ReviewTemplate(
            name="Technical Document Review",
            document_type="technical",
            required_gates=[
                ApprovalGate.PEER_REVIEW,
                ApprovalGate.TECHNICAL_REVIEW,
                ApprovalGate.FINAL_APPROVAL
            ],
            default_reviewers=["tech_lead", "senior_engineer"],
            sla_days=5,
            checklist_items=[
                "Technical accuracy verified",
                "Code examples functional",
                "API documentation complete",
                "Security considerations addressed",
                "Performance implications reviewed"
            ],
            automated_checks=[
                "validate_frontmatter",
                "check_cross_references",
                "validate_code_blocks",
                "check_terminology_consistency"
            ]
        )

        # Design Document Review Template
        design_template = ReviewTemplate(
            name="Design Document Review",
            document_type="design",
            required_gates=[
                ApprovalGate.PEER_REVIEW,
                ApprovalGate.MANAGEMENT_APPROVAL,
                ApprovalGate.FINAL_APPROVAL
            ],
            default_reviewers=["design_lead", "product_manager"],
            sla_days=7,
            checklist_items=[
                "Design requirements met",
                "User experience validated",
                "Accessibility standards met",
                "Visual design consistent",
                "Technical feasibility confirmed"
            ],
            automated_checks=[
                "validate_frontmatter",
                "check_design_references",
                "validate_accessibility",
                "check_brand_consistency"
            ]
        )

        # Process Document Review Template
        process_template = ReviewTemplate(
            name="Process Document Review",
            document_type="process",
            required_gates=[
                ApprovalGate.PEER_REVIEW,
                ApprovalGate.LEGAL_REVIEW,
                ApprovalGate.MANAGEMENT_APPROVAL,
                ApprovalGate.FINAL_APPROVAL
            ],
            default_reviewers=["process_owner", "compliance_officer", "management"],
            sla_days=10,
            checklist_items=[
                "Process steps clearly defined",
                "Roles and responsibilities assigned",
                "Compliance requirements met",
                "Risk assessment completed",
                "Training requirements identified"
            ],
            automated_checks=[
                "validate_frontmatter",
                "check_process_flow",
                "validate_compliance",
                "check_risk_assessment"
            ]
        )

        self.review_templates = {
            "technical": technical_template,
            "design": design_template,
            "process": process_template
        }

    def _load_review_data(self):
        """Load review data from storage"""
        review_dir = self.docs_root / ".." / "Tools" / "Docs" / "automation" / "review_data"

        if review_dir.exists():
            # Load active reviews
            active_file = review_dir / "active_reviews.json"
            if active_file.exists():
                try:
                    with open(active_file, 'r', encoding='utf-8') as f:
                        active_data = json.load(f)
                        for review_id, review_data in active_data.items():
                            review = ReviewCycle(**review_data)
                            self.active_reviews[review_id] = review
                except Exception as e:
                    logger.error(f"Error loading active reviews: {e}")

            # Load review history
            history_file = review_dir / "review_history.json"
            if history_file.exists():
                try:
                    with open(history_file, 'r', encoding='utf-8') as f:
                        history_data = json.load(f)
                        self.review_history = [ReviewCycle(**review) for review in history_data]
                except Exception as e:
                    logger.error(f"Error loading review history: {e}")

    def _save_review_data(self):
        """Save review data to storage"""
        review_dir = self.docs_root / ".." / "Tools" / "Docs" / "automation" / "review_data"
        review_dir.mkdir(parents=True, exist_ok=True)

        # Save active reviews
        active_data = {}
        for review_id, review in self.active_reviews.items():
            active_data[review_id] = {
                "id": review.id,
                "document_path": review.document_path,
                "version_id": review.version_id,
                "initiator": review.initiator,
                "reviewers": review.reviewers,
                "status": review.status.value,
                "priority": review.priority.value,
                "created_at": review.created_at.isoformat(),
                "due_date": review.due_date.isoformat(),
                "completed_at": review.completed_at.isoformat() if review.completed_at else None,
                "approval_gates": [gate.value for gate in review.approval_gates],
                "current_gate": review.current_gate.value if review.current_gate else None,
                "review_comments": review.review_comments,
                "metadata": review.metadata
            }

        with open(review_dir / "active_reviews.json", 'w', encoding='utf-8') as f:
            json.dump(active_data, f, indent=2, ensure_ascii=False)

        # Save review history
        history_data = []
        for review in self.review_history[-1000:]:  # Keep last 1000 reviews
            history_data.append({
                "id": review.id,
                "document_path": review.document_path,
                "version_id": review.version_id,
                "initiator": review.initiator,
                "reviewers": review.reviewers,
                "status": review.status.value,
                "priority": review.priority.value,
                "created_at": review.created_at.isoformat(),
                "due_date": review.due_date.isoformat(),
                "completed_at": review.completed_at.isoformat() if review.completed_at else None,
                "approval_gates": [gate.value for gate in review.approval_gates],
                "current_gate": review.current_gate.value if review.current_gate else None,
                "review_comments": review.review_comments,
                "metadata": review.metadata
            })

        with open(review_dir / "review_history.json", 'w', encoding='utf-8') as f:
            json.dump(history_data, f, indent=2, ensure_ascii=False)

    def initiate_review_cycle(self, document_path: str, version_id: str,
                            initiator: str, reviewers: List[str] = None,
                            priority: ReviewPriority = ReviewPriority.MEDIUM) -> str:
        """
        Initiate a new review cycle for a document
        """
        # Determine document type and get appropriate template
        document_type = self._determine_document_type(document_path)
        template = self.review_templates.get(document_type)

        if not template:
            # Use default template
            template = self.review_templates.get("technical", list(self.review_templates.values())[0])

        # Set reviewers
        if not reviewers:
            reviewers = template.default_reviewers.copy()

        # Create review cycle
        review_id = str(uuid.uuid4())
        due_date = datetime.now() + timedelta(days=template.sla_days)

        review_cycle = ReviewCycle(
            id=review_id,
            document_path=document_path,
            version_id=version_id,
            initiator=initiator,
            reviewers=reviewers,
            status=ReviewStatus.PENDING,
            priority=priority,
            created_at=datetime.now(),
            due_date=due_date,
            approval_gates=template.required_gates.copy(),
            current_gate=template.required_gates[0] if template.required_gates else None
        )

        self.active_reviews[review_id] = review_cycle

        # Create review assignments
        self._create_review_assignments(review_cycle, template)

        # Send initial notifications
        self._send_review_notifications(review_cycle, "initiated")

        # Log review initiation
        logger.info(f"Review cycle initiated: {review_id} for {document_path}")

        # Save data
        self._save_review_data()

        return review_id

    def _determine_document_type(self, document_path: str) -> str:
        """Determine document type from path or content"""
        # Simple heuristic based on path
        path_lower = document_path.lower()

        if "design" in path_lower or "ui" in path_lower or "ux" in path_lower:
            return "design"
        elif "process" in path_lower or "procedure" in path_lower or "workflow" in path_lower:
            return "process"
        else:
            return "technical"  # Default

    def _create_review_assignments(self, review_cycle: ReviewCycle, template: ReviewTemplate):
        """Create review assignments for all reviewers"""
        assignments = []

        for reviewer in review_cycle.reviewers:
            assignment = ReviewAssignment(
                id=str(uuid.uuid4()),
                review_cycle_id=review_cycle.id,
                reviewer=reviewer,
                assigned_at=datetime.now(),
                due_date=review_cycle.due_date,
                status=ReviewStatus.PENDING,
                priority=review_cycle.priority,
                gate=review_cycle.current_gate
            )
            assignments.append(assignment)

        self.review_assignments[review_cycle.id] = assignments

    def submit_review_feedback(self, review_id: str, reviewer: str,
                             feedback: Dict[str, Any]) -> bool:
        """
        Submit review feedback from a reviewer
        """
        if review_id not in self.active_reviews:
            logger.error(f"Review cycle {review_id} not found")
            return False

        review_cycle = self.active_reviews[review_id]
        assignments = self.review_assignments.get(review_id, [])

        # Find assignment for this reviewer
        assignment = None
        for assign in assignments:
            if assign.reviewer == reviewer:
                assignment = assign
                break

        if not assignment:
            logger.error(f"No assignment found for reviewer {reviewer} in review {review_id}")
            return False

        # Update assignment
        assignment.status = ReviewStatus(feedback.get("status", "approved"))
        assignment.completed_at = datetime.now()
        assignment.comments.append({
            "timestamp": datetime.now().isoformat(),
            "feedback": feedback
        })

        # Add to review cycle comments
        review_cycle.review_comments.append({
            "reviewer": reviewer,
            "timestamp": datetime.now().isoformat(),
            "feedback": feedback
        })

        # Check if all reviewers for current gate have completed
        self._check_gate_completion(review_cycle)

        # Save data
        self._save_review_data()

        # Send notifications
        self._send_review_notifications(review_cycle, "feedback_submitted", reviewer=reviewer)

        logger.info(f"Review feedback submitted by {reviewer} for review {review_id}")

        return True

    def _check_gate_completion(self, review_cycle: ReviewCycle):
        """Check if current approval gate is complete"""
        if not review_cycle.current_gate:
            return

        assignments = self.review_assignments.get(review_cycle.id, [])
        gate_assignments = [a for a in assignments if a.gate == review_cycle.current_gate]

        # Check if all assignments for this gate are complete
        completed_count = sum(1 for a in gate_assignments if a.completed_at is not None)

        if completed_count == len(gate_assignments):
            # All assignments complete, evaluate gate
            self._evaluate_gate_approval(review_cycle)

    def _evaluate_gate_approval(self, review_cycle: ReviewCycle):
        """Evaluate if the current gate should be approved"""
        assignments = self.review_assignments.get(review_cycle.id, [])
        gate_assignments = [a for a in assignments if a.gate == review_cycle.current_gate]

        # Simple majority approval (could be more sophisticated)
        approvals = sum(1 for a in gate_assignments if a.status == ReviewStatus.APPROVED)
        total_assignments = len(gate_assignments)

        approval_threshold = 0.5  # 50% approval required

        if approvals / total_assignments >= approval_threshold:
            # Gate approved, move to next gate
            self._advance_to_next_gate(review_cycle)
        else:
            # Gate rejected
            review_cycle.status = ReviewStatus.REQUIRES_CHANGES
            self._send_review_notifications(review_cycle, "gate_rejected")

    def _advance_to_next_gate(self, review_cycle: ReviewCycle):
        """Advance to the next approval gate"""
        current_index = review_cycle.approval_gates.index(review_cycle.current_gate)

        if current_index + 1 < len(review_cycle.approval_gates):
            # Move to next gate
            review_cycle.current_gate = review_cycle.approval_gates[current_index + 1]

            # Create new assignments for next gate
            template = self.review_templates.get(self._determine_document_type(review_cycle.document_path))
            if template:
                # Get reviewers for next gate (could be different based on gate type)
                next_reviewers = self._get_reviewers_for_gate(review_cycle.current_gate, template)
                review_cycle.reviewers.extend(next_reviewers)

                # Create assignments for new reviewers
                for reviewer in next_reviewers:
                    assignment = ReviewAssignment(
                        id=str(uuid.uuid4()),
                        review_cycle_id=review_cycle.id,
                        reviewer=reviewer,
                        assigned_at=datetime.now(),
                        due_date=review_cycle.due_date,
                        status=ReviewStatus.PENDING,
                        priority=review_cycle.priority,
                        gate=review_cycle.current_gate
                    )
                    self.review_assignments[review_cycle.id].append(assignment)

            self._send_review_notifications(review_cycle, "gate_approved")
        else:
            # All gates completed
            review_cycle.status = ReviewStatus.APPROVED
            review_cycle.completed_at = datetime.now()
            self._send_review_notifications(review_cycle, "review_completed")

            # Move to history
            self.review_history.append(review_cycle)
            del self.active_reviews[review_cycle.id]

    def _get_reviewers_for_gate(self, gate: ApprovalGate, template: ReviewTemplate) -> List[str]:
        """Get appropriate reviewers for a specific gate"""
        # This could be more sophisticated based on gate type and document
        gate_reviewers = {
            ApprovalGate.TECHNICAL_REVIEW: ["tech_lead", "architect"],
            ApprovalGate.LEGAL_REVIEW: ["legal_counsel", "compliance_officer"],
            ApprovalGate.MANAGEMENT_APPROVAL: ["department_head", "vp"],
            ApprovalGate.FINAL_APPROVAL: ["ceo", "board_member"]
        }

        return gate_reviewers.get(gate, [])

    def get_review_status(self, review_id: str) -> Dict[str, Any]:
        """Get comprehensive status of a review cycle"""
        if review_id not in self.active_reviews:
            return {"error": "Review cycle not found"}

        review_cycle = self.active_reviews[review_id]
        assignments = self.review_assignments.get(review_id, [])

        # Calculate progress
        total_assignments = len(assignments)
        completed_assignments = sum(1 for a in assignments if a.completed_at is not None)
        progress_percentage = (completed_assignments / total_assignments * 100) if total_assignments > 0 else 0

        # Check for overdue assignments
        overdue_assignments = []
        for assignment in assignments:
            if (not assignment.completed_at and
                datetime.now() > assignment.due_date):
                overdue_assignments.append(assignment.reviewer)

        return {
            "review_id": review_id,
            "document_path": review_cycle.document_path,
            "status": review_cycle.status.value,
            "priority": review_cycle.priority.value,
            "created_at": review_cycle.created_at.isoformat(),
            "due_date": review_cycle.due_date.isoformat(),
            "completed_at": review_cycle.completed_at.isoformat() if review_cycle.completed_at else None,
            "current_gate": review_cycle.current_gate.value if review_cycle.current_gate else None,
            "progress_percentage": progress_percentage,
            "total_assignments": total_assignments,
            "completed_assignments": completed_assignments,
            "overdue_assignments": overdue_assignments,
            "reviewers": review_cycle.reviewers,
            "comments_count": len(review_cycle.review_comments)
        }

    def send_reminders(self):
        """Send reminders for overdue reviews"""
        now = datetime.now()
        reminder_count = 0

        for review_id, review_cycle in self.active_reviews.items():
            if review_cycle.status in [ReviewStatus.PENDING, ReviewStatus.IN_REVIEW]:
                assignments = self.review_assignments.get(review_id, [])

                for assignment in assignments:
                    if (not assignment.completed_at and
                        now > assignment.due_date):

                        # Mark as overdue if not already
                        if assignment.status != ReviewStatus.OVERDUE:
                            assignment.status = ReviewStatus.OVERDUE
                            review_cycle.status = ReviewStatus.OVERDUE

                        # Send reminder email
                        self._send_reminder_email(assignment, review_cycle)
                        reminder_count += 1

        if reminder_count > 0:
            logger.info(f"Sent {reminder_count} review reminders")

        # Save updated data
        self._save_review_data()

    def _send_reminder_email(self, assignment: ReviewAssignment, review_cycle: ReviewCycle):
        """Send reminder email for overdue review"""
        try:
            msg = MIMEMultipart()
            msg['From'] = f"{self.email_config['sender_name']} <{self.email_config['sender_email']}>"
            msg['To'] = assignment.reviewer
            msg['Subject'] = f"Review Reminder: {review_cycle.document_path}"

            body = f"""
Dear {assignment.reviewer},

This is a reminder that your review for the following document is overdue:

Document: {review_cycle.document_path}
Review ID: {review_cycle.id}
Due Date: {assignment.due_date.strftime('%Y-%m-%d')}
Days Overdue: {(datetime.now() - assignment.due_date).days}

Please complete your review as soon as possible.

Review Link: [Review System Link]

Thank you,
Terminal Grounds Review System
"""

            msg.attach(MIMEText(body, 'plain'))

            # Note: Actual email sending would require proper SMTP configuration
            # For now, just log the reminder
            logger.info(f"Reminder email would be sent to {assignment.reviewer} for review {review_cycle.id}")

        except Exception as e:
            logger.error(f"Error sending reminder email: {e}")

    def _send_review_notifications(self, review_cycle: ReviewCycle, event_type: str,
                                 reviewer: str = None):
        """Send notifications for review events"""
        # Implementation would send emails/Slack notifications
        # For now, just log the events
        logger.info(f"Review notification: {event_type} for review {review_cycle.id}")

        if event_type == "initiated":
            message = f"New review cycle initiated for {review_cycle.document_path}"
        elif event_type == "feedback_submitted":
            message = f"Review feedback submitted by {reviewer} for {review_cycle.document_path}"
        elif event_type == "gate_approved":
            message = f"Approval gate {review_cycle.current_gate.value} approved for {review_cycle.document_path}"
        elif event_type == "gate_rejected":
            message = f"Approval gate {review_cycle.current_gate.value} rejected for {review_cycle.document_path}"
        elif event_type == "review_completed":
            message = f"Review cycle completed for {review_cycle.document_path}"
        else:
            message = f"Review event: {event_type} for {review_cycle.document_path}"

        logger.info(f"Notification: {message}")

    def get_review_analytics(self) -> Dict[str, Any]:
        """Get comprehensive review analytics"""
        # Update analytics
        self._update_analytics()

        return {
            "total_reviews": self.analytics.total_reviews,
            "completed_reviews": self.analytics.completed_reviews,
            "completion_rate": (self.analytics.completed_reviews / self.analytics.total_reviews * 100) if self.analytics.total_reviews > 0 else 0,
            "average_completion_time_days": self.analytics.average_completion_time,
            "overdue_reviews": self.analytics.overdue_reviews,
            "approval_rate": self.analytics.approval_rate * 100,
            "reviewer_workload": self.analytics.reviewer_workload,
            "gate_performance": self.analytics.gate_performance,
            "active_reviews": len(self.active_reviews)
        }

    def _update_analytics(self):
        """Update review analytics"""
        completed_reviews = [r for r in self.review_history if r.completed_at]

        self.analytics.total_reviews = len(self.review_history) + len(self.active_reviews)
        self.analytics.completed_reviews = len(completed_reviews)

        # Calculate average completion time
        if completed_reviews:
            total_time = sum((r.completed_at - r.created_at).days for r in completed_reviews)
            self.analytics.average_completion_time = total_time / len(completed_reviews)

        # Count overdue reviews
        self.analytics.overdue_reviews = sum(1 for r in self.active_reviews.values()
                                           if r.status == ReviewStatus.OVERDUE)

        # Calculate approval rate
        if completed_reviews:
            approved_reviews = sum(1 for r in completed_reviews if r.status == ReviewStatus.APPROVED)
            self.analytics.approval_rate = approved_reviews / len(completed_reviews)

        # Update reviewer workload
        self.analytics.reviewer_workload = {}
        for review in self.active_reviews.values():
            for reviewer in review.reviewers:
                self.analytics.reviewer_workload[reviewer] = \
                    self.analytics.reviewer_workload.get(reviewer, 0) + 1

        # Update gate performance
        self.analytics.gate_performance = {}
        for review in self.review_history:
            for gate in review.approval_gates:
                if gate.value not in self.analytics.gate_performance:
                    self.analytics.gate_performance[gate.value] = {
                        "total": 0,
                        "approved": 0,
                        "average_time": 0
                    }
                self.analytics.gate_performance[gate.value]["total"] += 1

    def cancel_review_cycle(self, review_id: str, reason: str) -> bool:
        """Cancel a review cycle"""
        if review_id not in self.active_reviews:
            return False

        review_cycle = self.active_reviews[review_id]
        review_cycle.status = ReviewStatus.CANCELLED
        review_cycle.metadata["cancellation_reason"] = reason
        review_cycle.completed_at = datetime.now()

        # Move to history
        self.review_history.append(review_cycle)
        del self.active_reviews[review_id]

        # Send notifications
        self._send_review_notifications(review_cycle, "cancelled")

        # Save data
        self._save_review_data()

        logger.info(f"Review cycle {review_id} cancelled: {reason}")

        return True

# Global review automation engine instance
review_engine = ReviewAutomationEngine()

def get_review_engine() -> ReviewAutomationEngine:
    """Get the global review automation engine instance"""
    return review_engine

if __name__ == "__main__":
    # Test the review automation system
    print("Testing Terminal Grounds Review Cycle Automation System")
    print("=" * 60)

    engine = get_review_engine()

    # Show available templates
    print("Available Review Templates:")
    for doc_type, template in engine.review_templates.items():
        print(f"  - {doc_type}: {template.name} ({len(template.required_gates)} gates, {template.sla_days} days SLA)")

    # Initiate a test review
    print("\nInitiating test review cycle...")
    review_id = engine.initiate_review_cycle(
        document_path="docs/test_review.md",
        version_id="v1.0",
        initiator="test_user",
        reviewers=["reviewer1", "reviewer2"],
        priority=ReviewPriority.HIGH
    )

    print(f"Review cycle initiated: {review_id}")

    # Get review status
    status = engine.get_review_status(review_id)
    print(f"\nReview Status:")
    print(f"  - Status: {status['status']}")
    print(f"  - Progress: {status['progress_percentage']:.1f}%")
    print(f"  - Current Gate: {status.get('current_gate', 'None')}")
    print(f"  - Reviewers: {', '.join(status['reviewers'])}")

    # Submit test feedback
    print("\nSubmitting test feedback...")
    feedback = {
        "status": "approved",
        "comments": "Looks good, minor suggestions for clarity",
        "rating": 4.5
    }

    success = engine.submit_review_feedback(review_id, "reviewer1", feedback)
    print(f"Feedback submission: {'Success' if success else 'Failed'}")

    # Get updated status
    updated_status = engine.get_review_status(review_id)
    print(f"\nUpdated Status:")
    print(f"  - Progress: {updated_status['progress_percentage']:.1f}%")
    print(f"  - Comments: {updated_status['comments_count']}")

    # Get analytics
    analytics = engine.get_review_analytics()
    print(f"\nReview Analytics:")
    print(f"  - Total Reviews: {analytics['total_reviews']}")
    print(f"  - Completion Rate: {analytics['completion_rate']:.1f}%")
    print(f"  - Average Completion Time: {analytics['average_completion_time_days']:.1f} days")
    print(f"  - Approval Rate: {analytics['approval_rate']:.1f}%")

    print("\nReview Cycle Automation System operational!")
    print("Phase 4.1.1.2 Review Cycle Automation ready for implementation.")
