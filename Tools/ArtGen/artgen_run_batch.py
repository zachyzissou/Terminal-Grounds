#!/usr/bin/env python3
"""
artgen_run_batch.py

Reads Tools/ArtGen/artgen_config.json and listed batch plan files, then generates
images using Hugging Face Inference API (Flux.1-schnell by default) and writes
them to the specified target paths on disk.

Requirements:
- Set environment variable HF_TOKEN to a valid Hugging Face access token
- Python 'requests' package available (uses stdlib fallback if missing instructs user)

Safety:
- Concurrency is limited (default 2). Retries with backoff on transient errors.
- Skips existing files by default (use --force to overwrite).
"""
import os
import sys
import json
import time
import hashlib
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

ROOT = Path(__file__).resolve().parents[2]
CFG_PATH = ROOT / "Tools/ArtGen/artgen_config.json"
LOG_PATH = ROOT / "Docs/Phase4_Implementation_Log.md"


def log(msg: str) -> None:
    print(msg, flush=True)
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(msg + "\n")


def load_json(p: Path) -> dict:
    with p.open("r", encoding="utf-8") as f:
        return json.load(f)


def ensure_requests():
    try:
        import requests  # noqa: F401
        return True
    except Exception:
        return False


def load_env_file(dotenv_path: Path) -> None:
    """Minimal .env loader to avoid extra deps.
    Lines like KEY=VALUE, ignores comments and blanks. Does not overwrite existing env vars.
    """
    try:
        if not dotenv_path.exists():
            return
        for raw in dotenv_path.read_text(encoding="utf-8").splitlines():
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                continue
            key, val = line.split("=", 1)
            key = key.strip()
            val = val.strip().strip('"').strip("'")
            if key and (key not in os.environ):
                os.environ[key] = val
    except Exception:
        # Non-fatal
        pass


def clamp_dims(w: int, h: int) -> tuple[int, int]:
    # Guardrails: 256..2048 and square by default
    w = max(256, min(2048, int(w)))
    h = max(256, min(2048, int(h)))
    return w, h


def infer_dims_from_target(target: str, default_w: int, default_h: int) -> tuple[int, int]:
    name = Path(target).name.lower()
    if "_2048" in name:
        return 2048, 2048
    if "_1024" in name:
        return 1024, 1024
    if "_512" in name:
        return 512, 512
    return clamp_dims(default_w, default_h)


def build_payload(prompt: str, negative: str | None, steps: int, width: int, height: int, seed: int | None):
    params = {
        "num_inference_steps": max(1, min(16, int(steps))),
        "width": width,
        "height": height,
    }
    if negative:
        params["negative_prompt"] = negative
    if seed is not None:
        params["seed"] = int(seed)
    return {
        "inputs": prompt,
        "parameters": params,
    }


def hf_generate_image(model_id: str, token: str, prompt: str, negative: str | None, steps: int, width: int, height: int, seed: int | None, retries: int = 3, backoff: float = 1.5) -> bytes:
    import requests

    url = f"https://api-inference.huggingface.co/models/{model_id}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "image/png",
        "Content-Type": "application/json",
    }
    payload = build_payload(prompt, negative, steps, width, height, seed)
    last_err = None
    for i in range(retries):
        try:
            r = requests.post(url, headers=headers, json=payload, timeout=120)
            if r.status_code == 200:
                return r.content
            # 503 (loading) or 5xx: backoff
            last_err = f"HTTP {r.status_code}: {r.text[:200]}"
        except Exception as e:
            last_err = str(e)
        sleep_s = backoff ** i
        time.sleep(sleep_s)
    raise RuntimeError(f"HF generation failed after {retries} attempts: {last_err}")


def sha_short(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()[:10]


def process_item(model_id: str, token: str, defaults: dict, item: dict, out_root: Path, force: bool = False) -> dict:
    target_rel = Path(item["target"]).as_posix()
    prompt = item.get("prompt", "")
    negative = item.get("negative")
    steps = int(defaults.get("steps", 6))
    w0 = int(defaults.get("width", 1024))
    h0 = int(defaults.get("height", 1024))
    # Derive dims
    width, height = infer_dims_from_target(target_rel, w0, h0)
    width, height = clamp_dims(width, height)
    # Decide seed: deterministic per target by default
    seed = item.get("seed")
    if seed is None:
        seed = int(hashlib.sha256(target_rel.encode("utf-8")).hexdigest(), 16) % (2**31 - 1)

    out_path = (out_root / target_rel).resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)

    if out_path.exists() and not force:
        return {"target": target_rel, "status": "skipped-exists", "width": width, "height": height}

    img_bytes = hf_generate_image(model_id, token, prompt, negative, steps, width, height, seed)
    out_path.write_bytes(img_bytes)
    return {
        "target": target_rel,
        "status": "ok",
        "width": width,
        "height": height,
        "sha": sha_short(img_bytes),
    }


def main(argv: list[str]) -> int:
    # Load ROOT/.env if present (doesn't overwrite existing vars)
    load_env_file(ROOT / ".env")

    if not ensure_requests():
        print("Missing dependency: requests. Please install it in your Python environment.")
        return 1

    token = os.getenv("HF_TOKEN")
    if not token:
        print("HF_TOKEN is not set. Set it in .env at repo root or export it in your environment (needs Inference API access).")
        return 1

    cfg = load_json(CFG_PATH)
    batch_files = cfg.get("batches", [])
    if not batch_files:
        print("No batches specified in Tools/ArtGen/artgen_config.json")
        return 0

    force = "--force" in argv
    try:
        max_workers = int(os.getenv("ARTGEN_MAX_WORKERS", "2"))
    except Exception:
        max_workers = 2

    total_items = 0
    total_ok = 0
    total_skip = 0
    results = []

    for batch in batch_files:
        plan_path = ROOT / batch
        if not plan_path.exists():
            log(f"[ArtGen] Plan not found: {batch}")
            continue
        plan = load_json(plan_path)
        model = plan.get("model") or "black-forest-labs/FLUX.1-schnell"
        defaults = plan.get("defaults", {"steps": 6, "width": 1024, "height": 1024})
        items = plan.get("items", [])
        total_items += len(items)
        log(f"[ArtGen] Batch: {batch} • model={model} • items={len(items)}")

        with ThreadPoolExecutor(max_workers=max_workers) as ex:
            futs = [
                ex.submit(process_item, model, token, defaults, it, ROOT, force)
                for it in items
            ]
            for fut in as_completed(futs):
                try:
                    r = fut.result()
                    results.append(r)
                    if r["status"] == "ok":
                        total_ok += 1
                        print(f"  • Wrote {r['target']} [{r['width']}x{r['height']}] {r.get('sha','')}")
                    else:
                        total_skip += 1
                        print(f"  • Skipped {r['target']} (exists)")
                except Exception as e:
                    print(f"  • Error: {e}")

    log(f"[ArtGen] Summary: items={total_items}, generated={total_ok}, skipped={total_skip}")
    # Write a machine-readable drop next to plans
    out_report = ROOT / "Tools/ArtGen/outputs/run_report.json"
    out_report.parent.mkdir(parents=True, exist_ok=True)
    out_report.write_text(json.dumps({
        "total": total_items,
        "ok": total_ok,
        "skipped": total_skip,
        "results": results,
    }, indent=2), encoding="utf-8")
    print("Wrote run report to Tools/ArtGen/outputs/run_report.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
