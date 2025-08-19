#!/usr/bin/env python3
"""
Terminal Grounds Asset Generation Pipeline v2.0
==============================================

The new unified entry point for all Terminal Grounds asset generation.
This script replaces the scattered approach with a professional, integrated pipeline.

Usage Examples:
    # Generate a single weapon
    python terminal_grounds_pipeline.py generate weapon "Plasma Rifle" --faction directorate
    
    # Generate from CSV
    python terminal_grounds_pipeline.py batch-csv Data/Tables/Weapons.csv --type weapon
    
    # Generate faction assets
    python terminal_grounds_pipeline.py faction-assets directorate --types weapon,vehicle --count 5
    
    # Validate pipeline
    python terminal_grounds_pipeline.py validate
    
    # Interactive mode
    python terminal_grounds_pipeline.py interactive
"""

import argparse
import json
import pathlib
import sys
from typing import Any, Dict, List, Optional

# Add pipeline to path
sys.path.insert(0, str(pathlib.Path(__file__).parent))

from pipeline import PipelineController, AssetSpecification
from pipeline.utils import PipelineConfig, setup_logger


def setup_logging(args):
    """Setup logging based on command line arguments."""
    log_level = "DEBUG" if args.verbose else "INFO"
    log_file = None
    
    if args.log_file:
        log_file = pathlib.Path(args.log_file)
    
    return setup_logger("TerminalGroundsPipeline", log_level, log_file)


def generate_single_asset(args, controller: PipelineController, logger):
    """Generate a single asset."""
    logger.info(f"Generating {args.asset_type}: {args.name}")
    
    # Create asset specification
    spec = AssetSpecification.create_quick(
        asset_type=args.asset_type,
        name=args.name,
        faction=args.faction,
        category=args.category or "generated",
        auto_import_ue5=args.import_ue5
    )
    
    # Override settings if provided
    if args.width or args.height:
        spec.render_settings.width = args.width or spec.render_settings.width
        spec.render_settings.height = args.height or spec.render_settings.height
    
    if args.steps:
        spec.render_settings.steps = args.steps
    
    if args.cfg:
        spec.render_settings.cfg = args.cfg
    
    if args.seed:
        spec.render_settings.seed = args.seed
    
    # Generate asset
    try:
        result = controller.generate_single_asset(spec)
        
        logger.info("Generation completed successfully!")
        
        if args.output_json:
            output_path = pathlib.Path(args.output_json)
            output_path.write_text(json.dumps(result, indent=2, default=str))
            logger.info(f"Results saved to: {output_path}")
        
        # Print summary
        print(f"\\nGeneration Summary:")
        print(f"Asset: {args.name}")
        print(f"Type: {args.asset_type}")
        print(f"Faction: {args.faction or 'neutral'}")
        
        if "organized_files" in result:
            print(f"Files generated: {len(result['organized_files'])}")
            for file_info in result["organized_files"]:
                print(f"  - {file_info['organized_filename']}")
        
        if "ue5_import" in result:
            ue5_result = result["ue5_import"]
            imported_count = ue5_result.get("total_imported", 0)
            print(f"UE5 Import: {imported_count} assets imported")
        
    except Exception as e:
        logger.error(f"Generation failed: {e}")
        sys.exit(1)


def generate_batch_csv(args, controller: PipelineController, logger):
    """Generate assets from CSV file."""
    csv_path = pathlib.Path(args.csv_file)
    
    if not csv_path.exists():
        logger.error(f"CSV file not found: {csv_path}")
        sys.exit(1)
    
    logger.info(f"Processing CSV batch: {csv_path}")
    
    # Create template specification
    template_spec = AssetSpecification.create_quick(
        asset_type=args.type or "weapon",
        name="Template",
        faction="neutral",
        auto_import_ue5=args.import_ue5
    )
    
    # Process batch
    def progress_callback(progress_info):
        percent = progress_info["progress_percent"]
        completed = progress_info["completed_jobs"]
        total = progress_info["total_jobs"]
        print(f"\\rProgress: {percent:.1f}% ({completed}/{total})", end="", flush=True)
    
    try:
        result = controller.generate_from_csv(csv_path, template_spec, progress_callback)
        
        print()  # New line after progress
        logger.info("Batch generation completed!")
        
        # Print summary
        summary = result["batch_summary"]
        print(f"\\nBatch Summary:")
        print(f"Total jobs: {summary['total_jobs']}")
        print(f"Successful: {summary['successful_jobs']}")
        print(f"Failed: {summary['failed_jobs']}")
        print(f"Success rate: {summary['success_rate']:.1f}%")
        print(f"Total time: {summary['total_execution_time']:.1f}s")
        print(f"Average quality: {summary['average_quality_score']:.1f}")
        
        if args.output_json:
            output_path = pathlib.Path(args.output_json)
            output_path.write_text(json.dumps(result, indent=2, default=str))
            logger.info(f"Results saved to: {output_path}")
        
    except Exception as e:
        logger.error(f"Batch generation failed: {e}")
        sys.exit(1)


