#!/usr/bin/env python3
"""Repository inventory script.
Walks the repo and records file metadata including path, type, size,
Git LFS tracking status, and suspicious names.
Outputs JSON inventory and Markdown summary.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, List

REPO_ROOT = Path(__file__).resolve().parents[2]
AUDIT_DIR = REPO_ROOT / "Docs" / "Audits"
AUDIT_DIR.mkdir(parents=True, exist_ok=True)

# build set of files tracked by Git LFS
LFS_FILES = {
    line.split(None, 2)[-1]: True
    for line in subprocess.run([
        "git",
        "lfs",
        "ls-files",
    ], capture_output=True, text=True).stdout.splitlines()
    if line.strip()
}

SUSPICIOUS_RE = re.compile(r"(temp|placeholder|wip|backup)", re.IGNORECASE)

EXT_TYPE_MAP: Dict[str, str] = {
    # code
    ".c": "code",
    ".cpp": "code",
    ".h": "code",
    ".hpp": "code",
    ".cs": "code",
    ".py": "code",
    ".sh": "code",
    # config
    ".ini": "config",
    ".json": "config",
    ".yml": "config",
    ".yaml": "config",
    ".cfg": "config",
    # docs
    ".md": "doc",
    ".rst": "doc",
    ".txt": "doc",
    # content/binary
    ".uasset": "content",
    ".umap": "content",
    ".png": "content",
    ".jpg": "content",
    ".jpeg": "content",
    ".tga": "content",
    ".wav": "content",
    ".flac": "content",
    ".mp3": "content",
    ".ogg": "content",
    ".fbx": "content",
}

@dataclass
class Entry:
    path: str
    type: str
    size: int
    lfs: bool
    suspicious: bool


def classify(path: Path) -> str:
    return EXT_TYPE_MAP.get(path.suffix.lower(), "other")


def gather() -> List[Entry]:
    entries: List[Entry] = []
    for root, _, files in os.walk(REPO_ROOT):
        for name in files:
            rel_path = os.path.relpath(os.path.join(root, name), REPO_ROOT)
            # skip inventory outputs
            if rel_path.startswith("Docs/Audits/.inventory"):
                continue
            fpath = Path(root) / name
            ftype = classify(fpath)
            size = fpath.stat().st_size
            lfs = rel_path in LFS_FILES
            suspicious = bool(SUSPICIOUS_RE.search(name))
            entries.append(Entry(rel_path.replace("\\", "/"), ftype, size, lfs, suspicious))
    return entries


def write_outputs(entries: List[Entry]) -> None:
    json_path = AUDIT_DIR / ".inventory.json"
    with json_path.open("w", encoding="utf-8") as jf:
        json.dump([asdict(e) for e in entries], jf, indent=2)

    total_by_type: Dict[str, int] = {}
    for e in entries:
        total_by_type[e.type] = total_by_type.get(e.type, 0) + 1

    suspicious_entries = [e for e in entries if e.suspicious]

    md_path = AUDIT_DIR / "TG_Audit_Inventory.md"
    with md_path.open("w", encoding="utf-8") as mf:
        mf.write("# Repository Inventory\n\n")
        mf.write("## Summary\n\n")
        for t, count in sorted(total_by_type.items()):
            mf.write(f"- **{t}**: {count} files\n")
        mf.write(f"- **Total**: {len(entries)} files\n\n")

        if suspicious_entries:
            mf.write("## Suspicious Filenames\n\n")
            mf.write("| Path | Notes |\n|---|---|\n")
            for e in suspicious_entries:
                note = "suspect name"
                mf.write(f"| {e.path} | {note} |\n")
        else:
            mf.write("No suspicious filenames detected.\n")


if __name__ == "__main__":
    write_outputs(gather())
