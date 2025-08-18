"""Validate generated image outputs and metadata."""

from __future__ import annotations

import hashlib
import json
import pathlib
import sys


def sha256(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def validate_one(img_path: pathlib.Path) -> bool:
    meta = img_path.with_suffix(img_path.suffix + ".json")
    if not img_path.exists():
        raise FileNotFoundError("image missing")
    if not meta.exists():
        raise FileNotFoundError("sidecar metadata missing")
    data = json.loads(meta.read_text())
    w = data.get("width")
    h = data.get("height")
    if not isinstance(w, int) or not isinstance(h, int) or w <= 0 or h <= 0:
        raise ValueError("bad resolution")
    model_hash = data.get("model", {}).get("hash")
    if not model_hash:
        raise ValueError("missing model hash")
    recorded = data.get("sha256")
    if recorded and recorded != sha256(img_path):
        raise ValueError("image hash mismatch")
    return True


def main(out_dir: str) -> None:
    out = pathlib.Path(out_dir)
    failures: list[tuple[str, str]] = []
    for p in out.rglob("*.png"):
        try:
            validate_one(p)
        except (FileNotFoundError, ValueError, json.JSONDecodeError) as exc:
            failures.append((str(p), str(exc)))
    if failures:
        print("QA FAIL:", json.dumps(failures, indent=2))
        sys.exit(2)
    print("QA PASS")


if __name__ == "__main__":
    main(sys.argv[1])