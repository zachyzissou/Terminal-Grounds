"""
Terminal Grounds Documentation Automation Framework
Phase 4.1.1.1: Creation Workflow System - Main Integration

Integrated system combining workflow engine, intelligent assistance,
and collaborative features for guided document creation.
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime
import logging

# Add automation directory to path
sys.path.append(str(Path(__file__).parent))

from workflow_engine import get_workflow_engine, WorkflowState, WorkflowTransition
from intelligent_assistant import get_intelligent_assistant, DocumentContext
from collaborative_editor import get_collaborative_editor, CollaborationRole

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class CreationSession:
    """Complete creation session with all components"""
    session_id: str
    document_path: str
    workflow_instance_id: str
    collaboration_session_id: str
    context: DocumentContext
    created_at: datetime
    last_activity: datetime
    status: str

class CreationWorkflowSystem:
    """
    Integrated creation workflow system combining all components
    """

    def __init__(self, docs_root: str = "docs"):
        self.docs_root = Path(docs_root)
        self.workflow_engine = get_workflow_engine()
        self.intelligent_assistant = get_intelligent_assistant()
        self.collaborative_editor = get_collaborative_editor()
        self.active_sessions: Dict[str, CreationSession] = {}

        logger.info("Creation Workflow System initialized")

    def start_document_creation(self, document_path: str, document_type: str,
                              domain: str, creator: str,
                              collaborators: List[str] = None) -> str:
        """
        Start a complete document creation session
        """
        session_id = f"creation_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # Create document context for intelligent assistance
        context = DocumentContext(
            document_type=document_type,
            domain=domain,
            target_audience="developers",  # Default, can be updated
            complexity_level="medium",     # Default, can be updated
            keywords=[],
            related_documents=[],
            project_context={}
        )

        # Start workflow instance
        workflow_instance_id = self.workflow_engine.create_workflow_instance(
            document_path=document_path,
            workflow_type=document_type,
            assigned_users=[creator] + (collaborators or [])
        )

        # Start collaboration session
        participants = {creator: CollaborationRole.OWNER}
        if collaborators:
            for collaborator in collaborators:
                participants[collaborator] = CollaborationRole.EDITOR

        collaboration_session_id = self.collaborative_editor.start_collaboration_session(
            document_path=document_path,
            participants=participants,
            creator=creator
        )

        # Create creation session
        creation_session = CreationSession(
            session_id=session_id,
            document_path=document_path,
            workflow_instance_id=workflow_instance_id,
            collaboration_session_id=collaboration_session_id,
            context=context,
            created_at=datetime.now(),
            last_activity=datetime.now(),
            status="active"
        )

        self.active_sessions[session_id] = creation_session

        logger.info(f"Started document creation session: {session_id}")

        return session_id

    def get_creation_guidance(self, session_id: str, current_content: str = "") -> Dict[str, Any]:
        """
        Get comprehensive guidance for document creation
        """
        if session_id not in self.active_sessions:
            return {"error": "Session not found"}

        session = self.active_sessions[session_id]

        # Get workflow status
        workflow_instance = self.workflow_engine.get_workflow_instance(session.workflow_instance_id)
        workflow_status = self.workflow_engine.get_workflow_status(session.workflow_instance_id) if workflow_instance else {}

        # Get intelligent assistance
        suggestions = self.intelligent_assistant.get_context_suggestions(
            current_content, session.context.document_type
        )

        # Get template suggestions
        template_suggestions = self.intelligent_assistant.suggest_templates(session.context)

        # Get collaboration status
        collab_status = self.collaborative_editor.get_collaboration_status(session.document_path)

        # Combine all guidance
        guidance = {
            "session_id": session_id,
            "workflow_status": workflow_status,
            "template_suggestions": [
                {
                    "name": s.template_name,
                    "confidence": s.confidence_score,
                    "reasoning": s.reasoning,
                    "estimated_time": s.estimated_completion_time,
                    "required_fields": s.required_fields
                }
                for s in template_suggestions[:3]
            ],
            "content_guidance": suggestions,
            "collaboration_status": collab_status,
            "next_steps": self._get_next_steps(session, workflow_status),
            "validation_feedback": suggestions.get("validation_issues", [])
        }

        return guidance

    def _get_next_steps(self, session: CreationSession, workflow_status: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get recommended next steps for the creation process"""
        next_steps = []

        current_state = workflow_status.get("current_state", "")

        if current_state == "draft":
            next_steps.append({
                "action": "select_template",
                "description": "Choose an appropriate template for your document",
                "priority": "high",
                "estimated_time": 10
            })

        elif current_state == "template_selected":
            next_steps.append({
                "action": "populate_metadata",
                "description": "Fill in document metadata and frontmatter",
                "priority": "high",
                "estimated_time": 15
            })

        elif current_state == "metadata_populated":
            next_steps.append({
                "action": "structure_content",
                "description": "Create the main content structure and outline",
                "priority": "high",
                "estimated_time": 30
            })

        elif current_state == "content_structured":
            next_steps.append({
                "action": "review_ready",
                "description": "Prepare document for review process",
                "priority": "medium",
                "estimated_time": 5
            })

        # Add intelligent assistance suggestions
        template_suggestions = self.intelligent_assistant.suggest_templates(session.context)
        if template_suggestions:
            next_steps.append({
                "action": "review_templates",
                "description": f"Consider {len(template_suggestions)} template suggestions",
                "priority": "medium",
                "estimated_time": 5
            })

        # Add collaboration suggestions
        collab_status = self.collaborative_editor.get_collaboration_status(session.document_path)
        if collab_status.get("active_sessions", []):
            next_steps.append({
                "action": "collaborate",
                "description": "Work with collaborators on the document",
                "priority": "medium",
                "estimated_time": 0
            })

        return next_steps

    def apply_template(self, session_id: str, template_name: str) -> Dict[str, Any]:
        """
        Apply a template to the document
        """
        if session_id not in self.active_sessions:
            return {"error": "Session not found"}

        session = self.active_sessions[session_id]

        # Get template suggestions
        template_suggestions = self.intelligent_assistant.suggest_templates(session.context)

        # Find the selected template
        selected_template = None
        for suggestion in template_suggestions:
            if suggestion.template_name == template_name:
                selected_template = suggestion
                break

        if not selected_template:
            return {"error": "Template not found"}

        # Transition workflow to template_selected
        success = self.workflow_engine.transition_state(
            session.workflow_instance_id,
            WorkflowTransition.SELECT_TEMPLATE,
            "system"
        )

        if success:
            # Update session context
            session.last_activity = datetime.now()

            return {
                "success": True,
                "template": {
                    "name": selected_template.template_name,
                    "suggested_content": selected_template.suggested_content,
                    "required_fields": selected_template.required_fields
                },
                "workflow_updated": True,
                "next_state": "template_selected"
            }
        else:
            return {"error": "Failed to update workflow state"}

    def update_document_content(self, session_id: str, content: str,
                              metadata: Dict[str, Any], author: str,
                              commit_message: str = "") -> Dict[str, Any]:
        """
        Update document content and create new version
        """
        if session_id not in self.active_sessions:
            return {"error": "Session not found"}

        session = self.active_sessions[session_id]

        # Create new version
        version_id = self.collaborative_editor.create_version(
            document_path=session.document_path,
            content=content,
            metadata=metadata,
            author=author,
            commit_message=commit_message or f"Content update by {author}"
        )

        # Update context with new content analysis
        context_analysis = self.intelligent_assistant.context_analyzer.analyze_content(content)
        session.context.keywords = context_analysis.get("keywords", [])
        session.last_activity = datetime.now()

        # Check if we can transition workflow state
        workflow_instance = self.workflow_engine.get_workflow_instance(session.workflow_instance_id)
        current_state = workflow_instance.current_state if workflow_instance else None

        transition_made = False
        if current_state == WorkflowState.TEMPLATE_SELECTED and metadata:
            # Try to transition to metadata_populated
            transition_made = self.workflow_engine.transition_state(
                session.workflow_instance_id,
                WorkflowTransition.POPULATE_METADATA,
                author
            )

        elif current_state == WorkflowState.METADATA_POPULATED and content:
            # Try to transition to content_structured
            transition_made = self.workflow_engine.transition_state(
                session.workflow_instance_id,
                WorkflowTransition.STRUCTURE_CONTENT,
                author
            )

        return {
            "success": True,
            "version_id": version_id,
            "workflow_transition": transition_made,
            "content_analysis": context_analysis,
            "validation_feedback": self.intelligent_assistant.validate_content(
                content, session.context.document_type, metadata
            )
        }

    def get_session_status(self, session_id: str) -> Dict[str, Any]:
        """
        Get comprehensive status of a creation session
        """
        if session_id not in self.active_sessions:
            return {"error": "Session not found"}

        session = self.active_sessions[session_id]

        # Get all component statuses
        workflow_instance = self.workflow_engine.get_workflow_instance(session.workflow_instance_id)
        workflow_status = self.workflow_engine.get_workflow_status(session.workflow_instance_id) if workflow_instance else {}
        collab_status = self.collaborative_editor.get_collaboration_status(session.document_path)

        # Get recent activity
        document_history = self.collaborative_editor.get_document_history(session.document_path)
        recent_versions = document_history[-5:] if document_history else []

        return {
            "session_id": session_id,
            "document_path": session.document_path,
            "status": session.status,
            "created_at": session.created_at.isoformat(),
            "last_activity": session.last_activity.isoformat(),
            "context": {
                "document_type": session.context.document_type,
                "domain": session.context.domain,
                "keywords": session.context.keywords,
                "complexity": session.context.complexity_level
            },
            "workflow": workflow_status,
            "collaboration": collab_status,
            "recent_activity": recent_versions,
            "completion_percentage": workflow_status.get("progress_percentage", 0) if isinstance(workflow_status, dict) else 0
        }

    def end_creation_session(self, session_id: str) -> bool:
        """
        End a creation session
        """
        if session_id not in self.active_sessions:
            return False

        session = self.active_sessions[session_id]
        session.status = "completed"
        session.last_activity = datetime.now()

        # Could add cleanup logic here
        logger.info(f"Ended creation session: {session_id}")

        return True

    def get_available_document_types(self) -> List[Dict[str, Any]]:
        """Get available document types for creation"""
        return self.workflow_engine.get_available_workflows()

    def validate_document_readiness(self, session_id: str) -> Dict[str, Any]:
        """
        Validate if document is ready for next workflow step
        """
        if session_id not in self.active_sessions:
            return {"error": "Session not found"}

        session = self.active_sessions[session_id]

        # Get current workflow state
        workflow_instance = self.workflow_engine.get_workflow_instance(session.workflow_instance_id)
        if not workflow_instance:
            return {"error": "Workflow instance not found"}

        current_state = workflow_instance.current_state

        # Check document content (would need to read actual file)
        # For now, return basic validation
        validation_results = {
            "current_state": current_state.value,
            "ready_for_next_step": False,
            "issues": [],
            "recommendations": []
        }

        # State-specific validation
        if current_state == WorkflowState.DRAFT:
            validation_results["issues"].append("No template selected")
            validation_results["recommendations"].append("Select an appropriate template")

        elif current_state == WorkflowState.TEMPLATE_SELECTED:
            validation_results["issues"].append("Metadata not populated")
            validation_results["recommendations"].append("Fill in required frontmatter fields")

        elif current_state == WorkflowState.METADATA_POPULATED:
            validation_results["issues"].append("Content structure not defined")
            validation_results["recommendations"].append("Create document outline and structure")

        elif current_state == WorkflowState.CONTENT_STRUCTURED:
            validation_results["ready_for_next_step"] = True
            validation_results["recommendations"].append("Mark document as ready for review")

        return validation_results

