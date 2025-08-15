#!/usr/bin/env python3
"""
Batch download/copy files from URLs (http/https) or local file paths into a target directory.
- Input JSON: {
    "output_dir": "Tools/ArtGen/inputs/downloads",
    "files": [ { "name": "my_asset.png", "url": "https://... or file:///C:/... or C:/..." } ]
  }
- Writes a small report next to the input file: <input>.report.json
"""
from __future__ import annotations
import argparse
import json
import os
from pathlib import Path
import shutil
import sys
from urllib.parse import urlparse
from urllib.request import urlopen

try:
    import requests  # type: ignore
except Exception:
    requests = None


def _resolve_local(url_or_path: str) -> Path | None:
    # Support file:// URLs or plain paths
    p = urlparse(url_or_path)
    if p.scheme == "file":
        candidate = Path(p.path)
    elif p.scheme == "":
        candidate = Path(url_or_path)
    else:
        return None
    if candidate.exists():
        return candidate
    return None


def _ensure_dir(d: Path) -> None:
    d.mkdir(parents=True, exist_ok=True)


def _http_download(url: str, dst: Path) -> tuple[bool, str]:
    # Prefer requests if available; fall back to urllib
    try:
        if requests is not None:
            with requests.get(url, stream=True, timeout=60) as r:
                r.raise_for_status()
                with open(dst, "wb") as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
            return True, "ok"
        else:
            with urlopen(url, timeout=60) as r, open(dst, "wb") as f:
                shutil.copyfileobj(r, f)
            return True, "ok"
    except Exception as e:
        return False, f"http-error: {e}"


def _copy_local(src: Path, dst: Path) -> tuple[bool, str]:
    try:
        if src.resolve() == dst.resolve():
            return True, "same-path"
        _ensure_dir(dst.parent)
        shutil.copy2(src, dst)
        return True, "copied"
    except Exception as e:
        return False, f"copy-error: {e}"


def run(input_json: Path) -> int:
    data = json.loads(input_json.read_text(encoding="utf-8"))
    out_dir = Path(data.get("output_dir", "."))
    _ensure_dir(out_dir)

    files = data.get("files", [])
    results = []
    ok = 0
    fail = 0

    for item in files:
        name = item.get("name")
        url = item.get("url")
        if not name or not url:
            results.append({"name": name, "url": url, "status": "missing-field"})
            fail += 1
            continue
        dst = out_dir / name

        # Try local copy first
        local = _resolve_local(url)
        if local is not None:
            success, msg = _copy_local(local, dst)
        else:
            success, msg = _http_download(url, dst)

        results.append({"name": name, "url": url, "dst": str(dst), "status": msg})
        if success:
            ok += 1
        else:
            fail += 1

    report = {
        "input": str(input_json),
        "output_dir": str(out_dir),
        "ok": ok,
        "fail": fail,
        "results": results,
    }
    report_path = input_json.with_suffix(".report.json")
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print(f"[URL-Download] ok={ok} fail={fail} → {report_path}")
    return 0 if fail == 0 else 1


def main() -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="mode")

    # JSON mode (default)
    ap_json = sub.add_parser("json", help="Download from input JSON file")
    ap_json.add_argument("input", type=str, help="Path to input JSON with output_dir and files")

    # Single mode
    ap_single = sub.add_parser("single", help="Download a single URL to a file name")
    ap_single.add_argument("url", type=str, help="Source URL or local path (supports file://)")
    ap_single.add_argument("name", type=str, help="Destination file name (e.g., my.png)")
    ap_single.add_argument("--outdir", type=str, default="Tools/ArtGen/inputs/downloads", help="Output directory")

    args = ap.parse_args()
    if args.mode == "single":
        out_dir = Path(args.outdir)
        _ensure_dir(out_dir)
        dst = out_dir / args.name
        local = _resolve_local(args.url)
        if local is not None:
            success, msg = _copy_local(local, dst)
        else:
            success, msg = _http_download(args.url, dst)
        report = {
            "mode": "single",
            "ok": 1 if success else 0,
            "fail": 0 if success else 1,
            "result": {"name": args.name, "url": args.url, "dst": str(dst), "status": msg},
        }
        report_path = dst.with_suffix(dst.suffix + ".report.json")
        report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
        print(f"[URL-Download:single] {msg} → {dst} • report: {report_path}")
        return 0 if success else 1

    # default to json mode if unspecified
    input_arg = getattr(args, "input", None)
    if not input_arg:
        ap.print_help()
        return 2
    return run(Path(input_arg))


if __name__ == "__main__":
    sys.exit(main())
