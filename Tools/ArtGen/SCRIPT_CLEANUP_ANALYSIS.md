# ArtGen Script Cleanup Analysis

Based on our working ComfyUI API setup and proven workflows, here's the analysis of which scripts are still needed:

## ✅ KEEP - Core Production Scripts

### Essential API & Generation
- `comfyui_api_client.py` - **PRODUCTION** - Main API client that works
- `working_flux_generator.py` - **PRODUCTION** - Proven generator
- `terminal_grounds_pipeline.py` - **PRODUCTION** - Main pipeline
- `terminal_grounds_generator.py` - **PRODUCTION** - Alternative generator

### Proven Utilities
- `build_lore_prompt.py` - **USEFUL** - Generates lore-accurate prompts
- `lore_prompt.py` - **USEFUL** - Lore integration
- `monitor_outputs.py` - **USEFUL** - Output monitoring
- `validate_workflow.py` - **USEFUL** - Workflow validation
- `create_final_workflows.py` - **USEFUL** - Creates production workflows

### UE5 Integration
- `ue5_import_ui_icons.py` - **KEEP** - UE5 asset import

## ⚠️ REVIEW - Potentially Useful

### Quality & Processing
- `production_quality_framework.py` - May be useful for quality assessment
- `refine_sharpen_pass.py` - Post-processing utility
- `upscale_image_once.py` - Single image upscaling
- `convert_to_png.py` - Format conversion

### Batch Processing
- `batch_hq_concepts.py` - Batch concept generation
- `pipeline_hq_batch.py` - High-quality batch processing
- `auto_copy_outputs.py` - Automated file management
- `simple_copy_outputs.py` - Basic file copying

## 🗑️ DELETE - Extraneous/Obsolete Scripts

### Organizational Scripts (No Longer Needed)
- `organize_workflows.py` - **DELETE** - One-time organization script
- `reorganize_artgen.py` - **DELETE** - One-time reorganization script  
- `consolidate_scripts.py` - **DELETE** - One-time consolidation script

### Experimental/Failed Approaches
- `aaa_multistage_final.py` - **DELETE** - Experimental approach
- `no_text_generation_workflow.py` - **DELETE** - Specific test case
- `debug_upscaling_parameters.py` - **DELETE** - Debug script
- `ultra_high_resolution_pipeline.py` - **DELETE** - Experimental
- `update_aaa_workflows.py` - **DELETE** - One-time update script

### Duplicate/Similar Functionality
- `flux_generator.py` - **DELETE** - Superseded by working_flux_generator.py
- `generate_concepts.py` - **DELETE** - Functionality in main client
- `sharp_emblem_workflow.py` - **DELETE** - Specific use case covered
- `atmospheric_concept_workflow.py` - **DELETE** - Specific workflow
- `documentation_workflow.py` - **DELETE** - Documentation-specific

### MCP/External Dependencies
- `artgen_run_mcp.py` - **DELETE** - External dependency
- `mcp_*.py` (3 files) - **DELETE** - External MCP integration
- `artgen_plan_from_placeholder_report.py` - **DELETE** - Specific use case

### Utility Scripts (Questionable Value)
- `download_urls.py` - **DELETE** - External downloads
- `list_upscale_models.py` - **DELETE** - One-time query
- `upscale_compare_ab.py` - **DELETE** - Testing script
- `downscale_lanczos.py` - **DELETE** - Specific processing
- `model_manager.py` - **DELETE** - ComfyUI handles this

## Summary

**Keep**: 15 core production scripts
**Review**: 8 potentially useful scripts  
**Delete**: 25+ extraneous scripts

## Recommended Actions

1. **Immediate deletion** - Organization/consolidation scripts (already served purpose)
2. **Archive experimental** - Move aaa_* and experimental scripts to archive/
3. **Review utilities** - Assess if batch processing scripts are actually used
4. **Test core scripts** - Verify the 15 core scripts work with current setup

This cleanup would reduce the ArtGen directory from ~50 scripts to ~15-20 essential ones.