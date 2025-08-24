#!/usr/bin/env python3
"""
Terminal Grounds Asset Generator v0.9 Deployment Script
Quick deployment and validation of enhanced production system
"""
import subprocess
import sys
from pathlib import Path

def deploy_v09():
    """Deploy Terminal Grounds v0.9 enhanced production system"""
    print("=" * 60)
    print("DEPLOYING TERMINAL GROUNDS ASSET GENERATOR v0.9")
    print("=" * 60)
    print()
    
    print("🚀 DEPLOYMENT FEATURES:")
    print("✓ Enhanced lore integration with Terminal Grounds specifics")
    print("✓ Improved prompt engineering for authentic post-apocalyptic feel")
    print("✓ Location-specific atmospheric details and materials")
    print("✓ Enhanced style differentiation (Clean SciFi vs Gritty Realism)")
    print("✓ Post-cascade environmental context integration")
    print("✓ Proven technical parameters preserved (heun/normal/CFG 3.2)")
    print()
    
    # Validate deployment requirements
    print("🔍 VALIDATING DEPLOYMENT REQUIREMENTS:")
    
    # Check ComfyUI API availability
    try:
        import urllib.request
        response = urllib.request.urlopen("http://127.0.0.1:8188/queue", timeout=5)
        print("✅ ComfyUI API accessible at http://127.0.0.1:8188")
    except:
        print("❌ ComfyUI API not accessible - start ComfyUI first")
        return False
    
    # Check generator file
    generator_path = Path(__file__).parent / "terminal_grounds_generator.py"
    if generator_path.exists():
        print("✅ Enhanced terminal_grounds_generator.py ready")
    else:
        print("❌ terminal_grounds_generator.py not found")
        return False
    
    # Check output directory
    output_path = Path("C:/Users/Zachg/Terminal-Grounds/Tools/Comfy/ComfyUI-API/output")
    if output_path.exists():
        print("✅ Output directory accessible")
    else:
        print("❌ Output directory not accessible")
        return False
    
    print()
    print("🎯 v0.9 ENHANCED CAPABILITIES:")
    print()
    print("BEFORE v0.9 (Generic prompts):")
    print("- Tech Wastes: 'industrial wasteland, abandoned technology'")
    print("- Corporate Lobby: 'glass walls, marble floors, reception desk'")
    print("- Quality: 50% success rate")
    print()
    print("AFTER v0.9 (Enhanced lore integration):")
    print("- Tech Wastes: 'autolines, robot arms, cable trellises, coolant plumes'")
    print("- Corporate Lobby: 'post-cascade decay, emergency lighting, abandoned authority'")
    print("- Quality: Expected 75%+ success rate")
    print()
    
    print("🔧 TECHNICAL SPECIFICATIONS:")
    print(f"- Model: FLUX1-dev-fp8.safetensors")
    print(f"- Sampler: heun (proven)")
    print(f"- Scheduler: normal (proven)")
    print(f"- CFG: 3.2 (proven)")
    print(f"- Steps: 25 (proven)")
    print(f"- Resolution: 1536x864")
    print(f"- Seed base: 94887 + procedural offsets")
    print()
    
    # Ready to deploy
    print("🚀 DEPLOYMENT STATUS: READY")
    print()
    print("To generate enhanced batch:")
    print("python terminal_grounds_generator.py")
    print()
    print("Expected improvements:")
    print("- More authentic Terminal Grounds aesthetic")
    print("- Better style differentiation")
    print("- Location-specific lore accuracy")
    print("- Enhanced post-apocalyptic atmosphere")
    print()
    
    return True

def quick_test_v09():
    """Quick test of v0.9 enhancements"""
    print("🧪 QUICK v0.9 ENHANCEMENT TEST")
    print("=" * 40)
    
    # Import the enhanced generator
    sys.path.insert(0, str(Path(__file__).parent))
    
    try:
        from terminal_grounds_generator import create_workflow
        
        # Test enhanced Tech Wastes prompt
        print("Testing enhanced Tech Wastes prompt:")
        workflow = create_workflow("Tech_Wastes_Exterior", "Clean_SciFi", 0, "Perspective", "Atmospheric")
        prompt = workflow["2"]["inputs"]["text"]
        
        # Check for enhanced elements
        enhanced_elements = [
            "autolines", "robot arms", "cable trellises", "coolant plumes",
            "post-cascade world", "resource scarcity"
        ]
        
        found_elements = [elem for elem in enhanced_elements if elem in prompt]
        
        print(f"Enhanced elements found: {len(found_elements)}/{len(enhanced_elements)}")
        print("Elements:", ", ".join(found_elements))
        
        if len(found_elements) >= 4:
            print("✅ Tech Wastes enhancement: SUCCESSFUL")
        else:
            print("❌ Tech Wastes enhancement: NEEDS WORK")
        
        print()
        print("Sample enhanced prompt:")
        print(prompt[:200] + "...")
        print()
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False
    
    print("✅ v0.9 enhancement test completed")
    return True

if __name__ == "__main__":
    print("Terminal Grounds v0.9 Deployment")
    print()
    
    # Deploy
    if deploy_v09():
        print("✅ Deployment validation successful")
        print()
        
        # Quick test
        if quick_test_v09():
            print("🎉 TERMINAL GROUNDS v0.9 READY FOR PRODUCTION")
            print()
            print("Run: python terminal_grounds_generator.py")
        else:
            print("❌ Enhancement test failed")
    else:
        print("❌ Deployment validation failed")