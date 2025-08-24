#!/usr/bin/env python3
"""
Generate Terminal Grounds Asset using production workflow
"""
import json
import urllib.request
import urllib.parse
import time
import uuid
from pathlib import Path

def submit_workflow(workflow_path, custom_prompt=None):
    """Submit a workflow to ComfyUI API"""
    
    # Load workflow
    with open(workflow_path, 'r') as f:
        workflow = json.load(f)
    
    # Optionally customize the prompt
    if custom_prompt and "2" in workflow:
        workflow["2"]["inputs"]["text"] = custom_prompt
    
    # Generate unique client ID
    client_id = str(uuid.uuid4())
    
    # Prepare API request
    prompt_data = {
        "prompt": workflow,
        "client_id": client_id
    }
    
    # Submit to API
    data = json.dumps(prompt_data).encode('utf-8')
    req = urllib.request.Request(
        "http://127.0.0.1:8188/prompt",
        data=data,
        headers={'Content-Type': 'application/json'}
    )
    
    try:
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read())
            return result.get('prompt_id'), client_id
    except Exception as e:
        print(f"Error submitting workflow: {e}")
        return None, None

def check_status(prompt_id):
    """Check generation status"""
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:8188/history/{prompt_id}") as response:
            history = json.loads(response.read())
            if prompt_id in history:
                status = history[prompt_id].get('status', {})
                if status.get('completed'):
                    return 'completed'
                elif status.get('status_str') == 'error':
                    return 'error'
            return 'running'
    except:
        return 'unknown'

def main():
    """Generate a Terminal Grounds asset"""
    
    print("=" * 60)
    print("TERMINAL GROUNDS ASSET GENERATOR")
    print("=" * 60)
    
    # Workflow options
    workflows = {
        "1": ("Metro Corridor", "Tools/ArtGen/workflows/TG_Metro_Corridor_FINAL.json"),
        "2": ("IEZ Facility", "Tools/ArtGen/workflows/TG_IEZ_Facility_FINAL.json"),
        "3": ("Tech Wastes", "Tools/ArtGen/workflows/TG_TechWastes_FINAL.json"),
    }
    
    print("\nAvailable workflows:")
    for key, (name, _) in workflows.items():
        print(f"  {key}. {name}")
    
    # For testing, let's use Metro Corridor
    choice = "1"
    workflow_name, workflow_path = workflows[choice]
    
    print(f"\n✓ Selected: {workflow_name}")
    print(f"✓ Workflow: {workflow_path}")
    
    # Custom prompt option
    custom_prompt = "Terminal Grounds Metro_Maintenance_Corridor, underground service tunnel, industrial sci-fi environment, metallic surfaces, emergency lighting, cable management systems, concrete walls with wear patterns, steam pipes, maintenance equipment, professional AAA game art, high detail environmental design, sharp focus, fine surface textures, balanced exposure, architectural quality"
    
    print(f"\n📝 Prompt: {custom_prompt[:100]}...")
    
    # Submit workflow
    print("\n🚀 Submitting workflow to ComfyUI...")
    prompt_id, client_id = submit_workflow(workflow_path, custom_prompt)
    
    if not prompt_id:
        print("❌ Failed to submit workflow")
        return
    
    print(f"✓ Workflow queued: {prompt_id}")
    
    # Monitor progress
    print("\n⏳ Generating asset (this takes ~5 minutes)...")
    start_time = time.time()
    
    while True:
        status = check_status(prompt_id)
        elapsed = int(time.time() - start_time)
        
        if status == 'completed':
            print(f"\n✅ Generation completed in {elapsed} seconds!")
            break
        elif status == 'error':
            print(f"\n❌ Generation failed after {elapsed} seconds")
            break
        else:
            print(f"  [{elapsed}s] Status: {status}...", end='\r')
            time.sleep(5)
    
    # Output location
    output_dir = Path("C:/Users/Zachg/Documents/ComfyUI/output")
    print(f"\n📁 Output location: {output_dir}")
    
    # List recent outputs
    if output_dir.exists():
        outputs = sorted(output_dir.glob("*.png"), key=lambda x: x.stat().st_mtime, reverse=True)[:5]
        if outputs:
            print("\n🎨 Recent outputs:")
            for output in outputs:
                print(f"  • {output.name}")
            print(f"\n✨ Latest: {outputs[0]}")
    
    print("\n" + "=" * 60)
    print("GENERATION COMPLETE!")
    print("=" * 60)

if __name__ == "__main__":
    main()