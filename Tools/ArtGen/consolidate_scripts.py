#!/usr/bin/env python3
"""
Consolidate duplicate Python scripts in ArtGen
Identifies similar scripts and recommends which to keep
"""
import os
import hashlib
from pathlib import Path
from datetime import datetime
import ast

def get_file_hash(filepath):
    """Get MD5 hash of file content"""
    try:
        with open(filepath, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()
    except:
        return None

def analyze_python_file(filepath):
    """Analyze Python file for imports and functions"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        tree = ast.parse(content)
        
        # Extract key information
        imports = []
        functions = []
        classes = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports.extend([n.name for n in node.names])
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.append(node.module)
            elif isinstance(node, ast.FunctionDef):
                functions.append(node.name)
            elif isinstance(node, ast.ClassDef):
                classes.append(node.name)
        
        return {
            'imports': sorted(set(imports)),
            'functions': sorted(functions),
            'classes': sorted(classes),
            'lines': len(content.splitlines()),
            'size': len(content)
        }
    except:
        return None

def find_similar_scripts():
    """Find similar Python scripts based on content analysis"""
    
    # Group scripts by category
    script_groups = {
        'generators': [],
        'pipelines': [],
        'workflows': [],
        'quality': [],
        'utils': [],
        'test': []
    }
    
    # Analyze all Python files
    for py_file in Path('.').glob('*.py'):
        filename = py_file.name.lower()
        
        if 'generator' in filename or 'generate' in filename:
            script_groups['generators'].append(py_file)
        elif 'pipeline' in filename:
            script_groups['pipelines'].append(py_file)
        elif 'workflow' in filename:
            script_groups['workflows'].append(py_file)
        elif 'quality' in filename or 'aaa' in filename:
            script_groups['quality'].append(py_file)
        elif 'test' in filename or 'debug' in filename:
            script_groups['test'].append(py_file)
        else:
            script_groups['utils'].append(py_file)
    
    # Analyze each group for duplicates
    consolidation_recommendations = []
    
    for category, scripts in script_groups.items():
        if len(scripts) > 1:
            group_analysis = []
            
            for script in scripts:
                analysis = analyze_python_file(script)
                if analysis:
                    group_analysis.append({
                        'file': script.name,
                        'analysis': analysis,
                        'modified': os.path.getmtime(script),
                        'hash': get_file_hash(script)
                    })
            
            # Sort by file size and modification time
            group_analysis.sort(key=lambda x: (-x['analysis']['lines'], -x['modified']))
            
            if group_analysis:
                # Recommend keeping the most comprehensive and recent
                primary = group_analysis[0]
                duplicates = group_analysis[1:]
                
                if duplicates:
                    consolidation_recommendations.append({
                        'category': category,
                        'keep': primary['file'],
                        'archive': [d['file'] for d in duplicates],
                        'reason': f"Most comprehensive ({primary['analysis']['lines']} lines) and recent"
                    })
    
    return consolidation_recommendations

def create_consolidation_script(recommendations):
    """Create a script to perform the consolidation"""
    
    script_lines = [
        "@echo off",
        "echo Starting script consolidation...",
        "",
        "REM Create archive directory",
        "if not exist archive\\scripts mkdir archive\\scripts",
        ""
    ]
    
    total_archived = 0
    
    for rec in recommendations:
        script_lines.append(f"REM {rec['category'].upper()} - Keep: {rec['keep']}")
        
        for file_to_archive in rec['archive']:
            script_lines.append(f'move "{file_to_archive}" "archive\\scripts\\{file_to_archive}"')
            total_archived += 1
        
        script_lines.append("")
    
    script_lines.extend([
        f"echo Archived {total_archived} duplicate scripts",
        "echo Consolidation complete!",
        "pause"
    ])
    
    with open("CONSOLIDATE_SCRIPTS.bat", "w") as f:
        f.write("\n".join(script_lines))
    
    return total_archived

def generate_consolidation_report():
    """Generate a detailed consolidation report"""
    
    recommendations = find_similar_scripts()
    
    report = [
        "# Script Consolidation Report",
        f"\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "\n## Analysis Summary"
    ]
    
    # Count total scripts
    all_scripts = list(Path('.').glob('*.py'))
    report.append(f"\nTotal Python scripts found: {len(all_scripts)}")
    
    if recommendations:
        report.append("\n## Consolidation Recommendations\n")
        
        for rec in recommendations:
            report.append(f"### {rec['category'].title()}")
            report.append(f"**Keep:** `{rec['keep']}`")
            report.append(f"**Reason:** {rec['reason']}")
            report.append("**Archive:**")
            for archive_file in rec['archive']:
                report.append(f"  - `{archive_file}`")
            report.append("")
        
        # Create consolidation script
        total_archived = create_consolidation_script(recommendations)
        
        report.extend([
            "## Execution",
            f"Run `CONSOLIDATE_SCRIPTS.bat` to archive {total_archived} duplicate scripts.",
            "",
            "## Post-Consolidation Structure",
            "```",
            "Tools/ArtGen/",
            "├── working_flux_generator.py     # Main generator",
            "├── aaa_quality_pipeline.py       # Quality assessment",
            "├── terminal_grounds_pipeline.py  # Pipeline controller", 
            "├── monitor_outputs.py            # Output monitoring",
            "└── archive/",
            "    └── scripts/                  # Archived duplicates",
            "```"
        ])
    else:
        report.append("\nNo duplicate scripts found that need consolidation.")
    
    # List of key scripts to keep
    report.extend([
        "\n## Essential Scripts to Retain",
        "",
        "| Script | Purpose |",
        "|--------|---------|",
        "| working_flux_generator.py | Production image generation |",
        "| aaa_quality_pipeline.py | Quality scoring system |",
        "| terminal_grounds_pipeline.py | Main pipeline controller |",
        "| create_final_workflows.py | Workflow generation |",
        "| monitor_outputs.py | Output directory monitoring |",
        "| build_lore_prompt.py | Lore-accurate prompts |"
    ])
    
    with open("SCRIPT_CONSOLIDATION_REPORT.md", "w", encoding="utf-8") as f:
        f.write("\n".join(report))
    
    return report

if __name__ == "__main__":
    report = generate_consolidation_report()
    
    print("Script Consolidation Analysis Complete!")
    print("\nReview SCRIPT_CONSOLIDATION_REPORT.md for details")
    print("Run CONSOLIDATE_SCRIPTS.bat to perform consolidation")