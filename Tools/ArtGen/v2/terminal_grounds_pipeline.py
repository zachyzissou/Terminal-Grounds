#!/usr/bin/env python3
"""
Terminal Grounds Asset Pipeline v2.0
====================================
Unified command-line interface for the Terminal Grounds asset generation pipeline.

This is the single entry point that replaces all scattered scripts with a unified,
intelligent asset generation system.

Usage Examples:
    # Generate single asset
    python terminal_grounds_pipeline.py generate weapon "Plasma Rifle" --faction directorate
    
    # Process CSV batch
    python terminal_grounds_pipeline.py batch-csv data/weapons.csv --auto-import
    
    # Generate faction asset pack
    python terminal_grounds_pipeline.py faction-pack directorate --types weapon,vehicle --count 10
    
    # Interactive mode
    python terminal_grounds_pipeline.py interactive
    
    # System validation
    python terminal_grounds_pipeline.py validate
"""

import argparse
import logging
import sys
import time
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
import signal
from datetime import datetime

# Pipeline imports - handle both module and script execution
try:
    from .pipeline_controller import PipelineController, TaskPriority
    from .config_manager import ConfigManager
    from .asset_spec import AssetType, FactionCode
    from .batch_processor import BatchConfiguration
except ImportError:
    # Running as script, use absolute imports
    from pipeline_controller import PipelineController, TaskPriority
    from config_manager import ConfigManager
    from asset_spec import AssetType, FactionCode
    from batch_processor import BatchConfiguration

# Version info
__version__ = "2.0.0"
__author__ = "Terminal Grounds Development Team"

# Global pipeline controller
pipeline_controller: Optional[PipelineController] = None

def setup_logging(level: str = "INFO", file_logging: bool = False):
    """Setup logging configuration"""
    
    log_level = getattr(logging, level.upper(), logging.INFO)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    )
    console_handler.setFormatter(console_formatter)
    
    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.addHandler(console_handler)
    
    # File handler if requested
    if file_logging:
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        file_handler = logging.FileHandler(
            log_dir / f"pipeline_{datetime.now().strftime('%Y%m%d')}.log"
        )
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(file_formatter)
        root_logger.addHandler(file_handler)

def signal_handler(signum, frame):
    """Handle shutdown signals gracefully"""
    print("\n[SHUTDOWN] Shutdown signal received...")
    if pipeline_controller:
        pipeline_controller.shutdown()
    sys.exit(0)

def init_pipeline(config_path: Optional[Path] = None) -> PipelineController:
    """Initialize the pipeline controller"""
    global pipeline_controller
    
    try:
        print("[INIT] Initializing Terminal Grounds Pipeline v2.0...")
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        # Initialize controller
        pipeline_controller = PipelineController(config_path)
        
        print("[OK] Pipeline initialized successfully!")
        return pipeline_controller
        
    except Exception as e:
        print(f"[ERROR] Pipeline initialization failed: {e}")
        sys.exit(1)

def cmd_generate(args) -> int:
    """Generate single asset command"""
    
    controller = init_pipeline(args.config)
    
    try:
        print(f"\n[GEN] Generating {args.asset_type}: {args.name}")
        print(f"   Faction: {args.faction}")
        print(f"   Description: {args.description}")
        
        # Custom parameters
        custom_params = {}
        if args.style:
            custom_params["style"] = args.style
        if args.quality:
            custom_params["quality_level"] = args.quality
        if args.resolution:
            width, height = map(int, args.resolution.split('x'))
            custom_params["width"] = width
            custom_params["height"] = height
        
        # Generate asset
        task_id = controller.generate_asset(
            name=args.name,
            asset_type=args.asset_type,
            faction=args.faction,
            description=args.description,
            custom_params=custom_params if custom_params else None,
            priority=TaskPriority.HIGH if args.priority == "high" else TaskPriority.NORMAL
        )
        
        print(f"[STATUS] Task queued: {task_id}")
        
        if not args.async_mode:
            # Wait for completion
            print("[WAIT] Waiting for generation...")
            wait_for_task_completion(controller, task_id)
        
        return 0
        
    except Exception as e:
        print(f"[ERROR] Generation failed: {e}")
        return 1
    finally:
        if not args.async_mode:
            controller.shutdown()

