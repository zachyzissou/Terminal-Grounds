#!/usr/bin/env python3
"""
Reorganize ArtGen directory structure for better maintainability
Creates organized subdirectories and moves files appropriately
"""
import os
import shutil
from pathlib import Path
from datetime import datetime

def create_directory_structure():
    """Create the new organized directory structure"""
    directories = [
        "workflows/production",
        "workflows/experimental", 
        "workflows/api",
        "workflows/archive",
        "scripts/core",
        "scripts/utils",
        "scripts/quality",
        "scripts/archive",
        "docs",
        "archive/old_scripts",
        "archive/old_workflows"
    ]
    
    for dir_path in directories:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
    
    return directories

def reorganize_workflows():
    """Move workflow files to appropriate subdirectories"""
    moves = []
    workflows_dir = Path("workflows")
    
    if not workflows_dir.exists():
        return moves
    
    # Define workflow mappings
    workflow_mappings = {
        "workflows/production": [
            "TG_Metro_Corridor_FINAL.json",
            "TG_IEZ_Facility_FINAL.json", 
            "TG_TechWastes_FINAL.json"
        ],
        "workflows/experimental": [
            "TG_AAA_Enhanced_MultiStage.json",
            "TG_Debug_SingleOutput.json",
            "TG_Integrated_MultiStage.json",
            "TG_Integrated_MultiStage_Fixed.json",
            "TG_Metro_AAA_Multistage.json",
            "TG_3D_Asset_Pipeline.json",
            "TG_QwenImage_Production.json"
        ],
        "workflows/api": [
            "concept_art.api.json",
            "environment_matte.api.json",
            "high_detail_render.api.json",
            "icon_generation.api.json",
            "poster_design.api.json",
            "style_board.api.json",
            "texture_decal.api.json"
        ],
        "workflows/archive": [
            "Terminal_Grounds_IEZ_Facility.json",
            "Terminal_Grounds_Metro_Corridor.json",
            "Terminal_Grounds_TechWastes.json"
        ]
    }
    
    for target_dir, files in workflow_mappings.items():
        for filename in files:
            src = workflows_dir / filename
            if src.exists():
                dst = Path(target_dir) / filename
                moves.append((str(src), str(dst)))
    
    return moves

def reorganize_scripts():
    """Categorize and move Python scripts"""
    moves = []
    
    # Define script mappings based on functionality
    script_mappings = {
        "scripts/core": [
            "working_flux_generator.py",
            "FINAL_WORKING_GENERATOR.py",
            "terminal_grounds_generator.py",
            "terminal_grounds_pipeline.py",
            "production_pipeline_v2.py"
        ],
        "scripts/quality": [
            "aaa_quality_pipeline.py",
            "production_quality_framework.py",
            "validate_workflow.py"
        ],
        "scripts/utils": [
            "create_final_workflows.py",
            "consolidate_workflows.py",
            "organize_workflows.py",
            "reorganize_artgen.py",
            "build_lore_prompt.py",
            "lore_prompt.py",
            "monitor_outputs.py",
            "smart_generation_monitor.py"
        ],
        "scripts/archive": [
            "aaa_locked_generator.py",
            "aaa_workflow_builder.py",
            "aaa_texture_enhancement_pipeline.py",
            "aaa_multistage_pipeline.py",
            "aaa_multistage_fixed.py",
            "aaa_multistage_final.py",
            "aaa_enhanced_pipeline.py",
            "send_flux_workflow.py",
            "send_integrated_workflow.py",
            "send_qwen_workflow.py",
            "create_uhd_workflow.py",
            "debug_upscaling_parameters.py",
            "no_text_generation_workflow.py"
        ]
    }
    
    for target_dir, files in script_mappings.items():
        for filename in files:
            src = Path(filename)
            if src.exists():
                dst = Path(target_dir) / filename
                moves.append((str(src), str(dst)))
    
    return moves