def generate_faction_assets(args, controller: PipelineController, logger):
    """Generate a complete set of assets for a faction."""
    logger.info(f"Generating faction assets for: {args.faction}")
    
    asset_types = args.types.split(",") if args.types else ["weapon", "vehicle"]
    count_per_type = args.count or 5
    
    try:
        result = controller.create_faction_assets(
            args.faction, asset_types, count_per_type
        )
        
        logger.info("Faction asset generation completed!")
        
        # Print summary
        summary = result["batch_summary"]
        print(f"\\nFaction Asset Summary:")
        print(f"Faction: {args.faction}")
        print(f"Asset types: {', '.join(asset_types)}")
        print(f"Count per type: {count_per_type}")
        print(f"Total generated: {summary['successful_jobs']}")
        print(f"Success rate: {summary['success_rate']:.1f}%")
        
        if args.output_json:
            output_path = pathlib.Path(args.output_json)
            output_path.write_text(json.dumps(result, indent=2, default=str))
            logger.info(f"Results saved to: {output_path}")
        
    except Exception as e:
        logger.error(f"Faction asset generation failed: {e}")
        sys.exit(1)


def validate_pipeline(args, controller: PipelineController, logger):
    """Validate the pipeline configuration and connections."""
    logger.info("Running pipeline validation...")
    
    try:
        validation_result = controller.validate_pipeline()
        
        print("\\nPipeline Validation Results:")
        print("=" * 40)
        
        # Overall status
        status = validation_result["overall_status"]
        print(f"Overall Status: {status}")
        
        # Individual checks
        checks = [
            ("ComfyUI Connection", validation_result["comfyui_connection"]),
            ("Workflows Valid", validation_result["workflows_valid"]),
            ("Faction Configs", validation_result["faction_configs"]),
            ("Output Directories", validation_result["output_directories"]),
            ("UE5 Connection", validation_result["ue5_connection"])
        ]
        
        for check_name, passed in checks:
            status_icon = "✓" if passed else "✗"
            print(f"{status_icon} {check_name}")
        
        # Errors and warnings
        if validation_result["errors"]:
            print("\\nErrors:")
            for error in validation_result["errors"]:
                print(f"  - {error}")
        
        if validation_result["warnings"]:
            print("\\nWarnings:")
            for warning in validation_result["warnings"]:
                print(f"  - {warning}")
        
        if args.output_json:
            output_path = pathlib.Path(args.output_json)
            output_path.write_text(json.dumps(validation_result, indent=2))
            logger.info(f"Validation results saved to: {output_path}")
        
        # Exit with error code if validation failed
        if validation_result["overall_status"] != "PASS":
            sys.exit(1)
        
    except Exception as e:
        logger.error(f"Validation failed: {e}")
        sys.exit(1)


