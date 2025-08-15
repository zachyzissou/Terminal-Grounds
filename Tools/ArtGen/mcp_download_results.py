#!/usr/bin/env python3
"""
Consume MCP result URLs and persist images to repo paths.

Inputs:
- Tools/ArtGen/outputs/mcp_jobs.json   (emitted by artgen_run_mcp.py)
- Tools/ArtGen/outputs/mcp_results.json  (list of {target_rel, url})

Writes:
- Downloads each URL to the corresponding job's output_path.
- Emits Tools/ArtGen/outputs/mcp_download_report.json
"""
from __future__ import annotations
import json
import sys
import time
from pathlib import Path
import shutil
from urllib.parse import urlparse, unquote

try:
    import requests
except Exception:
    requests = None

ROOT = Path(__file__).resolve().parents[2]
JOBS_PATH = ROOT / "Tools/ArtGen/outputs/mcp_jobs.json"
RESULTS_PATH = ROOT / "Tools/ArtGen/outputs/mcp_results.json"
REPORT_PATH = ROOT / "Tools/ArtGen/outputs/mcp_download_report.json"
LOG_PATH = ROOT / "Docs/Phase4_Implementation_Log.md"


def log(msg: str) -> None:
    print(msg, flush=True)
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(msg + "\n")


def load_json(p: Path):
    return json.loads(p.read_text(encoding="utf-8"))


def _copy_local(src: Path, dst: Path) -> str:
    """Copy a local file from src to dst. Returns status string."""
    try:
        src = src.resolve()
        dst = dst.resolve()
        if src == dst and dst.exists():
            return "same-path"
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, dst)
        return "ok"
    except Exception as e:
        return f"error:{e}"


def _resolve_local_url(url: str) -> Path | None:
    """If url is a file URL or plain path, return a Path, else None."""
    if not url:
        return None
    # file:// URL
    if url.lower().startswith("file://"):
        parsed = urlparse(url)
        # On Windows, parsed.path starts with a '/'
        p = unquote(parsed.path)
        if p.startswith('/') and len(p) > 3 and p[2] == ':':
            p = p[1:]
        return Path(p)
    # Plain absolute/relative path
    try:
        p = Path(url)
        if p.exists():
            return p
    except Exception:
        pass
    return None


def main() -> int:
    if requests is None:
        print("Missing dependency: requests. Install it in your Python environment.")
        return 1

    if not JOBS_PATH.exists():
        print("Job file missing. Run artgen_run_mcp.py first.")
        return 1
    if not RESULTS_PATH.exists():
        print("Results file missing. I need Tools/ArtGen/outputs/mcp_results.json with [{target_rel,url}].")
        return 1

    jobs = load_json(JOBS_PATH)["jobs"]
    results = load_json(RESULTS_PATH)
    url_map = {r["target_rel"]: r["url"] for r in results if r.get("url")}

    ok = 0
    fail = 0
    skipped = 0
    details = []

    for job in jobs:
        target = job["target_rel"]
        out_path = Path(job["output_path"])  # absolute
        url = url_map.get(target)
        if not url:
            details.append({"target": target, "status": "missing-url"})
            fail += 1
            continue

        # Try local copy first if URL is a file or path
        local_src = _resolve_local_url(url)
        if local_src is not None:
            status = _copy_local(local_src, out_path)
            if status == "ok":
                ok += 1
                print(f"  • Copied {target} from {local_src} -> {out_path}")
                details.append({"target": target, "status": "ok", "path": str(out_path)})
                continue
            if status == "same-path":
                ok += 1
                print(f"  • Skipped copy (same path) for {target}: {out_path}")
                details.append({"target": target, "status": "ok-same", "path": str(out_path)})
                continue
            # If copy failed, fall through to HTTP try with error recorded later

        out_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            with requests.get(url, timeout=300, stream=True) as r:
                r.raise_for_status()
                with out_path.open("wb") as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
            ok += 1
            print(f"  • Saved {target} -> {out_path}")
            details.append({"target": target, "status": "ok", "path": str(out_path)})
        except Exception as e:
            fail += 1
            print(f"  • Error saving {target}: {e}")
            details.append({"target": target, "status": "error", "error": str(e)})

    report = {"ok": ok, "fail": fail, "skipped": skipped, "time": time.time(), "details": details}
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(report, indent=2), encoding="utf-8")
    log(f"[MCP-Download] ok={ok} fail={fail} • wrote {REPORT_PATH.relative_to(ROOT)}")
    print(f"Report: {REPORT_PATH}")
    return 0 if fail == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
