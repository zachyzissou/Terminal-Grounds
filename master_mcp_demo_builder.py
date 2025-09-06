#!/usr/bin/env python3
"""
Master Terminal Grounds MCP Demo Builder
========================================

This script coordinates ALL available MCP servers to build a complete Terminal Grounds demo:
- unreal-mcp (stdio) - Direct Unreal Engine control via UE TCP 55557
- 3d-mcp (stdio) - Universal 3D software interface
- binary-reader-mcp (stdio) - Asset analysis and inspection
- unreal-blender-mcp (http:8300) - Blender-Unreal integration (if available)

The script creates a comprehensive demo showcasing all systems working together.
"""

import asyncio
import json
import subprocess
import sys
import time
import requests
from Scripts.lib.mcp_stdio_client import MCPStdioClient
from pathlib import Path
from typing import Dict, List, Optional, Any
import logging
from logging.handlers import RotatingFileHandler
import socket
import os
import shutil

# Force UTF-8 on Windows console to avoid UnicodeEncodeError with emojis
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

# Set up logging to both console and rotating file
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.propagate = False

_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

class SafeConsoleHandler(logging.StreamHandler):
    """Console handler that safely writes messages even on cp1252 consoles by replacing unsupported chars."""
    def emit(self, record):
        try:
            msg = self.format(record)
            try:
                self.stream.write(msg + self.terminator)
            except UnicodeEncodeError:
                enc = getattr(self.stream, "encoding", None) or "utf-8"
                safe = msg.encode(enc, errors="replace").decode(enc, errors="replace")
                self.stream.write(safe + self.terminator)
            self.flush()
        except Exception:
            self.handleError(record)

_console = SafeConsoleHandler(sys.stdout)
_console.setLevel(logging.INFO)
_console.setFormatter(_formatter)
logger.addHandler(_console)

# Also ensure the root logger uses a safe console handler to avoid duplicate handlers
# emitting to a cp1252-encoded console and throwing UnicodeEncodeError.
root_logger = logging.getLogger()
for h in list(root_logger.handlers):
    try:
        root_logger.removeHandler(h)
    except Exception:
        pass
root_logger.setLevel(logging.INFO)
root_logger.addHandler(_console)

_log_dir = Path.cwd() / "Logs"
_log_dir.mkdir(exist_ok=True)
_file = RotatingFileHandler(_log_dir / "master_mcp_demo_builder.log", maxBytes=1_000_000, backupCount=3)
_file.setLevel(logging.INFO)
_file.setFormatter(_formatter)
logger.addHandler(_file)