def interactive_mode(controller: PipelineController, logger):
    """Run in interactive mode."""
    print("\\nTerminal Grounds Asset Pipeline v2.0 - Interactive Mode")
    print("=" * 60)
    
    while True:
        print("\\nAvailable commands:")
        print("1. Generate single asset")
        print("2. Generate faction batch")
        print("3. Validate pipeline")
        print("4. Show pipeline status")
        print("5. Exit")
        
        try:
            choice = input("\\nSelect an option (1-5): ").strip()
            
            if choice == "1":
                # Interactive single asset generation
                asset_type = input("Asset type (weapon/vehicle/gear/etc.): ").strip()
                name = input("Asset name: ").strip()
                faction = input("Faction (or press Enter for neutral): ").strip() or "neutral"
                
                if asset_type and name:
                    spec = AssetSpecification.create_quick(asset_type, name, faction)
                    result = controller.generate_single_asset(spec)
                    print(f"\\nGenerated successfully! Files: {len(result.get('organized_files', []))}")
                else:
                    print("Asset type and name are required!")
            
            elif choice == "2":
                # Interactive faction batch
                faction = input("Faction name: ").strip()
                types_input = input("Asset types (comma-separated): ").strip()
                count_input = input("Count per type (default 3): ").strip()
                
                if faction and types_input:
                    asset_types = [t.strip() for t in types_input.split(",")]
                    count = int(count_input) if count_input else 3
                    
                    result = controller.create_faction_assets(faction, asset_types, count)
                    summary = result["batch_summary"]
                    print(f"\\nGenerated {summary['successful_jobs']} assets successfully!")
                else:
                    print("Faction and asset types are required!")
            
            elif choice == "3":
                # Validate pipeline
                validation_result = controller.validate_pipeline()
                status = validation_result["overall_status"]
                print(f"\\nValidation Status: {status}")
                
                if validation_result["errors"]:
                    print("Errors found:")
                    for error in validation_result["errors"]:
                        print(f"  - {error}")
            
            elif choice == "4":
                # Show status
                status = controller.get_status()
                print(f"\\nPipeline Status:")
                print(f"Version: {status['version']}")
                print(f"Timestamp: {status['timestamp']}")
                
                for component, component_status in status.items():
                    if isinstance(component_status, dict) and component != "version":
                        print(f"{component}: Online")
            
            elif choice == "5":
                print("Goodbye!")
                break
            
            else:
                print("Invalid choice. Please select 1-5.")
        
        except KeyboardInterrupt:
            print("\\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Terminal Grounds Asset Generation Pipeline v2.0",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    # Global options
    parser.add_argument("--config", type=str, help="Configuration file path")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose logging")
    parser.add_argument("--log-file", type=str, help="Log file path")
    parser.add_argument("--output-json", type=str, help="Save results to JSON file")
    
    # Subcommands
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Generate single asset
    generate_parser = subparsers.add_parser("generate", help="Generate a single asset")
    generate_parser.add_argument("asset_type", help="Asset type (weapon, vehicle, etc.)")
    generate_parser.add_argument("name", help="Asset name")
    generate_parser.add_argument("--faction", default="neutral", help="Faction affiliation")
    generate_parser.add_argument("--category", help="Asset category")
    generate_parser.add_argument("--width", type=int, help="Image width")
    generate_parser.add_argument("--height", type=int, help="Image height")
    generate_parser.add_argument("--steps", type=int, help="Generation steps")
    generate_parser.add_argument("--cfg", type=float, help="CFG scale")
    generate_parser.add_argument("--seed", type=int, help="Random seed")
    generate_parser.add_argument("--import-ue5", action="store_true", help="Auto-import to UE5")
    
    # Batch CSV generation
    csv_parser = subparsers.add_parser("batch-csv", help="Generate from CSV file")
    csv_parser.add_argument("csv_file", help="CSV file path")
    csv_parser.add_argument("--type", help="Asset type for template")
    csv_parser.add_argument("--import-ue5", action="store_true", help="Auto-import to UE5")
    
    # Faction assets
    faction_parser = subparsers.add_parser("faction-assets", help="Generate faction asset set")
    faction_parser.add_argument("faction", help="Faction name")
    faction_parser.add_argument("--types", default="weapon,vehicle", help="Asset types (comma-separated)")
    faction_parser.add_argument("--count", type=int, default=5, help="Count per type")
    faction_parser.add_argument("--import-ue5", action="store_true", help="Auto-import to UE5")
    
    # Validation
    validate_parser = subparsers.add_parser("validate", help="Validate pipeline")
    
    # Interactive mode
    interactive_parser = subparsers.add_parser("interactive", help="Interactive mode")
    
    # Status
    status_parser = subparsers.add_parser("status", help="Show pipeline status")
    
    args = parser.parse_args()
    
    # Setup logging
    logger = setup_logging(args)
    
    # Load configuration
    config_path = pathlib.Path(args.config) if args.config else None
    config = PipelineConfig(config_path)
    
    # Initialize pipeline controller
    try:
        controller = PipelineController(config)
        logger.info("Pipeline controller initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize pipeline controller: {e}")
        sys.exit(1)
    
    # Execute command
    try:
        if args.command == "generate":
            generate_single_asset(args, controller, logger)
        
        elif args.command == "batch-csv":
            generate_batch_csv(args, controller, logger)
        
        elif args.command == "faction-assets":
            generate_faction_assets(args, controller, logger)
        
        elif args.command == "validate":
            validate_pipeline(args, controller, logger)
        
        elif args.command == "interactive":
            interactive_mode(controller, logger)
        
        elif args.command == "status":
            status = controller.get_status()
            print(json.dumps(status, indent=2, default=str))
        
        else:
            # No command specified, show help
            parser.print_help()
            
            # Ask if user wants interactive mode
            response = input("\\nWould you like to enter interactive mode? (y/n): ")
            if response.lower().startswith('y'):
                interactive_mode(controller, logger)
    
    except KeyboardInterrupt:
        logger.info("Operation cancelled by user")
        sys.exit(1)
    
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)
    
    finally:
        # Cleanup
        controller.shutdown()


if __name__ == "__main__":
    main()