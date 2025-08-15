#!/usr/bin/env python3
"""
Quick ComfyUI API connectivity test for Terminal Grounds.
Detects port (env COMFYUI_SERVER or 8000/8188) and prints status.
"""
import os
import sys
import urllib.request

PORTS = []
if os.getenv("COMFYUI_SERVER"):
    PORTS.append(os.getenv("COMFYUI_SERVER"))
PORTS += ["127.0.0.1:8000", "127.0.0.1:8188"]

seen = set()
ports = [p for p in PORTS if not (p in seen or seen.add(p))]

ok = False
for hostport in ports:
    try:
        with urllib.request.urlopen(f"http://{hostport}/system_stats", timeout=2) as r:
            if r.status == 200:
                print(f"OK: ComfyUI reachable at http://{hostport}")
                ok = True
                break
    except Exception as e:
        print(f"Probe failed at http://{hostport} -> {e}")

if not ok:
    print("NOT RUNNING: Start ComfyUI in API mode.")
    print("Hint: C:\\ComfyUI\\run_comfyui_api.bat (from Tools/START_HERE_API_MODE.bat option 1)")
    sys.exit(1)

sys.exit(0)
