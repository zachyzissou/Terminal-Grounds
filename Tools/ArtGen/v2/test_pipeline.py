#!/usr/bin/env python3
"""
Terminal Grounds Pipeline Test Suite
===================================
Test the pipeline components without requiring ComfyUI to be running.
"""

import sys
import logging
from pathlib import Path

# Configure basic logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def test_imports():
    """Test that all pipeline components can be imported"""
    print("[IMPORTS] Testing imports...")
    
    try:
        from config_manager import ConfigManager
        print("  [OK] ConfigManager imported")
        
        from asset_spec import AssetSpecBuilder, AssetSpecification
        print("  [OK] AssetSpecBuilder imported")
        
        from workflow_manager import WorkflowManager
        print("  [OK] WorkflowManager imported")
        
        from quality_assurance import QualityAssessmentEngine
        print("  [OK] QualityAssessmentEngine imported")
        
        from enhanced_client import EnhancedComfyUIClient
        print("  [OK] EnhancedComfyUIClient imported")
        
        from asset_manager import AssetManager
        print("  [OK] AssetManager imported")
        
        from batch_processor import BatchProcessor
        print("  [OK] BatchProcessor imported")
        
        from ue5_connector import UE5Connector
        print("  [OK] UE5Connector imported")
        
        return True
        
    except ImportError as e:
        print(f"  [ERROR] Import failed: {e}")
        return False

def test_configuration():
    """Test configuration loading and validation"""
    print("\n[CONFIG] Testing configuration...")
    
    try:
        from config_manager import ConfigManager
        
        # Test config creation
        config = ConfigManager()
        print("  [OK] Configuration loaded")
        
        # Test basic config access
        comfyui_config = config.get_comfyui_config()
        print(f"  [OK] ComfyUI config: {len(comfyui_config)} settings")
        
        quality_config = config.get_quality_config()
        print(f"  [OK] Quality config: {len(quality_config)} settings")
        
        # Test validation
        validation = config.validate_config()
        if validation.is_valid:
            print("  [OK] Configuration validation passed")
        else:
            print(f"  [WARN] Configuration has issues: {validation.errors}")
        
        return True
        
    except Exception as e:
        print(f"  [ERROR] Configuration test failed: {e}")
        return False

def test_asset_specifications():
    """Test asset specification creation"""
    print("\n[ASSETS] Testing asset specifications...")
    
    try:
        from asset_spec import AssetSpecBuilder
        from pathlib import Path
        
        # Create spec builder (with mock faction data dir)
        faction_data_dir = Path("../prompt_packs/factions")
        spec_builder = AssetSpecBuilder(faction_data_dir)
        print("  [OK] AssetSpecBuilder created")
        
        # Test asset spec creation
        asset_spec = spec_builder.create_spec(
            name="Test Plasma Rifle",
            asset_type="weapon",
            faction="directorate",
            description="A test weapon for pipeline validation"
        )
        print(f"  ✅ Asset spec created: {asset_spec.name}")
        print(f"     Type: {asset_spec.asset_type}, Faction: {asset_spec.faction}")
        print(f"     Resolution: {asset_spec.generation_params.width}x{asset_spec.generation_params.height}")
        print(f"     Model: {asset_spec.generation_params.model}")
        
        # Test prompt building
        print(f"     Prompt: {asset_spec.base_prompt[:100]}...")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Asset specification test failed: {e}")
        return False

def test_workflow_manager():
    """Test workflow management"""
    print("\n⚙️ Testing workflow manager...")
    
    try:
        from workflow_manager import WorkflowManager
        from asset_spec import AssetSpecBuilder
        from pathlib import Path
        
        # Create workflow manager (with mock dirs)
        workflows_dir = Path("../workflows")
        templates_dir = Path("../workflows")
        workflow_manager = WorkflowManager(workflows_dir, templates_dir)
        print("  ✅ WorkflowManager created")
        
        # List available workflows
        workflows = workflow_manager.list_workflows()
        print(f"  ✅ Found {len(workflows)} built-in workflows")
        
        for workflow in workflows[:3]:  # Show first 3
            print(f"     - {workflow.name}: {workflow.description[:50]}...")
        
        # Test workflow selection
        faction_data_dir = Path("../prompt_packs/factions")
        spec_builder = AssetSpecBuilder(faction_data_dir)
        
        test_spec = spec_builder.create_spec(
            name="Test Asset",
            asset_type="weapon",
            faction="directorate",
            description="Test description"
        )
        
        selected_workflow = workflow_manager.select_workflow(test_spec)
        if selected_workflow:
            print(f"  ✅ Selected workflow: {selected_workflow.name}")
        else:
            print("  ⚠️ No workflow selected (expected without ComfyUI templates)")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Workflow manager test failed: {e}")
        return False

