#!/usr/bin/env python3
"""
Validate the workflow to see if there are any issues
"""
import requests
import json
from pathlib import Path

def validate_workflow():
    """Check if our workflow has validation issues"""
    
    # Load the workflow
    workflow_path = Path(__file__).parent / "workflows" / "TG_IEZ_Facility_FINAL.json"
    with open(workflow_path) as f:
        workflow = json.load(f)
    
    print("=== Workflow Validation Test ===")
    print(f"Testing: {workflow_path.name}")
    print()
    
    # Check each node for potential issues
    print("Workflow structure:")
    for node_id, node_data in workflow.items():
        class_type = node_data.get("class_type", "unknown")
        print(f"  Node {node_id}: {class_type}")
        
        # Check for common issues
        if class_type == "CheckpointLoaderSimple":
            model_name = node_data["inputs"]["ckpt_name"]
            print(f"    Model: {model_name}")
        
        elif class_type == "KSampler":
            sampler = node_data["inputs"]["sampler_name"]
            scheduler = node_data["inputs"]["scheduler"]
            print(f"    Sampler: {sampler}, Scheduler: {scheduler}")
    
    print()
    
    # Try to validate via API
    try:
        print("Testing API validation...")
        response = requests.post(
            "http://127.0.0.1:8000/prompt",
            json={
                "prompt": workflow,
                "client_id": "validation_test"
            },
            timeout=10
        )
        
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            prompt_id = result.get("prompt_id")
            print(f"Validation passed - Prompt ID: {prompt_id}")
            
            # Check if it actually queued
            queue_response = requests.get("http://127.0.0.1:8000/queue")
            queue_data = queue_response.json()
            
            running = len(queue_data.get("queue_running", []))
            pending = len(queue_data.get("queue_pending", []))
            
            print(f"Queue status: {running} running, {pending} pending")
            
            if running == 0 and pending == 0:
                print("ERROR: Prompt accepted but not queued!")
                print("This indicates a ComfyUI-electron API issue")
                return False
            else:
                print("SUCCESS: Prompt properly queued")
                return True
        
        elif response.status_code == 400:
            print("Validation failed (400 error):")
            print(response.text)
            return False
        
        else:
            print(f"Unexpected response: {response.status_code}")
            print(response.text)
            return False
            
    except Exception as e:
        print(f"Validation error: {e}")
        return False

if __name__ == "__main__":
    is_valid = validate_workflow()
    
    if is_valid:
        print("\\nWorkflow is valid and API is working!")
    else:
        print("\\nWorkflow has issues or API is not functioning properly")
        print("Recommendation: Use GUI workflows for reliable generation")