def cmd_batch_csv(args) -> int:
    """Process CSV batch command"""
    
    controller = init_pipeline(args.config)
    
    try:
        csv_file = Path(args.csv_file)
        if not csv_file.exists():
            print(f"[ERROR] CSV file not found: {csv_file}")
            return 1
        
        print(f"\n[BATCH] Processing batch CSV: {csv_file}")
        
        # Batch configuration
        batch_config = {}
        if args.max_concurrent:
            batch_config["max_concurrent_jobs"] = args.max_concurrent
        if args.quality_threshold:
            batch_config["quality_threshold"] = args.quality_threshold
        if args.auto_enhance is not None:
            batch_config["auto_enhance"] = args.auto_enhance
        if args.auto_import:
            batch_config["auto_import_ue5"] = args.auto_import
        
        # Progress callback
        def progress_callback(session, job):
            completed = session.completed_jobs + session.failed_jobs + session.skipped_jobs
            print(f"[PROGRESS] Progress: {completed}/{session.total_jobs} ({session.progress_percentage:.1f}%)")
        
        # Start batch processing
        task_id = controller.process_batch_csv(
            csv_file=csv_file,
            config=batch_config,
            priority=TaskPriority.HIGH,
            callback=progress_callback if not args.async_mode else None
        )
        
        print(f"[STATUS] Batch task queued: {task_id}")
        
        if not args.async_mode:
            # Wait for completion
            print("[WAIT] Processing batch...")
            result = wait_for_task_completion(controller, task_id)
            
            if result and result.get("result"):
                batch_result = result["result"]
                print(f"\n[BATCH] Batch Results:")
                print(f"   Total jobs: {batch_result['total_jobs']}")
                print(f"   Completed: {batch_result['completed_jobs']}")
                print(f"   Failed: {batch_result['failed_jobs']}")
                print(f"   Success rate: {batch_result['success_rate']:.1f}%")
        
        return 0
        
    except Exception as e:
        print(f"[ERROR] Batch processing failed: {e}")
        return 1
    finally:
        if not args.async_mode:
            controller.shutdown()

def cmd_faction_pack(args) -> int:
    """Generate faction asset pack command"""
    
    controller = init_pipeline(args.config)
    
    try:
        print(f"\n[FACTION] Generating {args.faction} faction pack")
        print(f"   Asset types: {', '.join(args.types)}")
        print(f"   Count per type: {args.count}")
        
        # Create temporary CSV for batch processing
        import tempfile
        import csv
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            writer = csv.writer(f)
            writer.writerow(['name', 'asset_type', 'faction', 'description'])
            
            for asset_type in args.types:
                for i in range(args.count):
                    name = f"{args.faction.title()}_{asset_type.title()}_{i+1:03d}"
                    description = f"Generated {asset_type} for {args.faction} faction"
                    writer.writerow([name, asset_type, args.faction, description])
            
            temp_csv = Path(f.name)
        
        # Process the temporary CSV
        task_id = controller.process_batch_csv(
            csv_file=temp_csv,
            config={"auto_import_ue5": args.auto_import},
            priority=TaskPriority.HIGH
        )
        
        print(f"[STATUS] Faction pack task queued: {task_id}")
        
        if not args.async_mode:
            print("[WAIT] Generating faction pack...")
            result = wait_for_task_completion(controller, task_id)
            
            # Cleanup temp file
            temp_csv.unlink(missing_ok=True)
            
            if result and result.get("result"):
                batch_result = result["result"]
                print(f"\n[FACTION] Faction Pack Results:")
                print(f"   Assets generated: {batch_result['completed_jobs']}")
                print(f"   Success rate: {batch_result['success_rate']:.1f}%")
        
        return 0
        
    except Exception as e:
        print(f"[ERROR] Faction pack generation failed: {e}")
        return 1
    finally:
        if not args.async_mode:
            controller.shutdown()

def cmd_enhance(args) -> int:
    """Enhance existing asset command"""
    
    controller = init_pipeline(args.config)
    
    try:
        print(f"\n[ENHANCE] Enhancing asset: {args.asset_id}")
        print(f"   Enhancements: {', '.join(args.enhancements)}")
        
        task_id = controller.enhance_asset(
            asset_id=args.asset_id,
            enhancement_types=args.enhancements,
            priority=TaskPriority.HIGH if args.priority == "high" else TaskPriority.NORMAL
        )
        
        print(f"[STATUS] Enhancement task queued: {task_id}")
        
        if not args.async_mode:
            print("[WAIT] Applying enhancements...")
            wait_for_task_completion(controller, task_id)
        
        return 0
        
    except Exception as e:
        print(f"[ERROR] Enhancement failed: {e}")
        return 1
    finally:
        if not args.async_mode:
            controller.shutdown()

