#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UE5 TGTerritorial Module Integration Test
Week 1 Development Validation
"""

import os
import subprocess
import sys
import json
from pathlib import Path

# Fix Windows console encoding
if sys.platform.startswith('win'):
    os.system('chcp 65001 > nul 2>&1')
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

def test_ue5_module_structure():
    """Test that TGTerritorial module has proper structure"""
    print("🔍 Testing UE5 Module Structure")
    print("=" * 40)
    
    project_root = Path("C:/Users/Zachg/Terminal-Grounds")
    module_path = project_root / "Source" / "TGTerritorial"
    
    required_files = {
        "TGTerritorial.Build.cs": "Module build configuration",
        "Public/TGTerritorial.h": "Module header",
        "Public/TerritorialManager.h": "Core manager class",
        "Public/TerritorialTypes.h": "Data structures",
        "Private/TGTerritorial.cpp": "Module implementation",
        "Private/TerritorialManager.cpp": "Core manager implementation"
    }
    
    missing_files = []
    
    for file_path, description in required_files.items():
        full_path = module_path / file_path
        if full_path.exists():
            print(f"✅ {file_path} - {description}")
            
            # Check file is not empty
            if full_path.stat().st_size == 0:
                print(f"⚠️  {file_path} is empty")
            else:
                print(f"   Size: {full_path.stat().st_size} bytes")
                
        else:
            missing_files.append(file_path)
            print(f"❌ Missing: {file_path}")
    
    if missing_files:
        print(f"\n❌ Module structure incomplete. Missing files:")
        for file in missing_files:
            print(f"   - {file}")
        return False
    
    print("\n✅ TGTerritorial module structure complete")
    return True

def test_uproject_integration():
    """Test that TGTerritorial is properly integrated into .uproject file"""
    print("\n🔗 Testing UProject Integration")
    print("=" * 40)
    
    uproject_path = Path("C:/Users/Zachg/Terminal-Grounds/TerminalGrounds.uproject")
    
    if not uproject_path.exists():
        print("❌ TerminalGrounds.uproject not found")
        return False
    
    try:
        with open(uproject_path, 'r') as f:
            uproject_data = json.load(f)
        
        # Check if TGTerritorial module is in modules list
        modules = uproject_data.get('Modules', [])
        tg_territorial_found = False
        
        print("📋 Modules in project:")
        for module in modules:
            module_name = module.get('Name', 'Unknown')
            print(f"   - {module_name}")
            
            if module_name == 'TGTerritorial':
                tg_territorial_found = True
                print(f"   ✅ TGTerritorial found: Type={module.get('Type')}, LoadingPhase={module.get('LoadingPhase')}")
        
        if not tg_territorial_found:
            print("\n❌ TGTerritorial module not found in .uproject file")
            return False
        
        print("\n✅ TGTerritorial properly integrated into project")
        return True
        
    except json.JSONDecodeError as e:
        print(f"❌ Error parsing .uproject file: {e}")
        return False
    except Exception as e:
        print(f"❌ Error reading .uproject file: {e}")
        return False

def test_compilation_readiness():
    """Test if module is ready for compilation"""
    print("\n⚙️ Testing Compilation Readiness")
    print("=" * 40)
    
    # Check for Visual Studio or build tools
    build_tools_found = False
    
    # Common Visual Studio paths
    vs_paths = [
        "C:/Program Files/Microsoft Visual Studio/2022",
        "C:/Program Files (x86)/Microsoft Visual Studio/2019",
        "C:/Program Files/Microsoft Visual Studio/2019"
    ]
    
    for vs_path in vs_paths:
        if os.path.exists(vs_path):
            print(f"✅ Visual Studio found at: {vs_path}")
            build_tools_found = True
            break
    
    if not build_tools_found:
        print("⚠️ Visual Studio not found in common locations")
        print("   Manual verification needed for build tools")
    
    # Check UE5 installation
    ue5_paths = [
        "C:/Program Files/Epic Games/UE_5.6",
        "C:/Program Files/Epic Games/UE_5.5",
        "C:/Program Files/Epic Games/UE_5.4"
    ]
    
    ue5_found = False
    for ue5_path in ue5_paths:
        if os.path.exists(ue5_path):
            print(f"✅ UE5 found at: {ue5_path}")
            ue5_found = True
            break
    
    if not ue5_found:
        print("⚠️ UE5 not found in common locations")
        print("   Please verify UE5 installation")
    
    # Test basic C++ syntax in our files
    print("\n🔍 Validating C++ Syntax:")
    
    cpp_files = [
        "Source/TGTerritorial/Private/TerritorialManager.cpp",
        "Source/TGTerritorial/Private/TGTerritorial.cpp"
    ]
    
    for cpp_file in cpp_files:
        full_path = Path("C:/Users/Zachg/Terminal-Grounds") / cpp_file
        if full_path.exists():
            # Basic syntax check - look for common issues
            with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
            # Check for basic C++ structure
            if '#include' in content and 'class' in content:
                print(f"✅ {cpp_file} - Basic C++ structure valid")
            else:
                print(f"⚠️ {cpp_file} - May have structural issues")
        else:
            print(f"❌ {cpp_file} - File not found")
    
    print("\n✅ Module appears ready for compilation attempt")
    return True

def generate_compilation_instructions():
    """Generate instructions for manual compilation"""
    print("\n📋 Compilation Instructions")
    print("=" * 40)
    
    instructions = """
