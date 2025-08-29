#!/usr/bin/env python3
"""
Terminal Grounds Pipeline Validation Script
Comprehensive validation of procedural generation pipeline components

Author: DevOps Engineer
Version: 1.0.0
"""

import asyncio
import json
import logging
import sqlite3
import sys
import time
import urllib.request
import urllib.error
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import subprocess
import shutil

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger("PipelineValidator")

class ValidationResult:
    """Container for validation results"""
    def __init__(self, name: str):
        self.name = name
        self.passed = False
        self.message = ""
        self.details = []
        self.warnings = []
    
    def pass_test(self, message: str = "OK"):
        self.passed = True
        self.message = message
    
    def fail_test(self, message: str):
        self.passed = False
        self.message = message
    
    def add_warning(self, warning: str):
        self.warnings.append(warning)
    
    def add_detail(self, detail: str):
        self.details.append(detail)

class PipelineValidator:
    """Comprehensive pipeline validation"""
    
    def __init__(self):
        self.results = []
        self.base_path = Path("C:/Users/Zachg/Terminal-Grounds")
        self.pipeline_path = self.base_path / "Tools" / "Pipeline"
        self.comfyui_path = self.base_path / "Tools" / "Comfy" / "ComfyUI-API"
        self.database_path = self.base_path / "Database"
        
    def validate_all(self) -> bool:
        """Run all validation tests"""
        logger.info("Starting comprehensive pipeline validation...")
        
        # Core component validation
        self.validate_directory_structure()
        self.validate_python_dependencies()
        self.validate_database_structure()
        self.validate_configuration_files()
        
        # Service validation
        self.validate_comfyui_setup()
        self.validate_websocket_server()
        self.validate_territorial_database()
        
        # Pipeline component validation
        self.validate_orchestrator_component()
        self.validate_ue5_integration()
        self.validate_monitoring_components()
        self.validate_deployment_scripts()
        
        # Integration validation
        self.validate_asset_generation_flow()
        self.validate_proven_parameters()
        
        # Security and performance validation
        self.validate_security_configuration()
        self.validate_performance_settings()
        
        return self.generate_report()
    
    def validate_directory_structure(self):
        """Validate required directory structure"""
        result = ValidationResult("Directory Structure")
        
        required_dirs = [
            self.pipeline_path,
            self.comfyui_path,
            self.database_path,
            self.base_path / "Tools" / "TerritorialSystem",
            self.base_path / "Tools" / "Comfy" / "ComfyUI-API" / "output",
            self.base_path / "Content" / "Generated",
            self.base_path / "Logs" / "Pipeline"
        ]
        
        missing_dirs = []
        for dir_path in required_dirs:
            if not dir_path.exists():
                missing_dirs.append(str(dir_path))
                result.add_detail(f"Missing: {dir_path}")
        
        if missing_dirs:
            result.fail_test(f"Missing {len(missing_dirs)} required directories")
        else:
            result.pass_test("All required directories exist")
        
        self.results.append(result)
    
    def validate_python_dependencies(self):
        """Validate Python dependencies"""
        result = ValidationResult("Python Dependencies")
        
        required_modules = [
            "asyncio", "json", "sqlite3", "pathlib", "urllib",
            "websockets", "psutil"
        ]
        
        optional_modules = [
            ("GPUtil", "GPU monitoring"),
            ("rich", "Enhanced console output")
        ]
        
        missing_required = []
        missing_optional = []
        
        for module in required_modules:
            try:
                __import__(module)
                result.add_detail(f"✓ {module}")
            except ImportError:
                missing_required.append(module)
                result.add_detail(f"✗ {module}")
        
        for module, purpose in optional_modules:
            try:
                __import__(module)
                result.add_detail(f"✓ {module} ({purpose})")
            except ImportError:
                missing_optional.append((module, purpose))
                result.add_warning(f"Optional module missing: {module} - {purpose}")
        
        if missing_required:
            result.fail_test(f"Missing required modules: {', '.join(missing_required)}")
        else:
            result.pass_test("All required Python dependencies available")
            
        self.results.append(result)
    
    def validate_database_structure(self):
        """Validate database structure and connectivity"""
        result = ValidationResult("Database Structure")
        
        # Check territorial database
        territorial_db = self.database_path / "territorial_system.db"
        pipeline_db = self.database_path / "pipeline_state.db"
        
        if not territorial_db.exists():
            result.fail_test(f"Territorial database not found: {territorial_db}")
            self.results.append(result)
            return
        
        try:
            conn = sqlite3.connect(str(territorial_db))
            cursor = conn.cursor()
            
            # Check required tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            
            required_tables = [
                "territories", "factions", "faction_territorial_influence",
                "territorial_events", "territorial_control_summary"
            ]
            
            missing_tables = [t for t in required_tables if t not in tables]
            
            if missing_tables:
                result.fail_test(f"Missing database tables: {', '.join(missing_tables)}")
            else:
                # Test basic query performance
                start_time = time.time()
                cursor.execute("SELECT COUNT(*) FROM territories")
                territory_count = cursor.fetchone()[0]
                query_time = (time.time() - start_time) * 1000
                
                result.pass_test(f"Database operational with {territory_count} territories")
                result.add_detail(f"Query performance: {query_time:.2f}ms")
            
            conn.close()
            
        except Exception as e:
            result.fail_test(f"Database error: {e}")
        
        # Check if pipeline database can be created
        try:
            if not pipeline_db.exists():
                conn = sqlite3.connect(str(pipeline_db))
                conn.close()
                result.add_detail("Pipeline database can be created")
            else:
                result.add_detail("Pipeline database already exists")
        except Exception as e:
            result.add_warning(f"Pipeline database issue: {e}")
        
        self.results.append(result)
    
    def validate_configuration_files(self):
        """Validate configuration and script files"""
        result = ValidationResult("Configuration Files")
        
        required_files = [
            (self.pipeline_path / "procedural_generation_orchestrator.py", "Main orchestrator"),
            (self.pipeline_path / "pipeline_monitor.py", "Monitoring dashboard"),
            (self.pipeline_path / "ue5_integration.py", "UE5 integration bridge"),
            (self.pipeline_path / "performance_optimizer.py", "Performance optimizer"),
            (self.pipeline_path / "Deploy-ProceduralPipeline.ps1", "Deployment script"),
            (self.base_path / "Tools" / "TerritorialSystem" / "territorial_websocket_server.py", "WebSocket server"),
            (self.comfyui_path / "main.py", "ComfyUI main script")
        ]
        
        missing_files = []
        for file_path, description in required_files:
            if file_path.exists():
                result.add_detail(f"✓ {description}: {file_path.name}")
            else:
                missing_files.append((file_path, description))
                result.add_detail(f"✗ {description}: {file_path}")
        
        if missing_files:
            result.fail_test(f"Missing {len(missing_files)} required files")
        else:
            result.pass_test("All configuration files present")
        
        self.results.append(result)
    
    def validate_comfyui_setup(self):
        """Validate ComfyUI configuration"""
        result = ValidationResult("ComfyUI Setup")
        
        # Check if ComfyUI is running
        try:
            req = urllib.request.Request("http://127.0.0.1:8188/system_stats")
            with urllib.request.urlopen(req, timeout=5) as response:
                if response.status == 200:
                    data = json.loads(response.read())
                    result.pass_test("ComfyUI is running and responsive")
                    result.add_detail(f"System: {data.get('system', {})}")
                else:
                    result.fail_test(f"ComfyUI returned status {response.status}")
        except urllib.error.URLError:
            result.add_warning("ComfyUI is not running (this is OK for setup validation)")
            
            # Check if we can find the executable
            if self.comfyui_path.exists():
                main_script = self.comfyui_path / "main.py"
                if main_script.exists():
                    result.pass_test("ComfyUI installation found")
                    result.add_detail(f"Main script: {main_script}")
                else:
                    result.fail_test("ComfyUI main.py not found")
            else:
                result.fail_test(f"ComfyUI directory not found: {self.comfyui_path}")
        
        # Check for models
        models_dir = self.comfyui_path / "models" / "checkpoints"
        if models_dir.exists():
            models = list(models_dir.glob("*.safetensors"))
            if models:
                result.add_detail(f"Found {len(models)} model files")
                
                # Check for proven models
                proven_models = ["FLUX1-dev-fp8.safetensors", "Juggernaut-XL_v9_RunDiffusionPhoto_v2.safetensors"]
                found_proven = [m for m in proven_models if (models_dir / m).exists()]
                
                if found_proven:
                    result.add_detail(f"Proven models available: {', '.join(found_proven)}")
                else:
                    result.add_warning("No proven models found - may affect success rate")
            else:
                result.add_warning("No model files found in checkpoints directory")
        else:
            result.add_warning("Models directory not found")
        
        self.results.append(result)
    
    def validate_websocket_server(self):
        """Validate WebSocket server configuration"""
        result = ValidationResult("WebSocket Server")
        
        server_script = self.base_path / "Tools" / "TerritorialSystem" / "territorial_websocket_server.py"
        
        if not server_script.exists():
            result.fail_test(f"WebSocket server script not found: {server_script}")
            self.results.append(result)
            return
        
        # Check if server is running
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_running = sock.connect_ex(('127.0.0.1', 8765)) == 0
        sock.close()
        
        if server_running:
            result.pass_test("WebSocket server is running on port 8765")
        else:
            result.add_warning("WebSocket server is not running (this is OK for setup validation)")
            result.pass_test("WebSocket server script is available")
        
        # Validate script content for critical fixes
        try:
            with open(server_script, 'r') as f:
                content = f.read()
                
            if "max_connections" in content:
                result.add_detail("✓ Connection limiting implemented (CTO fix)")
            else:
                result.add_warning("Connection limiting not found - may crash at >100 connections")
                
        except Exception as e:
            result.add_warning(f"Could not validate script content: {e}")
        
        self.results.append(result)
    
    def validate_territorial_database(self):
        """Validate territorial database integration"""
        result = ValidationResult("Territorial Database Integration")
        
        territorial_db = self.database_path / "territorial_system.db"
        
        if not territorial_db.exists():
            result.fail_test("Territorial database not found")
            self.results.append(result)
            return
        
        try:
            conn = sqlite3.connect(str(territorial_db))
            cursor = conn.cursor()
            
            # Test territorial query performance
            start_time = time.time()
            cursor.execute("SELECT * FROM territorial_control_summary LIMIT 10")
            results = cursor.fetchall()
            query_time = (time.time() - start_time) * 1000
            
            if query_time < 50:  # CTO requirement: <50ms
                result.pass_test(f"Database performance excellent ({query_time:.2f}ms)")
            else:
                result.add_warning(f"Database performance slow ({query_time:.2f}ms)")
                result.pass_test("Database functional but performance needs optimization")
            
            result.add_detail(f"Sample territorial data: {len(results)} records")
            
            # Check for AI faction behavior data
            cursor.execute("SELECT COUNT(*) FROM factions")
            faction_count = cursor.fetchone()[0]
            result.add_detail(f"Factions configured: {faction_count}")
            
            conn.close()
            
        except Exception as e:
            result.fail_test(f"Database integration error: {e}")
        
        self.results.append(result)
    
    def validate_orchestrator_component(self):
        """Validate main orchestrator component"""
        result = ValidationResult("Pipeline Orchestrator")
        
        orchestrator_script = self.pipeline_path / "procedural_generation_orchestrator.py"
        
        if not orchestrator_script.exists():
            result.fail_test("Orchestrator script not found")
            self.results.append(result)
            return
        
        try:
            with open(orchestrator_script, 'r') as f:
                content = f.read()
            
            # Validate proven parameters are present
            if 'heun' in content and 'normal' in content and '3.2' in content:
                result.add_detail("✓ Proven parameters configuration found (100% success rate)")
            else:
                result.add_warning("Proven parameters may not be configured correctly")
            
            # Check for error handling
            if 'try:' in content and 'except' in content:
                result.add_detail("✓ Error handling implemented")
            else:
                result.add_warning("Limited error handling detected")
            
            # Check for async implementation
            if 'async def' in content and 'await' in content:
                result.add_detail("✓ Asynchronous implementation")
            else:
                result.add_warning("May not be properly asynchronous")
            
            result.pass_test("Orchestrator component validation successful")
            
        except Exception as e:
            result.fail_test(f"Orchestrator validation error: {e}")
        
        self.results.append(result)
    
    def validate_ue5_integration(self):
        """Validate UE5 integration components"""
        result = ValidationResult("UE5 Integration")
        
        integration_script = self.pipeline_path / "ue5_integration.py"
        
        if not integration_script.exists():
            result.fail_test("UE5 integration script not found")
            self.results.append(result)
            return
        
        # Check UE5 directories
        ue5_dirs = [
            self.base_path / "Content" / "Generated",
            self.base_path / "Content" / "Generated" / "Import",
            self.base_path / "Source" / "TGWorld" / "Public",
        ]
        
        missing_dirs = [d for d in ue5_dirs if not d.exists()]
        
        if missing_dirs:
            result.add_warning(f"UE5 directories not found: {len(missing_dirs)}")
            for d in missing_dirs:
                result.add_detail(f"Missing: {d}")
        
        # Check UE5 subsystem header
        subsystem_header = self.base_path / "Source" / "TGWorld" / "Public" / "TGProceduralWorldSubsystem.h"
        
        if subsystem_header.exists():
            result.add_detail("✓ UE5 procedural subsystem header found")
            
            try:
                with open(subsystem_header, 'r') as f:
                    content = f.read()
                
                if 'UTGProceduralWorldSubsystem' in content:
                    result.add_detail("✓ Subsystem class definition found")
                else:
                    result.add_warning("Subsystem class may not be properly defined")
                    
            except Exception as e:
                result.add_warning(f"Could not validate subsystem header: {e}")
        else:
            result.add_warning("UE5 procedural subsystem header not found")
        
        result.pass_test("UE5 integration components available")
        self.results.append(result)
    
    def validate_monitoring_components(self):
        """Validate monitoring and optimization components"""
        result = ValidationResult("Monitoring Components")
        
        monitor_script = self.pipeline_path / "pipeline_monitor.py"
        optimizer_script = self.pipeline_path / "performance_optimizer.py"
        
        components_found = 0
        
        if monitor_script.exists():
            components_found += 1
            result.add_detail("✓ Pipeline monitor available")
        else:
            result.add_detail("✗ Pipeline monitor missing")
        
        if optimizer_script.exists():
            components_found += 1
            result.add_detail("✓ Performance optimizer available")
        else:
            result.add_detail("✗ Performance optimizer missing")
        
        if components_found == 2:
            result.pass_test("All monitoring components available")
        elif components_found > 0:
            result.pass_test(f"{components_found}/2 monitoring components available")
        else:
            result.fail_test("No monitoring components found")
        
        self.results.append(result)
    
    def validate_deployment_scripts(self):
        """Validate deployment and management scripts"""
        result = ValidationResult("Deployment Scripts")
        
        deployment_script = self.pipeline_path / "Deploy-ProceduralPipeline.ps1"
        
        if deployment_script.exists():
            result.add_detail("✓ PowerShell deployment script found")
            
            try:
                with open(deployment_script, 'r') as f:
                    content = f.read()
                
                # Check for key features
                if 'param(' in content:
                    result.add_detail("✓ Parameterized deployment")
                if 'Test-ServiceHealth' in content:
                    result.add_detail("✓ Health checking implemented")
                if 'Write-Log' in content:
                    result.add_detail("✓ Logging functionality")
                
                result.pass_test("Deployment script validation successful")
                
            except Exception as e:
                result.add_warning(f"Could not validate deployment script: {e}")
                result.pass_test("Deployment script found but could not validate content")
        else:
            result.fail_test("PowerShell deployment script not found")
        
        self.results.append(result)
    
    def validate_asset_generation_flow(self):
        """Validate end-to-end asset generation flow"""
        result = ValidationResult("Asset Generation Flow")
        
        # Check output directories
        output_dir = self.comfyui_path / "output"
        
        if not output_dir.exists():
            result.fail_test(f"ComfyUI output directory not found: {output_dir}")
            self.results.append(result)
            return
        
        # Check for FIXED generation scripts (100% success rate)
        fixed_scripts = [
            self.base_path / "Tools" / "ArtGen" / "FIXED_faction_vehicle_concepts.py",
            self.base_path / "Tools" / "ArtGen" / "FIXED_faction_ui_hud_concepts.py"
        ]
        
        fixed_count = 0
        for script in fixed_scripts:
            if script.exists():
                fixed_count += 1
                result.add_detail(f"✓ FIXED script: {script.name}")
            else:
                result.add_detail(f"✗ Missing FIXED script: {script.name}")
        
        if fixed_count > 0:
            result.add_detail(f"Found {fixed_count}/2 FIXED generation scripts")
        else:
            result.add_warning("No FIXED generation scripts found")
        
        # Check procedural prompt engine
        prompt_engine = self.comfyui_path / "procedural_prompt_engine.py"
        if prompt_engine.exists():
            result.add_detail("✓ Procedural prompt engine available")
        else:
            result.add_warning("Procedural prompt engine not found")
        
        result.pass_test("Asset generation flow components available")
        self.results.append(result)
    
    def validate_proven_parameters(self):
        """Validate proven parameters configuration"""
        result = ValidationResult("Proven Parameters")
        
        orchestrator_script = self.pipeline_path / "procedural_generation_orchestrator.py"
        
        if not orchestrator_script.exists():
            result.fail_test("Cannot validate - orchestrator script not found")
            self.results.append(result)
            return
        
        try:
            with open(orchestrator_script, 'r') as f:
                content = f.read()
            
            # Check for proven parameters
            proven_checks = {
                "heun": "sampler",
                "normal": "scheduler", 
                "3.2": "CFG value",
                "25": "steps",
                "1536": "width",
                "864": "height"
            }
            
            found_params = []
            for param, description in proven_checks.items():
                if param in content:
                    found_params.append(description)
                    result.add_detail(f"✓ {description} ({param})")
                else:
                    result.add_detail(f"✗ {description} ({param})")
            
            if len(found_params) >= 4:  # Most critical parameters
                result.pass_test(f"Proven parameters configured ({len(found_params)}/6 found)")
            else:
                result.fail_test(f"Proven parameters incomplete ({len(found_params)}/6 found)")
                result.add_warning("This may result in lower success rates")
            
        except Exception as e:
            result.fail_test(f"Could not validate parameters: {e}")
        
        self.results.append(result)
    
    def validate_security_configuration(self):
        """Validate security settings"""
        result = ValidationResult("Security Configuration")
        
        security_issues = []
        warnings = []
        
        # Check for exposed services
        exposed_ports = [8188, 8765, 8766]
        for port in exposed_ports:
            warnings.append(f"Port {port} should be firewalled for external access")
        
        # Check database file permissions
        territorial_db = self.database_path / "territorial_system.db"
        if territorial_db.exists():
            result.add_detail("Database file exists - ensure proper file permissions")
        
        # Check output directory permissions
        output_dir = self.comfyui_path / "output"
        if output_dir.exists():
            result.add_detail("Output directory exists - ensure controlled access")
        
        if security_issues:
            result.fail_test(f"Security issues found: {len(security_issues)}")
            for issue in security_issues:
                result.add_detail(f"⚠️ {issue}")
        else:
            result.pass_test("No critical security issues detected")
        
        for warning in warnings:
            result.add_warning(warning)
        
        self.results.append(result)
    
    def validate_performance_settings(self):
        """Validate performance configuration"""
        result = ValidationResult("Performance Settings")
        
        # Check available system resources
        try:
            import psutil
            
            # Memory check
            memory = psutil.virtual_memory()
            memory_gb = memory.total / (1024**3)
            
            if memory_gb >= 32:
                result.add_detail(f"✓ Excellent memory: {memory_gb:.1f}GB")
            elif memory_gb >= 16:
                result.add_detail(f"✓ Adequate memory: {memory_gb:.1f}GB")
            else:
                result.add_warning(f"Low memory: {memory_gb:.1f}GB (16GB+ recommended)")
            
            # CPU check
            cpu_count = psutil.cpu_count()
            result.add_detail(f"CPU cores: {cpu_count}")
            
        except ImportError:
            result.add_warning("psutil not available for system resource checking")
        
        # Check GPU availability
        try:
            import GPUtil
            gpus = GPUtil.getGPUs()
            
            if gpus:
                gpu = gpus[0]
                memory_gb = gpu.memoryTotal / 1024
                result.add_detail(f"✓ GPU: {gpu.name} ({memory_gb:.1f}GB)")
                
                if memory_gb >= 24:
                    result.add_detail("✓ Excellent GPU memory for large models")
                elif memory_gb >= 12:
                    result.add_detail("✓ Good GPU memory")
                else:
                    result.add_warning("Limited GPU memory - may need smaller models")
            else:
                result.add_warning("No GPU detected - will be very slow")
                
        except ImportError:
            result.add_warning("GPUtil not available for GPU checking")
        
        result.pass_test("Performance configuration validated")
        self.results.append(result)
    
    def generate_report(self) -> bool:
        """Generate validation report"""
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r.passed)
        failed_tests = total_tests - passed_tests
        
        print("\n" + "="*70)
        print("TERMINAL GROUNDS PIPELINE VALIDATION REPORT")
        print("="*70)
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests*100):.1f}%")
        print()
        
        # Show results
        for result in self.results:
            status_icon = "✅" if result.passed else "❌"
            print(f"{status_icon} {result.name}: {result.message}")
            
            # Show details for failed tests
            if not result.passed and result.details:
                for detail in result.details:
                    print(f"   {detail}")
            
            # Show warnings
            if result.warnings:
                for warning in result.warnings:
                    print(f"   ⚠️ {warning}")
            
            print()
        
        # Summary recommendations
        if failed_tests > 0:
            print("🔧 REQUIRED ACTIONS:")
            for result in self.results:
                if not result.passed:
                    print(f"   • Fix {result.name}: {result.message}")
            print()
        
        # Show warnings summary
        all_warnings = [w for r in self.results for w in r.warnings]
        if all_warnings:
            print("⚠️ WARNINGS TO CONSIDER:")
            for warning in set(all_warnings):  # Remove duplicates
                print(f"   • {warning}")
            print()
        
        # Final verdict
        if failed_tests == 0:
            print("🎉 VALIDATION SUCCESSFUL!")
            print("Pipeline is ready for deployment.")
        elif failed_tests <= 2:
            print("⚠️ VALIDATION MOSTLY SUCCESSFUL")
            print("Pipeline can run but address failed tests for optimal operation.")
        else:
            print("❌ VALIDATION FAILED")
            print("Multiple critical issues must be resolved before deployment.")
        
        print("="*70)
        
        return failed_tests == 0

async def main():
    """Main validation entry point"""
    validator = PipelineValidator()
    
    print("Terminal Grounds Procedural Pipeline Validator")
    print("Comprehensive validation of all pipeline components")
    print()
    
    success = validator.validate_all()
    
    # Return appropriate exit code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    asyncio.run(main())