def cmd_import_ue5(args) -> int:
    """Import assets to UE5 command"""
    
    controller = init_pipeline(args.config)
    
    try:
        print(f"\n[UE5] Importing {len(args.asset_ids)} assets to UE5")
        
        task_id = controller.import_to_ue5(
            asset_ids=args.asset_ids,
            create_materials=args.create_materials,
            priority=TaskPriority.HIGH
        )
        
        print(f"[STATUS] Import task queued: {task_id}")
        
        if not args.async_mode:
            print("[WAIT] Importing to UE5...")
            result = wait_for_task_completion(controller, task_id)
            
            if result and result.get("result"):
                import_result = result["result"]
                print(f"[UE5] Import completed: {import_result['imported_assets']} assets")
        
        return 0
        
    except Exception as e:
        print(f"[ERROR] UE5 import failed: {e}")
        return 1
    finally:
        if not args.async_mode:
            controller.shutdown()

def cmd_search(args) -> int:
    """Search assets command"""
    
    controller = init_pipeline(args.config)
    
    try:
        print(f"\n[SEARCH] Searching assets...")
        
        # Build search filters
        search_filters = {}
        if args.asset_type:
            search_filters["asset_type"] = args.asset_type
        if args.faction:
            search_filters["faction"] = args.faction
        if args.min_quality:
            search_filters["min_quality"] = args.min_quality
        if args.tags:
            search_filters["tags"] = args.tags.split(",")
        if args.name:
            search_filters["name_pattern"] = args.name
        
        # Search assets
        assets = controller.asset_manager.search_assets(**search_filters)
        
        print(f"[STATUS] Found {len(assets)} assets:")
        for asset in assets[:args.limit]:
            print(f"   {asset.asset_id}: {asset.asset_spec.name} ({asset.asset_spec.asset_type}, {asset.asset_spec.faction})")
            if asset.quality_score:
                print(f"      Quality: {asset.quality_score:.1f}")
        
        if len(assets) > args.limit:
            print(f"   ... and {len(assets) - args.limit} more")
        
        return 0
        
    except Exception as e:
        print(f"[ERROR] Search failed: {e}")
        return 1
    finally:
        controller.shutdown()

def cmd_status(args) -> int:
    """Show pipeline status command"""
    
    if args.task_id:
        # Show specific task status
        controller = init_pipeline(args.config)
        try:
            status = controller.get_task_status(args.task_id)
            if status:
                print(f"\n[STATUS] Task Status: {args.task_id}")
                print(f"   Type: {status['task_type']}")
                print(f"   Status: {status['status']}")
                print(f"   Progress: {status['progress']:.1f}%")
                if status.get('error'):
                    print(f"   Error: {status['error']}")
            else:
                print(f"[ERROR] Task not found: {args.task_id}")
                return 1
        finally:
            controller.shutdown()
    else:
        # Show overall pipeline status
        controller = init_pipeline(args.config)
        try:
            status = controller.get_pipeline_status()
            print(f"\n[INIT] Pipeline Status")
            print(f"   Status: {status['status']}")
            print(f"   Uptime: {status['uptime_seconds']:.0f}s")
            print(f"   Queue: {status['queue_size']} tasks")
            print(f"   Active: {status['active_tasks']} tasks")
            print(f"   Completed: {status['completed_tasks']} tasks")
            
            metrics = status['metrics']
            if metrics['total_tasks_processed'] > 0:
                print(f"   Success rate: {metrics['success_rate']:.1f}%")
            
            print(f"\n[HEALTH] Component Health:")
            for component, health in status['component_health'].items():
                emoji = "[OK]" if health == "healthy" else "[ERROR]" if health == "unhealthy" else "[INFO]"
                print(f"   {emoji} {component}: {health}")
        finally:
            controller.shutdown()
    
    return 0

def cmd_validate(args) -> int:
    """Validate pipeline command"""
    
    controller = init_pipeline(args.config)
    
    try:
        print("\n[SEARCH] Validating pipeline...")
        
        validation = controller.validate_pipeline()
        
        if validation["is_healthy"]:
            print("[OK] Pipeline validation passed!")
        else:
            print("[ERROR] Pipeline validation failed!")
            
        if validation["errors"]:
            print("\n[ERROR] Errors:")
            for error in validation["errors"]:
                print(f"   • {error}")
        
        if validation["warnings"]:
            print("\n[WARN] Warnings:")
            for warning in validation["warnings"]:
                print(f"   • {warning}")
        
        print("\n[HEALTH] Component Status:")
        for component, status in validation["component_status"].items():
            emoji = "[OK]" if status == "healthy" else "[ERROR]" if status == "error" else "[WARN]" if status == "issues" else "[INFO]"
            print(f"   {emoji} {component}: {status}")
        
        return 0 if validation["is_healthy"] else 1
        
    except Exception as e:
        print(f"[ERROR] Validation failed: {e}")
        return 1
    finally:
        controller.shutdown()

