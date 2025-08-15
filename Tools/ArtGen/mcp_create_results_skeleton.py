#!/usr/bin/env python3
"""
Create or update Tools/ArtGen/outputs/mcp_results.json with a full list of
{target_rel, url:""} entries based on Tools/ArtGen/outputs/mcp_jobs.json.

Use this to prepare the results file so an MCP client (Copilot) can fill in the
returned file URLs/paths after each generation.
"""
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
JOBS_PATH = ROOT / "Tools/ArtGen/outputs/mcp_jobs.json"
RESULTS_PATH = ROOT / "Tools/ArtGen/outputs/mcp_results.json"


def main() -> int:
    if not JOBS_PATH.exists():
        print("Missing jobs file. Run: python Tools/ArtGen/artgen_run_mcp.py")
        return 1

    data = json.loads(JOBS_PATH.read_text(encoding="utf-8"))
    jobs = data.get("jobs", [])
    existing = []
    if RESULTS_PATH.exists():
        try:
            existing = json.loads(RESULTS_PATH.read_text(encoding="utf-8"))
        except Exception:
            existing = []
    by_target = {e.get("target_rel"): e for e in existing if isinstance(e, dict)}

    out = []
    for j in jobs:
        target_rel = j.get("target_rel")
        if not target_rel:
            continue
        e = by_target.get(target_rel) or {"target_rel": target_rel, "url": ""}
        # normalize fields
        e = {"target_rel": e.get("target_rel"), "url": e.get("url", "")}
        out.append(e)

    RESULTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    RESULTS_PATH.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"Wrote skeleton with {len(out)} entries -> {RESULTS_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
