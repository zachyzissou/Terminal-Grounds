#!/usr/bin/env python3
"""
Batch Processor for Terminal Grounds v2.0
=========================================
High-performance CSV batch processing with intelligent queue management and progress tracking.
"""

import csv
import json
import time
import threading
import queue
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional, Union, Iterator, Callable
from dataclasses import dataclass, field
from enum import Enum
import concurrent.futures
from datetime import datetime

try:
    from .asset_spec import AssetSpecification, AssetSpecBuilder, AssetType, FactionCode
    from .enhanced_client import EnhancedComfyUIClient, GenerationJob, GenerationStatus
    from .workflow_manager import WorkflowManager, WorkflowTemplate
    from .quality_assurance import QualityAssuranceManager, QualityAssessmentEngine
except ImportError:
    from asset_spec import AssetSpecification, AssetSpecBuilder, AssetType, FactionCode
    from enhanced_client import EnhancedComfyUIClient, GenerationJob, GenerationStatus
    from workflow_manager import WorkflowManager, WorkflowTemplate
    from quality_assurance import QualityAssuranceManager, QualityAssessmentEngine

logger = logging.getLogger(__name__)

class BatchJobStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    QUALITY_CHECK = "quality_check"
    ENHANCING = "enhancing"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"

@dataclass
class BatchJob:
    """Individual job within a batch processing session"""
    id: str
    row_index: int
    asset_spec: AssetSpecification
    status: BatchJobStatus = BatchJobStatus.PENDING
    generation_job: Optional[GenerationJob] = None
    output_files: List[Path] = field(default_factory=list)
    quality_score: Optional[float] = None
    enhancement_count: int = 0
    error_message: Optional[str] = None
    start_time: Optional[float] = None
    completion_time: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class BatchConfiguration:
    """Configuration for batch processing"""
    max_concurrent_jobs: int = 2
    max_enhancement_attempts: int = 2
    quality_threshold: float = 70.0
    auto_enhance: bool = True
    auto_import_ue5: bool = False
    output_directory: Path = Path("outputs/batch")
    retry_failed_jobs: bool = True
    max_retries: int = 3
    progress_callback: Optional[Callable] = None
    
@dataclass
class BatchSession:
    """Complete batch processing session"""
    session_id: str
    csv_file: Path
    config: BatchConfiguration
    jobs: List[BatchJob] = field(default_factory=list)
    start_time: float = field(default_factory=time.time)
    completion_time: Optional[float] = None
    total_jobs: int = 0
    completed_jobs: int = 0
    failed_jobs: int = 0
    skipped_jobs: int = 0
    
    @property
    def is_complete(self) -> bool:
        return self.completion_time is not None
    
    @property
    def progress_percentage(self) -> float:
        if self.total_jobs == 0:
            return 0.0
        return (self.completed_jobs + self.failed_jobs + self.skipped_jobs) / self.total_jobs * 100
    
    @property
    def success_rate(self) -> float:
        total_processed = self.completed_jobs + self.failed_jobs
        if total_processed == 0:
            return 0.0
        return self.completed_jobs / total_processed * 100

