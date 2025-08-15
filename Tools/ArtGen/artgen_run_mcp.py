#!/usr/bin/env python3
"""
artgen_run_mcp.py

Purpose
- Read Tools/ArtGen/artgen_config.json and referenced plan files.
- Produce a single MCP jobs file with absolute output paths that an MCP client (this Copilot) can execute against the configured servers:
  - Generation: mcpserver:huggingface (Flux 1 Schnell)
  - Optional post: mcpserver:imagesorcery (resize/clamp)

Notes
- This script does NOT call the network or MCP itself; it prepares a deterministic job list for external execution.
- After generation is completed (images written to disk), use the existing import task to ingest into UE.

Outputs
- Tools/ArtGen/outputs/mcp_jobs.json (machine-readable queue)
"""
from __future__ import annotations
import json
import os
from pathlib import Path
from typing import Dict, Any, List, Tuple

ROOT = Path(__file__).resolve().parents[2]
CFG_PATH = ROOT / "Tools/ArtGen/artgen_config.json"
JOBS_PATH = ROOT / "Tools/ArtGen/outputs/mcp_jobs.json"
LOG_PATH = ROOT / "Docs/Phase4_Implementation_Log.md"


def log(msg: str) -> None:
    print(msg, flush=True)
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    LOG_PATH.write_text((LOG_PATH.read_text(encoding="utf-8") if LOG_PATH.exists() else "") + msg + "\n", encoding="utf-8")


def load_json(p: Path) -> Dict[str, Any]:
    return json.loads(p.read_text(encoding="utf-8"))


def clamp_dims(w: int, h: int) -> Tuple[int, int]:
    w = max(256, min(2048, int(w)))
    h = max(256, min(2048, int(h)))
    return w, h


def infer_dims_from_target(target: str, default_w: int, default_h: int) -> Tuple[int, int]:
    name = Path(target).name.lower()
    if "_2048" in name:
        return 2048, 2048
    if "_1024" in name:
        return 1024, 1024
    if "_512" in name:
        return 512, 512
    return clamp_dims(default_w, default_h)


def main() -> int:
    if not CFG_PATH.exists():
        print("Config missing: Tools/ArtGen/artgen_config.json")
        return 1

    cfg = load_json(CFG_PATH)
    batch_files: List[str] = cfg.get("batches", [])
    if not batch_files:
        print("No batches in artgen_config.json")
        return 0

    jobs: List[Dict[str, Any]] = []
    total_items = 0

    for batch in batch_files:
        plan_path = ROOT / batch
        if not plan_path.exists():
            print(f"[MCP-JOBS] Plan not found: {batch}")
            continue
        plan = load_json(plan_path)
        model = plan.get("model") or "black-forest-labs/FLUX.1-schnell"
        defaults = plan.get("defaults", {"steps": 6, "width": 1024, "height": 1024})
        items = plan.get("items", [])
        total_items += len(items)

        for it in items:
            target_rel = Path(it["target"]).as_posix()
            prompt = it.get("prompt", "")
            negative = it.get("negative")
            steps = int(defaults.get("steps", 6))
            w0 = int(defaults.get("width", 1024))
            h0 = int(defaults.get("height", 1024))
            width, height = infer_dims_from_target(target_rel, w0, h0)
            width, height = clamp_dims(width, height)

            out_path = (ROOT / target_rel).resolve()
            out_path.parent.mkdir(parents=True, exist_ok=True)

            job: Dict[str, Any] = {
                "type": "huggingface.flux1_schnell",
                "model": model,
                "parameters": {
                    "prompt": prompt,
                    "negative": negative,
                    "num_inference_steps": max(1, min(16, steps)),
                    "width": width,
                    "height": height,
                    # Deterministic seed from path for stability across runs
                    "seed": abs(hash(target_rel)) % (2**31 - 1),
                },
                "output_path": str(out_path),
                "target_rel": target_rel,
            }
            jobs.append(job)

    JOBS_PATH.parent.mkdir(parents=True, exist_ok=True)
    JOBS_PATH.write_text(json.dumps({
        "root": str(ROOT),
        "jobs": jobs,
        "notes": "Execute with MCP server: huggingface (Flux 1 Schnell). Write PNG bytes to output_path.",
    }, indent=2), encoding="utf-8")

    print(f"Prepared {len(jobs)} MCP jobs (from {len(batch_files)} batches, {total_items} items).")
    print(f"Job file: {JOBS_PATH}")
    print("Next: I (Copilot) will execute the jobs via MCP and write images to disk, then we can run import + manifest.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
