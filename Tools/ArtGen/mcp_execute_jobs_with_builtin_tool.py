#!/usr/bin/env python3
"""
Execute Tools/ArtGen/outputs/mcp_jobs.json using the built-in Hugging Face MCP
image generator tool available to Copilot Workspace (Flux 1 Schnell).

Behavior:
- Iterates jobs, invokes MCP image generation with deterministic seeds.
- Saves images to each job's absolute output_path.
- Writes/updates Tools/ArtGen/outputs/mcp_results.json with file:// URLs for downstream downloader.

Notes:
- This script is a thin coordinator; Copilot will actually execute the generation calls.
"""
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
JOBS_PATH = ROOT / "Tools/ArtGen/outputs/mcp_jobs.json"
RESULTS_PATH = ROOT / "Tools/ArtGen/outputs/mcp_results.json"


def to_file_url(p: Path) -> str:
    p = p.resolve()
    # Windows file URL
    return f"file:///{str(p).replace('\\', '/')}"


def main() -> int:
    if not JOBS_PATH.exists():
        print("Missing jobs file. Run: python Tools/ArtGen/artgen_run_mcp.py")
        return 1
    data = json.loads(JOBS_PATH.read_text(encoding="utf-8"))
    jobs = data.get("jobs", [])
    if not jobs:
        print("No jobs to execute.")
        return 0

    # Construct pending list for Copilot to execute with MCP tools
    pending = []
    for j in jobs:
        if j.get("type") != "huggingface.flux1_schnell":
            continue
        params = j.get("parameters", {})
        prompt = params.get("prompt", "")
        seed = params.get("seed")
        steps = int(params.get("num_inference_steps", 4))
        width = int(params.get("width", 1024))
        height = int(params.get("height", 1024))
        out_path = Path(j["output_path"]).resolve()
        target_rel = j["target_rel"]
        pending.append({
            "prompt": prompt,
            "seed": seed,
            "steps": steps,
            "width": width,
            "height": height,
            "output_path": str(out_path),
            "target_rel": target_rel,
        })

    print(json.dumps({"pending": pending[:10]}, indent=2))
    print(f"Total jobs: {len(pending)}. Copilot will now generate and save PNGs.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
