#!/usr/bin/env python3
"""
Start All MCP Servers for Terminal Grounds
==========================================

This script starts all available MCP servers in the correct order and configuration.
"""

import subprocess
import time
import sys
from pathlib import Path
import logging
import os

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def start_unreal_mcp_kvick_bridge():
    """Start the Unreal MCP kvick bridge (stdio) which connects to the UE plugin on TCP 13377."""
    try:
        logger.info("Starting Unreal MCP kvick bridge (stdio → UE TCP 13377)...")
        cwd = Path.cwd() / "kvick-UnrealMCP" / "MCP"

        process = subprocess.Popen(
            [sys.executable, "unreal_mcp_bridge.py"],
            cwd=cwd,
            stdin=subprocess.PIPE,  # keep stdin open for stdio transport
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if sys.platform == "win32" else 0,
        )

        time.sleep(3)

        if process.poll() is None:
            logger.info("✓ Unreal MCP kvick bridge started (PID: %s)", process.pid)
            return process
        else:
            stderr = process.stderr.read().decode(errors="ignore")
            logger.error("✗ Unreal MCP kvick bridge failed to start: %s", stderr[:500])
            return None

    except Exception as e:
        logger.error("✗ Failed to start Unreal MCP kvick bridge: %s", e)
        return None

def start_binary_reader_mcp():
    """Start the Binary Reader MCP server."""
    try:
        logger.info("Starting Binary Reader MCP server...")
        cwd = Path.cwd() / "binary-reader-mcp"

        process = subprocess.Popen(
            [sys.executable, "main.py"],
            cwd=cwd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if sys.platform == "win32" else 0,
        )

        time.sleep(2)

        if process.poll() is None:
            logger.info("✓ Binary Reader MCP server started (PID: {})".format(process.pid))
            return process
        else:
            stderr = process.stderr.read().decode()
            logger.error(f"✗ Binary Reader MCP server failed: {stderr}")
            return None

    except Exception as e:
        logger.error(f"✗ Failed to start Binary Reader MCP: {e}")
        return None

def start_3d_mcp():
    """Start the 3D MCP server."""
    try:
        logger.info("Starting 3D MCP server...")
        cwd = Path.cwd() / "3d-mcp"

        # Try to use the compiled JavaScript version first
        js_file = cwd / "index.js"
        if js_file.exists():
            process = subprocess.Popen(
                ["node", "index.js"],
                cwd=cwd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if sys.platform == "win32" else 0,
            )

            time.sleep(2)

            if process.poll() is None:
                logger.info("✓ 3D MCP server started (PID: {})".format(process.pid))
                return process
            else:
                stderr = process.stderr.read().decode(errors="ignore")
                logger.warning(f"⚠ 3D MCP index.js exited early: {stderr[:300]}")

                # Fallback 1: try ts-node ESM loader if available
                ts_entry = cwd / "index.ts"
                ts_node_pkg = cwd / "node_modules" / "ts-node"
                if ts_entry.exists() and ts_node_pkg.exists():
                    logger.info("Attempting ts-node ESM fallback for 3D MCP...")
                    process_ts = subprocess.Popen(
                        ["node", "--loader", "ts-node/esm", "index.ts"],
                        cwd=cwd,
                        stdin=subprocess.PIPE,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if sys.platform == "win32" else 0,
                    )
                    time.sleep(2)
                    if process_ts.poll() is None:
                        logger.info("✓ 3D MCP (ts-node) started (PID: %s)", process_ts.pid)
                        return process_ts
                    else:
                        stderr2 = process_ts.stderr.read().decode(errors="ignore")
                        logger.error("✗ 3D MCP ts-node fallback failed: %s", stderr2[:300])
                        # Fall through to Bun fallback
                # Fallback 2: try Bun to run TypeScript directly
                if (cwd / "index.ts").exists():
                    logger.info("Attempting Bun fallback for 3D MCP (running index.ts)...")
                    try:
                        process_bun = subprocess.Popen(
                            ["bun", "index.ts"],
                            cwd=cwd,
                            stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if sys.platform == "win32" else 0,
                        )
                        time.sleep(2)
                        if process_bun.poll() is None:
                            logger.info("✓ 3D MCP (bun) started (PID: %s)", process_bun.pid)
                            return process_bun
                        else:
                            stderr3 = process_bun.stderr.read().decode(errors="ignore")
                            logger.error("✗ 3D MCP bun fallback failed: %s", stderr3[:300])
                    except FileNotFoundError:
                        logger.error("✗ Bun is not installed or not on PATH; cannot run bun fallback for 3D MCP")
                logger.error("✗ 3D MCP could not start (no working JS and no ts-node/bun fallback)")
                return None
        else:
            logger.warning("⚠ 3D MCP: index.js not found, skipping")
            return None

    except Exception as e:
        logger.error(f"✗ Failed to start 3D MCP: {e}")
        return None

