#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Terminal Grounds - Header Validator

Purpose:
- Validate that source files contain the required project header.
- Optionally warn on Unreal UCLASS macros missing Blueprintable when BlueprintSpawnableComponent is present.

Notes:
- By default, this script is non-strict and will return exit code 0 even if warnings are found.
- Set STRICT mode via CLI flag (--strict) to make warnings fail the check with exit code 1.
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path
from typing import List, Tuple


REQUIRED_HEADER = "// Copyright Terminal Grounds. All Rights Reserved."

# Files to check (extensions)
CHECK_EXTENSIONS = {".h", ".hpp", ".cpp", ".cc", ".cxx"}


def find_source_files(root: Path) -> List[Path]:
    files: List[Path] = []
    include_dirs = [
        root / "Source",
        root / "Plugins",
        root / "Plugins_Disabled",
    ]
    for base in include_dirs:
        if not base.exists():
            continue
        for p in base.rglob("*"):
            if p.is_file() and p.suffix.lower() in CHECK_EXTENSIONS:
                files.append(p)
    return files


def has_required_header(path: Path) -> bool:
    try:
        with path.open("r", encoding="utf-8", errors="ignore") as f:
            # Read just the first few lines
            head = "\n".join([next(f, "") for _ in range(5)])
            return REQUIRED_HEADER in head
    except Exception:
        return False


UCLASS_RE = re.compile(r"^\s*UCLASS\s*\(([^)]*)\)")


def check_uclass_attributes(path: Path) -> List[str]:
    """Warn if a UCLASS with BlueprintSpawnableComponent lacks Blueprintable."""
    warnings: List[str] = []
    try:
        with path.open("r", encoding="utf-8", errors="ignore") as f:
            for i, line in enumerate(f, start=1):
                m = UCLASS_RE.search(line)
                if not m:
                    continue
                attrs = m.group(1)
                has_spawnable = "BlueprintSpawnableComponent" in attrs
                has_blueprintable = "Blueprintable" in attrs
                if has_spawnable and not has_blueprintable:
                    warnings.append(
                        f"{path}:{i}: UCLASS has BlueprintSpawnableComponent but is missing Blueprintable"
                    )
    except Exception:
        # Ignore unreadable files
        pass
    return warnings


def main(argv: List[str]) -> int:
    parser = argparse.ArgumentParser(description="Validate source file headers for Terminal Grounds")
    parser.add_argument("--root", type=str, default=str(Path(__file__).resolve().parents[1]), help="Project root path")
    parser.add_argument("--strict", action="store_true", help="Fail on warnings (exit code 1)")
    args = parser.parse_args(argv)

    root = Path(args.root).resolve()
    if not root.exists():
        print(f"[ERROR] Root path does not exist: {root}")
        return 1

    print("= Terminal Grounds Header Validator =")
    print(f"Root: {root}")

    files = find_source_files(root)
    print(f"Scanning {len(files)} source files...")

    missing_header: List[Path] = []
    uclass_warnings: List[str] = []

    for fp in files:
        if not has_required_header(fp):
            missing_header.append(fp)
        # Only check headers for UCLASS attributes; cpp may also contain macros but cheaper to check all
        uclass_warnings.extend(check_uclass_attributes(fp))

    status = 0

    if missing_header:
        print("\n[WARN] Files missing required project header:")
        for p in missing_header[:50]:
            print(f" - {p}")
        if len(missing_header) > 50:
            print(f"   ... and {len(missing_header) - 50} more")
        if args.strict:
            status = 1

    if uclass_warnings:
        print("\n[WARN] UCLASS attribute issues:")
        for w in uclass_warnings[:100]:
            print(" - " + w)
        if len(uclass_warnings) > 100:
            print(f"   ... and {len(uclass_warnings) - 100} more")
        if args.strict:
            status = 1

    if status == 0:
        print("\n[SUCCESS] Header validation completed with no blocking issues.")
    else:
        print("\n[FAIL] Header validation found issues. Run with --strict disabled to bypass, or fix warnings.")

    return status


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