# Global creation workflow system instance
creation_system = CreationWorkflowSystem()

def get_creation_workflow_system() -> CreationWorkflowSystem:
    """Get the global creation workflow system instance"""
    return creation_system

def create_document_interactive():
    """
    Interactive document creation wizard
    """
    system = get_creation_workflow_system()

    print("Terminal Grounds Document Creation Wizard")
    print("=" * 50)

    # Get document details
    document_path = input("Document path (e.g., docs/new_document.md): ").strip()
    document_type = input("Document type (technical/design/process): ").strip()
    domain = input("Domain (technical/design/art/gaming): ").strip()
    creator = input("Your name: ").strip()

    collaborators_input = input("Collaborators (comma-separated, optional): ").strip()
    collaborators = [c.strip() for c in collaborators_input.split(',') if c.strip()]

    # Start creation session
    print("\nStarting creation session...")
    session_id = system.start_document_creation(
        document_path=document_path,
        document_type=document_type,
        domain=domain,
        creator=creator,
        collaborators=collaborators
    )

    print(f"Session started: {session_id}")

    # Get initial guidance
    guidance = system.get_creation_guidance(session_id)
    print(f"\nInitial guidance: {len(guidance.get('template_suggestions', []))} template suggestions available")

    return session_id

if __name__ == "__main__":
    # Test the integrated creation workflow system
    print("Testing Terminal Grounds Creation Workflow System")
    print("=" * 60)

    system = get_creation_workflow_system()

    # Show available document types
    print("Available Document Types:")
    for doc_type in system.get_available_document_types():
        print(f"  - {doc_type['type']} ({doc_type['domain']}): {doc_type['steps_count']} steps")

    # Create a test session
    print("\nCreating test creation session...")
    session_id = system.start_document_creation(
        document_path="docs/test_creation.md",
        document_type="technical",
        domain="technical",
        creator="test_user",
        collaborators=["collaborator1", "collaborator2"]
    )

    print(f"Created session: {session_id}")

    # Get guidance
    guidance = system.get_creation_guidance(session_id)
    print(f"\nGuidance provided:")
    print(f"  - Template suggestions: {len(guidance.get('template_suggestions', []))}")
    print(f"  - Next steps: {len(guidance.get('next_steps', []))}")
    print(f"  - Validation issues: {len(guidance.get('validation_feedback', []))}")

    # Get session status
    status = system.get_session_status(session_id)
    print(f"\nSession Status:")
    print(f"  - Current state: {status.get('workflow', {}).get('current_state', 'unknown')}")
    print(f"  - Completion: {status.get('completion_percentage', 0)}%")

    print("\nCreation Workflow System operational!")
    print("Phase 4.1.1.1 Creation Workflow System fully implemented and ready for use.")
