#!/usr/bin/env python3
"""
Probe the binary-reader-mcp stdio server: list tools and run a sample call.

This script starts the server in-process for a clean session, performs
initialize -> tools/list -> tools/call (read-binary-metadata), and prints results.
"""

import asyncio
import sys
from pathlib import Path
from Scripts.lib.mcp_stdio_client import MCPStdioClient


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SERVER_PATH = PROJECT_ROOT / "binary-reader-mcp" / "main.py"


async def probe():
    if not SERVER_PATH.exists():
        print(f"Server not found: {SERVER_PATH}")
        sys.exit(1)

    client = MCPStdioClient([sys.executable, str(SERVER_PATH)], cwd=str(SERVER_PATH.parent))
    await client.start()

    try:
    init = await client.initialize()
    print("initialize →", init)

    listed = await client.list_tools()
    print("tools/list →", listed)

    sample_file = str(PROJECT_ROOT / "TerminalGrounds.uproject")
    called = await client.call_tool("read-binary-metadata", {"file_path": sample_file, "format": "auto"})
    print("tools/call(read-binary-metadata) →", called)

    finally:
    await client.stop()


if __name__ == "__main__":
    asyncio.run(probe())
