#!/usr/bin/env python3
"""
Dead Sky Region Builder - Complete Production Pipeline
Orchestrates the full Terminal Grounds region creation workflow
"""

import asyncio
import sys
import logging
import json
import time
from pathlib import Path
from typing import Dict, Any, Optional

# Import our components
try:
    from dead_sky_working_prototype import DeadSkyRegionBuilderPrototype
    from download_flux_models import FLUXModelDownloader
except ImportError as e:
    print(f"❌ Missing dependencies: {e}")
    print("Please ensure all required scripts are in the same directory")
    sys.exit(1)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DeadSkyProductionPipeline:
    """Complete production pipeline for Dead Sky region creation"""

    def __init__(self):
        self.start_time = time.time()
        self.pipeline_results = {
            "pipeline_id": f"deadsky_production_{int(self.start_time)}",
            "status": "initializing",
            "stages": {},
            "final_metrics": {}
        }

    async def stage_1_infrastructure_setup(self) -> Dict[str, Any]:
        """Stage 1: Complete infrastructure setup and verification"""
        logger.info("🔧 STAGE 1: Infrastructure Setup")
        logger.info("=" * 50)

        stage_results = {
            "stage": "infrastructure_setup",
            "status": "in_progress",
            "components": {}
        }

        # Initialize prototype builder for infrastructure verification
        prototype_builder = DeadSkyRegionBuilderPrototype()
        infrastructure = await prototype_builder.verify_infrastructure()
        stage_results["components"]["infrastructure"] = infrastructure

        # Check ComfyUI model status
        model_downloader = FLUXModelDownloader()
        existing_models = model_downloader.check_existing_models()
        models_complete = all(existing_models.values())

        stage_results["components"]["models"] = {
            "existing_models": existing_models,
            "complete": models_complete,
            "missing_count": sum(1 for exists in existing_models.values() if not exists)
        }

        logger.info(f"MCP Servers: {len(infrastructure['mcp_servers'])} operational")
        logger.info(f"ComfyUI: {infrastructure['comfyui']['status']}")
        logger.info(f"Unreal Engine: {infrastructure['unreal_engine']['status']}")
        logger.info(f"FLUX Models: {'✅ Complete' if models_complete else '❌ Incomplete'}")

        stage_results["status"] = "completed"
        return stage_results

    async def stage_2_model_preparation(self, force_download: bool = False) -> Dict[str, Any]:
        """Stage 2: Download and verify FLUX models"""
        logger.info("📦 STAGE 2: Model Preparation")
        logger.info("=" * 50)

        stage_results = {
            "stage": "model_preparation",
            "status": "in_progress",
            "download_results": {}
        }

        model_downloader = FLUXModelDownloader()

        # Check if models already exist
        existing_models = model_downloader.check_existing_models()
        if all(existing_models.values()) and not force_download:
            logger.info("✅ All FLUX models already present, skipping download")
            stage_results["download_results"] = {
                "success": True,
                "downloaded": [],
                "skipped": list(existing_models.keys()),
                "failed": [],
                "total_size_gb": 0
            }
        else:
            logger.info("Downloading required FLUX models...")
            download_results = model_downloader.download_all_models(force_download)
            stage_results["download_results"] = download_results

            if not download_results["success"]:
                stage_results["status"] = "failed"
                return stage_results

        # Verify installation
        verification_success = model_downloader.verify_installation()
        stage_results["verification_success"] = verification_success

        if verification_success:
            logger.info("🎉 FLUX models ready for production!")
            stage_results["status"] = "completed"
        else:
            logger.error("❌ Model verification failed")
            stage_results["status"] = "failed"

        return stage_results

    async def stage_3_region_generation(self) -> Dict[str, Any]:
        """Stage 3: Execute complete Dead Sky region generation"""
        logger.info("🎨 STAGE 3: Region Generation")
        logger.info("=" * 50)

        stage_results = {
            "stage": "region_generation",
            "status": "in_progress",
            "generation_results": {}
        }

        # Execute the prototype builder (which now has access to complete FLUX workflow)
        prototype_builder = DeadSkyRegionBuilderPrototype()
        generation_results = await prototype_builder.build_dead_sky_prototype()

        stage_results["generation_results"] = generation_results

        if generation_results["status"] == "completed":
            logger.info("🎉 Dead Sky region generation completed!")
            stage_results["status"] = "completed"
        else:
            logger.error("❌ Region generation failed")
            stage_results["status"] = "failed"

        return stage_results

    async def stage_4_integration_validation(self) -> Dict[str, Any]:
        """Stage 4: Validate and prepare for Unreal Engine integration"""
        logger.info("🔗 STAGE 4: Integration Validation")
        logger.info("=" * 50)

        stage_results = {
            "stage": "integration_validation",
            "status": "in_progress",
            "validation_results": {}
        }

        # Check generated assets
        output_path = Path("Content/TG/Regions/DeadSky")
        manifest_path = output_path / "dead_sky_prototype_manifest.json"

        if manifest_path.exists():
            with open(manifest_path, 'r') as f:
                manifest = json.load(f)

            validation_results = {
                "manifest_found": True,
                "assets_generated": manifest["prototype_execution"]["metrics"]["total_assets_generated"],
                "mcp_operations": manifest["prototype_execution"]["metrics"]["mcp_operations_completed"],
                "region_area_km2": manifest["prototype_execution"]["metrics"]["total_area_km2"],
                "ready_for_unreal": True
            }

            logger.info(f"✅ Manifest validated: {validation_results['assets_generated']} assets generated")
            logger.info(f"✅ MCP Operations: {validation_results['mcp_operations']} completed")
            logger.info(f"✅ Region Area: {validation_results['region_area_km2']:,.0f} km²")

            stage_results["validation_results"] = validation_results
            stage_results["status"] = "completed"
        else:
            logger.error("❌ No manifest found - generation may have failed")
            stage_results["validation_results"] = {"manifest_found": False}
            stage_results["status"] = "failed"

        return stage_results

    async def execute_complete_pipeline(self, force_model_download: bool = False) -> Dict[str, Any]:
        """Execute the complete Dead Sky production pipeline"""
        logger.info("🚀 DEAD SKY PRODUCTION PIPELINE - FULL EXECUTION")
        logger.info("=" * 70)

        try:
            # Stage 1: Infrastructure Setup
            stage1_results = await self.stage_1_infrastructure_setup()
            self.pipeline_results["stages"]["stage_1"] = stage1_results

            if stage1_results["status"] != "completed":
                raise Exception("Stage 1 failed - infrastructure not ready")

            # Stage 2: Model Preparation
            stage2_results = await self.stage_2_model_preparation(force_model_download)
            self.pipeline_results["stages"]["stage_2"] = stage2_results

            if stage2_results["status"] != "completed":
                raise Exception("Stage 2 failed - model preparation failed")

            # Stage 3: Region Generation
            stage3_results = await self.stage_3_region_generation()
            self.pipeline_results["stages"]["stage_3"] = stage3_results

            if stage3_results["status"] != "completed":
                raise Exception("Stage 3 failed - region generation failed")

            # Stage 4: Integration Validation
            stage4_results = await self.stage_4_integration_validation()
            self.pipeline_results["stages"]["stage_4"] = stage4_results

            if stage4_results["status"] != "completed":
                raise Exception("Stage 4 failed - validation failed")

            # Calculate final metrics
            end_time = time.time()
            execution_time = end_time - self.start_time

            self.pipeline_results["final_metrics"] = {
                "total_execution_time": execution_time,
                "stages_completed": 4,
                "infrastructure_services": len(stage1_results["components"]["infrastructure"]["mcp_servers"]),
                "models_downloaded": len(stage2_results["download_results"]["downloaded"]),
                "assets_generated": stage3_results["generation_results"]["metrics"]["total_assets_generated"],
                "pipeline_success": True
            }

            self.pipeline_results["status"] = "completed"

            # Save final pipeline report
            pipeline_report_path = Path("Content/TG/Regions/DeadSky/pipeline_execution_report.json")
            with open(pipeline_report_path, 'w') as f:
                json.dump(self.pipeline_results, f, indent=2)

            logger.info("💾 Pipeline report saved: " + str(pipeline_report_path))

            return self.pipeline_results

        except Exception as e:
            logger.error(f"❌ Pipeline failed: {e}")
            self.pipeline_results["status"] = "failed"
            self.pipeline_results["error"] = str(e)
            return self.pipeline_results

