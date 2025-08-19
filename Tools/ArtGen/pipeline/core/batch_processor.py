"""
Batch Processor - Intelligent batch processing with queue management
===================================================================

Handles batch generation jobs with intelligent queue management, progress tracking,
resource optimization, and failure recovery. Supports CSV import, faction batch
generation, and custom batch specifications.
"""

from __future__ import annotations

import csv
import json
import pathlib
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Callable
import logging
from queue import Queue, PriorityQueue
from enum import Enum

from .asset_spec import AssetSpecification
from .workflow_manager import WorkflowManager
from .quality_assurance import QualityAssurance
from ..utils.logger import setup_logger


class JobStatus(Enum):
    """Status values for batch jobs."""
    PENDING = "pending"
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    RETRYING = "retrying"


@dataclass
class BatchJob:
    """Individual job within a batch."""
    id: str
    spec: AssetSpecification
    priority: int = 5
    status: JobStatus = JobStatus.PENDING
    created_at: datetime = field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    attempts: int = 0
    max_retries: int = 3
    error_message: Optional[str] = None
    result: Optional[Dict[str, Any]] = None
    
    def __lt__(self, other):
        """For priority queue ordering (higher priority first)."""
        return self.priority > other.priority


@dataclass
class BatchJobResult:
    """Result of a batch job execution."""
    job_id: str
    success: bool
    generation_result: Optional[Dict[str, Any]] = None
    quality_report: Optional[Any] = None  # QualityReport
    error: Optional[str] = None
    execution_time: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class BatchConfiguration:
    """Configuration for batch processing."""
    max_concurrent_jobs: int = 2
    retry_failed_jobs: bool = True
    max_retries_per_job: int = 3
    job_timeout: float = 600.0
    save_intermediate_results: bool = True
    continue_on_failure: bool = True
    quality_gate_enabled: bool = True
    auto_enhance_assets: bool = True
    progress_reporting_interval: float = 10.0


