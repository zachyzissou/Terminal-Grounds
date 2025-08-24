#!/usr/bin/env python3
"""
Update AAA workflows with sgm_uniform scheduler (your successful discovery!)
"""
import json
from pathlib import Path

def update_workflows_with_sgm_uniform():
    """Update all AAA workflows to use sgm_uniform scheduler"""
    
    workflows_dir = Path(__file__).parent / "aaa_workflows"
    v2_dir = Path(__file__).parent / "aaa_workflows_v2"
    v2_dir.mkdir(exist_ok=True)
    
    updated_workflows = []
    
    # Process all existing workflow files
    for workflow_file in workflows_dir.glob("*.json"):
        if workflow_file.name == "README.md":
            continue
            
        print(f"Updating: {workflow_file.name}")
        
        # Read original workflow
        with open(workflow_file) as f:
            workflow = json.load(f)
        
        # Update the KSampler scheduler to sgm_uniform
        if "5" in workflow and workflow["5"]["class_type"] == "KSampler":
            workflow["5"]["inputs"]["scheduler"] = "sgm_uniform"
            print(f"  - Updated scheduler to sgm_uniform")
        
        # Update filename prefix to indicate v2
        if "7" in workflow and workflow["7"]["class_type"] == "SaveImage":
            old_prefix = workflow["7"]["inputs"]["filename_prefix"]
            new_prefix = old_prefix.replace("AAA_", "AAA_V2_SGM_")
            workflow["7"]["inputs"]["filename_prefix"] = new_prefix
            print(f"  - Updated filename prefix: {new_prefix}")
        
        # Save updated workflow
        v2_filename = workflow_file.name.replace("AAA_", "AAA_V2_SGM_")
        v2_path = v2_dir / v2_filename
        
        with open(v2_path, 'w') as f:
            json.dump(workflow, f, indent=2)
        
        updated_workflows.append({
            "original": workflow_file.name,
            "updated": v2_filename,
            "path": str(v2_path)
        })
        
        print(f"  - Saved: {v2_filename}")
    
    # Create updated README
    readme_content = f"""# AAA-Quality Workflows V2 (SGM_UNIFORM)

## Updated Parameters
Based on successful testing, these workflows use:
- **Scheduler**: `sgm_uniform` (your successful discovery!)
- **Model**: FLUX1-dev-fp8
- **Steps**: 25
- **CFG**: 3.5
- **Sampler**: dpmpp_2m

## Files Updated
"""
    
    for workflow in updated_workflows:
        readme_content += f"- `{workflow['updated']}` (from {workflow['original']})\n"
    
    readme_content += f"""
## Usage
1. Open ComfyUI in browser
2. Drag any .json file into ComfyUI
3. Click "Queue Prompt"
4. Expect better quality with sgm_uniform scheduler!

## Quality Improvement
The sgm_uniform scheduler should provide:
- Better detail retention
- More coherent compositions
- Less abstract/blurry outputs
- Improved Terminal Grounds aesthetic

Generated: {Path(__file__).stat().st_mtime}
"""
    
    readme_path = v2_dir / "README.md"
    with open(readme_path, 'w') as f:
        f.write(readme_content)
    
    print(f"\n✓ Updated {len(updated_workflows)} workflows with sgm_uniform scheduler")
    print(f"✓ Created: {readme_path}")
    print(f"\nLocation: {v2_dir.absolute()}")
    print("\nThese workflows should generate much better quality!")
    
    return updated_workflows

if __name__ == "__main__":
    update_workflows_with_sgm_uniform()