def cmd_interactive(args) -> int:
    """Interactive mode command"""
    
    controller = init_pipeline(args.config)
    
    try:
        print("\n[INTER] Terminal Grounds Pipeline - Interactive Mode")
        print("Type 'help' for commands, 'quit' to exit")
        
        while True:
            try:
                command = input("\nTG> ").strip()
                
                if command in ["quit", "exit", "q"]:
                    break
                elif command == "help":
                    show_interactive_help()
                elif command == "status":
                    status = controller.get_pipeline_status()
                    print(f"Status: {status['status']}, Queue: {status['queue_size']}, Active: {status['active_tasks']}")
                elif command.startswith("generate "):
                    handle_interactive_generate(controller, command)
                elif command.startswith("search "):
                    handle_interactive_search(controller, command)
                elif command == "":
                    continue
                else:
                    print("Unknown command. Type 'help' for available commands.")
                    
            except KeyboardInterrupt:
                print("\nUse 'quit' to exit.")
            except EOFError:
                break
        
        print("\n[BYE] Goodbye!")
        return 0
        
    except Exception as e:
        print(f"[ERROR] Interactive mode failed: {e}")
        return 1
    finally:
        controller.shutdown()

def show_interactive_help():
    """Show interactive mode help"""
    print("""
Available commands:
  generate <type> <name> [faction]  - Generate an asset
  search [filters]                  - Search existing assets
  status                           - Show pipeline status
  help                             - Show this help
  quit                             - Exit interactive mode

Examples:
  generate weapon "Plasma Rifle" directorate
  search type:weapon faction:free77
  status
""")

def handle_interactive_generate(controller, command):
    """Handle interactive generate command"""
    try:
        parts = command.split()[1:]  # Skip 'generate'
        if len(parts) < 2:
            print("Usage: generate <type> <name> [faction]")
            return
        
        asset_type = parts[0]
        name = parts[1].strip('"')
        faction = parts[2] if len(parts) > 2 else "neutral"
        
        task_id = controller.generate_asset(
            name=name,
            asset_type=asset_type,
            faction=faction,
            description=f"Interactively generated {asset_type}"
        )
        
        print(f"Task queued: {task_id}")
        
    except Exception as e:
        print(f"Generation failed: {e}")

def handle_interactive_search(controller, command):
    """Handle interactive search command"""
    try:
        # Simple search implementation
        assets = controller.asset_manager.search_assets(limit=10)
        print(f"Found {len(assets)} recent assets:")
        for asset in assets:
            print(f"  {asset.asset_spec.name} ({asset.asset_spec.asset_type}, {asset.asset_spec.faction})")
    except Exception as e:
        print(f"Search failed: {e}")

def wait_for_task_completion(controller: PipelineController, task_id: str, timeout: int = 300) -> Optional[Dict[str, Any]]:
    """Wait for task completion with progress updates"""
    
    start_time = time.time()
    last_progress = -1
    
    while time.time() - start_time < timeout:
        status = controller.get_task_status(task_id)
        
        if not status:
            print("[ERROR] Task not found")
            return None
        
        # Show progress updates
        if status["progress"] != last_progress:
            print(f"[PROGRESS] Progress: {status['progress']:.1f}%")
            last_progress = status["progress"]
        
        # Check if complete
        if status["is_complete"]:
            if status["status"] == "completed":
                print("[OK] Task completed successfully!")
                return status
            else:
                print(f"[ERROR] Task failed: {status.get('error', 'Unknown error')}")
                return status
        
        time.sleep(2)
    
    print("[TIMEOUT] Task timeout")
    return None

