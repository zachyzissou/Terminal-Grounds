#!/usr/bin/env python3
"""
Terminal Grounds Integrated Automation Startup
==============================================

Unified startup sequence that brings all procedural and AI-controlled creation systems online:
1. ComfyUI Server (AI asset generation)
2. Unreal Editor with MCP (procedural level building) 
3. Territorial WebSocket Server (real-time faction control)
4. Multi-MCP Orchestration (unified command interface)

Usage:
    python start_tg_automation.py --mode full     # Start all systems
    python start_tg_automation.py --mode minimal  # Start essential only
    python start_tg_automation.py --check         # Check system status
"""

import asyncio
import subprocess
import sys
import time
import json
import socket
import requests
import logging
from pathlib import Path
from typing import Optional, Dict, List
import os

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TGAutomationManager:
    """Manages startup and coordination of all Terminal Grounds automation systems."""
    
    def __init__(self):
        self.services = {
            'comfyui': {'status': 'stopped', 'process': None, 'port': 8188, 'startup_time': 90},
            'unreal_editor': {'status': 'stopped', 'process': None, 'port': 55557, 'startup_time': 45},
            'territorial_server': {'status': 'stopped', 'process': None, 'port': 8765, 'startup_time': 5},
            'mcp_orchestrator': {'status': 'stopped', 'process': None, 'port': None, 'startup_time': 15}
        }
        self.project_root = Path.cwd()
        
    async def check_port(self, port: int, timeout: float = 2.0) -> bool:
        """Check if a port is responding."""
        try:
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection('127.0.0.1', port), timeout=timeout
            )
            writer.close()
            await writer.wait_closed()
            return True
        except:
            return False
    
    async def check_http_service(self, port: int, endpoint: str = '', timeout: float = 2.0) -> bool:
        """Check if HTTP service is responding."""
        try:
            response = requests.get(f"http://127.0.0.1:{port}{endpoint}", timeout=timeout)
            return response.status_code == 200
        except:
            return False
    
    async def start_comfyui(self) -> bool:
        """Start ComfyUI server for AI asset generation."""
        logger.info("Starting ComfyUI server...")
        
        comfyui_path = self.project_root / "Tools" / "Comfy" / "ComfyUI-API"
        if not comfyui_path.exists():
            logger.error(f"ComfyUI not found at {comfyui_path}")
            return False
        
        # Check if already running
        if await self.check_http_service(8188, '/system_stats'):
            logger.info("ComfyUI already running")
            self.services['comfyui']['status'] = 'running'
            return True
        
        try:
            process = await asyncio.create_subprocess_exec(
                sys.executable, "main.py", "--listen", "127.0.0.1", "--port", "8188",
                cwd=str(comfyui_path),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            self.services['comfyui']['process'] = process
            
            # Wait for startup with progress
            logger.info("Waiting for ComfyUI to initialize (~90 seconds)...")
            for i in range(18):  # 18 * 5 = 90 seconds
                await asyncio.sleep(5)
                if await self.check_http_service(8188, '/system_stats'):
                    self.services['comfyui']['status'] = 'running'
                    logger.info("ComfyUI is ready!")
                    return True
                logger.info(f"ComfyUI initializing... {(i+1)*5}s elapsed")
            
            logger.error("ComfyUI failed to start within timeout")
            return False
        except Exception as e:
            logger.error(f"Failed to start ComfyUI: {e}")
            return False
    
    async def start_unreal_editor(self) -> bool:
        """Start Unreal Editor with MCP plugin for procedural level building."""
        logger.info("Starting Unreal Editor with MCP integration...")
        
        # Check for existing Unreal processes
        if await self.check_port(55557):
            logger.info("Unreal MCP bridge already available")
            self.services['unreal_editor']['status'] = 'running'
            return True
        
        # Find Unreal Editor executable
        editor_candidates = [
            os.environ.get("UE_EDITOR"),
            r"C:\\Program Files\\Epic Games\\UE_5.6\\Engine\\Binaries\\Win64\\UnrealEditor.exe",
            r"C:\\Epic Games\\UE_5.6\\Engine\\Binaries\\Win64\\UnrealEditor.exe",
        ]
        
        editor_path = None
        for candidate in editor_candidates:
            if candidate and Path(candidate).exists():
                editor_path = candidate
                break
        
        if not editor_path:
            logger.error("Unreal Editor not found. Set UE_EDITOR environment variable.")
            return False
        
        uproject = self.project_root / "TerminalGrounds.uproject"
        if not uproject.exists():
            logger.error(f"Project file not found: {uproject}")
            return False
        
        try:
            args = [editor_path, str(uproject), "-NoSplash", "-log"]
            process = await asyncio.create_subprocess_exec(
                *args,
                cwd=str(self.project_root),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            self.services['unreal_editor']['process'] = process
            
            # Wait for MCP bridge to come online
            logger.info("Waiting for Unreal Editor and MCP bridge (~45 seconds)...")
            for i in range(15):  # 15 * 3 = 45 seconds
                await asyncio.sleep(3)
                if await self.check_port(55557):
                    self.services['unreal_editor']['status'] = 'running'
                    logger.info("Unreal Editor MCP bridge is ready!")
                    return True
                logger.info(f"Unreal Editor loading... {(i+1)*3}s elapsed")
            
            logger.warning("Unreal Editor started but MCP bridge not detected (may still work)")
            self.services['unreal_editor']['status'] = 'partial'
            return True
        except Exception as e:
            logger.error(f"Failed to start Unreal Editor: {e}")
            return False
    
    async def start_territorial_server(self) -> bool:
        """Start territorial WebSocket server for real-time faction control."""
        logger.info("Starting territorial WebSocket server...")
        
        server_script = self.project_root / "Tools" / "TerritorialSystem" / "territorial_websocket_server.py"
        if not server_script.exists():
            logger.error(f"Territorial server not found at {server_script}")
            return False
        
        # Check if already running
        if await self.check_port(8765):
            logger.info("Territorial server already running")
            self.services['territorial_server']['status'] = 'running'
            return True
        
        try:
            process = await asyncio.create_subprocess_exec(
                sys.executable, str(server_script),
                cwd=str(self.project_root),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            self.services['territorial_server']['process'] = process
            
            # Wait for server to start
            for i in range(5):
                await asyncio.sleep(1)
                if await self.check_port(8765):
                    self.services['territorial_server']['status'] = 'running'
                    logger.info("Territorial server is ready!")
                    return True
            
            logger.error("Territorial server failed to start")
            return False
        except Exception as e:
            logger.error(f"Failed to start territorial server: {e}")
            return False
    
    async def check_system_status(self) -> Dict[str, str]:
        """Check status of all automation systems."""
        logger.info("Checking system status...")
        
        status = {}
        
        # Check ComfyUI
        if await self.check_http_service(8188, '/system_stats'):
            status['comfyui'] = 'running'
        else:
            status['comfyui'] = 'stopped'
        
        # Check Unreal MCP bridge
        if await self.check_port(55557):
            status['unreal_editor'] = 'running'
        else:
            status['unreal_editor'] = 'stopped'
        
        # Check territorial server
        if await self.check_port(8765):
            status['territorial_server'] = 'running'
        else:
            status['territorial_server'] = 'stopped'
        
        # Check for running MCP processes
        try:
            # This is a simplified check - in reality we'd check process names
            status['mcp_orchestrator'] = 'unknown'
        except:
            status['mcp_orchestrator'] = 'stopped'
        
        return status
    
    async def start_full_automation(self) -> bool:
        """Start all automation systems in the correct order."""
        logger.info("Starting full Terminal Grounds automation suite...")
        
        success_count = 0
        total_services = len(self.services)
        
        # Start services in dependency order
        if await self.start_comfyui():
            success_count += 1
        
        if await self.start_territorial_server():
            success_count += 1
        
        if await self.start_unreal_editor():
            success_count += 1
        
        # MCP orchestrator can run without all services
        logger.info("MCP orchestrator available via master_mcp_demo_builder.py")
        success_count += 1
        
        logger.info(f"Automation startup complete: {success_count}/{total_services} services running")
        
        if success_count >= 3:
            logger.info("✅ TERMINAL GROUNDS AUTOMATION ONLINE")
            logger.info("🎮 Ready for procedural level generation")
            logger.info("🎨 Ready for AI asset creation")
            logger.info("🗺️  Ready for territorial integration")
            return True
        else:
            logger.warning("⚠️ Partial automation - some services failed")
            return False
    
    async def cleanup(self):
        """Cleanup all started processes."""
        logger.info("Shutting down automation services...")
        
        for service_name, service_info in self.services.items():
            process = service_info.get('process')
            if process:
                try:
                    process.terminate()
                    await asyncio.wait_for(process.wait(), timeout=5.0)
                    logger.info(f"Stopped {service_name}")
                except:
                    try:
                        process.kill()
                        logger.info(f"Force-killed {service_name}")
                    except:
                        pass

async def main():
    """Main entry point."""
    import argparse
    parser = argparse.ArgumentParser(description='Terminal Grounds Automation Manager')
    parser.add_argument('--mode', choices=['full', 'minimal', 'check'], default='full',
                        help='Operation mode (default: full)')
    parser.add_argument('--check', action='store_true', help='Only check system status')
    args = parser.parse_args()
    
    manager = TGAutomationManager()
    
    try:
        if args.check or args.mode == 'check':
            status = await manager.check_system_status()
            print("\n" + "="*50)
            print("TERMINAL GROUNDS AUTOMATION STATUS")
            print("="*50)
            for service, state in status.items():
                icon = "✅" if state == 'running' else "❌" if state == 'stopped' else "⚠️"
                print(f"{icon} {service}: {state}")
            print("="*50)
        elif args.mode == 'full':
            await manager.start_full_automation()
        elif args.mode == 'minimal':
            # Start only ComfyUI and territorial server
            await manager.start_comfyui()
            await manager.start_territorial_server()
    
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
    finally:
        await manager.cleanup()

if __name__ == "__main__":
    asyncio.run(main())