def create_documentation():
    """Create README files for each major directory"""
    docs = {
        "workflows/README.md": """# ComfyUI Workflows

## Directory Structure

- **production/** - Ready-to-use workflows with proven parameters
- **experimental/** - Development and testing workflows
- **api/** - API-specific workflow configurations
- **archive/** - Deprecated or duplicate workflows

## Production Workflows

| Workflow | Purpose | Success Rate |
|----------|---------|--------------|
| TG_Metro_Corridor_FINAL.json | Underground maintenance areas | 85%+ |
| TG_IEZ_Facility_FINAL.json | Corporate facility interiors | 85%+ |
| TG_TechWastes_FINAL.json | Industrial wasteland zones | 85%+ |

## Usage

1. Open ComfyUI at http://127.0.0.1:8188
2. Drag workflow .json file into interface
3. Click "Queue Prompt"
4. Wait ~5 minutes for generation
""",
        "scripts/README.md": """# ArtGen Scripts

## Directory Structure

- **core/** - Main generation and pipeline scripts
- **quality/** - Quality assessment and validation tools
- **utils/** - Helper utilities and monitoring tools
- **archive/** - Deprecated scripts (kept for reference)

## Key Scripts

### Core Generation
- `working_flux_generator.py` - Current production generator
- `terminal_grounds_pipeline.py` - Main pipeline controller

### Quality Assessment
- `aaa_quality_pipeline.py` - Quality scoring system
- `validate_workflow.py` - Workflow validation

### Utilities
- `monitor_outputs.py` - Output directory monitoring
- `build_lore_prompt.py` - Lore-accurate prompt generation
"""
    }
    
    for filepath, content in docs.items():
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
    
    return list(docs.keys())

def generate_move_script():
    """Generate a batch script to perform the actual file moves"""
    create_directory_structure()
    
    workflow_moves = reorganize_workflows()
    script_moves = reorganize_scripts()
    docs_created = create_documentation()
    
    # Create batch file for Windows
    batch_content = ["@echo off", "echo Starting ArtGen reorganization...", ""]
    
    for src, dst in workflow_moves + script_moves:
        batch_content.append(f'move "{src}" "{dst}"')
    
    batch_content.extend([
        "",
        "echo Reorganization complete!",
        "echo.",
        "echo Created documentation files:",
    ])
    
    for doc in docs_created:
        batch_content.append(f"echo   - {doc}")
    
    batch_content.append("pause")
    
    with open("EXECUTE_REORGANIZATION.bat", "w") as f:
        f.write("\n".join(batch_content))
    
    # Create summary report
    report = [
        "# ArtGen Reorganization Plan",
        f"\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "\n## File Moves Planned",
        f"\n### Workflows ({len(workflow_moves)} files)"
    ]
    
    for src, dst in workflow_moves:
        report.append(f"  - {src} → {dst}")
    
    report.append(f"\n### Scripts ({len(script_moves)} files)")
    
    for src, dst in script_moves:
        report.append(f"  - {src} → {dst}")
    
    report.extend([
        "\n## Documentation Created",
        *[f"  - {doc}" for doc in docs_created],
        "\n## To Execute",
        "Run `EXECUTE_REORGANIZATION.bat` to perform the reorganization.",
        "\n## Benefits",
        "- Clear separation of production vs experimental code",
        "- Easier navigation and maintenance",
        "- Better version control with organized structure",
        "- Documentation at each level"
    ])
    
    with open("REORGANIZATION_PLAN.md", "w", encoding="utf-8") as f:
        f.write("\n".join(report))
    
    return len(workflow_moves) + len(script_moves)

if __name__ == "__main__":
    total_moves = generate_move_script()
    
    print(f"Reorganization plan created:")
    print(f"  - {total_moves} files to be moved")
    print(f"  - Documentation files will be created")
    print(f"\nReview REORGANIZATION_PLAN.md for details")
    print(f"Run EXECUTE_REORGANIZATION.bat to perform the reorganization")