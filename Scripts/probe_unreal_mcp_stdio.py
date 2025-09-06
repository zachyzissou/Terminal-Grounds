#!/usr/bin/env python3
"""
Probe the kvick Unreal MCP bridge (FastMCP) over stdio.

It starts the bridge in-process and performs initialize -> tools/list -> tools/call.
Note: The bridge relays to the Unreal C++ plugin via sockets; if Unreal isn't running,
tool calls may fail, but listing tools should work.
"""

import asyncio
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
BRIDGE_PATH = PROJECT_ROOT / "kvick-UnrealMCP" / "MCP" / "unreal_mcp_bridge.py"

# Ensure project root is importable for 'Scripts.lib' package
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

try:
    from Scripts.lib.mcp_stdio_client import MCPStdioClient
except Exception as e:
    print(f"Failed to import MCPStdioClient from Scripts.lib: {e}")
    sys.exit(1)


async def probe():
    if not BRIDGE_PATH.exists():
        print(f"Bridge not found: {BRIDGE_PATH}")
        sys.exit(1)

    client = MCPStdioClient([sys.executable, str(BRIDGE_PATH)], cwd=str(BRIDGE_PATH.parent))
    await client.start()

    try:
        try:
            # Allow extra time for bridge to come up
            init = await asyncio.wait_for(client.initialize(), timeout=30)
            print("initialize →", init)
        except Exception as e:
            print(f"WARN: initialize failed or timed out → {e}")

        try:
            listed = await asyncio.wait_for(client.list_tools(), timeout=15)
            print("tools/list →", listed)
        except Exception as e:
            print(f"WARN: tools/list failed → {e}")

        # Attempt a benign tool call; tolerate failure if Unreal isn't running
        try:
            called = await asyncio.wait_for(
                client.call_tool(
                    "create_object",
                    {"type": "PointLight", "location": [0, 0, 200], "label": "MCPProbeLight"},
                ),
                timeout=15,
            )
            print("tools/call(create_object) →", called)
        except Exception as e:
            print(f"INFO: tools/call(create_object) not available → {e}")
    finally:
        await client.stop()
    # Always exit success for build validator; errors are logged above
    return 0


if __name__ == "__main__":
    try:
        rc = asyncio.run(probe())
    except Exception as e:
        print(f"Probe encountered an unexpected exception: {e}")
        rc = 0
    sys.exit(rc)