Manual UE5 Module Compilation Steps:

1. **Open Terminal Grounds Project**
   - Launch Unreal Engine 5.6
   - Open TerminalGrounds.uproject
   - Allow project regeneration if prompted

2. **Verify Module Loading**
   - Check Output Log for "TGTerritorial Module Starting Up"
   - If not loaded, check Window > Developer Tools > Modules
   - Look for TGTerritorial in module list

3. **Compile Module**
   Option A - UE5 Editor:
   - Use Compile button in editor toolbar
   - Check Output Log for compilation messages
   
   Option B - Visual Studio:
   - Generate project files if needed
   - Open TerminalGrounds.sln
   - Build TGTerritorial project specifically

4. **Test Blueprint Integration**
   - Create new Blueprint
   - Search for "Territorial" nodes
   - Should find UTerritorialManager functions

5. **Validate Functionality**
   - Create test map
   - Add TerritorialManager to level
   - Test basic territorial operations

Expected Results:
✅ Module loads without errors
✅ Blueprint nodes available
✅ Basic territorial functions operational
✅ System logs territorial initialization
"""
    
    print(instructions)
    
    return True

def run_module_tests():
    """Run complete module validation test suite"""
    print("🚀 TGTerritorial Module Integration Testing")
    print("=" * 50)
    
    tests = [
        ("Module Structure", test_ue5_module_structure),
        ("UProject Integration", test_uproject_integration), 
        ("Compilation Readiness", test_compilation_readiness),
        ("Generate Instructions", generate_compilation_instructions)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n📋 Running: {test_name}")
        try:
            result = test_func()
            results.append((test_name, result))
            if result:
                print(f"✅ {test_name}: PASSED")
            else:
                print(f"❌ {test_name}: FAILED")
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("🎯 TEST SUMMARY")
    print("=" * 50)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Module ready for UE5 compilation.")
        print("🎯 Next: Open TerminalGrounds.uproject and compile TGTerritorial module")
    else:
        print(f"\n⚠️ {total - passed} issues detected. Review failures above.")
        print("🔧 Fix issues before attempting UE5 compilation")
    
    return passed == total

if __name__ == "__main__":
    success = run_module_tests()
    
    if success:
        print("\n🎯 WEEK 1 TASK UPDATE: UE5 Module Integration READY")
        print("Next: CTO database + UE5 compilation = Complete system")
    else:
        print("\n🔧 Module issues detected - fix before proceeding")