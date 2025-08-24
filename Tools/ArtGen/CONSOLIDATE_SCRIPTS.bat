@echo off
echo Starting script consolidation...

REM Create archive directory
if not exist archive\scripts mkdir archive\scripts

REM GENERATORS - Keep: terminal_grounds_generator.py
move "generate_assets.py" "archive\scripts\generate_assets.py"
move "flux_generator.py" "archive\scripts\flux_generator.py"
move "local_generate.py" "archive\scripts\local_generate.py"
move "working_flux_generator.py" "archive\scripts\working_flux_generator.py"
move "generate_concepts.py" "archive\scripts\generate_concepts.py"

REM PIPELINES - Keep: pipeline_hq_batch.py
move "terminal_grounds_pipeline.py" "archive\scripts\terminal_grounds_pipeline.py"
move "ultra_high_resolution_pipeline.py" "archive\scripts\ultra_high_resolution_pipeline.py"
move "production_pipeline_v2.py" "archive\scripts\production_pipeline_v2.py"

REM WORKFLOWS - Keep: no_text_generation_workflow.py
move "create_final_workflows.py" "archive\scripts\create_final_workflows.py"
move "atmospheric_concept_workflow.py" "archive\scripts\atmospheric_concept_workflow.py"
move "organize_workflows.py" "archive\scripts\organize_workflows.py"
move "documentation_workflow.py" "archive\scripts\documentation_workflow.py"
move "sharp_emblem_workflow.py" "archive\scripts\sharp_emblem_workflow.py"
move "upscale_concept_workflow.py" "archive\scripts\upscale_concept_workflow.py"
move "update_aaa_workflows.py" "archive\scripts\update_aaa_workflows.py"
move "validate_workflow.py" "archive\scripts\validate_workflow.py"
move "run_smoke_workflow.py" "archive\scripts\run_smoke_workflow.py"

REM QUALITY - Keep: production_quality_framework.py
move "aaa_multistage_final.py" "archive\scripts\aaa_multistage_final.py"

REM UTILS - Keep: comfyui_api_client.py
move "reorganize_artgen.py" "archive\scripts\reorganize_artgen.py"
move "artgen_run_batch.py" "archive\scripts\artgen_run_batch.py"
move "consolidate_scripts.py" "archive\scripts\consolidate_scripts.py"
move "lore_accurate_prompts.py" "archive\scripts\lore_accurate_prompts.py"
move "smart_generation_monitor.py" "archive\scripts\smart_generation_monitor.py"
move "download_urls.py" "archive\scripts\download_urls.py"
move "mcp_download_results.py" "archive\scripts\mcp_download_results.py"
move "ue5_import_ui_icons.py" "archive\scripts\ue5_import_ui_icons.py"
move "refine_sharpen_pass.py" "archive\scripts\refine_sharpen_pass.py"
move "auto_copy_outputs.py" "archive\scripts\auto_copy_outputs.py"
move "batch_hq_concepts.py" "archive\scripts\batch_hq_concepts.py"
move "artgen_run_mcp.py" "archive\scripts\artgen_run_mcp.py"
move "upscale_image_once.py" "archive\scripts\upscale_image_once.py"
move "list_upscale_models.py" "archive\scripts\list_upscale_models.py"
move "build_review_index.py" "archive\scripts\build_review_index.py"
move "upscale_compare_ab.py" "archive\scripts\upscale_compare_ab.py"
move "downscale_lanczos.py" "archive\scripts\downscale_lanczos.py"
move "mcp_execute_jobs_with_builtin_tool.py" "archive\scripts\mcp_execute_jobs_with_builtin_tool.py"
move "monitor_outputs.py" "archive\scripts\monitor_outputs.py"
move "simple_copy_outputs.py" "archive\scripts\simple_copy_outputs.py"
move "lore_prompt.py" "archive\scripts\lore_prompt.py"
move "mcp_create_results_skeleton.py" "archive\scripts\mcp_create_results_skeleton.py"
move "artgen_plan_from_placeholder_report.py" "archive\scripts\artgen_plan_from_placeholder_report.py"
move "artgen_import.py" "archive\scripts\artgen_import.py"
move "build_lore_prompt.py" "archive\scripts\build_lore_prompt.py"
move "convert_to_png.py" "archive\scripts\convert_to_png.py"

echo Archived 44 duplicate scripts
echo Consolidation complete!
pause