def start_unreal_blender_mcp():
    """Start the Unreal-Blender MCP server."""
    try:
        logger.info("Starting Unreal-Blender MCP server...")
        cwd = Path.cwd() / "unreal-blender-mcp"
        # Ensure blender_mcp can be imported from blender-mcp-integration/src
        env = dict(**os.environ)
        blender_src = str((Path.cwd() / "blender-mcp-integration" / "src").resolve())
        existing = env.get("PYTHONPATH", "")
        sep = ";" if sys.platform == "win32" else ":"
        env["PYTHONPATH"] = blender_src + (sep + existing if existing else "")

        process = subprocess.Popen(
            [sys.executable, "main.py", "--port", "8300"],
            cwd=cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if sys.platform == "win32" else 0,
        )

        time.sleep(3)

        if process.poll() is None:
            logger.info("✓ Unreal-Blender MCP server started (PID: {})".format(process.pid))
            return process
        else:
            stderr = process.stderr.read().decode()
            logger.warning(f"⚠ Unreal-Blender MCP has issues: {stderr[:200]}...")
            return None

    except Exception as e:
        logger.error(f"✗ Failed to start Unreal-Blender MCP: {e}")
        return None

def start_unreal_mcp_python():
    """Start the Unreal MCP Python server (stdio) that talks to UE TCP 55557."""
    try:
        logger.info("Starting Unreal MCP (Python stdio → UE TCP 55557)...")
        cwd = Path.cwd() / "unreal-mcp" / "Python"
        entry = cwd / "unreal_mcp_server.py"
        if not entry.exists():
            logger.warning("⚠ Unreal MCP Python server not found at %s", entry)
            return None
        process = subprocess.Popen(
            [sys.executable, str(entry)],
            cwd=cwd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if sys.platform == "win32" else 0,
        )
        time.sleep(2)
        if process.poll() is None:
            logger.info("✓ Unreal MCP (Python) started (PID: %s)", process.pid)
            return process
        else:
            stderr = process.stderr.read().decode(errors="ignore")
            logger.warning("⚠ Unreal MCP (Python) exit: %s", stderr[:500])
            return None
    except Exception as e:
        logger.error("✗ Failed to start Unreal MCP (Python): %s", e)
        return None

def start_unreal_mcp_flopperam():
    """Start the Flopperam Advanced Unreal MCP (stdio)."""
    try:
        logger.info("Starting Flopperam Unreal MCP Advanced (stdio)...")
        cwd = Path.cwd() / "flopperam-unreal-mcp" / "Python"
        entry = cwd / "unreal_mcp_server_advanced.py"
        if not entry.exists():
            logger.warning("⚠ Flopperam Unreal MCP Advanced not found at %s", entry)
            return None
        process = subprocess.Popen(
            [sys.executable, str(entry)],
            cwd=cwd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if sys.platform == "win32" else 0,
        )
        time.sleep(2)
        if process.poll() is None:
            logger.info("✓ Flopperam Unreal MCP Advanced started (PID: %s)", process.pid)
            return process
        else:
            stderr = process.stderr.read().decode(errors="ignore")
            logger.warning("⚠ Flopperam Unreal MCP Advanced exit: %s", stderr[:500])
            return None
    except Exception as e:
        logger.error("✗ Failed to start Flopperam Unreal MCP Advanced: %s", e)
        return None

def start_unreal_mcp_chong():
    """Start the Chongdashu Unreal MCP (stdio)."""
    try:
        logger.info("Starting Chongdashu Unreal MCP (stdio)...")
        cwd = Path.cwd() / "chongdashu-unreal-mcp-complete" / "Python"
        entry = cwd / "unreal_mcp_server.py"
        if not entry.exists():
            logger.warning("⚠ Chongdashu Unreal MCP not found at %s", entry)
            return None
        process = subprocess.Popen(
            [sys.executable, str(entry)],
            cwd=cwd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if sys.platform == "win32" else 0,
        )
        time.sleep(2)
        if process.poll() is None:
            logger.info("✓ Chongdashu Unreal MCP started (PID: %s)", process.pid)
            return process
        else:
            stderr = process.stderr.read().decode(errors="ignore")
            logger.warning("⚠ Chongdashu Unreal MCP exit: %s", stderr[:500])
            return None
    except Exception as e:
        logger.error("✗ Failed to start Chongdashu Unreal MCP: %s", e)
        return None

def start_blender_mcp_integration():
    """Start the Blender MCP Integration (stdio)."""
    try:
        logger.info("Starting Blender MCP Integration (stdio)...")
        cwd = Path.cwd() / "blender-mcp-integration"
        entry = cwd / "main.py"
        if not entry.exists():
            logger.warning("⚠ Blender MCP Integration not found at %s", entry)
            return None
        # Ensure local src is importable as blender_mcp
        env = dict(**os.environ)
        blender_src = str((cwd / "src").resolve())
        existing = env.get("PYTHONPATH", "")
        sep = ";" if sys.platform == "win32" else ":"
        env["PYTHONPATH"] = blender_src + (sep + existing if existing else "")
        process = subprocess.Popen(
            [sys.executable, str(entry)],
            cwd=cwd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if sys.platform == "win32" else 0,
        )
        time.sleep(2)
        if process.poll() is None:
            logger.info("✓ Blender MCP Integration started (PID: %s)", process.pid)
            return process
        else:
            stderr = process.stderr.read().decode(errors="ignore")
            logger.warning("⚠ Blender MCP Integration exit: %s", stderr[:500])
            return None
    except Exception as e:
        logger.error("✗ Failed to start Blender MCP Integration: %s", e)
        return None