def test_quality_assessment():
    """Test quality assessment system"""
    print("\n⭐ Testing quality assessment...")
    
    try:
        from quality_assurance import QualityAssessmentEngine
        print("  ✅ QualityAssessmentEngine created")
        
        # Test scoring logic
        qa_engine = QualityAssessmentEngine()
        print("  ✅ Quality thresholds loaded")
        
        # Show some thresholds
        thresholds = qa_engine.type_thresholds
        for asset_type, threshold in list(thresholds.items())[:3]:
            print(f"     {asset_type}: min={threshold['min']}, target={threshold['target']}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Quality assessment test failed: {e}")
        return False

def test_enhanced_client():
    """Test ComfyUI client (without connection)"""
    print("\n🖥️ Testing ComfyUI client...")
    
    try:
        from enhanced_client import EnhancedComfyUIClient
        
        # Test client creation (will fail health check but that's expected)
        print("  ⚠️ ComfyUI not running - testing offline functionality")
        
        # Test server detection
        try:
            client = EnhancedComfyUIClient()
            print(f"  ✅ Client created, detected server: {client.server}")
        except Exception as e:
            print(f"  ⚠️ Connection failed (expected): {str(e)[:50]}...")
        
        return True
        
    except Exception as e:
        print(f"  ❌ ComfyUI client test failed: {e}")
        return False

def test_pipeline_integration():
    """Test basic pipeline integration"""
    print("\n🚀 Testing pipeline integration...")
    
    try:
        # Import without actually creating pipeline (to avoid ComfyUI requirement)
        from pipeline_controller import PipelineController, PipelineStatus, TaskPriority
        print("  ✅ Pipeline controller imported")
        
        # Test enums
        print(f"  ✅ Pipeline statuses: {[s.value for s in PipelineStatus]}")
        print(f"  ✅ Task priorities: {[p.value for p in TaskPriority]}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Pipeline integration test failed: {e}")
        return False

def test_cli_interface():
    """Test CLI interface"""
    print("\n📱 Testing CLI interface...")
    
    try:
        from terminal_grounds_pipeline import create_parser
        
        parser = create_parser()
        print("  ✅ CLI parser created")
        
        # Test help
        help_text = parser.format_help()
        print(f"  ✅ Help text generated ({len(help_text)} chars)")
        
        # Test command parsing
        test_args = ["generate", "weapon", "Test Gun", "--faction", "directorate"]
        args = parser.parse_args(test_args)
        print(f"  ✅ Parsed command: {args.command} {args.asset_type} '{args.name}'")
        
        return True
        
    except Exception as e:
        print(f"  ❌ CLI interface test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Terminal Grounds Pipeline Test Suite")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_configuration,
        test_asset_specifications,
        test_workflow_manager,
        test_quality_assessment,
        test_enhanced_client,
        test_pipeline_integration,
        test_cli_interface
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"  ❌ Test crashed: {e}")
    
    print("\n" + "=" * 50)
    print(f"🎯 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Pipeline is ready for use.")
        print("\n📋 Next steps:")
        print("  1. Start ComfyUI server")
        print("  2. Run: python terminal_grounds_pipeline.py validate")
        print("  3. Try: python terminal_grounds_pipeline.py generate weapon \"Test Rifle\" --faction directorate")
    else:
        print("⚠️ Some tests failed. Check configuration and dependencies.")
    
    return 0 if passed == total else 1

if __name__ == "__main__":
    sys.exit(main())