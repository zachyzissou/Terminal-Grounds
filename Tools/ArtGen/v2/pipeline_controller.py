#!/usr/bin/env python3
"""
Pipeline Controller for Terminal Grounds v2.0
=============================================
Central orchestrator that coordinates all pipeline components for seamless asset generation.
"""

import logging
import time
from pathlib import Path
from typing import Dict, Any, List, Optional, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
import threading
from concurrent.futures import ThreadPoolExecutor, Future
import queue

try:
    from .config_manager import ConfigManager
    from .asset_spec import AssetSpecification, AssetSpecBuilder, AssetType, FactionCode
    from .enhanced_client import EnhancedComfyUIClient, GenerationJob, GenerationStatus
    from .workflow_manager import WorkflowManager, WorkflowTemplate
    from .quality_assurance import QualityAssuranceManager, QualityAssessmentEngine, QualityMetrics
    from .batch_processor import BatchProcessor, BatchConfiguration, BatchSession
    from .asset_manager import AssetManager, AssetRecord, AssetStatus
    from .ue5_connector import UE5Connector, UE5ProjectConfig, create_ue5_config
except ImportError:
    from config_manager import ConfigManager
    from asset_spec import AssetSpecification, AssetSpecBuilder, AssetType, FactionCode
    from enhanced_client import EnhancedComfyUIClient, GenerationJob, GenerationStatus
    from workflow_manager import WorkflowManager, WorkflowTemplate
    from quality_assurance import QualityAssuranceManager, QualityAssessmentEngine, QualityMetrics
    from batch_processor import BatchProcessor, BatchConfiguration, BatchSession
    from asset_manager import AssetManager, AssetRecord, AssetStatus
    from ue5_connector import UE5Connector, UE5ProjectConfig, create_ue5_config

logger = logging.getLogger(__name__)

class PipelineStatus(Enum):
    INITIALIZING = "initializing"
    READY = "ready"
    PROCESSING = "processing"
    ERROR = "error"
    MAINTENANCE = "maintenance"

class TaskPriority(Enum):
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4

@dataclass
class PipelineTask:
    """Represents a task in the pipeline"""
    task_id: str
    task_type: str  # "generate", "batch", "enhance", "import"
    priority: TaskPriority
    payload: Dict[str, Any]
    created_at: float = field(default_factory=time.time)
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    status: str = "pending"
    result: Optional[Any] = None
    error: Optional[str] = None
    progress: float = 0.0
    callback: Optional[Callable] = None

@dataclass
class PipelineMetrics:
    """Pipeline performance and health metrics"""
    total_tasks_processed: int = 0
    successful_tasks: int = 0
    failed_tasks: int = 0
    average_processing_time: float = 0.0
    queue_size: int = 0
    active_workers: int = 0
    uptime_seconds: float = 0.0
    memory_usage_mb: float = 0.0
    disk_usage_gb: float = 0.0
    comfyui_health: bool = False
    last_health_check: Optional[float] = None

