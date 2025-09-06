#!/usr/bin/env python3
"""
Execute Dead Sky Region Builder
=============================
Simple launcher for the comprehensive Dead Sky region builder
"""

import sys
import subprocess
from pathlib import Path

def main():
    print("🌌 Launching Dead Sky (IEZ) Region Builder...")
    print("=" * 60)

    # Get the builder script path
    builder_script = Path(__file__).parent / "build_dead_sky_comprehensive.py"

    if not builder_script.exists():
        print(f"❌ Builder script not found: {builder_script}")
        return 1

    print(f"📍 Builder script: {builder_script}")
    print("🚀 Starting MCP-coordinated build...")
    print()

    # Run the builder
    try:
        result = subprocess.run([sys.executable, str(builder_script)],
                              capture_output=False,
                              text=True)
        return result.returncode
    except Exception as e:
        print(f"❌ Error running builder: {e}")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
