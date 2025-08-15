#!/usr/bin/env python3
"""
Diagnostic: queue an atmospheric workflow and poll history for outputs/errors.
"""
import argparse
import json
import os
import sys
import time
from pathlib import Path
import urllib.request
import urllib.error
from comfyui_api_client import ComfyUIAPIClient, COMFYUI_OUTPUT
from atmospheric_concept_workflow import create_atmospheric_concept_workflow

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--prompt", default="underground metro corridor, industrial lighting, wet concrete, atmospheric depth")
    p.add_argument("--width", type=int, default=1024)
    p.add_argument("--height", type=int, default=576)
    p.add_argument("--steps", type=int, default=12)
    p.add_argument("--cfg", type=float, default=4.0)
    p.add_argument("--timeout", type=int, default=600,
                   help="Max seconds to wait for completion (defaults to 10 minutes for high-res)")
    p.add_argument("--poll-output", action="store_true",
                   help="Also watch the ComfyUI output folder for new files while waiting")
    p.add_argument("--copy-to-staging", action="store_true",
                   help="Copy any found outputs to staging after completion")
    p.add_argument("--sampler", default="euler")
    p.add_argument("--scheduler", default="normal")
    p.add_argument("--seed", type=int, default=94887)
    p.add_argument("--prefix", default="PROD_CONCEPT_ART")
    p.add_argument("--negative", default="")
    args = p.parse_args()

    client = ComfyUIAPIClient()
    print("Server:", client.base_url)
    if not client.check_server():
        print("Server not reachable; start ComfyUI first.")
        return 2

    wf = create_atmospheric_concept_workflow(
        prompt=args.prompt,
        seed=args.seed,
        width=args.width,
        height=args.height,
        steps=args.steps,
        cfg=args.cfg,
        sampler_name=args.sampler,
        scheduler=args.scheduler,
    filename_prefix=args.prefix,
    negative_text=(args.negative or None),
    )

    # Queue
    data = json.dumps({"prompt": wf}).encode("utf-8")
    req = urllib.request.Request(f"{client.base_url}/prompt", data=data, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            body = resp.read().decode("utf-8", errors="ignore")
            print("Queued:", body)
            try:
                queued = json.loads(body)
                prompt_id = queued.get("prompt_id", "")
                qnum = queued.get("number")
                if qnum is not None:
                    print(f"Queue position: {qnum}")
            except Exception:
                prompt_id = ""
    except urllib.error.HTTPError as e:
        print("HTTPError queueing:", e.code)
        try:
            print(e.read().decode("utf-8", errors="ignore"))
        except Exception:
            pass
        return 3
    except Exception as e:
        print("Error queueing:", e)
        return 4

    if not prompt_id:
        print("No prompt_id returned.")
        return 5

    # Prepare optional output folder polling
    start = time.time()
    last_print = 0
    seen_files = set()
    output_dir: Path = COMFYUI_OUTPUT
    if args.poll_output:
        try:
            if output_dir.exists():
                for f in output_dir.glob("PROD_CONCEPT_ART*.png"):
                    seen_files.add(f.name)
        except Exception:
            pass

    # Poll history
    while time.time() - start < args.timeout:
        try:
            with urllib.request.urlopen(f"{client.base_url}/history/{prompt_id}", timeout=10) as resp:
                hist = json.loads(resp.read().decode("utf-8", errors="ignore"))
            if prompt_id in hist:
                entry = hist[prompt_id]
                # Print any errors
                if entry.get("node_errors"):
                    print("node_errors:")
                    print(json.dumps(entry["node_errors"], indent=2))
                outputs = entry.get("outputs", {})
                images = []
                for node_output in outputs.values():
                    for img in node_output.get("images", []):
                        images.append(img.get("filename"))
                if images:
                    elapsed = int(time.time() - start)
                    print("Images:", images)
                    print(f"Elapsed: {elapsed}s")
                    if args.copy_to_staging:
                        try:
                            for fn in images:
                                client.copy_to_staging(fn)
                        except Exception:
                            pass
                    return 0
            else:
                # print a dot every 3s
                if time.time() - last_print > 3:
                    print("waiting...")
                    last_print = time.time()
        except Exception as e:
            if time.time() - last_print > 3:
                print("history error:", e)
                last_print = time.time()

        # Optional output folder polling: detect new files by prefix and mtime
        if args.poll_output and output_dir.exists():
            try:
                for f in sorted(output_dir.glob("PROD_CONCEPT_ART*.png"), key=lambda p: p.stat().st_mtime, reverse=True):
                    if f.name not in seen_files and f.stat().st_mtime >= start - 1:
                        elapsed = int(time.time() - start)
                        print(f"Found new output in folder: {f.name}")
                        print(f"Elapsed: {elapsed}s")
                        if args.copy_to_staging:
                            try:
                                client.copy_to_staging(f.name)
                            except Exception:
                                pass
                        return 0
            except Exception:
                pass
        time.sleep(1)

    print("Timeout waiting for completion.")
    return 6

if __name__ == "__main__":
    sys.exit(main())
