"""
Terminal Grounds Documentation Automation Framework
Phase 4.1.1.1: Creation Workflow System

Guided document creation workflows with intelligent assistance,
automated validation, and collaborative features for enterprise-grade documentation.
"""

import os
import uuid
import yaml
import json
from pathlib import Path
from typing import Dict, List, Optional, Any, Union, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import logging
from collections import defaultdict

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class WorkflowState(Enum):
    """States in the document creation workflow"""
    DRAFT = "draft"
    TEMPLATE_SELECTED = "template_selected"
    METADATA_POPULATED = "metadata_populated"
    CONTENT_STRUCTURED = "content_structured"
    REVIEW_READY = "review_ready"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    PUBLISHED = "published"
    ARCHIVED = "archived"

class WorkflowTransition(Enum):
    """Valid transitions between workflow states"""
    SELECT_TEMPLATE = "select_template"
    POPULATE_METADATA = "populate_metadata"
    STRUCTURE_CONTENT = "structure_content"
    MARK_REVIEW_READY = "mark_review_ready"
    SUBMIT_REVIEW = "submit_review"
    APPROVE = "approve"
    REJECT = "reject"
    PUBLISH = "publish"
    ARCHIVE = "archive"

@dataclass
class WorkflowStep:
    """A step in the document creation workflow"""
    id: str
    name: str
    description: str
    state: WorkflowState
    required_actions: List[str]
    automated_actions: List[str]
    validation_rules: List[Dict[str, Any]]
    estimated_duration: int  # minutes
    dependencies: List[str] = field(default_factory=list)

@dataclass
class DocumentWorkflow:
    """Complete workflow for a document type"""
    document_type: str
    domain: str
    steps: List[WorkflowStep]
    state_machine: Dict[WorkflowState, List[WorkflowTransition]]
    entry_criteria: Dict[str, Any]
    exit_criteria: Dict[str, Any]
    quality_gates: List[Dict[str, Any]]

@dataclass
class WorkflowInstance:
    """Instance of a workflow for a specific document"""
    id: str
    document_path: str
    workflow_type: str
    current_state: WorkflowState
    created_at: datetime
    updated_at: datetime
    assigned_users: List[str]
    completed_steps: List[str]
    pending_actions: List[str]
    metadata: Dict[str, Any]
    history: List[Dict[str, Any]] = field(default_factory=list)