def create_parser() -> argparse.ArgumentParser:
    """Create command line argument parser"""
    
    parser = argparse.ArgumentParser(
        description="Terminal Grounds Asset Pipeline v2.0",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s generate weapon "Plasma Rifle" --faction directorate
  %(prog)s batch-csv data/weapons.csv --auto-import
  %(prog)s faction-pack free77 --types weapon,vehicle --count 5
  %(prog)s validate
  %(prog)s interactive
        """
    )
    
    # Global arguments
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument("--config", type=Path, help="Configuration file path")
    parser.add_argument("--log-level", choices=["DEBUG", "INFO", "WARNING", "ERROR"], 
                       default="INFO", help="Logging level")
    parser.add_argument("--log-file", action="store_true", help="Enable file logging")
    parser.add_argument("--async", dest="async_mode", action="store_true", 
                       help="Run in async mode (don't wait for completion)")
    
    # Subcommands
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Generate command
    gen_parser = subparsers.add_parser("generate", help="Generate single asset")
    gen_parser.add_argument("asset_type", choices=["weapon", "vehicle", "emblem", "poster", "icon", "concept", "environment", "texture", "ui"])
    gen_parser.add_argument("name", help="Asset name")
    gen_parser.add_argument("--faction", choices=["directorate", "free77", "vultures", "combine", "nomads", "archivists", "wardens", "neutral"], default="neutral")
    gen_parser.add_argument("--description", help="Asset description")
    gen_parser.add_argument("--style", help="Additional style keywords")
    gen_parser.add_argument("--quality", choices=["draft", "production", "hero"], default="production")
    gen_parser.add_argument("--resolution", help="Resolution (e.g., 1024x1024)")
    gen_parser.add_argument("--priority", choices=["normal", "high"], default="normal")
    
    # Batch CSV command
    batch_parser = subparsers.add_parser("batch-csv", help="Process CSV batch")
    batch_parser.add_argument("csv_file", help="CSV file path")
    batch_parser.add_argument("--max-concurrent", type=int, help="Max concurrent jobs")
    batch_parser.add_argument("--quality-threshold", type=float, help="Quality threshold")
    batch_parser.add_argument("--auto-enhance", action="store_true", help="Enable auto enhancement")
    batch_parser.add_argument("--no-auto-enhance", dest="auto_enhance", action="store_false", help="Disable auto enhancement")
    batch_parser.add_argument("--auto-import", action="store_true", help="Auto import to UE5")
    
    # Faction pack command
    faction_parser = subparsers.add_parser("faction-pack", help="Generate faction asset pack")
    faction_parser.add_argument("faction", choices=["directorate", "free77", "vultures", "combine", "nomads", "archivists", "wardens"])
    faction_parser.add_argument("--types", required=True, help="Asset types (comma-separated)")
    faction_parser.add_argument("--count", type=int, default=5, help="Assets per type")
    faction_parser.add_argument("--auto-import", action="store_true", help="Auto import to UE5")
    
    # Enhance command
    enhance_parser = subparsers.add_parser("enhance", help="Enhance existing asset")
    enhance_parser.add_argument("asset_id", help="Asset ID to enhance")
    enhance_parser.add_argument("--enhancements", required=True, help="Enhancement types (comma-separated)")
    enhance_parser.add_argument("--priority", choices=["normal", "high"], default="normal")
    
    # Import UE5 command
    import_parser = subparsers.add_parser("import-ue5", help="Import assets to UE5")
    import_parser.add_argument("asset_ids", nargs="+", help="Asset IDs to import")
    import_parser.add_argument("--no-materials", dest="create_materials", action="store_false", help="Don't create materials")
    
    # Search command
    search_parser = subparsers.add_parser("search", help="Search assets")
    search_parser.add_argument("--asset-type", help="Filter by asset type")
    search_parser.add_argument("--faction", help="Filter by faction")
    search_parser.add_argument("--min-quality", type=float, help="Minimum quality score")
    search_parser.add_argument("--tags", help="Filter by tags (comma-separated)")
    search_parser.add_argument("--name", help="Filter by name pattern")
    search_parser.add_argument("--limit", type=int, default=20, help="Max results")
    
    # Status command
    status_parser = subparsers.add_parser("status", help="Show status")
    status_parser.add_argument("task_id", nargs="?", help="Specific task ID")
    
    # Validate command
    subparsers.add_parser("validate", help="Validate pipeline")
    
    # Interactive command
    subparsers.add_parser("interactive", help="Interactive mode")
    
    return parser

def main() -> int:
    """Main entry point"""
    
    parser = create_parser()
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.log_level, args.log_file)
    
    # Handle missing command
    if not args.command:
        parser.print_help()
        return 1
    
    # Parse faction pack types
    if args.command == "faction-pack":
        args.types = [t.strip() for t in args.types.split(",")]
    
    # Parse enhancement types
    if args.command == "enhance":
        args.enhancements = [e.strip() for e in args.enhancements.split(",")]
    
    # Route to command handlers
    command_handlers = {
        "generate": cmd_generate,
        "batch-csv": cmd_batch_csv,
        "faction-pack": cmd_faction_pack,
        "enhance": cmd_enhance,
        "import-ue5": cmd_import_ue5,
        "search": cmd_search,
        "status": cmd_status,
        "validate": cmd_validate,
        "interactive": cmd_interactive
    }
    
    handler = command_handlers.get(args.command)
    if handler:
        return handler(args)
    else:
        print(f"[ERROR] Unknown command: {args.command}")
        return 1

if __name__ == "__main__":
    sys.exit(main())