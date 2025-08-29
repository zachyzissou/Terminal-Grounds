#!/usr/bin/env python3
"""
Documentation Cleanup Script
Terminal Grounds Documentation Control Specialist
"""

import os
import hashlib
from pathlib import Path
from typing import Dict, List, Set

class DocumentationCleanup:
    def __init__(self, root_path: str):
        self.root_path = Path(root_path)
        self.docs_path = self.root_path / "docs"
        self.tools_path = self.root_path / "Tools"

    def find_duplicate_files(self) -> Dict[str, List[Path]]:
        """Find duplicate files based on content hash"""
        file_hashes = {}
        duplicates = {}

        # Scan docs directory
        for md_file in self.docs_path.rglob("*.md"):
            if md_file.is_file():
                file_hash = self._get_file_hash(md_file)
                if file_hash in file_hashes:
                    if file_hash not in duplicates:
                        duplicates[file_hash] = [file_hashes[file_hash]]
                    duplicates[file_hash].append(md_file)
                else:
                    file_hashes[file_hash] = md_file

        return duplicates

    def _get_file_hash(self, file_path: Path) -> str:
        """Calculate SHA256 hash of file content"""
        hasher = hashlib.sha256()
        with open(file_path, 'rb') as f:
            hasher.update(f.read())
        return hasher.hexdigest()

    def identify_problematic_duplicates(self) -> Dict[str, List[Path]]:
        """Identify specific problematic duplicate files"""
        problematic = {}

        # Check for known duplicate patterns
        duplicate_patterns = [
            "CODE_OF_CONDUCT.md",
            "SECURITY.md",
            "README.md"
        ]

        for pattern in duplicate_patterns:
            matches = list(self.root_path.rglob(pattern))
            if len(matches) > 1:
                # Use first file's hash as key
                first_hash = self._get_file_hash(matches[0])
                problematic[first_hash] = matches

        return problematic

    def generate_cleanup_report(self) -> str:
        """Generate a cleanup report"""
        duplicates = self.find_duplicate_files()
        problematic = self.identify_problematic_duplicates()

        report = "# Documentation Cleanup Report\n\n"
        report += f"Generated: {Path(__file__).name}\n\n"

        report += "## Summary\n"
        report += f"- Total duplicate groups: {len(duplicates)}\n"
        report += f"- Problematic duplicates: {len(problematic)}\n\n"

        if problematic:
            report += "## Critical Duplicates to Remove\n"
            for hash_key, files in problematic.items():
                report += f"### {files[0].name}\n"
                for file in files[1:]:  # Skip first file (keep one)
                    report += f"- DELETE: {file.relative_to(self.root_path)}\n"
                report += "\n"

        if duplicates:
            report += "## All Duplicates Found\n"
            for hash_key, files in duplicates.items():
                if len(files) > 1:
                    report += f"### Group ({len(files)} files)\n"
                    for file in files:
                        report += f"- {file.relative_to(self.root_path)}\n"
                    report += "\n"

        return report

def main():
    # Get the script directory - handle both direct execution and -c execution
    if '__file__' in globals():
        script_dir = Path(__file__).parent
        project_root = script_dir.parent.parent  # Tools/DocumentControl -> Tools -> root
    else:
        # Fallback for when running with python -c
        project_root = Path.cwd()

    cleanup = DocumentationCleanup(str(project_root))
    report = cleanup.generate_cleanup_report()

    # Write report
    report_path = project_root / "docs" / "Cleanup_Report.md"
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)

    print(f"Cleanup report generated: {report_path}")

if __name__ == "__main__":
    main()