class WorkflowEngine:
    """
    Core workflow engine for guided document creation
    """

    def __init__(self, docs_root: str = "docs"):
        self.docs_root = Path(docs_root)
        self.workflows: Dict[str, DocumentWorkflow] = {}
        self.active_instances: Dict[str, WorkflowInstance] = {}
        self.workflow_templates: Dict[str, Dict[str, Any]] = {}

        # Load existing workflows
        self._load_workflows()

    def _load_workflows(self):
        """Load workflow definitions from configuration"""
        workflow_config_path = self.docs_root / ".." / "Tools" / "Docs" / "automation" / "workflows"

        if workflow_config_path.exists():
            for config_file in workflow_config_path.glob("*.yaml"):
                try:
                    with open(config_file, 'r', encoding='utf-8') as f:
                        workflow_data = yaml.safe_load(f)

                    workflow = self._parse_workflow_config(workflow_data)
                    self.workflows[workflow.document_type] = workflow

                except Exception as e:
                    logger.error(f"Error loading workflow {config_file}: {e}")

        # Create default workflows if none exist
        if not self.workflows:
            self._create_default_workflows()

    def _parse_workflow_config(self, config: Dict[str, Any]) -> DocumentWorkflow:
        """Parse workflow configuration from YAML"""
        steps = []
        for step_data in config.get('steps', []):
            step = WorkflowStep(
                id=step_data['id'],
                name=step_data['name'],
                description=step_data['description'],
                state=WorkflowState(step_data['state']),
                required_actions=step_data.get('required_actions', []),
                automated_actions=step_data.get('automated_actions', []),
                validation_rules=step_data.get('validation_rules', []),
                estimated_duration=step_data.get('estimated_duration', 30),
                dependencies=step_data.get('dependencies', [])
            )
            steps.append(step)

        # Build state machine
        state_machine = defaultdict(list)
        for transition_data in config.get('transitions', []):
            from_state = WorkflowState(transition_data['from'])
            to_state = WorkflowState(transition_data['to'])
            transition = WorkflowTransition(transition_data['transition'])

            # Add transition to state machine
            state_machine[from_state].append(transition)

        return DocumentWorkflow(
            document_type=config['document_type'],
            domain=config['domain'],
            steps=steps,
            state_machine=dict(state_machine),
            entry_criteria=config.get('entry_criteria', {}),
            exit_criteria=config.get('exit_criteria', {}),
            quality_gates=config.get('quality_gates', [])
        )

    def _create_default_workflows(self):
        """Create default workflow templates for common document types"""

        # Technical Documentation Workflow
        tech_workflow = DocumentWorkflow(
            document_type="technical",
            domain="technical",
            steps=[
                WorkflowStep(
                    id="select_template",
                    name="Select Template",
                    description="Choose appropriate template based on document type",
                    state=WorkflowState.DRAFT,
                    required_actions=["choose_template"],
                    automated_actions=["suggest_templates"],
                    validation_rules=[{"field": "template", "required": True}],
                    estimated_duration=10
                ),
                WorkflowStep(
                    id="populate_metadata",
                    name="Populate Metadata",
                    description="Fill in frontmatter and document metadata",
                    state=WorkflowState.TEMPLATE_SELECTED,
                    required_actions=["fill_frontmatter"],
                    automated_actions=["auto_populate_fields", "suggest_tags"],
                    validation_rules=[
                        {"field": "title", "required": True},
                        {"field": "type", "required": True},
                        {"field": "domain", "required": True}
                    ],
                    estimated_duration=15,
                    dependencies=["select_template"]
                ),
                WorkflowStep(
                    id="structure_content",
                    name="Structure Content",
                    description="Create document structure and outline",
                    state=WorkflowState.METADATA_POPULATED,
                    required_actions=["create_outline"],
                    automated_actions=["suggest_structure", "validate_structure"],
                    validation_rules=[{"field": "content_structure", "required": True}],
                    estimated_duration=30,
                    dependencies=["populate_metadata"]
                ),
                WorkflowStep(
                    id="review_ready",
                    name="Mark Review Ready",
                    description="Prepare document for review process",
                    state=WorkflowState.CONTENT_STRUCTURED,
                    required_actions=["mark_review_ready"],
                    automated_actions=["validate_completeness"],
                    validation_rules=[{"field": "review_ready", "value": True}],
                    estimated_duration=5,
                    dependencies=["structure_content"]
                )
            ],
            state_machine={
                WorkflowState.DRAFT: [WorkflowTransition.SELECT_TEMPLATE],
                WorkflowState.TEMPLATE_SELECTED: [WorkflowTransition.POPULATE_METADATA],
                WorkflowState.METADATA_POPULATED: [WorkflowTransition.STRUCTURE_CONTENT],
                WorkflowState.CONTENT_STRUCTURED: [WorkflowTransition.MARK_REVIEW_READY],
                WorkflowState.REVIEW_READY: [WorkflowTransition.SUBMIT_REVIEW]
            },
            entry_criteria={"has_template": True},
            exit_criteria={"review_complete": True},
            quality_gates=[
                {
                    "name": "metadata_complete",
                    "description": "All required metadata fields populated",
                    "checks": ["title", "type", "domain", "maintainer"]
                },
                {
                    "name": "structure_valid",
                    "description": "Document structure follows standards",
                    "checks": ["headings_hierarchy", "required_sections"]
                }
            ]
        )

        self.workflows["technical"] = tech_workflow

        # Design Documentation Workflow
        design_workflow = DocumentWorkflow(
            document_type="design",
            domain="design",
            steps=[
                WorkflowStep(
                    id="select_template",
                    name="Select Design Template",
                    description="Choose design documentation template",
                    state=WorkflowState.DRAFT,
                    required_actions=["choose_design_template"],
                    automated_actions=["suggest_design_templates"],
                    validation_rules=[{"field": "template", "required": True}],
                    estimated_duration=10
                ),
                WorkflowStep(
                    id="populate_metadata",
                    name="Populate Design Metadata",
                    description="Fill in design-specific metadata",
                    state=WorkflowState.TEMPLATE_SELECTED,
                    required_actions=["fill_design_metadata"],
                    automated_actions=["auto_populate_design_fields"],
                    validation_rules=[
                        {"field": "title", "required": True},
                        {"field": "design_type", "required": True},
                        {"field": "target_audience", "required": True}
                    ],
                    estimated_duration=20,
                    dependencies=["select_template"]
                ),
                WorkflowStep(
                    id="structure_content",
                    name="Structure Design Content",
                    description="Create design document structure",
                    state=WorkflowState.METADATA_POPULATED,
                    required_actions=["create_design_outline"],
                    automated_actions=["suggest_design_sections"],
                    validation_rules=[{"field": "design_structure", "required": True}],
                    estimated_duration=45,
                    dependencies=["populate_metadata"]
                )
            ],
            state_machine={
                WorkflowState.DRAFT: [WorkflowTransition.SELECT_TEMPLATE],
                WorkflowState.TEMPLATE_SELECTED: [WorkflowTransition.POPULATE_METADATA],
                WorkflowState.METADATA_POPULATED: [WorkflowTransition.STRUCTURE_CONTENT],
                WorkflowState.CONTENT_STRUCTURED: [WorkflowTransition.MARK_REVIEW_READY]
            },
            entry_criteria={"design_context": True},
            exit_criteria={"design_review_complete": True},
            quality_gates=[
                {
                    "name": "design_metadata_complete",
                    "description": "Design-specific metadata populated",
                    "checks": ["design_type", "stakeholders", "requirements"]
                }
            ]
        )

        self.workflows["design"] = design_workflow

    def create_workflow_instance(self, document_path: str, workflow_type: str,
                               assigned_users: List[str] = None) -> str:
        """
        Create a new workflow instance for a document
        """
        if workflow_type not in self.workflows:
            raise ValueError(f"Unknown workflow type: {workflow_type}")

        instance_id = str(uuid.uuid4())
        workflow = self.workflows[workflow_type]

        instance = WorkflowInstance(
            id=instance_id,
            document_path=document_path,
            workflow_type=workflow_type,
            current_state=WorkflowState.DRAFT,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            assigned_users=assigned_users or [],
            completed_steps=[],
            pending_actions=self._get_initial_actions(workflow),
            metadata={
                "workflow_type": workflow_type,
                "domain": workflow.domain,
                "created_by": "system",
                "priority": "medium"
            }
        )

        self.active_instances[instance_id] = instance

        # Log workflow creation
        self._log_workflow_event(instance_id, "created", {
            "workflow_type": workflow_type,
            "document_path": document_path
        })

        return instance_id

    def _get_initial_actions(self, workflow: DocumentWorkflow) -> List[str]:
        """Get initial actions for a workflow"""
        initial_step = next((step for step in workflow.steps
                           if step.state == WorkflowState.DRAFT), None)
        if initial_step:
            return initial_step.required_actions + initial_step.automated_actions
        return []

    def get_workflow_instance(self, instance_id: str) -> Optional[WorkflowInstance]:
        """Get workflow instance by ID"""
        return self.active_instances.get(instance_id)

    def transition_state(self, instance_id: str, transition: WorkflowTransition,
                        user: str = "system", notes: str = "") -> bool:
        """
        Transition workflow instance to new state
        """
        instance = self.active_instances.get(instance_id)
        if not instance:
            logger.error(f"Workflow instance {instance_id} not found")
            return False

        workflow = self.workflows.get(instance.workflow_type)
        if not workflow:
            logger.error(f"Workflow type {instance.workflow_type} not found")
            return False

        # Check if transition is valid from current state
        valid_transitions = workflow.state_machine.get(instance.current_state, [])
        if transition not in valid_transitions:
            logger.error(f"Invalid transition {transition} from state {instance.current_state}")
            return False

        # Determine new state based on transition
        new_state = self._get_new_state_from_transition(instance.current_state, transition)
        if not new_state:
            logger.error(f"Could not determine new state for transition {transition}")
            return False

        # Update instance
        old_state = instance.current_state
        instance.current_state = new_state
        instance.updated_at = datetime.now()

        # Update pending actions based on new state
        instance.pending_actions = self._get_actions_for_state(workflow, new_state)

        # Log transition
        self._log_workflow_event(instance_id, "transition", {
            "from_state": old_state.value,
            "to_state": new_state.value,
            "transition": transition.value,
            "user": user,
            "notes": notes
        })

        return True

    def _get_new_state_from_transition(self, current_state: WorkflowState,
                                     transition: WorkflowTransition) -> Optional[WorkflowState]:
        """Determine new state from transition"""
        state_transitions = {
            (WorkflowState.DRAFT, WorkflowTransition.SELECT_TEMPLATE): WorkflowState.TEMPLATE_SELECTED,
            (WorkflowState.TEMPLATE_SELECTED, WorkflowTransition.POPULATE_METADATA): WorkflowState.METADATA_POPULATED,
            (WorkflowState.METADATA_POPULATED, WorkflowTransition.STRUCTURE_CONTENT): WorkflowState.CONTENT_STRUCTURED,
            (WorkflowState.CONTENT_STRUCTURED, WorkflowTransition.MARK_REVIEW_READY): WorkflowState.REVIEW_READY,
            (WorkflowState.REVIEW_READY, WorkflowTransition.SUBMIT_REVIEW): WorkflowState.UNDER_REVIEW,
            (WorkflowState.UNDER_REVIEW, WorkflowTransition.APPROVE): WorkflowState.APPROVED,
            (WorkflowState.UNDER_REVIEW, WorkflowTransition.REJECT): WorkflowState.CONTENT_STRUCTURED,
            (WorkflowState.APPROVED, WorkflowTransition.PUBLISH): WorkflowState.PUBLISHED,
            (WorkflowState.PUBLISHED, WorkflowTransition.ARCHIVE): WorkflowState.ARCHIVED
        }

        return state_transitions.get((current_state, transition))

    def _get_actions_for_state(self, workflow: DocumentWorkflow, state: WorkflowState) -> List[str]:
        """Get required actions for a workflow state"""
        step = next((step for step in workflow.steps if step.state == state), None)
        if step:
            return step.required_actions + step.automated_actions
        return []

    def _log_workflow_event(self, instance_id: str, event_type: str, details: Dict[str, Any]):
        """Log workflow event"""
        instance = self.active_instances[instance_id]
        event = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "instance_id": instance_id,
            "details": details
        }
        instance.history.append(event)

        logger.info(f"Workflow {instance_id}: {event_type} - {details}")

    def get_workflow_status(self, instance_id: str) -> Dict[str, Any]:
        """Get comprehensive workflow status"""
        instance = self.active_instances.get(instance_id)
        if not instance:
            return {"error": "Workflow instance not found"}

        workflow = self.workflows.get(instance.workflow_type)
        if not workflow:
            return {"error": "Workflow type not found"}

        # Calculate progress
        total_steps = len(workflow.steps)
        completed_steps = len(instance.completed_steps)
        progress_percentage = (completed_steps / total_steps) * 100 if total_steps > 0 else 0

        # Get current step info
        current_step = next((step for step in workflow.steps
                           if step.state == instance.current_state), None)

        return {
            "instance_id": instance_id,
            "document_path": instance.document_path,
            "workflow_type": instance.workflow_type,
            "current_state": instance.current_state.value,
            "progress_percentage": progress_percentage,
            "completed_steps": instance.completed_steps,
            "pending_actions": instance.pending_actions,
            "assigned_users": instance.assigned_users,
            "created_at": instance.created_at.isoformat(),
            "updated_at": instance.updated_at.isoformat(),
            "current_step": {
                "name": current_step.name if current_step else "Unknown",
                "description": current_step.description if current_step else "",
                "estimated_duration": current_step.estimated_duration if current_step else 0
            } if current_step else None,
            "quality_gates": self._check_quality_gates(instance, workflow)
        }

    def _check_quality_gates(self, instance: WorkflowInstance,
                           workflow: DocumentWorkflow) -> List[Dict[str, Any]]:
        """Check status of quality gates"""
        gate_statuses = []

        for gate in workflow.quality_gates:
            # This would integrate with validation system
            # For now, return placeholder status
            gate_statuses.append({
                "name": gate["name"],
                "description": gate["description"],
                "status": "pending",  # Would be "passed" or "failed" based on validation
                "checks": gate["checks"]
            })

        return gate_statuses

    def get_available_workflows(self) -> List[Dict[str, Any]]:
        """Get list of available workflow types"""
        return [
            {
                "type": workflow_type,
                "domain": workflow.domain,
                "description": f"Workflow for {workflow_type} documents",
                "steps_count": len(workflow.steps),
                "estimated_duration": sum(step.estimated_duration for step in workflow.steps)
            }
            for workflow_type, workflow in self.workflows.items()
        ]

    def save_workflow_state(self):
        """Save current workflow state to disk"""
        state_file = self.docs_root / ".." / "Tools" / "Docs" / "automation" / "workflow_state.json"

        state_data = {
            "active_instances": {
                instance_id: {
                    "id": instance.id,
                    "document_path": instance.document_path,
                    "workflow_type": instance.workflow_type,
                    "current_state": instance.current_state.value,
                    "created_at": instance.created_at.isoformat(),
                    "updated_at": instance.updated_at.isoformat(),
                    "assigned_users": instance.assigned_users,
                    "completed_steps": instance.completed_steps,
                    "pending_actions": instance.pending_actions,
                    "metadata": instance.metadata,
                    "history": instance.history
                }
                for instance_id, instance in self.active_instances.items()
            },
            "last_updated": datetime.now().isoformat()
        }

        with open(state_file, 'w', encoding='utf-8') as f:
            json.dump(state_data, f, indent=2, ensure_ascii=False)

    def load_workflow_state(self):
        """Load workflow state from disk"""
        state_file = self.docs_root / ".." / "Tools" / "Docs" / "automation" / "workflow_state.json"

        if not state_file.exists():
            return

        try:
            with open(state_file, 'r', encoding='utf-8') as f:
                state_data = json.load(f)

            for instance_data in state_data.get("active_instances", {}).values():
                instance = WorkflowInstance(
                    id=instance_data["id"],
                    document_path=instance_data["document_path"],
                    workflow_type=instance_data["workflow_type"],
                    current_state=WorkflowState(instance_data["current_state"]),
                    created_at=datetime.fromisoformat(instance_data["created_at"]),
                    updated_at=datetime.fromisoformat(instance_data["updated_at"]),
                    assigned_users=instance_data["assigned_users"],
                    completed_steps=instance_data["completed_steps"],
                    pending_actions=instance_data["pending_actions"],
                    metadata=instance_data["metadata"],
                    history=instance_data["history"]
                )
                self.active_instances[instance.id] = instance

        except Exception as e:
            logger.error(f"Error loading workflow state: {e}")

# Global workflow engine instance
workflow_engine = WorkflowEngine()

def get_workflow_engine() -> WorkflowEngine:
    """Get the global workflow engine instance"""
    return workflow_engine

if __name__ == "__main__":
    # Test the workflow engine
    print("Testing Terminal Grounds Creation Workflow System")
    print("=" * 60)

    engine = get_workflow_engine()

    # Show available workflows
    print("Available Workflows:")
    for workflow in engine.get_available_workflows():
        print(f"  - {workflow['type']} ({workflow['domain']}): {workflow['steps_count']} steps, ~{workflow['estimated_duration']}min")

    # Create a test workflow instance
    print("\nCreating test workflow instance...")
    instance_id = engine.create_workflow_instance(
        document_path="docs/test_document.md",
        workflow_type="technical",
        assigned_users=["test_user"]
    )

    print(f"Created workflow instance: {instance_id}")

    # Get workflow status
    status = engine.get_workflow_status(instance_id)
    print(f"Current state: {status['current_state']}")
    print(".1f")

    print("\nWorkflow system operational!")
    print("Phase 4.1.1.1 Creation Workflow System ready for implementation.")