def start_maya_mcp_integration():
    """Start the Maya MCP Integration (stdio). Requires Maya to be listening on its command port for full functionality."""
    try:
        logger.info("Starting Maya MCP Integration (stdio)...")
        cwd = Path.cwd() / "maya-mcp-integration"
        entry = cwd / "src" / "maya_mcp_server.py"
        if not entry.exists():
            logger.warning("⚠ Maya MCP Integration not found at %s", entry)
            return None
        process = subprocess.Popen(
            [sys.executable, str(entry)],
            cwd=cwd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if sys.platform == "win32" else 0,
        )
        time.sleep(2)
        if process.poll() is None:
            logger.info("✓ Maya MCP Integration started (PID: %s)", process.pid)
            return process
        else:
            stderr = process.stderr.read().decode(errors="ignore")
            logger.warning("⚠ Maya MCP Integration exit: %s", stderr[:500])
            return None
    except Exception as e:
        logger.error("✗ Failed to start Maya MCP Integration: %s", e)
        return None

def start_unity_mcp_server():
    """Start the Unity MCP Node server (stdio)."""
    try:
        logger.info("Starting Unity MCP server (Node stdio)...")
        cwd = Path.cwd() / "unity-mcp-integration" / "Server~" / "build"
        entry = cwd / "index.js"
        if not entry.exists():
            logger.warning("⚠ Unity MCP build/index.js not found at %s", entry)
            return None
        process = subprocess.Popen(
            ["node", str(entry)],
            cwd=cwd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if sys.platform == "win32" else 0,
        )
        time.sleep(2)
        if process.poll() is None:
            logger.info("✓ Unity MCP server started (PID: %s)", process.pid)
            return process
        else:
            stderr = process.stderr.read().decode(errors="ignore")
            logger.warning("⚠ Unity MCP server exit: %s", stderr[:500])
            return None
    except Exception as e:
        logger.error("✗ Failed to start Unity MCP server: %s", e)
        return None

def main():
    """Start all MCP servers."""
    logger.info("🚀 Starting all Terminal Grounds MCP servers...")

    processes = {}

    # Start each server
    processes['unreal-mcp-kvick-bridge'] = start_unreal_mcp_kvick_bridge()
    processes['unreal-mcp-python'] = start_unreal_mcp_python()
    processes['unreal-mcp-flopperam'] = start_unreal_mcp_flopperam()
    processes['unreal-mcp-chong'] = start_unreal_mcp_chong()
    processes['binary-reader-mcp'] = start_binary_reader_mcp()
    processes['3d-mcp'] = start_3d_mcp()
    processes['unreal-blender-mcp'] = start_unreal_blender_mcp()
    processes['blender-mcp-integration'] = start_blender_mcp_integration()
    processes['maya-mcp-integration'] = start_maya_mcp_integration()
    processes['unity-mcp'] = start_unity_mcp_server()

    # Summary
    running = [name for name, proc in processes.items() if proc is not None]
    failed = [name for name, proc in processes.items() if proc is None]

    print("\n" + "="*50)
    print("📊 MCP SERVER STARTUP SUMMARY")
    print("="*50)

    print(f"✅ Running servers ({len(running)}/{len(processes)}):")
    for server in running:
        pid = processes[server].pid if processes[server] else "N/A"
        print(f"   • {server} (PID: {pid})")

    if failed:
        print(f"\n❌ Failed servers ({len(failed)}/{len(processes)}):")
        for server in failed:
            print(f"   • {server}")

    print(f"\n🎯 {len(running)}/{len(processes)} MCP servers operational")

    if len(running) >= 6:
        print("\n✅ SUCCESS: Multiple MCP servers running!")
        print("You can now run: python master_mcp_demo_builder.py")
    elif len(running) == 1:
        print("\n⚠️  PARTIAL: Only one MCP server running")
    else:
        print("\n❌ FAILED: No MCP servers started successfully")

    return processes

if __name__ == "__main__":
    # Check we're in the right directory
    if not Path("TerminalGrounds.uproject").exists():
        print("❌ Please run this script from the Terminal Grounds root directory")
        sys.exit(1)

    processes = main()

    # Keep the script running to maintain the processes
    try:
        print("\n🔄 Press Ctrl+C to stop all servers and exit")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Stopping all MCP servers...")
        for name, process in processes.items():
            if process:
                try:
                    process.terminate()
                    process.wait(timeout=5)
                    print(f"✓ Stopped {name}")
                except:
                    try:
                        process.kill()
                        print(f"✓ Force stopped {name}")
                    except:
                        pass
        print("👋 All servers stopped. Goodbye!")