class CSVParser:
    """Intelligent CSV parser for Terminal Grounds data"""
    
    def __init__(self, spec_builder: AssetSpecBuilder):
        self.spec_builder = spec_builder
        
        # Column mapping strategies
        self.column_mappings = {
            "name": ["name", "asset_name", "item_name", "title"],
            "asset_type": ["type", "asset_type", "category", "kind"],
            "faction": ["faction", "faction_code", "allegiance", "owner"],
            "description": ["description", "desc", "details", "notes", "summary"],
            "prompt": ["prompt", "generation_prompt", "custom_prompt"],
            "style": ["style", "visual_style", "aesthetic"],
            "tags": ["tags", "keywords", "labels"],
            "priority": ["priority", "importance", "urgency"],
            "quality_level": ["quality", "quality_level", "target_quality"]
        }
        
    def parse_csv(self, csv_file: Path) -> Iterator[AssetSpecification]:
        """Parse CSV file and yield asset specifications"""
        try:
            with open(csv_file, 'r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                
                # Analyze headers
                headers = reader.fieldnames or []
                column_map = self._map_columns(headers)
                
                logger.info(f"Parsing CSV with {len(headers)} columns: {headers}")
                logger.info(f"Column mapping: {column_map}")
                
                for row_index, row in enumerate(reader):
                    try:
                        asset_spec = self._row_to_asset_spec(row, column_map, row_index)
                        if asset_spec:
                            yield asset_spec
                        else:
                            logger.warning(f"Skipping row {row_index + 1}: Could not create asset specification")
                    except Exception as e:
                        logger.error(f"Error parsing row {row_index + 1}: {e}")
                        continue
                        
        except Exception as e:
            logger.error(f"Failed to parse CSV file {csv_file}: {e}")
            raise
    
    def _map_columns(self, headers: List[str]) -> Dict[str, str]:
        """Map CSV headers to our expected column names"""
        column_map = {}
        headers_lower = [h.lower().strip() for h in headers]
        
        for field, possible_names in self.column_mappings.items():
            for possible_name in possible_names:
                if possible_name in headers_lower:
                    original_header = headers[headers_lower.index(possible_name)]
                    column_map[field] = original_header
                    break
        
        return column_map
    
    def _row_to_asset_spec(self, row: Dict[str, str], column_map: Dict[str, str], row_index: int) -> Optional[AssetSpecification]:
        """Convert CSV row to asset specification"""
        try:
            # Extract required fields
            name = self._get_value(row, column_map, "name", f"Asset_{row_index}")
            asset_type = self._get_value(row, column_map, "asset_type", "concept")
            faction = self._get_value(row, column_map, "faction", "neutral")
            description = self._get_value(row, column_map, "description", "Generated asset")
            
            # Validate and normalize asset type
            asset_type = self._normalize_asset_type(asset_type)
            faction = self._normalize_faction(faction)
            
            # Extract optional fields
            custom_prompt = self._get_value(row, column_map, "prompt", None)
            style = self._get_value(row, column_map, "style", None)
            tags_str = self._get_value(row, column_map, "tags", "")
            quality_level = self._get_value(row, column_map, "quality_level", "production")
            
            # Parse tags
            tags = [tag.strip() for tag in tags_str.split(",") if tag.strip()] if tags_str else []
            
            # Create base specification
            asset_spec = self.spec_builder.create_spec(
                name=name,
                asset_type=asset_type,
                faction=faction,
                description=description
            )
            
            # Apply custom modifications
            if custom_prompt:
                asset_spec.base_prompt = custom_prompt
            
            if style:
                asset_spec.base_prompt += f", {style}"
                asset_spec.tags.append(style)
            
            if tags:
                asset_spec.tags.extend(tags)
            
            # Adjust quality requirements based on specified level
            if quality_level.lower() in ["hero", "cinematic"]:
                asset_spec.quality_requirements.min_quality_score = 85.0
                asset_spec.quality_requirements.target_resolution = 4096
                asset_spec.generation_params.steps = 35
            elif quality_level.lower() in ["high", "production"]:
                asset_spec.quality_requirements.min_quality_score = 75.0
                asset_spec.quality_requirements.target_resolution = 2048
                asset_spec.generation_params.steps = 30
            elif quality_level.lower() in ["draft", "preview"]:
                asset_spec.quality_requirements.min_quality_score = 60.0
                asset_spec.quality_requirements.target_resolution = 1024
                asset_spec.generation_params.steps = 20
            
            # Add CSV metadata
            asset_spec.metadata.update({
                "csv_row": row_index,
                "csv_source": True,
                "original_row": dict(row)  # Keep original data for reference
            })
            
            return asset_spec
            
        except Exception as e:
            logger.error(f"Failed to create asset spec from row {row_index}: {e}")
            return None
    
    def _get_value(self, row: Dict[str, str], column_map: Dict[str, str], field: str, default: Any = None) -> str:
        """Get value from row using column mapping"""
        if field in column_map:
            return row.get(column_map[field], str(default) if default is not None else "").strip()
        return str(default) if default is not None else ""
    
    def _normalize_asset_type(self, asset_type: str) -> AssetType:
        """Normalize asset type to valid values"""
        asset_type = asset_type.lower().strip()
        
        # Direct matches
        valid_types = ["weapon", "vehicle", "emblem", "poster", "icon", "concept", "environment", "texture", "ui"]
        if asset_type in valid_types:
            return asset_type
        
        # Fuzzy matching
        type_mappings = {
            "weapons": "weapon",
            "firearms": "weapon",
            "guns": "weapon",
            "melee": "weapon",
            "vehicles": "vehicle",
            "transport": "vehicle",
            "ships": "vehicle",
            "aircraft": "vehicle",
            "emblems": "emblem",
            "logos": "emblem",
            "insignia": "emblem",
            "badges": "emblem",
            "posters": "poster",
            "propaganda": "poster",
            "banners": "poster",
            "icons": "icon",
            "symbols": "icon",
            "ui_elements": "ui",
            "interface": "ui",
            "concepts": "concept",
            "concept_art": "concept",
            "environments": "environment",
            "scenes": "environment",
            "backgrounds": "environment",
            "textures": "texture",
            "materials": "texture"
        }
        
        return type_mappings.get(asset_type, "concept")
    
    def _normalize_faction(self, faction: str) -> FactionCode:
        """Normalize faction to valid codes"""
        faction = faction.lower().strip()
        
        # Direct matches
        valid_factions = ["directorate", "free77", "vultures", "combine", "nomads", "archivists", "wardens", "neutral"]
        if faction in valid_factions:
            return faction
        
        # Fuzzy matching
        faction_mappings = {
            "dir": "directorate",
            "corporate": "directorate",
            "military": "directorate",
            "f77": "free77",
            "free_77": "free77",
            "mercenaries": "free77",
            "mercs": "free77",
            "vlt": "vultures",
            "vultures_union": "vultures",
            "scavengers": "vultures",
            "corporate_combine": "combine",
            "corp": "combine",
            "nomad_clans": "nomads",
            "nomadic": "nomads",
            "tribal": "nomads",
            "vaulted_archivists": "archivists",
            "archive": "archivists",
            "scholars": "archivists",
            "civic_wardens": "wardens",
            "wardens": "wardens",
            "civic": "wardens",
            "peacekeepers": "wardens"
        }
        
        return faction_mappings.get(faction, "neutral")

class BatchProcessor:
    """
    High-performance batch processor for CSV-driven asset generation.
    Handles concurrent generation, quality assessment, and enhancement workflows.
    """
    
    def __init__(self, 
                 comfyui_client: EnhancedComfyUIClient,
                 workflow_manager: WorkflowManager,
                 qa_manager: QualityAssuranceManager,
                 spec_builder: AssetSpecBuilder):
        self.comfyui_client = comfyui_client
        self.workflow_manager = workflow_manager
        self.qa_manager = qa_manager
        self.spec_builder = spec_builder
        self.csv_parser = CSVParser(spec_builder)
        
        # Session management
        self.current_session: Optional[BatchSession] = None
        self.job_queue: queue.Queue = queue.Queue()
        self.completed_jobs: queue.Queue = queue.Queue()
        
        # Threading
        self.worker_threads: List[threading.Thread] = []
        self.is_processing = False
        self.shutdown_event = threading.Event()
        
    def process_csv(self, csv_file: Path, config: BatchConfiguration) -> BatchSession:
        """
        Process entire CSV file with configured parameters
        
        Args:
            csv_file: Path to CSV file containing asset definitions
            config: Batch processing configuration
            
        Returns:
            Batch session with results
        """
        # Create new session
        session_id = f"batch_{int(time.time())}"
        session = BatchSession(
            session_id=session_id,
            csv_file=csv_file,
            config=config
        )
        
        self.current_session = session
        
        try:
            # Parse CSV and create jobs
            logger.info(f"Starting batch processing of {csv_file}")
            jobs = self._create_jobs_from_csv(csv_file, session_id)
            session.jobs = jobs
            session.total_jobs = len(jobs)
            
            if not jobs:
                logger.warning("No valid jobs created from CSV")
                session.completion_time = time.time()
                return session
            
            # Setup output directory
            config.output_directory.mkdir(parents=True, exist_ok=True)
            
            # Start processing
            self._process_jobs(session)
            
            # Mark session complete
            session.completion_time = time.time()
            
            # Generate summary report
            self._generate_session_report(session)
            
            logger.info(f"Batch processing complete: {session.completed_jobs}/{session.total_jobs} successful")
            return session
            
        except Exception as e:
            logger.error(f"Batch processing failed: {e}")
            session.completion_time = time.time()
            raise
    
    def _create_jobs_from_csv(self, csv_file: Path, session_id: str) -> List[BatchJob]:
        """Create batch jobs from CSV file"""
        jobs = []
        
        for row_index, asset_spec in enumerate(self.csv_parser.parse_csv(csv_file)):
            job_id = f"{session_id}_job_{row_index}"
            
            job = BatchJob(
                id=job_id,
                row_index=row_index,
                asset_spec=asset_spec
            )
            
            jobs.append(job)
        
        logger.info(f"Created {len(jobs)} batch jobs from CSV")
        return jobs
    
    def _process_jobs(self, session: BatchSession):
        """Process all jobs in the session"""
        config = session.config
        
        # Fill job queue
        for job in session.jobs:
            self.job_queue.put(job)
        
        # Start worker threads
        self.is_processing = True
        self.shutdown_event.clear()
        
        for i in range(config.max_concurrent_jobs):
            worker = threading.Thread(
                target=self._worker_thread,
                args=(session,),
                name=f"BatchWorker-{i}"
            )
            worker.start()
            self.worker_threads.append(worker)
        
        # Monitor progress
        self._monitor_progress(session)
        
        # Wait for completion
        for worker in self.worker_threads:
            worker.join()
        
        self.is_processing = False
        self.worker_threads.clear()
    
    def _worker_thread(self, session: BatchSession):
        """Worker thread for processing individual jobs"""
        while not self.shutdown_event.is_set():
            try:
                # Get next job
                job = self.job_queue.get(timeout=1.0)
                
                # Process job
                self._process_single_job(job, session)
                
                # Update session counters
                if job.status == BatchJobStatus.COMPLETED:
                    session.completed_jobs += 1
                elif job.status == BatchJobStatus.FAILED:
                    session.failed_jobs += 1
                elif job.status == BatchJobStatus.SKIPPED:
                    session.skipped_jobs += 1
                
                # Report progress
                if session.config.progress_callback:
                    session.config.progress_callback(session, job)
                
                self.job_queue.task_done()
                
            except queue.Empty:
                # Check if we should shutdown
                if self.job_queue.empty():
                    break
                continue
            except Exception as e:
                logger.error(f"Worker thread error: {e}")
                continue
    
    def _process_single_job(self, job: BatchJob, session: BatchSession):
        """Process a single batch job"""
        job.start_time = time.time()
        job.status = BatchJobStatus.PROCESSING
        
        try:
            logger.info(f"Processing job {job.id}: {job.asset_spec.name}")
            
            # Generate asset
            success = self._generate_asset(job, session)
            if not success:
                job.status = BatchJobStatus.FAILED
                return
            
            # Quality assessment
            if job.output_files:
                self._assess_quality(job, session)
                
                # Enhancement if needed
                if session.config.auto_enhance and job.quality_score and job.quality_score < session.config.quality_threshold:
                    self._enhance_asset(job, session)
            
            # UE5 import if configured
            if session.config.auto_import_ue5 and job.output_files:
                self._import_to_ue5(job, session)
            
            job.status = BatchJobStatus.COMPLETED
            job.completion_time = time.time()
            
        except Exception as e:
            logger.error(f"Failed to process job {job.id}: {e}")
            job.status = BatchJobStatus.FAILED
            job.error_message = str(e)
            job.completion_time = time.time()
    
    def _generate_asset(self, job: BatchJob, session: BatchSession) -> bool:
        """Generate asset for the job"""
        try:
            asset_spec = job.asset_spec
            
            # Select workflow
            workflow_template = self.workflow_manager.select_workflow(asset_spec)
            if not workflow_template:
                logger.error(f"No compatible workflow found for {asset_spec.asset_type}")
                job.error_message = "No compatible workflow found"
                return False
            
            # Customize workflow
            workflow = self.workflow_manager.customize_workflow(workflow_template, asset_spec)
            if not workflow:
                logger.error(f"Failed to customize workflow for {asset_spec.name}")
                job.error_message = "Workflow customization failed"
                return False
            
            # Queue generation
            generation_job = self.comfyui_client.queue_prompt(workflow, job.id)
            job.generation_job = generation_job
            
            # Wait for completion
            completed_job = self.comfyui_client.wait_for_completion(
                generation_job,
                progress_callback=lambda job, elapsed, pos: self._update_job_progress(job, elapsed, pos)
            )
            
            if completed_job.status == GenerationStatus.COMPLETED:
                # Copy output files to batch output directory
                output_files = self._organize_output_files(completed_job, job, session)
                job.output_files = output_files
                return True
            else:
                job.error_message = completed_job.error or "Generation failed"
                return False
                
        except Exception as e:
            logger.error(f"Generation failed for job {job.id}: {e}")
            job.error_message = str(e)
            return False
    
    def _assess_quality(self, job: BatchJob, session: BatchSession):
        """Assess quality of generated asset"""
        try:
            if not job.output_files:
                return
            
            # Assess the first output file
            primary_output = job.output_files[0]
            result = self.qa_manager.process_asset(primary_output, job.asset_spec)
            
            job.quality_score = result["assessment"].metrics.overall_score
            job.metadata["quality_assessment"] = result
            job.status = BatchJobStatus.QUALITY_CHECK
            
            logger.info(f"Quality score for {job.id}: {job.quality_score:.1f}")
            
        except Exception as e:
            logger.warning(f"Quality assessment failed for job {job.id}: {e}")
            job.quality_score = 50.0  # Default score if assessment fails
    
    def _enhance_asset(self, job: BatchJob, session: BatchSession):
        """Enhance asset if quality is below threshold"""
        if job.enhancement_count >= session.config.max_enhancement_attempts:
            logger.warning(f"Max enhancement attempts reached for job {job.id}")
            return
        
        try:
            job.status = BatchJobStatus.ENHANCING
            job.enhancement_count += 1
            
            # Get quality assessment recommendations
            quality_result = job.metadata.get("quality_assessment", {})
            gate_decision = quality_result.get("gate_decision", {})
            required_enhancements = gate_decision.get("required_enhancements", [])
            
            if "upscale" in required_enhancements and job.output_files:
                enhanced_file = self._upscale_image(job.output_files[0], job, session)
                if enhanced_file:
                    job.output_files[0] = enhanced_file
                    
                    # Re-assess quality
                    self._assess_quality(job, session)
            
            logger.info(f"Enhanced job {job.id}, new quality score: {job.quality_score}")
            
        except Exception as e:
            logger.error(f"Enhancement failed for job {job.id}: {e}")
    
    def _upscale_image(self, image_path: Path, job: BatchJob, session: BatchSession) -> Optional[Path]:
        """Upscale image using available upscaler"""
        try:
            # This would interface with your existing upscaling tools
            # For now, return the original path as a placeholder
            logger.info(f"Upscaling {image_path} (placeholder implementation)")
            return image_path
            
        except Exception as e:
            logger.error(f"Upscaling failed for {image_path}: {e}")
            return None
    
    def _import_to_ue5(self, job: BatchJob, session: BatchSession):
        """Import asset to UE5"""
        try:
            # This would interface with your UE5 import tools
            logger.info(f"Importing {job.id} to UE5 (placeholder implementation)")
            job.metadata["ue5_imported"] = True
            
        except Exception as e:
            logger.error(f"UE5 import failed for job {job.id}: {e}")
            job.metadata["ue5_import_error"] = str(e)
    
    def _organize_output_files(self, generation_job: GenerationJob, batch_job: BatchJob, session: BatchSession) -> List[Path]:
        """Organize output files in batch directory structure"""
        output_files = []
        
        try:
            batch_output_dir = session.config.output_directory / session.session_id
            batch_output_dir.mkdir(parents=True, exist_ok=True)
            
            # Create asset-specific subdirectory
            asset_dir = batch_output_dir / f"{batch_job.asset_spec.faction}" / f"{batch_job.asset_spec.asset_type}"
            asset_dir.mkdir(parents=True, exist_ok=True)
            
            # Copy generated files
            for filename in generation_job.output_files:
                # Construct source path (this would depend on your ComfyUI setup)
                source_path = Path("C:/Users/Zachg/Documents/ComfyUI/output") / filename
                
                if source_path.exists():
                    # Create destination filename
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    dest_filename = f"{batch_job.asset_spec.name}_{timestamp}.png"
                    dest_path = asset_dir / dest_filename
                    
                    # Copy file
                    import shutil
                    shutil.copy2(source_path, dest_path)
                    output_files.append(dest_path)
                    
                    # Save metadata sidecar
                    metadata_path = dest_path.with_suffix('.json')
                    with open(metadata_path, 'w') as f:
                        json.dump({
                            "asset_spec": batch_job.asset_spec.to_dict(),
                            "generation_metadata": generation_job.metadata,
                            "batch_info": {
                                "session_id": session.session_id,
                                "job_id": batch_job.id,
                                "csv_row": batch_job.row_index
                            }
                        }, f, indent=2)
        
        except Exception as e:
            logger.error(f"Failed to organize output files for job {batch_job.id}: {e}")
        
        return output_files
    
    def _update_job_progress(self, generation_job: GenerationJob, elapsed: float, queue_position: int):
        """Update job progress callback"""
        # This could be used to update UI or progress indicators
        pass
    
    def _monitor_progress(self, session: BatchSession):
        """Monitor overall progress and provide updates"""
        start_time = time.time()
        
        while self.is_processing and not self.shutdown_event.is_set():
            try:
                # Calculate progress
                progress = session.progress_percentage
                elapsed = time.time() - start_time
                
                if session.total_jobs > 0:
                    completed = session.completed_jobs + session.failed_jobs + session.skipped_jobs
                    remaining = session.total_jobs - completed
                    
                    # Estimate completion time
                    if completed > 0:
                        avg_time_per_job = elapsed / completed
                        eta = remaining * avg_time_per_job
                        
                        logger.info(f"Batch progress: {progress:.1f}% ({completed}/{session.total_jobs}), ETA: {eta/60:.1f}min")
                
                time.sleep(10)  # Update every 10 seconds
                
            except Exception as e:
                logger.error(f"Progress monitoring error: {e}")
                break
    
    def _generate_session_report(self, session: BatchSession):
        """Generate comprehensive session report"""
        try:
            report = {
                "session_info": {
                    "session_id": session.session_id,
                    "csv_file": str(session.csv_file),
                    "start_time": session.start_time,
                    "completion_time": session.completion_time,
                    "duration_minutes": (session.completion_time - session.start_time) / 60 if session.completion_time else 0
                },
                "statistics": {
                    "total_jobs": session.total_jobs,
                    "completed_jobs": session.completed_jobs,
                    "failed_jobs": session.failed_jobs,
                    "skipped_jobs": session.skipped_jobs,
                    "success_rate": session.success_rate
                },
                "quality_metrics": self._calculate_session_quality_metrics(session),
                "performance_metrics": self._calculate_performance_metrics(session),
                "job_details": []
            }
            
            # Add job details
            for job in session.jobs:
                job_detail = {
                    "job_id": job.id,
                    "asset_name": job.asset_spec.name,
                    "asset_type": job.asset_spec.asset_type,
                    "faction": job.asset_spec.faction,
                    "status": job.status.value,
                    "quality_score": job.quality_score,
                    "enhancement_count": job.enhancement_count,
                    "processing_time": (job.completion_time - job.start_time) if job.completion_time and job.start_time else 0,
                    "output_files": [str(f) for f in job.output_files],
                    "error_message": job.error_message
                }
                report["job_details"].append(job_detail)
            
            # Save report
            report_path = session.config.output_directory / session.session_id / "batch_report.json"
            report_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(report_path, 'w') as f:
                json.dump(report, f, indent=2)
            
            logger.info(f"Session report saved: {report_path}")
            
        except Exception as e:
            logger.error(f"Failed to generate session report: {e}")
    
    def _calculate_session_quality_metrics(self, session: BatchSession) -> Dict[str, Any]:
        """Calculate quality metrics for the session"""
        quality_scores = [job.quality_score for job in session.jobs if job.quality_score is not None]
        
        if not quality_scores:
            return {"message": "No quality data available"}
        
        return {
            "average_quality": sum(quality_scores) / len(quality_scores),
            "min_quality": min(quality_scores),
            "max_quality": max(quality_scores),
            "quality_distribution": {
                "excellent": len([s for s in quality_scores if s >= 85]),
                "good": len([s for s in quality_scores if 75 <= s < 85]),
                "acceptable": len([s for s in quality_scores if 60 <= s < 75]),
                "poor": len([s for s in quality_scores if s < 60])
            }
        }
    
    def _calculate_performance_metrics(self, session: BatchSession) -> Dict[str, Any]:
        """Calculate performance metrics for the session"""
        processing_times = []
        enhancement_counts = []
        
        for job in session.jobs:
            if job.start_time and job.completion_time:
                processing_times.append(job.completion_time - job.start_time)
            enhancement_counts.append(job.enhancement_count)
        
        metrics = {
            "total_enhancements": sum(enhancement_counts),
            "avg_enhancements_per_job": sum(enhancement_counts) / len(enhancement_counts) if enhancement_counts else 0
        }
        
        if processing_times:
            metrics.update({
                "avg_processing_time": sum(processing_times) / len(processing_times),
                "min_processing_time": min(processing_times),
                "max_processing_time": max(processing_times)
            })
        
        return metrics
    
    def stop_processing(self):
        """Stop batch processing gracefully"""
        logger.info("Stopping batch processing...")
        self.shutdown_event.set()
        self.is_processing = False
    
    def get_session_status(self) -> Optional[Dict[str, Any]]:
        """Get current session status"""
        if not self.current_session:
            return None
        
        session = self.current_session
        return {
            "session_id": session.session_id,
            "progress_percentage": session.progress_percentage,
            "total_jobs": session.total_jobs,
            "completed_jobs": session.completed_jobs,
            "failed_jobs": session.failed_jobs,
            "skipped_jobs": session.skipped_jobs,
            "success_rate": session.success_rate,
            "is_complete": session.is_complete,
            "elapsed_time": time.time() - session.start_time
        }