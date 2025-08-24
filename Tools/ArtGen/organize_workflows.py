#!/usr/bin/env python3
"""
Organize and consolidate ComfyUI workflows for Terminal Grounds
Removes duplicates and standardizes naming
"""
import json
import os
import shutil
from pathlib import Path
from datetime import datetime

def organize_workflows():
    """Organize workflow files into categories"""
    
    workflows_dir = Path("workflows")
    archive_dir = Path("workflows/archive")
    archive_dir.mkdir(exist_ok=True)
    
    # Define workflow categories
    categories = {
        "production": [],  # FINAL workflows ready for use
        "experimental": [],  # Test and development workflows
        "api": [],  # API-specific workflows
        "archive": []  # Duplicates and obsolete
    }
    
    # Analyze existing workflows
    workflow_analysis = {}
    
    for workflow_file in workflows_dir.glob("*.json"):
        filename = workflow_file.name
        
        # Categorize based on naming patterns
        if "FINAL" in filename:
            categories["production"].append(filename)
        elif "api.json" in filename:
            categories["api"].append(filename)
        elif any(x in filename.lower() for x in ["debug", "test", "multistage", "enhanced"]):
            categories["experimental"].append(filename)
        else:
            # Check for duplicates (e.g., TG_ vs Terminal_Grounds_ prefix)
            base_name = filename.replace("Terminal_Grounds_", "").replace("TG_", "")
            if base_name not in workflow_analysis:
                workflow_analysis[base_name] = []
            workflow_analysis[base_name].append(filename)
    
    # Identify duplicates
    duplicates_found = []
    for base_name, files in workflow_analysis.items():
        if len(files) > 1:
            # Keep the one with TG_ prefix or FINAL suffix as primary
            primary = None
            for f in files:
                if "FINAL" in f or f.startswith("TG_"):
                    primary = f
                    break
            if not primary:
                primary = files[0]
            
            for f in files:
                if f != primary:
                    duplicates_found.append(f)
                    categories["archive"].append(f)
    
    return categories, duplicates_found

def consolidate_python_scripts():
    """Consolidate similar Python scripts"""
    
    scripts_to_consolidate = {
        "aaa_pipelines": [
            "aaa_quality_pipeline.py",
            "aaa_multistage_pipeline.py", 
            "aaa_multistage_fixed.py",
            "aaa_multistage_final.py",
            "aaa_enhanced_pipeline.py",
            "aaa_texture_enhancement_pipeline.py"
        ],
        "generators": [
            "aaa_locked_generator.py",
            "aaa_workflow_builder.py",
            "working_flux_generator.py",
            "FINAL_WORKING_GENERATOR.py"
        ],
        "workflow_tools": [
            "send_flux_workflow.py",
            "send_integrated_workflow.py", 
            "send_qwen_workflow.py",
            "create_final_workflows.py",
            "create_uhd_workflow.py",
            "consolidate_workflows.py"
        ]
    }
    
    archive_dir = Path("archive/scripts_" + datetime.now().strftime("%Y%m%d"))
    archive_dir.mkdir(parents=True, exist_ok=True)
    
    consolidation_report = []
    
    for category, scripts in scripts_to_consolidate.items():
        existing_scripts = [s for s in scripts if Path(s).exists()]
        if len(existing_scripts) > 1:
            consolidation_report.append(f"\n{category.upper()}:")
            consolidation_report.append(f"  Found {len(existing_scripts)} similar scripts")
            
            # Determine primary script (usually the 'final' or most recent one)
            primary = None
            for script in existing_scripts:
                if "final" in script.lower() or "working" in script.lower():
                    primary = script
                    break
            if not primary:
                primary = existing_scripts[-1]
                
            consolidation_report.append(f"  Primary: {primary}")
            consolidation_report.append(f"  Archiving: {', '.join([s for s in existing_scripts if s != primary])}")
            
            # Archive non-primary scripts
            for script in existing_scripts:
                if script != primary:
                    if Path(script).exists():
                        try:
                            shutil.move(script, archive_dir / script)
                        except:
                            pass
    
    return "\n".join(consolidation_report)

def create_organization_report():
    """Create a report of the organization changes"""
    
    categories, duplicates = organize_workflows()
    script_report = consolidate_python_scripts()
    
    report = [
        "# Terminal Grounds - Workflow Organization Report",
        f"\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "\n## Workflow Files Organization\n",
        f"### Production Workflows ({len(categories['production'])} files)",
        "Ready for immediate use:"
    ]
    
    for wf in categories['production']:
        report.append(f"  - {wf}")
    
    report.extend([
        f"\n### Experimental Workflows ({len(categories['experimental'])} files)",
        "Development and testing:"
    ])
    
    for wf in categories['experimental']:
        report.append(f"  - {wf}")
    
    report.extend([
        f"\n### API Workflows ({len(categories['api'])} files)",
        "API-specific implementations:"
    ])
    
    for wf in categories['api']:
        report.append(f"  - {wf}")
    
    if duplicates:
        report.extend([
            f"\n### Duplicates to Archive ({len(duplicates)} files)",
            "These appear to be duplicates of other workflows:"
        ])
        for wf in duplicates:
            report.append(f"  - {wf}")
    
    report.extend([
        "\n## Python Scripts Consolidation",
        script_report,
        "\n## Recommended Actions",
        "1. Review and confirm the categorization",
        "2. Archive duplicate workflows",  
        "3. Update documentation to reference correct files",
        "4. Consider renaming experimental workflows for clarity",
        "\n## Directory Structure After Organization",
        "```",
        "Tools/ArtGen/",
        "├── workflows/",
        "│   ├── production/     # Ready-to-use workflows",
        "│   ├── experimental/   # Development workflows", 
        "│   ├── api/           # API-specific workflows",
        "│   └── archive/       # Old/duplicate workflows",
        "├── scripts/",
        "│   ├── core/          # Main generation scripts",
        "│   ├── utils/         # Helper utilities",
        "│   └── archive/       # Obsolete scripts",
        "└── docs/              # Documentation",
        "```"
    ])
    
    return "\n".join(report)

if __name__ == "__main__":
    report = create_organization_report()
    
    # Save report with UTF-8 encoding
    with open("ORGANIZATION_REPORT.md", "w", encoding="utf-8") as f:
        f.write(report)
    
    print(report.encode('ascii', 'ignore').decode('ascii'))
    print("\nOrganization report saved to ORGANIZATION_REPORT.md")
    print("Review the report before executing the actual file moves.")