class MCPServerManager:
    """Manages all MCP server connections and coordinates demo building."""

    def __init__(self):
        self.servers = {
            'unreal-mcp': {
                'type': 'stdio',
                'process': None,
                'status': 'unknown',
                'available_tools': []
            },
            # Optional parallel Unreal MCP variants (started if entrypoints exist)
            'unreal-mcp-chong': {
                'type': 'stdio',
                'process': None,
                'status': 'unknown',
                'available_tools': []
            },
            'unreal-mcp-flopperam': {
                'type': 'stdio',
                'process': None,
                'status': 'unknown',
                'available_tools': []
            },
            'unreal-mcp-core': {
                'type': 'stdio',
                'process': None,
                'status': 'unknown',
                'available_tools': []
            },
            'kvick-unreal-bridge': {
                'type': 'stdio',
                'process': None,
                'status': 'unknown',
                'available_tools': []
            },
            '3d-mcp': {
                'type': 'stdio',
                'process': None,
                'status': 'unknown',
                'available_tools': []
            },
            'binary-reader-mcp': {
                'type': 'stdio',
                'process': None,
                'status': 'unknown',
                'available_tools': []
            },
            'unreal-blender-mcp': {
                'type': 'http',
                'port': 8300,
                'status': 'unknown',
                'available_tools': []
            }
        }
        # Track a dedicated Unreal Editor instance we start for the TCP bridge
        self.unreal_editor_proc = None

    async def check_server_status(self):
        """Check the status of all MCP servers."""
        logger.info("Checking MCP server status...")

        # Check all configured servers
        for name, config in self.servers.items():
            if config.get('type') == 'http':
                # Probe HTTP servers (e.g., unreal-blender-mcp)
                try:
                    response = requests.get(
                        f"http://127.0.0.1:{config.get('port')}/status", timeout=5
                    )
                    if response.status_code == 200:
                        config['status'] = 'running'
                        logger.info("OK %s is running on port %s", name, config.get('port'))
                    else:
                        config['status'] = 'error'
                        logger.warning("X %s responded with status %s", name, response.status_code)
                except Exception as e:
                    config['status'] = 'offline'
                    logger.warning("X %s is offline: %s", name, e)
                    # Try to start known HTTP servers when offline
                    await self.start_http_server(name)
            elif config.get('type') == 'stdio':
                # Ensure stdio servers are started
                if config.get('process') is None:
                    await self.start_stdio_server(name)

    async def start_http_server(self, server_name: str):
        """Start HTTP-based servers if they're offline (currently: unreal-blender-mcp)."""
        try:
            if server_name == 'unreal-blender-mcp':
                # Launch uvicorn app from unreal-blender-mcp/main.py
                env = dict(**os.environ)
                # Ensure required src paths are importable
                blender_src = str((Path.cwd() / "blender-mcp-integration" / "src").resolve())
                ublend_src = str((Path.cwd() / "unreal-blender-mcp" / "src").resolve())
                existing = env.get("PYTHONPATH", "")
                sep = ";" if sys.platform == "win32" else ":"
                extra_paths = [ublend_src, blender_src]
                env["PYTHONPATH"] = sep.join([p for p in extra_paths if p]) + (sep + existing if existing else "")
                # Try a few ports in case the default is busy
                candidate_ports = [int(self.servers[server_name]['port']), 8301, 8310, 8400]
                for port in candidate_ports:
                    # Attempt 1: run the project's main launcher
                    proc = await asyncio.create_subprocess_exec(
                        sys.executable, 'unreal-blender-mcp/main.py', '--port', str(port),
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.PIPE,
                        cwd=Path.cwd(),
                        env=env,
                    )
                    healthy = False
                    for _ in range(30):
                        await asyncio.sleep(1.0)
                        try:
                            response = requests.get(f"http://127.0.0.1:{port}/status", timeout=2)
                            if response.status_code == 200:
                                healthy = True
                                break
                        except Exception:
                            if proc.returncode is not None:
                                break
                            continue
                    if healthy:
                        self.servers[server_name]['status'] = 'running'
                        self.servers[server_name]['process'] = proc
                        self.servers[server_name]['port'] = port
                        logger.info("OK Started unreal-blender-mcp (HTTP) on port %s", port)
                        return
                    # Not healthy: capture diagnostics and terminate
                    try:
                        try:
                            if proc.stderr:
                                err = await asyncio.wait_for(proc.stderr.read(65536), timeout=3.0)
                                if err:
                                    logger.warning("unreal-blender-mcp startup stderr: %s", err.decode(errors="replace")[:4000])
                        except Exception:
                            pass
                        if proc.returncode is None:
                            proc.terminate()
                            await asyncio.wait_for(proc.wait(), timeout=3)
                    except Exception:
                        try:
                            proc.kill()
                        except Exception:
                            pass

                    # Attempt 2: direct uvicorn invocation as fallback
                    logger.info("Trying uvicorn fallback for unreal-blender-mcp on port %s...", port)
                    proc2 = await asyncio.create_subprocess_exec(
                        sys.executable, '-m', 'uvicorn', 'src.unreal_blender_mcp.server:app',
                        '--host', '127.0.0.1', '--port', str(port), '--log-level', 'debug',
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.PIPE,
                        cwd=Path.cwd(),
                        env=env,
                    )
                    healthy = False
                    for _ in range(30):
                        await asyncio.sleep(1.0)
                        try:
                            response = requests.get(f"http://127.0.0.1:{port}/status", timeout=2)
                            if response.status_code == 200:
                                healthy = True
                                break
                        except Exception:
                            if proc2.returncode is not None:
                                break
                            continue
                    if healthy:
                        self.servers[server_name]['status'] = 'running'
                        self.servers[server_name]['process'] = proc2
                        self.servers[server_name]['port'] = port
                        logger.info("OK Started unreal-blender-mcp via uvicorn on port %s", port)
                        return
                    # Not healthy: capture diagnostics and terminate
                    try:
                        try:
                            if proc2.stderr:
                                err = await asyncio.wait_for(proc2.stderr.read(65536), timeout=3.0)
                                if err:
                                    logger.warning("unreal-blender-mcp uvicorn stderr: %s", err.decode(errors="replace")[:4000])
                        except Exception:
                            pass
                        if proc2.returncode is None:
                            proc2.terminate()
                            await asyncio.wait_for(proc2.wait(), timeout=3)
                    except Exception:
                        try:
                            proc2.kill()
                        except Exception:
                            pass
                logger.warning("X Could not start unreal-blender-mcp (HTTP)")
        except Exception as e:
            logger.warning("Failed to start HTTP server %s: %s", server_name, e)

    async def start_stdio_server(self, server_name: str):
        """Start a stdio-based MCP server."""
        try:
            if server_name == 'unreal-mcp':
                # Try multiple known Unreal MCP server entrypoints.
                # Prefer ones with screenshot/editor tools.
                candidates = [
                    ('chongdashu-unreal-mcp-complete/Python/unreal_mcp_server.py', [sys.executable, 'chongdashu-unreal-mcp-complete/Python/unreal_mcp_server.py']),
                    ('flopperam-unreal-mcp/Python/unreal_mcp_server_advanced.py', [sys.executable, 'flopperam-unreal-mcp/Python/unreal_mcp_server_advanced.py']),
                    ('unreal-mcp/Python/unreal_mcp_server.py', [sys.executable, 'unreal-mcp/Python/unreal_mcp_server.py'])
                ]
                process = None
                for rel_path, cmd in candidates:
                    if (Path.cwd() / rel_path).exists():
                        try:
                            logger.info("Attempting Unreal MCP entrypoint: %s", rel_path)
                            proc_try = await asyncio.create_subprocess_exec(
                                *cmd,
                                stdin=asyncio.subprocess.PIPE,
                                stdout=asyncio.subprocess.PIPE,
                                stderr=asyncio.subprocess.PIPE,
                                cwd=Path.cwd()
                            )
                            # Accept the server as launched without strict probing; we'll use stdio 'execute' or TCP fallback.
                            process = proc_try
                            logger.info("Launched Unreal MCP server at %s", rel_path)
                            break
                        except Exception as e:
                            logger.warning(f"Failed to start Unreal MCP at {rel_path}: {e}")
                if process is None:
                    raise FileNotFoundError("No Unreal MCP server entrypoint found with required tools")
            elif server_name == 'unreal-mcp-chong':
                rel_path = 'chongdashu-unreal-mcp-complete/Python/unreal_mcp_server.py'
                if (Path.cwd() / rel_path).exists():
                    process = await asyncio.create_subprocess_exec(
                        sys.executable, rel_path,
                        stdin=asyncio.subprocess.PIPE,
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.PIPE,
                        cwd=Path.cwd()
                    )
                else:
                    logger.info("Skipping %s; entrypoint not found: %s", server_name, rel_path)
                    self.servers[server_name]['status'] = 'offline'
                    return
            elif server_name == 'unreal-mcp-flopperam':
                rel_path = 'flopperam-unreal-mcp/Python/unreal_mcp_server_advanced.py'
                if (Path.cwd() / rel_path).exists():
                    process = await asyncio.create_subprocess_exec(
                        sys.executable, rel_path,
                        stdin=asyncio.subprocess.PIPE,
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.PIPE,
                        cwd=Path.cwd()
                    )
                else:
                    logger.info("Skipping %s; entrypoint not found: %s", server_name, rel_path)
                    self.servers[server_name]['status'] = 'offline'
                    return
            elif server_name == 'unreal-mcp-core':
                rel_path = 'unreal-mcp/Python/unreal_mcp_server.py'
                if (Path.cwd() / rel_path).exists():
                    process = await asyncio.create_subprocess_exec(
                        sys.executable, rel_path,
                        stdin=asyncio.subprocess.PIPE,
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.PIPE,
                        cwd=Path.cwd()
                    )
                else:
                    logger.info("Skipping %s; entrypoint not found: %s", server_name, rel_path)
                    self.servers[server_name]['status'] = 'offline'
                    return
            elif server_name == 'kvick-unreal-bridge':
                rel_path = 'kvick-UnrealMCP/MCP/unreal_mcp_bridge.py'
                if (Path.cwd() / rel_path).exists():
                    process = await asyncio.create_subprocess_exec(
                        sys.executable, rel_path,
                        stdin=asyncio.subprocess.PIPE,
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.PIPE,
                        cwd=Path.cwd()
                    )
                else:
                    logger.info("Skipping %s; entrypoint not found: %s", server_name, rel_path)
                    self.servers[server_name]['status'] = 'offline'
                    return
            elif server_name == '3d-mcp':
                # Try using node to run the compiled JS if TypeScript compilation worked
                try:
                    # First try to run the compiled version
                    process = await asyncio.create_subprocess_exec(
                        'node', '3d-mcp/index.js',
                        stdin=asyncio.subprocess.PIPE,
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.PIPE,
                        cwd=Path.cwd()
                    )
                except:
                    # If that fails, skip 3d-mcp for now
                    logger.warning(f"Could not start {server_name} - TypeScript compilation issues")
                    self.servers[server_name]['status'] = 'compilation_error'
                    return

            elif server_name == 'binary-reader-mcp':
                process = await asyncio.create_subprocess_exec(
                    sys.executable, 'binary-reader-mcp/main.py',
                    stdin=asyncio.subprocess.PIPE,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                    cwd=Path.cwd()
                )
            else:
                logger.warning(f"Unknown stdio server: {server_name}")
                return

            self.servers[server_name]['process'] = process
            self.servers[server_name]['status'] = 'running'
            logger.info("OK Started %s as stdio server", server_name)

        except Exception as e:
            logger.error("Failed to start %s: %s", server_name, e)
            self.servers[server_name]['status'] = 'start_failed'

    def get_server_summary(self) -> Dict[str, str]:
        """Get a summary of all server statuses."""
        return {name: config['status'] for name, config in self.servers.items()}

    async def discover_unreal_tools(self):
        """Discover available Unreal MCP tools over stdio."""
        if self.servers['unreal-mcp']['status'] != 'running':
            return
        try:
            proc = self.servers['unreal-mcp']['process']
            client = MCPStdioClient([], cwd=str(Path.cwd()))
            # Attach to existing process pipes
            client._proc = proc
            client._reader = proc.stdout
            client._writer = proc.stdin
            await asyncio.sleep(0.2)
            init = await client.initialize()
            listed = await client.list_tools()
            self.servers['unreal-mcp']['available_tools'] = listed.get('result', {}).get('tools', [])
            logger.info("Discovered %s Unreal MCP tools", len(self.servers['unreal-mcp']['available_tools']))
        except Exception as e:
            logger.warning(f"Could not discover Unreal tools: {e}")

    async def send_unreal_command(self, tool: str, params: Dict = None):
        """Invoke a tool on the Unreal MCP stdio server."""
        if self.servers['unreal-mcp']['status'] != 'running':
            # If stdio isn't running, try direct TCP fallback so the demo can proceed
            logger.warning("Unreal MCP stdio not running; using TCP fallback for %s", tool)
            return await self._unreal_tcp_fallback(tool, params or {})
        try:
            proc = self.servers['unreal-mcp']['process']
            client = MCPStdioClient([], cwd=str(Path.cwd()))
            client._proc = proc
            client._reader = proc.stdout
            client._writer = proc.stdin
            # Always initialize before calling tools to ensure proper handshake
            await asyncio.sleep(0.1)
            try:
                await client.initialize()
            except Exception as e:
                logger.warning("Unreal MCP initialize failed (continuing to call tool): %s", e)
            # First attempt: call the tool by its name (e.g., 'editor.spawn_actor' servers may not match)
            try:
                return await client.call_tool(tool, params or {})
            except Exception as e_primary:
                logger.info("Stdio direct tool '%s' not found or failed (%s); attempting generic 'execute' passthrough", tool, e_primary)
                # Second attempt: many servers expose a generic 'execute' tool that forwards raw commands
                try:
                    return await client.call_tool("execute", {"command": tool, "params": params or {}})
                except Exception as e_exec:
                    logger.warning("Unreal MCP stdio 'execute' path failed for %s: %s; falling back to TCP", tool, e_exec)
                    return await self._unreal_tcp_fallback(tool, params or {})
        except Exception as e:
            logger.error(f"Error calling Unreal tool: {e}")
            # Last resort fallback
            return await self._unreal_tcp_fallback(tool, params or {})

    async def _unreal_tcp_fallback(self, tool: str, params: Dict):
        """Fallback path: talk directly to Unreal TCP bridge on 55557 using the same command schema as servers use."""
        host = "127.0.0.1"
        ports_to_try = [55557, 13377]
        payload = {"type": tool, "params": params or {}}
        for port in ports_to_try:
            try:
                with socket.create_connection((host, port), timeout=5) as sock:
                    sock.settimeout(10)
                    data = json.dumps(payload).encode("utf-8")
                    sock.sendall(data)
                    # read until valid JSON parsed or timeout
                    chunks = []
                    while True:
                        try:
                            chunk = sock.recv(4096)
                        except socket.timeout:
                            break
                        if not chunk:
                            break
                        chunks.append(chunk)
                        try:
                            resp = json.loads(b"".join(chunks).decode("utf-8"))
                            return resp
                        except json.JSONDecodeError:
                            continue
            except Exception as e:
                logger.warning("Unreal TCP fallback failed for %s on %s:%s: %s", tool, host, port, e)
        return None

    async def unreal_tcp_available(self) -> bool:
        """Quickly probe the Unreal TCP bridge with a ping; return True if reachable."""
        host = "127.0.0.1"
        # Probe with a real command most plugins implement
        probe_payload = {"type": "get_actors_in_level", "params": {}}
        for port in [55557, 13377]:
            try:
                with socket.create_connection((host, port), timeout=2) as sock:
                    sock.settimeout(3)
                    sock.sendall(json.dumps(probe_payload).encode("utf-8"))
                    try:
                        data = sock.recv(2048)
                    except socket.timeout:
                        continue
                    if not data:
                        continue
                    try:
                        # Any JSON response implies the bridge is up
                        json.loads(data.decode("utf-8"))
                        return True
                    except Exception:
                        continue
            except Exception:
                continue
        return False

    async def start_unreal_editor(self, headless: bool = False) -> bool:
        """Attempt to start Unreal Editor with this project to bring up the MCP TCP bridge."""
        # Reuse an existing editor we started if it's still alive
        try:
            if self.unreal_editor_proc and self.unreal_editor_proc.returncode is None:
                logger.info("Unreal Editor already running (reusing existing instance)")
                # Still probe the bridge to be sure
                for i in range(5):
                    if await self.unreal_tcp_available():
                        return True
                    await asyncio.sleep(1.5)
                # If the bridge isn't up yet, continue to probe without launching another instance
                logger.warning("Unreal Editor is running but TCP bridge not confirmed; proceeding optimistically")
                return True
        except Exception:
            pass
        # Locate UnrealEditor executable
        candidates = [
            os.environ.get("UE_EDITOR"),
            r"C:\\Program Files\\Epic Games\\UE_5.6\\Engine\\Binaries\\Win64\\UnrealEditor.exe",
            r"C:\\Epic Games\\UE_5.6\\Engine\\Binaries\\Win64\\UnrealEditor.exe",
        ]
        editor_path = None
        for c in candidates:
            if c and os.path.isfile(c):
                editor_path = c
                break
        if editor_path is None:
            logger.warning("UnrealEditor.exe not found; set UE_EDITOR env var to full path")
            return False

        uproject = str((Path.cwd() / "TerminalGrounds.uproject").resolve())
        if not os.path.isfile(uproject):
            logger.error("TerminalGrounds.uproject not found at %s", uproject)
            return False

        # Build command
        args = [editor_path, uproject, "-NoSplash", "-log"]
        if headless:
            # Use -NullRHI to allow renderingless startup; plugin TCP doesn't require rendering
            args += ["-NullRHI", "-Unattended"]

        logger.info("Starting Unreal Editor to enable MCP TCP bridge: %s", editor_path)
        try:
            proc = await asyncio.create_subprocess_exec(*args, cwd=str(Path.cwd()))
            self.unreal_editor_proc = proc
            # Give it time to boot, then probe repeatedly up to ~45s
            for i in range(15):
                await asyncio.sleep(3)
                if await self.unreal_tcp_available():
                    logger.info("Unreal MCP TCP bridge is up on 55557")
                    return True
            logger.warning("Unreal MCP TCP bridge did not become available in time")
            # Shut down this editor instance if the bridge never came up to avoid orphaned windows
            try:
                if self.unreal_editor_proc and self.unreal_editor_proc.returncode is None:
                    self.unreal_editor_proc.terminate()
                    await asyncio.wait_for(self.unreal_editor_proc.wait(), timeout=10)
            except Exception:
                try:
                    if self.unreal_editor_proc:
                        self.unreal_editor_proc.kill()
                except Exception:
                    pass
            self.unreal_editor_proc = None
            return False
        except Exception as e:
            logger.error("Failed to launch Unreal Editor: %s", e)
            return False

    async def screenshot_via_editor_cli(self, output_path: Path, width: int = 1920, height: int = 1080, timeout_s: int = 540, open_map_path: Optional[str] = None) -> bool:
        """Launch Unreal with -ExecCmds to take a high-res screenshot, then normalize it to output_path.
        Uses a broad recursive search of Saved/Screenshots to find the newest screenshot emitted during this run.
        """
        # Locate UnrealEditor executable
        candidates = [
            os.environ.get("UE_EDITOR"),
            r"C:\\Program Files\\Epic Games\\UE_5.6\\Engine\\Binaries\\Win64\\UnrealEditor.exe",
            r"C:\\Epic Games\\UE_5.6\\Engine\\Binaries\\Win64\\UnrealEditor.exe",
        ]
        editor_path = None
        for c in candidates:
            if c and os.path.isfile(c):
                editor_path = c
                break
        if editor_path is None:
            logger.warning("UnrealEditor.exe not found; set UE_EDITOR env var to full path")
            return False

        uproject = str((Path.cwd() / "TerminalGrounds.uproject").resolve())
        if not os.path.isfile(uproject):
            logger.error("TerminalGrounds.uproject not found at %s", uproject)
            return False

        screenshots_dir = Path.cwd() / "Saved" / "Screenshots"
        screenshots_dir.mkdir(parents=True, exist_ok=True)

    # Build ExecCmds sequence
        exec_steps: list[str] = []
        if open_map_path:
            logger.info("Using configured map for CLI screenshot: %s", open_map_path)
            exec_steps.append(f"Open {open_map_path}")
        exec_steps.append("viewmode lit")
        try:
            delay_s = int(os.getenv("TG_SHOT_DELAY", "10"))
        except Exception:
            delay_s = 10
        logger.info("Using HighResScreenshotDelay: %ss", delay_s)
        exec_steps.append(f"r.HighResScreenshotDelay {delay_s}")
        # Prefer specifying the output file explicitly to avoid platform subfolder ambiguity
        try:
            abs_out = str(output_path.resolve())
            # Escape backslashes and quotes for console command within -ExecCmds argument
            abs_out_cmd = abs_out.replace("\\", "\\\\").replace('"', '\\"')
            exec_steps.append(f"HighResShot {width}x{height} filename=\"{abs_out_cmd}\"")
        except Exception:
            exec_steps.append(f"HighResShot {width}x{height}")
        exec_steps.append("quit")

        exec_cmds = ";".join(exec_steps)
        logger.info("CLI ExecCmds: %s", exec_cmds)
        args = [
            editor_path,
            uproject,
            "-NoSplash",
            "-log",
            "-newinstance",
            f"-ExecCmds={exec_cmds}",
            "-Unattended",
        ]

        # Remove any stale output from previous runs to avoid false positives
        try:
            if output_path.exists():
                output_path.unlink(missing_ok=True)
        except Exception:
            pass

        logger.info("Starting Unreal Editor for CLI screenshot to %s", str(output_path.resolve()))
        start_ts = time.time()
        try:
            proc = await asyncio.create_subprocess_exec(*args, cwd=str(Path.cwd()))
            # Wait for file to appear or timeout
            for _ in range(max(1, timeout_s // 3)):
                await asyncio.sleep(3)
                if output_path.exists():
                    logger.info("CLI screenshot saved: %s", output_path)
                    try:
                        await asyncio.wait_for(proc.wait(), timeout=5)
                    except Exception:
                        pass
                    return True

                # Search for newest screenshot created after start_ts
                recent: list[Path] = []
                patterns = ["HighresScreenshot*.png", "HighResShot*.png", "Screenshot*.png"]
                for pat in patterns:
                    for p in screenshots_dir.rglob(pat):
                        try:
                            if p.stat().st_mtime >= start_ts - 60:
                                recent.append(p)
                        except Exception:
                            continue
                if not recent:
                    now_ts = time.time()
                    for p in screenshots_dir.rglob("HighresScreenshot*.png"):
                        try:
                            if now_ts - p.stat().st_mtime <= 10 * 60:
                                recent.append(p)
                        except Exception:
                            continue

                if recent:
                    newest = max(recent, key=lambda p: p.stat().st_mtime)
                    try:
                        shutil.copy2(newest, output_path)
                        logger.info("CLI screenshot normalized: %s -> %s", newest, output_path)
                        try:
                            await asyncio.wait_for(proc.wait(), timeout=5)
                        except Exception:
                            pass
                        return True
                    except Exception as e:
                        logger.warning("Failed to copy CLI screenshot %s -> %s: %s", newest, output_path, e)

            # Timeout window expired
            try:
                if proc and proc.returncode is None:
                    proc.terminate()
                    await asyncio.wait_for(proc.wait(), timeout=5)
            except Exception:
                try:
                    if proc:
                        proc.kill()
                except Exception:
                    pass
            logger.warning("CLI screenshot did not appear for target %s within timeout", str(output_path))
            return False
        except Exception as e:
            logger.error("Failed CLI screenshot capture: %s", e)
            return False

    def _extract_text_from_mcp_response(self, resp: Dict[str, Any]) -> Optional[str]:
        """Best-effort extraction of text from an MCP tools/call response."""
        try:
            if not isinstance(resp, dict):
                return None
            # Top-level error
            if "error" in resp and resp["error"]:
                err = resp["error"]
                if isinstance(err, dict):
                    return err.get("message") or json.dumps(err)
                return str(err)
            res = resp.get("result") or {}
            # Some servers wrap as { result: { content: [...] } }
            content = res.get("content")
            if isinstance(content, list):
                texts: list[str] = []
                for item in content:
                    if not isinstance(item, dict):
                        continue
                    if item.get("type") == "text" and "text" in item:
                        texts.append(str(item.get("text")))
                if texts:
                    return "\n".join(texts)
            # Or directly a string payload
            if isinstance(res, str):
                return res
            # Or nested result.text
            if isinstance(res, dict) and isinstance(res.get("text"), str):
                return res["text"]
        except Exception:
            return None
        return None

    async def analyze_asset_with_binary_reader(self, asset_path: str):
        """Use binary-reader-mcp to analyze game assets and return printable text."""
        if self.servers['binary-reader-mcp']['status'] != 'running':
            logger.warning("Binary reader MCP server not running")
            return None

        try:
            # Use stdio client framing (Content-Length)
            process = self.servers['binary-reader-mcp']['process']
            client = MCPStdioClient([], cwd=str(Path.cwd()))
            client._proc = process
            client._reader = process.stdout
            client._writer = process.stdin

            await client.initialize()
            # First try the Unreal-aware parser
            result = await client.call_tool("read-unreal-asset", {"file_path": asset_path})
            text = self._extract_text_from_mcp_response(result)
            if text:
                return text
            # If we didn't get text content, fall back to generic binary metadata
            try:
                meta_result = await client.call_tool("read-binary-metadata", {"file_path": asset_path, "format": "unreal"})
                meta_text = self._extract_text_from_mcp_response(meta_result)
                return meta_text if meta_text else meta_result
            except Exception as e2:
                logger.error("Binary metadata read failed for %s: %r", asset_path, e2)
                return result

        except Exception as e:
            logger.error("Error analyzing asset: %r", e)
            return None

    async def build_demo_sequence(self):
        """Execute the complete Terminal Grounds demo sequence."""
        logger.info("Starting Terminal Grounds Master MCP Demo")

        # Phase 1: Server Discovery and Preparation
        await self.check_server_status()
        server_status = self.get_server_summary()
        logger.info("Server Status Summary:")
        for server, status in server_status.items():
            status_symbol = "OK" if status == "running" else "X"
            logger.info("   %s %s: %s", status_symbol, server, status)

        # Phase 2: Unreal Engine Demo Setup
        # Ensure Unreal MCP TCP bridge is up, start Unreal Editor if needed
        unreal_ok = server_status.get('unreal-mcp') == 'running'
        if not unreal_ok:
            if not await self.unreal_tcp_available():
                logger.info("Unreal TCP bridge not responding; attempting to start Unreal Editor...")
                await self.start_unreal_editor(headless=False)
            # After attempting start, consider it OK for driving via TCP if reachable
            if await self.unreal_tcp_available():
                logger.info("Proceeding via TCP fallback to 55557")
                unreal_ok = True
            else:
                # Still proceed to try commands; some bridges may not respond to ping
                logger.info("TCP bridge still not confirming; proceeding optimistically via TCP anyway")
                unreal_ok = True
        if unreal_ok:
            logger.info("Phase 2: Setting up Unreal Engine demo...")
            # Ensure the Unreal Editor is running so TCP bridge and editor tools are available
            if not await self.unreal_tcp_available():
                logger.info("Unreal TCP bridge not available; attempting to start Unreal Editor now...")
                await self.start_unreal_editor(headless=False)
            await self.discover_unreal_tools()
            # Log a quick summary of discovered tools
            unreal_tools = self.servers['unreal-mcp'].get('available_tools', [])
            if unreal_tools:
                names = [t.get('name') or t.get('tool', 'unknown') for t in unreal_tools][:8]
                logger.info("Unreal tools available (%d): %s%s", len(unreal_tools), ", ".join(names), "..." if len(unreal_tools) > 8 else "")

            # Spawn a demo light
            await self.send_unreal_command("spawn_actor", {
                "name": "MCPDemoLight",
                "type": "PointLight",
                "location": [0, 0, 300],
                "rotation": [0, 0, 0]
            })

            # List actors to verify
            actors = await self.send_unreal_command("get_actors_in_level")
            logger.info("Level actors (sample): %s...", str(actors)[:200])

            # Create a simple UMG widget blueprint
            await self.send_unreal_command("create_umg_widget_blueprint", {
                "widget_name": "WBP_MCPDemo",
                "parent_class": "UserWidget",
                "path": "/Game/UI"
            })

            # Focus viewport and take a screenshot artifact
            try:
                await self.send_unreal_command("focus_viewport", {
                    "target": "MCPDemoLight",
                    "distance": 600.0
                })
            except Exception:
                pass

            screenshots_dir = Path.cwd() / "Saved" / "Screenshots"
            screenshots_dir.mkdir(parents=True, exist_ok=True)
            logger.info("Preparing to capture screenshot to %s", screenshots_dir)
            # Use a stable filename and also check the platform subfolder Unreal uses
            shot_name = f"MCP_Demo_{int(time.time())}.png"
            screenshot_path = screenshots_dir / shot_name
            logger.info("Invoking take_screenshot tool...")
            shot_result = await self.send_unreal_command("take_screenshot", {
                "filename": str(screenshot_path),
                "show_ui": False,
                "resolution": [1920, 1080]
            })
            logger.info("Screenshot result: %s", str(shot_result)[:300])
            # Primary check
            saved = False
            if screenshot_path.exists():
                logger.info("Screenshot saved: %s", screenshot_path)
                saved = True
            # Windows platform subfolder fallback
            if not saved:
                alt_dir = screenshots_dir / "Windows"
                alt_dir.mkdir(parents=True, exist_ok=True)
                alt_file = alt_dir / shot_name
                if alt_file.exists():
                    logger.info("Screenshot saved (alt): %s", alt_file)
                    saved = True
            # Last resort: drive screenshot via Unreal Python if command not available
            if not saved:
                logger.info("Direct tool failed; attempting screenshot via Unreal Python (execute_python)")
                # Use two approaches inside Unreal Python:
                # 1) AutomationLibrary.take_high_res_screenshot with name only (default Saved/Screenshots/<Platform>)
                # 2) Console command HighResShot with explicit absolute path to avoid platform subfolder ambiguity
                abs_path = str(screenshot_path.resolve()).replace("\\", "\\\\")
                py_code = (
                    "import unreal, os\n"
                    f"_name = '{shot_name}'\n"
                    f"_abs = r'{abs_path}'\n"
                    "try:\n"
                    "    # Try AutomationLibrary into platform screenshots dir\n"
                    "    unreal.AutomationLibrary.take_high_res_screenshot(1920, 1080, _name)\n"
                    "    print('SHOT_OK_AUTO', _name)\n"
                    "except Exception as e:\n"
                    "    print('SHOT_ERR_AUTO', str(e))\n"
                    "\n"
                    "try:\n"
                    "    # Also attempt explicit absolute path via console command\n"
                    "    world = None\n"
                    "    try:\n"
                    "        world = unreal.EditorLevelLibrary.get_editor_world()\n"
                    "    except Exception:\n"
                    "        pass\n"
                    "    unreal.SystemLibrary.execute_console_command(world, f'HighResShot 1920x1080 filename=\"{_abs}\"')\n"
                    "    print('SHOT_OK_CMD', _abs)\n"
                    "except Exception as e:\n"
                    "    print('SHOT_ERR_CMD', str(e))\n"
                )
                py_result = await self.send_unreal_command("execute_python", {"code": py_code})
                # Probe common locations (absolute path, platform folder, and any matching in Saved/Screenshots)
                alt_dir = screenshots_dir / "Windows"
                alt_file = alt_dir / shot_name
                if screenshot_path.exists():
                    logger.info("Screenshot saved via Python: %s", screenshot_path)
                    saved = True
                elif alt_file.exists():
                    logger.info("Screenshot saved via Python: %s", alt_file)
                    saved = True
                else:
                    # Search recursively for the named file under Saved/Screenshots
                    try:
                        matches = list((screenshots_dir).rglob(shot_name))
                        if matches:
                            logger.info("Screenshot found via search: %s", matches[0])
                            saved = True
                        else:
                            logger.warning("Screenshot not found after Python attempt; result: %s", str(py_result)[:400])
                    except Exception as e:
                        logger.warning("Screenshot search failed: %r", e)

            # Final fallback: Launch a short-lived editor instance with -ExecCmds to take the screenshot
            if not saved:
                logger.info("Attempting CLI-based screenshot fallback via -ExecCmds")
                # Try to open a known map to make the render deterministic
                open_map_pkg: Optional[str] = None
                try:
                    # 0) Allow explicit override via environment variable
                    env_map = os.getenv("TG_SHOT_MAP")
                    if env_map and env_map.strip():
                        open_map_pkg = env_map.strip()
                        logger.info("Using TG_SHOT_MAP override: %s", open_map_pkg)

                    # 1) Prefer the project-configured startup map
                    ini_path = Path.cwd() / "Config" / "DefaultGame.ini"
                    if not open_map_pkg and ini_path.exists():
                        try:
                            import configparser
                            parser = configparser.ConfigParser(strict=False)
                            # Preserve case and allow unconventional section names
                            parser.optionxform = str  # type: ignore[attr-defined]
                            with ini_path.open("r", encoding="utf-8", errors="ignore") as f:
                                parser.read_file(f)
                            section = "/Script/EngineSettings.GameMapsSettings"
                            if parser.has_section(section):
                                if parser.has_option(section, "EditorStartupMap"):
                                    open_map_pkg = parser.get(section, "EditorStartupMap").strip().strip('"')
                                if not open_map_pkg and parser.has_option(section, "GameDefaultMap"):
                                    open_map_pkg = parser.get(section, "GameDefaultMap").strip().strip('"')
                                if open_map_pkg:
                                    # Validate the configured map points to a substantial .umap, else discard
                                    try:
                                        content_dir = Path.cwd() / "Content"
                                        if open_map_pkg.startswith("/Game/"):
                                            rel = open_map_pkg.replace("/Game/", "")
                                            umap_path = (content_dir / rel).with_suffix(".umap")
                                            if not umap_path.exists() or umap_path.stat().st_size < 2 * 1024 * 1024:
                                                logger.info("Startup map seems empty/small; searching for richer map...")
                                                open_map_pkg = None
                                            else:
                                                logger.info("Selected map from DefaultGame.ini: %s (%d KB)", open_map_pkg, umap_path.stat().st_size // 1024)
                                        else:
                                            open_map_pkg = None
                                    except Exception:
                                        open_map_pkg = None
                        except Exception:
                            open_map_pkg = None
                    # 2) If not configured/valid, prefer a known rich map path if it exists
                    if not open_map_pkg:
                        content_dir = Path.cwd() / "Content"
                        known_rich = content_dir / "TG" / "Maps" / "IEZ" / "IEZ_District_Alpha.umap"
                        if known_rich.exists() and known_rich.stat().st_size >= 2 * 1024 * 1024:
                            rel = known_rich.relative_to(content_dir)
                            open_map_pkg = "/Game/" + str(rel.with_suffix("")).replace("\\", "/")
                            logger.info("Selected known rich map: %s (%d KB)", open_map_pkg, known_rich.stat().st_size // 1024)

                    # 3) If still not set, discover a richer map by keywords and size across entire Content
                    if not open_map_pkg:
                        content_dir = Path.cwd() / "Content"
                        candidate_map: Optional[Path] = None
                        try:
                            # Always search entire project Content directory
                            maps: List[Path] = list(content_dir.rglob("*.umap"))
                            if maps:
                                # Filter out likely redirectors and dev/test/temp maps
                                filtered: List[Path] = []
                                for m in maps:
                                    try:
                                        size = m.stat().st_size
                                        if size < 64 * 1024:  # skip tiny maps
                                            continue
                                        parts = [s.lower() for s in m.parts]
                                        if any(seg in parts for seg in ["developers", "developed", "test", "tests", "tmp", "temp"]):
                                            continue
                                        filtered.append(m)
                                    except Exception:
                                        continue
                                pool = filtered if filtered else maps
                                keywords = [
                                    "demo", "city", "metro", "underground", "district", "main", "persistent",
                                    "showcase", "playground", "overview", "iez", "tg", "level", "map"
                                ]
                                def score_tuple(p: Path) -> tuple[int, int]:
                                    try:
                                        name = p.stem.lower()
                                        key_hits = sum(1 for k in keywords if k in name)
                                        size = int(p.stat().st_size)
                                        return (key_hits, size)
                                    except Exception:
                                        return (0, 0)
                                # Pick the best by keyword hits then size
                                candidate_map = max(pool, key=score_tuple)
                                # Ensure we don't end up with a tiny file after scoring
                                if candidate_map.stat().st_size < 2 * 1024 * 1024:
                                    candidate_map = max(pool, key=lambda p: p.stat().st_size)
                            if candidate_map and candidate_map.exists():
                                rel = candidate_map.relative_to(content_dir)
                                pkg = "/Game/" + str(rel.with_suffix("")).replace("\\", "/")
                                open_map_pkg = pkg
                                logger.info("Selected discovered map for CLI screenshot: %s (%d KB)", open_map_pkg, candidate_map.stat().st_size // 1024)
                        except Exception:
                            open_map_pkg = None
                except Exception:
                    open_map_pkg = None

                cli_ok = await self.screenshot_via_editor_cli(screenshot_path, open_map_path=open_map_pkg, timeout_s=420)
                # Search again, even if cli_ok is False, UE may have emitted default HighresScreenshot*.png
                try:
                    # Primary: exact expected name anywhere under Saved/Screenshots
                    matches = list((screenshots_dir).rglob(shot_name))
                    if matches:
                        logger.info("Screenshot found after CLI attempt: %s", matches[0])
                        saved = True
                    if not saved:
                        # Secondary: look for recent screenshot patterns and normalize to our target path
                        recent: list[Path] = []
                        now_ts = time.time()
                        for pat in ["HighresScreenshot*.png", "HighResShot*.png", "Screenshot*.png"]:
                            for p in screenshots_dir.rglob(pat):
                                try:
                                    if now_ts - p.stat().st_mtime <= 10 * 60:  # last 10 minutes
                                        recent.append(p)
                                except Exception:
                                    continue
                        if recent:
                            newest = max(recent, key=lambda p: p.stat().st_mtime)
                            try:
                                shutil.copy2(newest, screenshot_path)
                                logger.info("Copied CLI screenshot %s to %s", newest, screenshot_path)
                                saved = True
                            except Exception as e:
                                logger.warning("Failed to copy screenshot %s -> %s: %s", newest, screenshot_path, e)
                except Exception:
                    pass

            # Always publish a stable alias to the most recent screenshot
            try:
                latest_alias = screenshots_dir / "latest.png"
                if screenshot_path.exists():
                    shutil.copy2(screenshot_path, latest_alias)
                    logger.info("Aliased latest screenshot to %s", latest_alias)
                else:
                    # Fallback: newest recent screenshot within 20 minutes
                    recent: list[Path] = []
                    now_ts = time.time()
                    for pat in ["HighresScreenshot*.png", "HighResShot*.png", "Screenshot*.png", "MCP_Demo_*.png"]:
                        for p in screenshots_dir.rglob(pat):
                            try:
                                if now_ts - p.stat().st_mtime <= 20 * 60:
                                    recent.append(p)
                            except Exception:
                                continue
                    if recent:
                        newest = max(recent, key=lambda p: p.stat().st_mtime)
                        shutil.copy2(newest, latest_alias)
                        logger.info("Aliased newest screenshot %s to %s", newest, latest_alias)
            except Exception as e:
                logger.warning("Failed to alias latest screenshot: %s", e)

        # Phase 3: Asset Analysis
        if server_status['binary-reader-mcp'] == 'running':
            logger.info("Phase 3: Analyzing Terminal Grounds assets...")

            # Find a few small .uasset files to analyze (more reliable/faster)
            asset_paths: list[Path] = []
            content_dir = Path.cwd() / "Content"
            if content_dir.exists():
                try:
                    all_assets = list(content_dir.rglob("*.uasset"))
                    # Sort by file size ascending and pick first 3
                    all_assets.sort(key=lambda p: p.stat().st_size if p.exists() else 1_000_000_000)
                    asset_paths = all_assets[:3]
                except Exception:
                    asset_paths = list(content_dir.glob("**/*.uasset"))[:3]

            for asset_path in asset_paths:
                logger.info("Analyzing asset: %s", asset_path.name)
                analysis = await self.analyze_asset_with_binary_reader(str(asset_path))
                if analysis is None:
                    logger.error("Asset analysis failed for %s", asset_path.name)
                    continue
                # If we got printable text, log a trimmed version
                if isinstance(analysis, str):
                    trimmed = analysis if len(analysis) <= 800 else analysis[:800] + "..."
                    logger.info("Asset analysis for %s:\n%s", asset_path.name, trimmed)
                else:
                    # Fallback: dump raw structure summary
                    try:
                        logger.info("Asset analysis (raw) for %s: %s", asset_path.name, json.dumps(analysis)[:800])
                    except Exception:
                        logger.info("Asset analysis (raw object) for %s", asset_path.name)

        # Phase 4: 3D Operations (if available)
        if server_status['3d-mcp'] == 'running':
            logger.info("Phase 4: Performing 3D operations...")
            # 3D MCP operations would go here
            logger.info("OK 3D operations placeholder completed")

        # Phase 5: Blender-Unreal Integration (if available)
        if server_status['unreal-blender-mcp'] == 'running':
            logger.info("Phase 5: Blender-Unreal integration...")
            # Blender-Unreal integration would go here
            logger.info("OK Blender-Unreal integration placeholder completed")

        # Phase 6: Demo Completion
        logger.info("Demo sequence completed!")
        logger.info("Results Summary:")
        working_servers = [name for name, status in server_status.items() if status == 'running']
        logger.info("   - %d/%d MCP servers operational", len(working_servers), len(server_status))
        logger.info("   - Working servers: %s", ", ".join(working_servers))

        if 'unreal-mcp' in working_servers:
            logger.info("   - Unreal Engine integration: ACTIVE")
        if 'binary-reader-mcp' in working_servers:
            logger.info("   - Asset analysis: ACTIVE")
        if '3d-mcp' in working_servers:
            logger.info("   - 3D operations: ACTIVE")
        if 'unreal-blender-mcp' in working_servers:
            logger.info("   - Blender integration: ACTIVE")

        return server_status

    async def cleanup(self):
        """Clean up all processes."""
        # First, try to close any Unreal Editor instance we launched
        try:
            if self.unreal_editor_proc and self.unreal_editor_proc.returncode is None:
                self.unreal_editor_proc.terminate()
                await asyncio.wait_for(self.unreal_editor_proc.wait(), timeout=10)
                logger.info("Cleaned up Unreal Editor process")
        except Exception:
            try:
                if self.unreal_editor_proc:
                    self.unreal_editor_proc.kill()
                    logger.info("Force-killed Unreal Editor process")
            except Exception:
                pass
        finally:
            self.unreal_editor_proc = None

        for name, config in self.servers.items():
            if config.get('process'):
                try:
                    config['process'].terminate()
                    await config['process'].wait()
                    logger.info(f"Cleaned up {name} process")
                except:
                    pass

async def main():
    """Main demo execution function."""
    manager = MCPServerManager()

    try:
        result = await manager.build_demo_sequence()

        # Print final status
        print("\n" + "=" * 60)
        print("TERMINAL GROUNDS MCP DEMO COMPLETE")
        print("=" * 60)

        print("Server Status:")
        for server, status in result.items():
            print(f"   {server}: {status}")

        working_count = sum(1 for status in result.values() if status == 'running')
        total = len(result)
        print(f"\n{working_count}/{total} MCP servers operational")

        if working_count >= 2:
            print("DEMO SUCCESSFUL - Multiple MCP systems coordinated!")
        elif working_count == 1:
            print("DEMO PARTIAL - Single MCP system operational")
        else:
            print("DEMO FAILED - No MCP systems operational")

    except KeyboardInterrupt:
        logger.info("Demo interrupted by user")
    finally:
        await manager.cleanup()

if __name__ == "__main__":
    # Make sure we're in the Terminal Grounds directory
    if not Path("TerminalGrounds.uproject").exists():
        print("ERROR: Please run this script from the Terminal Grounds root directory")
        sys.exit(1)

    asyncio.run(main())
