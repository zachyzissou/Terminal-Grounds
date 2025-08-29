#!/usr/bin/env python3
"""
Simple validation script for Phase 4.1 roadmap document
"""

import sys
import os
sys.path.append('Tools/Docs/automation')

from validators import DocValidator, ValidationResult
import yaml
from pathlib import Path

class SimpleValidator(DocValidator):
    def validate_document(self, doc_path):
        content, frontmatter = self.read_document(doc_path)
        if not content:
            return ValidationResult(False, ['Cannot read document'], [], [])

        errors = []
        warnings = []

        # Check for duplicate H1 headings
        lines = content.split('\n')
        h1_count = sum(1 for line in lines if line.strip().startswith('# '))
        if h1_count > 1:
            errors.append(f'Found {h1_count} H1 headings, expected 1')

        # Check for proper list formatting
        for i, line in enumerate(lines):
            if line.strip().startswith('- ') and i > 0:
                prev_line = lines[i-1].strip()
                if prev_line and not prev_line.endswith(':') and not prev_line.startswith('#'):
                    warnings.append(f'Line {i+1}: List item may need blank line before it')

        return ValidationResult(len(errors) == 0, errors, warnings, [])

if __name__ == "__main__":
    validator = SimpleValidator('docs')
    result = validator.validate_document('docs/PHASE_4_1_CONTENT_GOVERNANCE_ROADMAP.md')

    print("Phase 4.1 Roadmap Validation Results")
    print("=" * 40)
    print(f'Status: {"PASS" if result.is_valid else "FAIL"}')

    if result.errors:
        print('\nErrors:')
        for error in result.errors:
            print(f'  - {error}')

    if result.warnings:
        print('\nWarnings:')
        for warning in result.warnings:
            print(f'  - {warning}')

    if result.is_valid and not result.warnings:
        print('\n✅ Document formatting is valid!')
