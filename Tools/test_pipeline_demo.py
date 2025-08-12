#!/usr/bin/env python3
"""
test_pipeline_demo.py
Terminal Grounds Content Pipeline Demonstration

Demonstrates the complete content pipeline workflow:
1. Asset audit and placeholder detection
2. AI-powered asset generation via Hugging Face
3. Unreal Engine integration preparation
4. Quality assurance validation

This script shows the pipeline capabilities without requiring actual Hugging Face API access.
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime

# Add the parent directory to path for imports
sys.path.append(str(Path(__file__).parent))
from TG_ContentPipelineMain import TerminalGroundsContentPipeline

def create_demo_placeholder_assets():
    """Create some demo placeholder assets for testing"""
    ROOT = Path(__file__).resolve().parents[1]
    
    # Create a temporary placeholder asset for demonstration
    demo_dir = ROOT / "Content/TG/Demo"
    demo_dir.mkdir(parents=True, exist_ok=True)
    
    placeholder_files = [
        "placeholder_faction_logo.png",
        "temp_weapon_concept.jpg", 
        "untitled_poster.png",
        "generic_ui_icon.png"
    ]
    
    for filename in placeholder_files:
        placeholder_path = demo_dir / filename
        if not placeholder_path.exists():
            # Create a minimal PNG file (just header)
            with open(placeholder_path, 'wb') as f:
                # Minimal PNG header
                f.write(b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x01\x00\x00\x00\x007n\xf9$\x00\x00\x00\nIDAT\x08\x1dc\xf8\x00\x00\x00\x01\x00\x01')
            print(f"📄 Created demo placeholder: {placeholder_path.relative_to(ROOT)}")
    
    return demo_dir

def demonstrate_pipeline_components():
    """Demonstrate individual pipeline components"""
    print("🔧 COMPONENT DEMONSTRATION")
    print("=" * 50)
    
    # Import and test individual components
    from TG_ContentPipelineAgent import TerminalGroundsContentAgent, AssetCategory
    from TG_HuggingFaceGenerator import HuggingFaceGenerator, ModelStyle, GenerationQuality
    from TG_UnrealEngineIntegrator import TerminalGroundsUnrealIntegrator
    
    # Test content agent
    print("1. Testing Content Agent...")
    content_agent = TerminalGroundsContentAgent()
    
    # Test faction data loading
    print(f"   ✅ Loaded {len(content_agent.faction_data)} factions")
    for faction in content_agent.faction_data.keys():
        print(f"      - {faction}")
    
    # Test art bible loading
    print(f"   ✅ Loaded art bible with {len(content_agent.art_bible)} sections")
    
    # Test HF generator
    print("\n2. Testing Hugging Face Generator...")
    hf_generator = HuggingFaceGenerator(content_agent)
    
    # Test prompt generation
    from TG_HuggingFaceGenerator import GenerationRequest
    sample_request = GenerationRequest(
        category=AssetCategory.FACTION_LOGO,
        style=ModelStyle.VECTOR,
        resolution=(1024, 1024),
        quality=GenerationQuality.HIGH,
        faction="Directorate",
        subject="Directorate faction emblem",
        prompt_template="faction_logo",
        negative_prompts=["photorealistic"],
        output_path=Path("test.png"),
        metadata={"faction": "Directorate"}
    )
    
    prompt = hf_generator.prompt_engine.build_prompt(sample_request)
    print(f"   ✅ Generated prompt: {prompt[:100]}...")
    
    # Test Unreal integrator
    print("\n3. Testing Unreal Engine Integrator...")
    unreal_integrator = TerminalGroundsUnrealIntegrator(content_agent)
    
    # Test asset path generation
    asset_path = unreal_integrator.get_unreal_asset_path(
        AssetCategory.FACTION_LOGO, "Directorate_Logo", "Directorate"
    )
    print(f"   ✅ Generated UE path: {asset_path}")
    
    # Test import script generation
    test_path = Path("test_asset.png")
    script = unreal_integrator.generate_import_script(test_path, AssetCategory.UI_ICON)
    print(f"   ✅ Generated import script ({len(script.split('\\n'))} lines)")
    
    print("\n✅ All components working correctly!")

def run_full_pipeline_demo():
    """Run a complete pipeline demonstration"""
    print("\n🚀 FULL PIPELINE DEMONSTRATION")
    print("=" * 50)
    
    # Create demo placeholder assets
    demo_dir = create_demo_placeholder_assets()
    
    # Create pipeline instance
    config = {
        "audit": {"enabled": True, "scan_on_startup": True},
        "generation": {"enabled": True, "quality": "high", "max_assets_per_run": 5},
        "integration": {"enabled": True, "auto_import": False},
        "quality_assurance": {"enabled": True}
    }
    
    pipeline = TerminalGroundsContentPipeline(config)
    
    # Run the complete pipeline
    try:
        results = pipeline.run_complete_pipeline()
        
        print("\n📊 PIPELINE RESULTS SUMMARY")
        print("=" * 40)
        print(f"Duration: {results.get('duration_seconds', 0):.1f} seconds")
        print(f"Status: {results.get('status', 'unknown')}")
        
        if "phases" in results:
            phases = results["phases"]
            
            if "audit" in phases:
                audit = phases["audit"]
                print(f"\nAudit Phase:")
                print(f"  - Assets scanned: {audit.get('total_assets_scanned', 0)}")
                print(f"  - Assets flagged: {audit.get('flagged_for_replacement', 0)}")
            
            if "generation" in phases:
                gen = phases["generation"]
                print(f"\nGeneration Phase:")
                print(f"  - Assets generated: {gen.get('total_generated', 0)}")
                for category, count in gen.get('categories', {}).items():
                    print(f"    - {category}: {count}")
            
            if "integration" in phases:
                integ = phases["integration"]
                print(f"\nIntegration Phase:")
                print(f"  - Import scripts: {len(integ.get('import_scripts', []))}")
                print(f"  - Template docs: {len(integ.get('template_docs', []))}")
            
            if "qa" in phases:
                qa = phases["qa"]
                print(f"\nQuality Assurance:")
                print(f"  - Style compliance: {'✅' if qa.get('style_compliance') else '❌'}")
                print(f"  - Proper naming: {'✅' if qa.get('proper_naming') else '❌'}")
                print(f"  - Issues found: {len(qa.get('issues_found', []))}")
        
        return True
        
    except Exception as e:
        print(f"❌ Pipeline demo failed: {str(e)}")
        return False
    
    finally:
        # Clean up demo assets
        import shutil
        if demo_dir.exists():
            shutil.rmtree(demo_dir)
            print(f"\n🧹 Cleaned up demo assets: {demo_dir}")

def show_pipeline_capabilities():
    """Show what the pipeline can do"""
    print("🎯 TERMINAL GROUNDS CONTENT PIPELINE CAPABILITIES")
    print("=" * 60)
    
    capabilities = [
        "🔍 Asset Audit System",
        "  • Recursive scanning of all image content folders",
        "  • Placeholder and watermark detection algorithms", 
        "  • Asset categorization (concept art, logos, posters, UI)",
        "  • Priority-based flagging for replacement",
        "",
        "🎨 AI-Powered Asset Generation",
        "  • Hugging Face model integration (Flux 1 Schnell)",
        "  • Terminal Grounds-specific prompt templates",
        "  • Faction-aware generation with art bible compliance",
        "  • Multi-resolution support (512x512 to 2048x2048+)",
        "  • Quality levels: draft, standard, high, premium",
        "",
        "🏗️ Unreal Engine 5.6 Integration", 
        "  • Automated import with correct naming conventions",
        "  • Texture group and compression settings",
        "  • Material instance creation from M_TG_Decal_Master",
        "  • GameplayTags application for UI assets",
        "  • Python script generation for UE5 automation",
        "",
        "🔧 Workflow Automation",
        "  • Complete pipeline orchestration",
        "  • Continuous monitoring mode",
        "  • Quality assurance validation",
        "  • Comprehensive logging and reporting",
        "  • Non-placeholder asset protection",
        "",
        "📊 Asset Categories Supported",
        "  • Faction logos and emblems (1024x1024)",
        "  • Propaganda posters and decals (1024x2048)",
        "  • UI icons and interface elements (512x512)",
        "  • Weapon and vehicle concept art (2048x1024)",
        "  • Biome and environment concepts (2048x1024)",
        "  • General concept art (2048x2048)",
        "",
        "🎭 Terminal Grounds Integration",
        "  • 7 faction support with unique styles",
        "  • Art bible compliance checking",
        "  • Lore-appropriate prompt generation",
        "  • Military sci-fi aesthetic consistency",
        "  • Post-apocalyptic mood alignment"
    ]
    
    for line in capabilities:
        print(line)
    
    print("\n" + "=" * 60)

def main():
    """Main demo entry point"""
    print("Terminal Grounds Content Pipeline Agent - Demo")
    print("Version 1.0.0")
    print("=" * 60)
    
    # Show capabilities
    show_pipeline_capabilities()
    
    # Demonstrate components
    demonstrate_pipeline_components()
    
    # Run full pipeline demo
    success = run_full_pipeline_demo()
    
    if success:
        print("\n🎉 DEMO COMPLETED SUCCESSFULLY!")
        print("=" * 40)
        print("The Terminal Grounds Content Pipeline Agent is ready to:")
        print("• Audit existing assets for placeholder content")
        print("• Generate high-quality replacements via Hugging Face")
        print("• Integrate seamlessly with Unreal Engine 5.6")
        print("• Maintain Terminal Grounds art direction and lore")
        print("• Automate the complete content creation workflow")
        print("\nTo use the pipeline:")
        print("python Tools/TG_ContentPipelineMain.py")
    else:
        print("\n❌ Demo encountered issues. Check logs for details.")

if __name__ == "__main__":
    main()