async def main():
    """Main execution function"""
    try:
        print("🚀 DEAD SKY PRODUCTION PIPELINE")
        print("🎯 Terminal Grounds - Complete Region Creation")
        print("=" * 70)

        pipeline = DeadSkyProductionPipeline()

        # Check command line arguments
        force_download = "--force-download" in sys.argv
        if force_download:
            print("🔄 Force download mode enabled")

        # Execute complete pipeline
        results = await pipeline.execute_complete_pipeline(force_download)

        # Display final results
        print("\n" + "=" * 70)
        print("📊 PIPELINE EXECUTION RESULTS")
        print("=" * 70)

        if results["status"] == "completed":
            metrics = results["final_metrics"]
            print(f"✅ Status: SUCCESS")
            print(f"⏱️  Total Time: {metrics['total_execution_time']:.2f} seconds")
            print(f"🔧 Infrastructure Services: {metrics['infrastructure_services']}")
            print(f"📦 Models Downloaded: {metrics['models_downloaded']}")
            print(f"🎨 Assets Generated: {metrics['assets_generated']}")
            print(f"📋 Stages Completed: {metrics['stages_completed']}/4")
            print("\n🎉 DEAD SKY REGION IS READY!")
            print("📁 Output: Content/TG/Regions/DeadSky/")
            print("🚀 Ready for Unreal Engine integration!")
            return True
        else:
            print(f"❌ Status: FAILED")
            if "error" in results:
                print(f"💥 Error: {results['error']}")
            print("\n📋 Completed Stages:")
            for stage_name, stage_data in results["stages"].items():
                status_icon = "✅" if stage_data["status"] == "completed" else "❌"
                print(f"  {status_icon} {stage_name}: {stage_data['status']}")
            return False

    except Exception as e:
        logger.error(f"Fatal error: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
