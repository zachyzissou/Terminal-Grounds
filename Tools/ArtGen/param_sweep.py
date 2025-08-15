#!/usr/bin/env python3
"""
Run a tiny parameter sweep over sampler/scheduler/steps/cfg to compare sharpness.
Writes filename prefixes to identify settings and copies results to staging.
"""
import argparse
import json
import os
import urllib.request
from typing import Dict, Any, List, Tuple

from comfyui_api_client import ComfyUIAPIClient
from atmospheric_concept_workflow import create_atmospheric_concept_workflow


def queue_and_wait(client: ComfyUIAPIClient, wf: Dict[str, Any], timeout: int) -> List[str]:
    data = json.dumps({"prompt": wf}).encode("utf-8")
    req = urllib.request.Request(f"{client.base_url}/prompt", data=data, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        body = json.loads(resp.read().decode("utf-8", errors="ignore"))
    pid = body.get("prompt_id", "")
    if not pid:
        return []
    return client.wait_for_completion(pid, timeout=timeout)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--prompt", default="underground metro corridor, single-point perspective, leading lines, vanishing point, industrial lighting fixtures, wet concrete, low haze, atmospheric depth, sharp focus, crisp edges, high micro-contrast, fine surface detail")
    ap.add_argument("--seed", type=int, default=94887)
    ap.add_argument("--width", type=int, default=1920)
    ap.add_argument("--height", type=int, default=1080)
    ap.add_argument("--timeout", type=int, default=600)
    ap.add_argument("--mode", choices=["sharp", "rollback"], default="sharp",
                    help="sharp = edge-crisp profiles; rollback = softer atmospheric profiles")
    args = ap.parse_args()

    client = ComfyUIAPIClient()
    if not client.check_server():
        print("ComfyUI not reachable")
        return 2

    if args.mode == "sharp":
        # Candidates focused on crisp edges
        settings: List[Tuple[str, str, int, float]] = [
            ("euler", "normal", 36, 4.6),
            ("dpmpp_2m", "karras", 28, 4.8),
            ("dpmpp_2m_sde", "karras", 26, 5.0),
            ("heun", "karras", 34, 4.6),
        ]
    else:
        # Softer atmospheric rollback set (closer to earlier look)
        settings = [
            ("euler", "normal", 30, 4.2),
            ("euler", "normal", 28, 4.0),
            ("euler", "normal", 26, 3.8),
        ]

    print(f"Parameter sweep ({args.mode}) (sampler/scheduler/steps/cfg):")
    for sampler, sched, steps, cfg in settings:
        prefix = "SWEEP" if args.mode == "sharp" else "ROLLBACK"
        tag = f"{prefix}_{sampler}_{sched}_s{steps}_cfg{cfg}".replace(".", "p")
        print(f" - {tag}")
        # Slightly bias prompt towards softness in rollback mode
        tuned_prompt = args.prompt
        if args.mode == "rollback":
            tuned_prompt = args.prompt + ", soft volumetric fog, cinematic bloom, gentle contrast, natural texture, not oversharpened"

        wf = create_atmospheric_concept_workflow(
            prompt=tuned_prompt,
            seed=args.seed,
            width=args.width,
            height=args.height,
            steps=steps,
            cfg=cfg,
            sampler_name=sampler,
            scheduler=sched,
            filename_prefix=tag,
        )
        imgs = queue_and_wait(client, wf, timeout=args.timeout)
        if imgs:
            for fn in imgs:
                client.copy_to_staging(fn)
        else:
            print(f"   ✗ No image (timeout or failure) for {tag}")

    print("Done.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