class BatchProcessor:
    """
    Intelligent batch processor for asset generation.
    
    Features:
    - Priority-based job queue
    - Concurrent execution with resource management
    - Automatic retry logic for failed jobs
    - Progress tracking and reporting
    - Quality gate integration
    - CSV import support
    - Faction batch generation
    """
    
    def __init__(self, config):
        self.config = config
        self.logger = setup_logger("BatchProcessor", config.log_level)
        
        # Processing configuration
        self.batch_config = BatchConfiguration(
            max_concurrent_jobs=getattr(config, 'max_concurrent_jobs', 2),
            job_timeout=getattr(config, 'job_timeout', 600.0)
        )
        
        # Job management
        self.job_queue = PriorityQueue()
        self.active_jobs: Dict[str, BatchJob] = {}
        self.completed_jobs: Dict[str, BatchJobResult] = {}
        self.job_counter = 0
        
        # Processing state
        self.is_processing = False
        self.processing_thread: Optional[threading.Thread] = None
        self.stop_event = threading.Event()
        
        # Dependencies (will be injected)
        self.workflow_manager: Optional[WorkflowManager] = None
        self.quality_assurance: Optional[QualityAssurance] = None
        
        self.logger.info("Batch Processor initialized")
    
    def set_dependencies(
        self,
        workflow_manager: WorkflowManager,
        quality_assurance: QualityAssurance
    ):
        """Inject dependencies for processing."""
        self.workflow_manager = workflow_manager
        self.quality_assurance = quality_assurance
    
    def load_batch_spec(self, spec_path: pathlib.Path) -> List[AssetSpecification]:
        """Load batch specification from file."""
        self.logger.info(f"Loading batch specification: {spec_path}")
        
        try:
            if spec_path.suffix.lower() == '.json':
                return self._load_json_batch(spec_path)
            elif spec_path.suffix.lower() == '.csv':
                return self._load_csv_batch(spec_path)
            else:
                raise ValueError(f"Unsupported batch file format: {spec_path.suffix}")
        
        except Exception as e:
            self.logger.error(f"Failed to load batch specification: {e}")
            raise
    
    def _load_json_batch(self, json_path: pathlib.Path) -> List[AssetSpecification]:
        """Load batch from JSON specification file."""
        data = json.loads(json_path.read_text())
        
        if "assets" in data:
            # Structured batch file
            specs = []
            for asset_data in data["assets"]:
                spec = AssetSpecification.from_dict(asset_data)
                specs.append(spec)
            return specs
        
        elif isinstance(data, list):
            # Array of asset specifications
            return [AssetSpecification.from_dict(item) for item in data]
        
        else:
            # Single asset specification
            return [AssetSpecification.from_dict(data)]
    
    def _load_csv_batch(
        self,
        csv_path: pathlib.Path,
        template_spec: Optional[AssetSpecification] = None
    ) -> List[AssetSpecification]:
        """Load batch from CSV file (like Weapons.csv)."""
        if not template_spec:
            # Create default template for weapons
            template_spec = AssetSpecification(
                name="Template",
                asset_type="weapon",
                workflow_type="high_detail_render"
            )
        
        specs = []
        
        with open(csv_path, 'r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            
            for row in reader:
                try:
                    spec = AssetSpecification.create_from_csv_row(row, template_spec)
                    specs.append(spec)
                except Exception as e:
                    self.logger.warning(f"Skipping invalid CSV row: {e}")
        
        return specs
    
    def process_batch(
        self,
        asset_specs: List[AssetSpecification],
        progress_callback: Optional[Callable] = None
    ) -> Dict[str, Any]:
        """
        Process a batch of asset specifications.
        
        Args:
            asset_specs: List of asset specifications to process
            progress_callback: Optional callback for progress updates
            
        Returns:
            Batch processing results
        """
        self.logger.info(f"Starting batch processing: {len(asset_specs)} assets")
        
        start_time = time.time()
        
        # Queue all jobs
        job_ids = []
        for spec in asset_specs:
            job_id = self.queue_job(spec)
            job_ids.append(job_id)
        
        # Start processing
        if not self.is_processing:
            self.start_processing()
        
        # Wait for completion with progress reporting
        return self._wait_for_batch_completion(
            job_ids, progress_callback, start_time
        )
    
    def process_csv_batch(
        self,
        csv_path: pathlib.Path,
        template_spec: AssetSpecification,
        progress_callback: Optional[Callable] = None
    ) -> Dict[str, Any]:
        """Process assets from CSV file."""
        specs = self._load_csv_batch(csv_path, template_spec)
        return self.process_batch(specs, progress_callback)
    
    def queue_job(self, spec: AssetSpecification) -> str:
        """Queue a single job for processing."""
        self.job_counter += 1
        job_id = f"job_{self.job_counter:06d}_{spec.name.replace(' ', '_')}"
        
        job = BatchJob(
            id=job_id,
            spec=spec,
            priority=spec.priority,
            status=JobStatus.QUEUED
        )
        
        self.job_queue.put(job)
        self.active_jobs[job_id] = job
        
        self.logger.debug(f"Queued job: {job_id}")
        return job_id
    
    def start_processing(self):
        """Start the batch processing thread."""
        if self.is_processing:
            self.logger.warning("Batch processing already running")
            return
        
        if not self.workflow_manager or not self.quality_assurance:
            raise RuntimeError("Dependencies not set. Call set_dependencies() first.")
        
        self.is_processing = True
        self.stop_event.clear()
        
        self.processing_thread = threading.Thread(
            target=self._processing_loop,
            daemon=True
        )
        self.processing_thread.start()
        
        self.logger.info("Batch processing started")
    
    def stop_processing(self):
        """Stop batch processing gracefully."""
        if not self.is_processing:
            return
        
        self.logger.info("Stopping batch processing...")
        self.stop_event.set()
        
        if self.processing_thread:
            self.processing_thread.join(timeout=30.0)
        
        self.is_processing = False
        self.logger.info("Batch processing stopped")
    
    def _processing_loop(self):
        """Main processing loop for batch jobs."""
        self.logger.info("Batch processing loop started")
        
        with ThreadPoolExecutor(
            max_workers=self.batch_config.max_concurrent_jobs
        ) as executor:
            
            active_futures = {}
            
            while not self.stop_event.is_set():
                # Submit new jobs up to the concurrent limit
                while (len(active_futures) < self.batch_config.max_concurrent_jobs and
                       not self.job_queue.empty()):
                    
                    try:
                        job = self.job_queue.get_nowait()
                        job.status = JobStatus.RUNNING
                        job.started_at = datetime.utcnow()
                        
                        future = executor.submit(self._execute_job, job)
                        active_futures[future] = job
                        
                        self.logger.debug(f"Started job: {job.id}")
                        
                    except Exception as e:
                        self.logger.error(f"Error submitting job: {e}")
                        break
                
                # Check for completed jobs
                if active_futures:
                    completed_futures = []
                    
                    for future in as_completed(active_futures, timeout=1.0):
                        job = active_futures[future]
                        
                        try:
                            result = future.result()
                            self._handle_job_completion(job, result)
                            completed_futures.append(future)
                            
                        except Exception as e:
                            self._handle_job_failure(job, str(e))
                            completed_futures.append(future)
                    
                    # Remove completed futures
                    for future in completed_futures:
                        del active_futures[future]
                
                # Check if we're done
                if (self.job_queue.empty() and 
                    not active_futures and 
                    not self._has_pending_retries()):
                    break
                
                time.sleep(0.1)
        
        self.is_processing = False
        self.logger.info("Batch processing loop completed")
    
    def _execute_job(self, job: BatchJob) -> BatchJobResult:
        """Execute a single batch job."""
        job.attempts += 1
        start_time = time.time()
        
        self.logger.info(f"Executing job: {job.id} (attempt {job.attempts})")
        
        try:
            # Select and execute workflow
            workflow = self.workflow_manager.select_workflow(job.spec)
            generation_result = self.workflow_manager.execute_workflow(
                workflow, job.spec
            )
            
            # Quality assurance
            quality_report = None
            if self.batch_config.quality_gate_enabled:
                quality_report = self.quality_assurance.validate_output(
                    generation_result, job.spec
                )
                
                # Auto-enhance if needed and enabled
                if (self.batch_config.auto_enhance_assets and 
                    quality_report.needs_enhancement):
                    generation_result = self.quality_assurance.enhance_asset(
                        generation_result, job.spec
                    )
                
                # Check quality gate
                if not quality_report.passes_quality_gate:
                    self.logger.warning(
                        f"Job {job.id} failed quality gate: "
                        f"score {quality_report.overall_score:.1f}"
                    )
            
            execution_time = time.time() - start_time
            
            return BatchJobResult(
                job_id=job.id,
                success=True,
                generation_result=generation_result,
                quality_report=quality_report,
                execution_time=execution_time,
                metadata={
                    "attempts": job.attempts,
                    "workflow_used": workflow.name
                }
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            error_msg = f"Job execution failed: {e}"
            
            self.logger.error(f"Job {job.id} failed: {error_msg}")
            
            return BatchJobResult(
                job_id=job.id,
                success=False,
                error=error_msg,
                execution_time=execution_time,
                metadata={"attempts": job.attempts}
            )
    
    def _handle_job_completion(self, job: BatchJob, result: BatchJobResult):
        """Handle successful job completion."""
        job.status = JobStatus.COMPLETED
        job.completed_at = datetime.utcnow()
        job.result = result.generation_result
        
        self.completed_jobs[job.id] = result
        
        # Save intermediate results if enabled
        if self.batch_config.save_intermediate_results:
            self._save_job_result(job, result)
        
        self.logger.info(
            f"Job completed: {job.id} "
            f"({result.execution_time:.1f}s)"
        )
    
    def _handle_job_failure(self, job: BatchJob, error: str):
        """Handle job failure with retry logic."""
        job.error_message = error
        
        # Check if we should retry
        if (self.batch_config.retry_failed_jobs and 
            job.attempts < job.max_retries):
            
            job.status = JobStatus.RETRYING
            
            # Add delay before retry
            retry_delay = min(2 ** job.attempts, 60)  # Exponential backoff
            
            def retry_job():
                time.sleep(retry_delay)
                if not self.stop_event.is_set():
                    self.job_queue.put(job)
            
            threading.Thread(target=retry_job, daemon=True).start()
            
            self.logger.warning(
                f"Job {job.id} failed, retrying in {retry_delay}s "
                f"(attempt {job.attempts + 1}/{job.max_retries})"
            )
        
        else:
            job.status = JobStatus.FAILED
            job.completed_at = datetime.utcnow()
            
            # Save failure result
            failure_result = BatchJobResult(
                job_id=job.id,
                success=False,
                error=error,
                metadata={"attempts": job.attempts}
            )
            self.completed_jobs[job.id] = failure_result
            
            self.logger.error(f"Job {job.id} failed permanently: {error}")
    
    def _has_pending_retries(self) -> bool:
        """Check if there are jobs pending retry."""
        return any(
            job.status == JobStatus.RETRYING 
            for job in self.active_jobs.values()
        )
    
    def _save_job_result(self, job: BatchJob, result: BatchJobResult):
        """Save individual job result to disk."""
        try:
            if result.generation_result and "output_directory" in result.generation_result:
                output_dir = pathlib.Path(result.generation_result["output_directory"])
                result_file = output_dir / f"{job.id}_result.json"
                
                result_data = {
                    "job_id": job.id,
                    "asset_name": job.spec.name,
                    "success": result.success,
                    "execution_time": result.execution_time,
                    "attempts": job.attempts,
                    "completed_at": job.completed_at.isoformat() if job.completed_at else None,
                    "quality_score": (
                        result.quality_report.overall_score 
                        if result.quality_report else None
                    ),
                    "generation_result": result.generation_result,
                    "metadata": result.metadata
                }
                
                result_file.write_text(json.dumps(result_data, indent=2))
                
        except Exception as e:
            self.logger.warning(f"Failed to save job result: {e}")
    
    def _wait_for_batch_completion(
        self,
        job_ids: List[str],
        progress_callback: Optional[Callable],
        start_time: float
    ) -> Dict[str, Any]:
        """Wait for batch completion and provide progress updates."""
        last_progress_report = 0.0
        
        while True:
            # Check completion status
            completed_count = sum(
                1 for job_id in job_ids 
                if job_id in self.completed_jobs
            )
            
            all_completed = completed_count == len(job_ids)
            
            # Progress reporting
            current_time = time.time()
            if (progress_callback and 
                current_time - last_progress_report > self.batch_config.progress_reporting_interval):
                
                progress_info = {
                    "total_jobs": len(job_ids),
                    "completed_jobs": completed_count,
                    "progress_percent": (completed_count / len(job_ids)) * 100,
                    "elapsed_time": current_time - start_time,
                    "estimated_remaining": self._estimate_remaining_time(
                        job_ids, completed_count, current_time - start_time
                    )
                }
                
                progress_callback(progress_info)
                last_progress_report = current_time
            
            if all_completed:
                break
            
            time.sleep(1.0)
        
        # Generate final results
        return self._generate_batch_results(job_ids, start_time)
    
    def _estimate_remaining_time(
        self,
        job_ids: List[str],
        completed_count: int,
        elapsed_time: float
    ) -> float:
        """Estimate remaining processing time."""
        if completed_count == 0:
            return 0.0
        
        average_time_per_job = elapsed_time / completed_count
        remaining_jobs = len(job_ids) - completed_count
        
        return remaining_jobs * average_time_per_job
    
    def _generate_batch_results(
        self,
        job_ids: List[str],
        start_time: float
    ) -> Dict[str, Any]:
        """Generate comprehensive batch processing results."""
        end_time = time.time()
        total_time = end_time - start_time
        
        # Collect results
        successful_jobs = []
        failed_jobs = []
        quality_scores = []
        
        for job_id in job_ids:
            if job_id in self.completed_jobs:
                result = self.completed_jobs[job_id]
                
                if result.success:
                    successful_jobs.append(result)
                    if result.quality_report:
                        quality_scores.append(result.quality_report.overall_score)
                else:
                    failed_jobs.append(result)
        
        # Calculate statistics
        success_rate = len(successful_jobs) / len(job_ids) * 100
        average_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0.0
        average_execution_time = (
            sum(result.execution_time for result in successful_jobs) / 
            len(successful_jobs) if successful_jobs else 0.0
        )
        
        results = {
            "batch_summary": {
                "total_jobs": len(job_ids),
                "successful_jobs": len(successful_jobs),
                "failed_jobs": len(failed_jobs),
                "success_rate": success_rate,
                "total_execution_time": total_time,
                "average_execution_time": average_execution_time,
                "average_quality_score": average_quality
            },
            "successful_results": successful_jobs,
            "failed_results": failed_jobs,
            "timestamp": datetime.utcnow().isoformat(),
            "configuration": {
                "max_concurrent_jobs": self.batch_config.max_concurrent_jobs,
                "quality_gate_enabled": self.batch_config.quality_gate_enabled,
                "auto_enhance_assets": self.batch_config.auto_enhance_assets
            }
        }
        
        self.logger.info(
            f"Batch processing completed: "
            f"{len(successful_jobs)}/{len(job_ids)} successful "
            f"({success_rate:.1f}%), "
            f"total time: {total_time:.1f}s"
        )
        
        return results
    
    def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a specific job."""
        if job_id in self.active_jobs:
            job = self.active_jobs[job_id]
            return {
                "job_id": job_id,
                "status": job.status.value,
                "priority": job.priority,
                "attempts": job.attempts,
                "created_at": job.created_at.isoformat(),
                "started_at": job.started_at.isoformat() if job.started_at else None,
                "completed_at": job.completed_at.isoformat() if job.completed_at else None,
                "error_message": job.error_message
            }
        
        return None
    
    def cancel_job(self, job_id: str) -> bool:
        """Cancel a specific job."""
        if job_id in self.active_jobs:
            job = self.active_jobs[job_id]
            if job.status in [JobStatus.QUEUED, JobStatus.PENDING]:
                job.status = JobStatus.CANCELLED
                self.logger.info(f"Job cancelled: {job_id}")
                return True
        
        return False
    
    def get_status(self) -> Dict[str, Any]:
        """Get batch processor status."""
        return {
            "is_processing": self.is_processing,
            "queued_jobs": self.job_queue.qsize(),
            "active_jobs": len(self.active_jobs),
            "completed_jobs": len(self.completed_jobs),
            "configuration": {
                "max_concurrent_jobs": self.batch_config.max_concurrent_jobs,
                "retry_failed_jobs": self.batch_config.retry_failed_jobs,
                "max_retries_per_job": self.batch_config.max_retries_per_job,
                "job_timeout": self.batch_config.job_timeout
            }
        }
    
    def shutdown(self):
        """Shutdown the batch processor."""
        self.logger.info("Shutting down Batch Processor")
        self.stop_processing()
        
        # Clear queues
        while not self.job_queue.empty():
            try:
                self.job_queue.get_nowait()
            except:
                break
        
        self.active_jobs.clear()
        self.logger.info("Batch Processor shutdown complete")