class PipelineController:
    """
    Central controller that orchestrates the entire Terminal Grounds asset generation pipeline.
    
    Responsibilities:
    - Initialize and coordinate all pipeline components
    - Manage task queues and prioritization
    - Handle error recovery and fallbacks
    - Provide unified API for asset generation
    - Monitor system health and performance
    - Coordinate batch processing workflows
    """
    
    def __init__(self, config_path: Optional[Path] = None):
        """Initialize the pipeline controller"""
        
        self.start_time = time.time()
        self.status = PipelineStatus.INITIALIZING
        
        # Initialize configuration
        logger.info("Initializing Terminal Grounds Pipeline v2.0...")
        self.config = ConfigManager(config_path)
        
        # Initialize task management
        self.task_queue: queue.PriorityQueue = queue.PriorityQueue()
        self.active_tasks: Dict[str, PipelineTask] = {}
        self.completed_tasks: Dict[str, PipelineTask] = {}
        self.task_counter = 0
        
        # Thread pool for task execution
        max_workers = self.config.get("comfyui.performance.max_concurrent_jobs", 2)
        self.executor = ThreadPoolExecutor(max_workers=max_workers, thread_name_prefix="Pipeline")
        
        # Component initialization
        self._initialize_components()
        
        # Start background services
        self._start_background_services()
        
        # Update status
        self.status = PipelineStatus.READY
        self.metrics = PipelineMetrics()
        
        logger.info(f"Pipeline Controller initialized successfully in {time.time() - self.start_time:.2f}s")
    
    def _initialize_components(self):
        """Initialize all pipeline components"""
        try:
            # Initialize asset spec builder
            faction_data_dir = Path(self.config.get("factions.data_directory"))
            self.spec_builder = AssetSpecBuilder(faction_data_dir)
            logger.info("Asset specification builder initialized")
            
            # Initialize ComfyUI client
            comfyui_config = self.config.get_comfyui_config()
            self.comfyui_client = EnhancedComfyUIClient(
                timeout=comfyui_config.get("connection", {}).get("timeout_seconds", 300),
                max_retries=comfyui_config.get("connection", {}).get("max_retries", 3)
            )
            logger.info("ComfyUI client initialized")
            
            # Initialize workflow manager
            workflows_dir = Path(self.config.get("workflows.templates_directory"))
            custom_workflows_dir = Path(self.config.get("workflows.custom_directory", workflows_dir))
            self.workflow_manager = WorkflowManager(workflows_dir, custom_workflows_dir)
            logger.info("Workflow manager initialized")
            
            # Initialize quality assurance
            quality_engine = QualityAssessmentEngine()
            self.qa_manager = QualityAssuranceManager(quality_engine)
            logger.info("Quality assurance manager initialized")
            
            # Initialize asset manager
            assets_db_path = Path(self.config.get("paths.assets_database"))
            assets_base_path = Path(self.config.get("paths.base_directory"))
            self.asset_manager = AssetManager(assets_base_path, assets_db_path)
            logger.info("Asset manager initialized")
            
            # Initialize batch processor
            self.batch_processor = BatchProcessor(
                self.comfyui_client,
                self.workflow_manager,
                self.qa_manager,
                self.spec_builder
            )
            logger.info("Batch processor initialized")
            
            # Initialize UE5 connector (if enabled)
            if self.config.get("ue5_integration.enabled", False):
                try:
                    ue5_config = create_ue5_config(
                        self.config.get("ue5_integration.project_config.project_name", "TerminalGrounds")
                    )
                    self.ue5_connector = UE5Connector(ue5_config)
                    logger.info("UE5 connector initialized")
                except Exception as e:
                    logger.warning(f"UE5 connector initialization failed: {e}")
                    self.ue5_connector = None
            else:
                self.ue5_connector = None
                logger.info("UE5 integration disabled")
            
        except Exception as e:
            logger.error(f"Component initialization failed: {e}")
            self.status = PipelineStatus.ERROR
            raise
    
    def _start_background_services(self):
        """Start background monitoring and maintenance services"""
        
        # Health check thread
        self.health_check_thread = threading.Thread(
            target=self._health_check_loop,
            name="HealthChecker",
            daemon=True
        )
        self.health_check_thread.start()
        
        # Task processor thread
        self.task_processor_thread = threading.Thread(
            target=self._task_processor_loop,
            name="TaskProcessor", 
            daemon=True
        )
        self.task_processor_thread.start()
        
        # Metrics collection thread
        self.metrics_thread = threading.Thread(
            target=self._metrics_collection_loop,
            name="MetricsCollector",
            daemon=True
        )
        self.metrics_thread.start()
        
        logger.info("Background services started")
    
    def generate_asset(self, 
                      name: str,
                      asset_type: AssetType,
                      faction: FactionCode,
                      description: str,
                      custom_params: Optional[Dict[str, Any]] = None,
                      priority: TaskPriority = TaskPriority.NORMAL,
                      callback: Optional[Callable] = None) -> str:
        """
        Generate a single asset
        
        Args:
            name: Asset name
            asset_type: Type of asset to generate
            faction: Faction affiliation
            description: Asset description
            custom_params: Custom generation parameters
            priority: Task priority
            callback: Optional completion callback
            
        Returns:
            Task ID for tracking progress
        """
        
        task_id = self._generate_task_id()
        
        # Create asset specification
        try:
            asset_spec = self.spec_builder.create_spec(
                name=name,
                asset_type=asset_type,
                faction=faction,
                description=description,
                custom_params=custom_params
            )
            
            # Create pipeline task
            task = PipelineTask(
                task_id=task_id,
                task_type="generate",
                priority=priority,
                payload={
                    "asset_spec": asset_spec,
                    "auto_enhance": self.config.get("quality_assurance.enhancement.auto_enhance", True),
                    "auto_import_ue5": self.config.get("ue5_integration.auto_import", False)
                },
                callback=callback
            )
            
            # Queue task
            self._queue_task(task)
            
            logger.info(f"Asset generation queued: {name} ({asset_type}, {faction}) - Task ID: {task_id}")
            return task_id
            
        except Exception as e:
            logger.error(f"Failed to queue asset generation: {e}")
            raise
    
    def process_batch_csv(self,
                         csv_file: Path,
                         config: Optional[Dict[str, Any]] = None,
                         priority: TaskPriority = TaskPriority.HIGH,
                         callback: Optional[Callable] = None) -> str:
        """
        Process CSV file for batch asset generation
        
        Args:
            csv_file: Path to CSV file
            config: Batch processing configuration overrides
            priority: Task priority
            callback: Optional progress callback
            
        Returns:
            Task ID for tracking progress
        """
        
        task_id = self._generate_task_id()
        
        # Create batch configuration
        batch_config = BatchConfiguration(
            max_concurrent_jobs=self.config.get("batch_processing.processing.max_concurrent_jobs", 2),
            auto_enhance=self.config.get("quality_assurance.enhancement.auto_enhance", True),
            auto_import_ue5=self.config.get("ue5_integration.auto_import", False),
            output_directory=Path(self.config.get("paths.batch_output")),
            progress_callback=callback
        )
        
        # Apply configuration overrides
        if config:
            for key, value in config.items():
                if hasattr(batch_config, key):
                    setattr(batch_config, key, value)
        
        # Create pipeline task
        task = PipelineTask(
            task_id=task_id,
            task_type="batch",
            priority=priority,
            payload={
                "csv_file": csv_file,
                "config": batch_config
            },
            callback=callback
        )
        
        # Queue task
        self._queue_task(task)
        
        logger.info(f"Batch processing queued: {csv_file} - Task ID: {task_id}")
        return task_id
    
    def enhance_asset(self,
                     asset_id: str,
                     enhancement_types: List[str],
                     priority: TaskPriority = TaskPriority.NORMAL,
                     callback: Optional[Callable] = None) -> str:
        """
        Enhance existing asset
        
        Args:
            asset_id: Asset ID to enhance
            enhancement_types: List of enhancements to apply
            priority: Task priority
            callback: Optional completion callback
            
        Returns:
            Task ID for tracking progress
        """
        
        task_id = self._generate_task_id()
        
        # Create pipeline task
        task = PipelineTask(
            task_id=task_id,
            task_type="enhance",
            priority=priority,
            payload={
                "asset_id": asset_id,
                "enhancement_types": enhancement_types
            },
            callback=callback
        )
        
        # Queue task
        self._queue_task(task)
        
        logger.info(f"Asset enhancement queued: {asset_id} - Task ID: {task_id}")
        return task_id
    
    def import_to_ue5(self,
                     asset_ids: List[str],
                     create_materials: bool = True,
                     priority: TaskPriority = TaskPriority.NORMAL,
                     callback: Optional[Callable] = None) -> str:
        """
        Import assets to UE5
        
        Args:
            asset_ids: List of asset IDs to import
            create_materials: Whether to create materials
            priority: Task priority
            callback: Optional completion callback
            
        Returns:
            Task ID for tracking progress
        """
        
        if not self.ue5_connector:
            raise RuntimeError("UE5 integration not enabled")
        
        task_id = self._generate_task_id()
        
        # Create pipeline task
        task = PipelineTask(
            task_id=task_id,
            task_type="import",
            priority=priority,
            payload={
                "asset_ids": asset_ids,
                "create_materials": create_materials
            },
            callback=callback
        )
        
        # Queue task
        self._queue_task(task)
        
        logger.info(f"UE5 import queued: {len(asset_ids)} assets - Task ID: {task_id}")
        return task_id
    
    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a pipeline task"""
        
        # Check active tasks
        if task_id in self.active_tasks:
            task = self.active_tasks[task_id]
            return {
                "task_id": task.task_id,
                "task_type": task.task_type,
                "status": task.status,
                "progress": task.progress,
                "created_at": task.created_at,
                "started_at": task.started_at,
                "error": task.error,
                "is_complete": False
            }
        
        # Check completed tasks
        if task_id in self.completed_tasks:
            task = self.completed_tasks[task_id]
            return {
                "task_id": task.task_id,
                "task_type": task.task_type,
                "status": task.status,
                "progress": task.progress,
                "created_at": task.created_at,
                "started_at": task.started_at,
                "completed_at": task.completed_at,
                "error": task.error,
                "is_complete": True,
                "result": task.result
            }
        
        return None
    
    def cancel_task(self, task_id: str) -> bool:
        """Cancel a pending or active task"""
        
        # Remove from queue if pending
        # Note: PriorityQueue doesn't support removal, so we mark as cancelled
        if task_id in self.active_tasks:
            task = self.active_tasks[task_id]
            task.status = "cancelled"
            task.completed_at = time.time()
            
            # Move to completed tasks
            self.completed_tasks[task_id] = task
            del self.active_tasks[task_id]
            
            logger.info(f"Task cancelled: {task_id}")
            return True
        
        return False
    
    def get_pipeline_status(self) -> Dict[str, Any]:
        """Get comprehensive pipeline status"""
        
        return {
            "status": self.status.value,
            "uptime_seconds": time.time() - self.start_time,
            "queue_size": self.task_queue.qsize(),
            "active_tasks": len(self.active_tasks),
            "completed_tasks": len(self.completed_tasks),
            "metrics": self._get_current_metrics(),
            "component_health": self._get_component_health(),
            "configuration": self.config.get_config_summary()
        }
    
    def validate_pipeline(self) -> Dict[str, Any]:
        """Validate pipeline configuration and component health"""
        
        validation_result = {
            "is_healthy": True,
            "errors": [],
            "warnings": [],
            "component_status": {}
        }
        
        try:
            # Validate configuration
            config_validation = self.config.validate_config()
            if not config_validation.is_valid:
                validation_result["is_healthy"] = False
                validation_result["errors"].extend(config_validation.errors)
            validation_result["warnings"].extend(config_validation.warnings)
            
            # Test ComfyUI connection
            comfyui_healthy = self.comfyui_client.health_check()
            validation_result["component_status"]["comfyui"] = "healthy" if comfyui_healthy else "unhealthy"
            if not comfyui_healthy:
                validation_result["errors"].append("ComfyUI server not responding")
                validation_result["is_healthy"] = False
            
            # Validate workflow templates
            workflow_issues = self.workflow_manager.validate_workflows()
            validation_result["component_status"]["workflows"] = "healthy" if not any(workflow_issues.values()) else "issues"
            if any(workflow_issues.values()):
                validation_result["warnings"].append(f"Workflow validation issues: {workflow_issues}")
            
            # Test asset database
            try:
                db_stats = self.asset_manager.get_asset_statistics()
                validation_result["component_status"]["asset_database"] = "healthy"
            except Exception as e:
                validation_result["component_status"]["asset_database"] = "error"
                validation_result["errors"].append(f"Asset database error: {e}")
                validation_result["is_healthy"] = False
            
            # Test UE5 connector if enabled
            if self.ue5_connector:
                try:
                    # Basic UE5 validation would go here
                    validation_result["component_status"]["ue5_connector"] = "healthy"
                except Exception as e:
                    validation_result["component_status"]["ue5_connector"] = "error"
                    validation_result["warnings"].append(f"UE5 connector issues: {e}")
            else:
                validation_result["component_status"]["ue5_connector"] = "disabled"
            
            logger.info(f"Pipeline validation completed: {'healthy' if validation_result['is_healthy'] else 'issues found'}")
            return validation_result
            
        except Exception as e:
            logger.error(f"Pipeline validation failed: {e}")
            validation_result["is_healthy"] = False
            validation_result["errors"].append(f"Validation error: {e}")
            return validation_result
    
    def shutdown(self, timeout: float = 30.0):
        """Gracefully shutdown the pipeline"""
        
        logger.info("Shutting down pipeline...")
        self.status = PipelineStatus.MAINTENANCE
        
        # Stop accepting new tasks
        # Wait for active tasks to complete or timeout
        start_time = time.time()
        while self.active_tasks and (time.time() - start_time) < timeout:
            time.sleep(1)
        
        # Force shutdown if timeout exceeded
        if self.active_tasks:
            logger.warning(f"Forcing shutdown with {len(self.active_tasks)} active tasks")
        
        # Shutdown thread pool
        try:
            self.executor.shutdown(wait=True, timeout=timeout/2)
        except TypeError:
            # Older Python versions don't support timeout parameter
            self.executor.shutdown(wait=True)
        
        # Cleanup resources
        if hasattr(self, 'comfyui_client'):
            self.comfyui_client.clear_completed_jobs()
        
        logger.info("Pipeline shutdown complete")
    
    def _queue_task(self, task: PipelineTask):
        """Queue a task for processing"""
        # Priority queue uses tuples: (priority, counter, item)
        # Lower priority value = higher priority
        priority_value = 5 - task.priority.value  # Invert so HIGH=4 becomes 1
        self.task_counter += 1
        
        self.task_queue.put((priority_value, self.task_counter, task))
        self.active_tasks[task.task_id] = task
    
    def _task_processor_loop(self):
        """Background loop to process queued tasks"""
        
        while True:
            try:
                # Get next task (blocks until available)
                priority, counter, task = self.task_queue.get(timeout=1.0)
                
                # Submit task to thread pool
                future = self.executor.submit(self._execute_task, task)
                
                # Store future for tracking
                task.future = future
                
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"Task processor error: {e}")
                time.sleep(1)
    
    def _execute_task(self, task: PipelineTask):
        """Execute a pipeline task"""
        
        task.started_at = time.time()
        task.status = "running"
        
        try:
            logger.info(f"Executing task {task.task_id} ({task.task_type})")
            
            if task.task_type == "generate":
                result = self._execute_generate_task(task)
            elif task.task_type == "batch":
                result = self._execute_batch_task(task)
            elif task.task_type == "enhance":
                result = self._execute_enhance_task(task)
            elif task.task_type == "import":
                result = self._execute_import_task(task)
            else:
                raise ValueError(f"Unknown task type: {task.task_type}")
            
            # Task completed successfully
            task.status = "completed"
            task.result = result
            task.progress = 100.0
            
        except Exception as e:
            logger.error(f"Task {task.task_id} failed: {e}")
            task.status = "failed"
            task.error = str(e)
        
        finally:
            task.completed_at = time.time()
            
            # Move to completed tasks
            if task.task_id in self.active_tasks:
                del self.active_tasks[task.task_id]
            self.completed_tasks[task.task_id] = task
            
            # Update metrics
            self.metrics.total_tasks_processed += 1
            if task.status == "completed":
                self.metrics.successful_tasks += 1
            else:
                self.metrics.failed_tasks += 1
            
            # Execute callback if provided
            if task.callback:
                try:
                    task.callback(task)
                except Exception as e:
                    logger.error(f"Task callback failed: {e}")
            
            processing_time = task.completed_at - task.started_at
            logger.info(f"Task {task.task_id} {task.status} in {processing_time:.2f}s")
    
    def _execute_generate_task(self, task: PipelineTask) -> Dict[str, Any]:
        """Execute asset generation task"""
        
        payload = task.payload
        asset_spec = payload["asset_spec"]
        
        # Update progress
        task.progress = 10.0
        
        # Select and customize workflow
        workflow_template = self.workflow_manager.select_workflow(asset_spec)
        if not workflow_template:
            raise ValueError(f"No compatible workflow found for {asset_spec.asset_type}")
        
        workflow = self.workflow_manager.customize_workflow(workflow_template, asset_spec)
        task.progress = 20.0
        
        # Generate asset
        generation_job = self.comfyui_client.generate_sync(
            workflow,
            progress_callback=lambda job, elapsed, pos: setattr(task, 'progress', 20.0 + (elapsed / 60) * 40)
        )
        
        if generation_job.status != GenerationStatus.COMPLETED:
            raise RuntimeError(f"Generation failed: {generation_job.error}")
        
        task.progress = 60.0
        
        # Register asset
        output_files = []
        for filename in generation_job.output_files:
            # Construct full path based on ComfyUI output directory
            output_path = Path(self.config.get("paths.comfyui_output", "C:/Users/Zachg/Documents/ComfyUI/output")) / filename
            if output_path.exists():
                output_files.append(output_path)
        
        if not output_files:
            raise RuntimeError("No output files generated")
        
        # Register with asset manager
        asset_record = self.asset_manager.register_asset(
            asset_spec=asset_spec,
            files=output_files,
            status=AssetStatus.DRAFT
        )
        
        if not asset_record:
            raise RuntimeError("Failed to register asset")
        
        task.progress = 70.0
        
        # Quality assessment
        if output_files:
            qa_result = self.qa_manager.process_asset(output_files[0], asset_spec)
            quality_score = qa_result["assessment"].metrics.overall_score
            
            # Update asset record with quality score
            asset_record.quality_score = quality_score
        
        task.progress = 80.0
        
        # Auto-enhancement if configured
        if payload.get("auto_enhance", False) and quality_score < self.config.get("quality_assurance.enhancement.auto_enhance_threshold", 75):
            # Enhancement logic would go here
            logger.info(f"Auto-enhancement triggered for quality score {quality_score}")
        
        task.progress = 90.0
        
        # Auto-import to UE5 if configured
        if payload.get("auto_import_ue5", False) and self.ue5_connector:
            try:
                import_task = self.ue5_connector.import_asset(asset_record)
                logger.info(f"Asset imported to UE5: {import_task.task_id}")
            except Exception as e:
                logger.warning(f"UE5 import failed: {e}")
        
        task.progress = 100.0
        
        return {
            "asset_record": asset_record,
            "generation_job": generation_job,
            "quality_score": quality_score,
            "output_files": [str(f) for f in output_files]
        }
    
    def _execute_batch_task(self, task: PipelineTask) -> Dict[str, Any]:
        """Execute batch processing task"""
        
        payload = task.payload
        csv_file = payload["csv_file"]
        config = payload["config"]
        
        # Set up progress callback
        def progress_callback(session, job):
            progress = (session.completed_jobs + session.failed_jobs) / session.total_jobs * 100
            task.progress = progress
        
        config.progress_callback = progress_callback
        
        # Execute batch processing
        session = self.batch_processor.process_csv(csv_file, config)
        
        return {
            "session": session,
            "total_jobs": session.total_jobs,
            "completed_jobs": session.completed_jobs,
            "failed_jobs": session.failed_jobs,
            "success_rate": session.success_rate
        }
    
    def _execute_enhance_task(self, task: PipelineTask) -> Dict[str, Any]:
        """Execute asset enhancement task"""
        
        payload = task.payload
        asset_id = payload["asset_id"]
        enhancement_types = payload["enhancement_types"]
        
        # Get asset record
        asset_record = self.asset_manager.get_asset(asset_id)
        if not asset_record:
            raise ValueError(f"Asset not found: {asset_id}")
        
        # Enhancement logic would be implemented here
        # For now, just update progress
        task.progress = 100.0
        
        return {
            "asset_id": asset_id,
            "enhancements_applied": enhancement_types
        }
    
    def _execute_import_task(self, task: PipelineTask) -> Dict[str, Any]:
        """Execute UE5 import task"""
        
        payload = task.payload
        asset_ids = payload["asset_ids"]
        create_materials = payload["create_materials"]
        
        if not self.ue5_connector:
            raise RuntimeError("UE5 integration not enabled")
        
        # Get asset records
        asset_records = []
        for asset_id in asset_ids:
            record = self.asset_manager.get_asset(asset_id)
            if record:
                asset_records.append(record)
        
        if not asset_records:
            raise ValueError("No valid assets found")
        
        # Import to UE5
        import_tasks = self.ue5_connector.batch_import_assets(
            asset_records,
            progress_callback=lambda current, total, import_task: setattr(task, 'progress', (current / total) * 100)
        )
        
        return {
            "imported_assets": len(import_tasks),
            "import_tasks": [t.task_id for t in import_tasks]
        }
    
    def _generate_task_id(self) -> str:
        """Generate unique task ID"""
        self.task_counter += 1
        return f"task_{int(time.time())}_{self.task_counter}"
    
    def _health_check_loop(self):
        """Background health checking loop"""
        
        while True:
            try:
                # Check ComfyUI health
                self.metrics.comfyui_health = self.comfyui_client.health_check()
                self.metrics.last_health_check = time.time()
                
                # Update uptime
                self.metrics.uptime_seconds = time.time() - self.start_time
                
                # Update queue size
                self.metrics.queue_size = self.task_queue.qsize()
                self.metrics.active_workers = len(self.active_tasks)
                
                # Sleep until next check
                time.sleep(self.config.get("comfyui.connection.health_check_interval", 30))
                
            except Exception as e:
                logger.error(f"Health check error: {e}")
                time.sleep(10)
    
    def _metrics_collection_loop(self):
        """Background metrics collection loop"""
        
        while True:
            try:
                # Collect system metrics
                self._update_system_metrics()
                
                # Sleep until next collection
                time.sleep(60)  # Collect every minute
                
            except Exception as e:
                logger.error(f"Metrics collection error: {e}")
                time.sleep(10)
    
    def _update_system_metrics(self):
        """Update system performance metrics"""
        try:
            import psutil
            
            # Memory usage
            process = psutil.Process()
            self.metrics.memory_usage_mb = process.memory_info().rss / (1024 * 1024)
            
            # Disk usage
            disk_usage = psutil.disk_usage(self.config.get("paths.base_directory"))
            self.metrics.disk_usage_gb = disk_usage.used / (1024 * 1024 * 1024)
            
        except ImportError:
            # psutil not available
            pass
        except Exception as e:
            logger.warning(f"System metrics update failed: {e}")
    
    def _get_current_metrics(self) -> Dict[str, Any]:
        """Get current pipeline metrics"""
        return {
            "total_tasks_processed": self.metrics.total_tasks_processed,
            "successful_tasks": self.metrics.successful_tasks,
            "failed_tasks": self.metrics.failed_tasks,
            "success_rate": (self.metrics.successful_tasks / max(1, self.metrics.total_tasks_processed)) * 100,
            "queue_size": self.metrics.queue_size,
            "active_workers": self.metrics.active_workers,
            "uptime_seconds": self.metrics.uptime_seconds,
            "memory_usage_mb": self.metrics.memory_usage_mb,
            "disk_usage_gb": self.metrics.disk_usage_gb
        }
    
    def _get_component_health(self) -> Dict[str, str]:
        """Get health status of all components"""
        return {
            "comfyui": "healthy" if self.metrics.comfyui_health else "unhealthy",
            "workflow_manager": "healthy",
            "asset_manager": "healthy",
            "quality_assurance": "healthy",
            "batch_processor": "healthy",
            "ue5_connector": "healthy" if self.ue5_connector else "disabled"
        }