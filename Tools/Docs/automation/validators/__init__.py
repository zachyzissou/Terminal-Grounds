"""
Terminal Grounds Documentation Automation Framework
Phase 3: Advanced Governance & Automation

Core automation classes for documentation validation, generation, and monitoring.
Built upon Phase 2 foundation for automated documentation excellence.
"""

import os
import yaml
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class ValidationResult:
    """Result of a validation check"""
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    suggestions: List[str]

@dataclass
class DocumentMetadata:
    """Standardized document metadata"""
    title: str
    type: str
    domain: str
    status: str
    last_reviewed: str
    maintainer: str
    tags: List[str]
    related_docs: List[str]

class DocValidator:
    """
    Base class for document validation
    Provides common validation functionality
    """

    def __init__(self, docs_root: str = "docs"):
        self.docs_root = Path(docs_root)
        self.logger = logging.getLogger(self.__class__.__name__)

    def validate_document(self, doc_path: str) -> ValidationResult:
        """
        Main validation method - override in subclasses
        """
        raise NotImplementedError("Subclasses must implement validate_document")

    def read_document(self, doc_path: str) -> Tuple[Optional[str], Optional[Dict[str, Any]]]:
        """
        Read document content and extract frontmatter
        """
        try:
            with open(doc_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Extract frontmatter if present
            if content.startswith('---'):
                parts = content.split('---', 2)
                if len(parts) >= 3:
                    frontmatter_content = parts[1]
                    body_content = parts[2]

                    try:
                        frontmatter = yaml.safe_load(frontmatter_content)
                        return body_content.strip(), frontmatter
                    except yaml.YAMLError as e:
                        self.logger.error(f"YAML parsing error in {doc_path}: {e}")
                        return content, None

            return content, None

        except Exception as e:
            self.logger.error(f"Error reading document {doc_path}: {e}")
            return None, None

    def validate_frontmatter(self, frontmatter: Optional[Dict[str, Any]]) -> ValidationResult:
        """
        Validate frontmatter structure and content
        """
        errors = []
        warnings = []
        suggestions = []

        if not frontmatter:
            errors.append("Missing frontmatter")
            return ValidationResult(False, errors, warnings, suggestions)

        # Required fields
        required_fields = ['title', 'type', 'domain', 'status', 'last_reviewed', 'maintainer']
        for field in required_fields:
            if field not in frontmatter:
                errors.append(f"Missing required field: {field}")
            elif not frontmatter[field]:
                errors.append(f"Empty required field: {field}")

        # Validate field types and values
        if 'type' in frontmatter:
            valid_types = ['guide', 'reference', 'process', 'spec', 'api']
            if frontmatter['type'] not in valid_types:
                errors.append(f"Invalid type: {frontmatter['type']}. Must be one of {valid_types}")

        if 'domain' in frontmatter:
            valid_domains = ['technical', 'design', 'lore', 'art', 'process']
            if frontmatter['domain'] not in valid_domains:
                errors.append(f"Invalid domain: {frontmatter['domain']}. Must be one of {valid_domains}")

        if 'status' in frontmatter:
            valid_statuses = ['draft', 'review', 'approved', 'deprecated']
            if frontmatter['status'] not in valid_statuses:
                errors.append(f"Invalid status: {frontmatter['status']}. Must be one of {valid_statuses}")

        # Validate date format
        if 'last_reviewed' in frontmatter:
            try:
                datetime.strptime(frontmatter['last_reviewed'], '%Y-%m-%d')
            except ValueError:
                errors.append("last_reviewed must be in YYYY-MM-DD format")

        # Validate tags and related_docs are lists
        for field in ['tags', 'related_docs']:
            if field in frontmatter and not isinstance(frontmatter[field], list):
                errors.append(f"{field} must be a list")

        return ValidationResult(
            len(errors) == 0,
            errors,
            warnings,
            suggestions
        )

class FrontmatterValidator(DocValidator):
    """
    Validates document frontmatter compliance
    """

    def validate_document(self, doc_path: str) -> ValidationResult:
        """
        Validate frontmatter for a single document
        """
        content, frontmatter = self.read_document(doc_path)

        if not content:
            return ValidationResult(False, ["Unable to read document"], [], [])

        return self.validate_frontmatter(frontmatter)

class CrossReferenceValidator(DocValidator):
    """
    Validates cross-references between documents
    """

    def __init__(self, docs_root: str = "docs"):
        super().__init__(docs_root)
        self.doc_index = {}

    def build_document_index(self) -> None:
        """
        Build index of all documents and their metadata
        """
        self.doc_index = {}

        for md_file in self.docs_root.rglob("*.md"):
            if md_file.name.lower() == "readme.md":
                continue

            content, frontmatter = self.read_document(str(md_file))
            if frontmatter:
                relative_path = md_file.relative_to(self.docs_root)
                # Normalize path separators to forward slashes for consistent lookup
                normalized_path = str(relative_path).replace('\\', '/')
                self.doc_index[normalized_path] = frontmatter

    def validate_document(self, doc_path: str) -> ValidationResult:
        """
        Validate cross-references in a document
        """
        errors = []
        warnings = []
        suggestions = []

        content, frontmatter = self.read_document(doc_path)

        if not frontmatter or 'related_docs' not in frontmatter:
            return ValidationResult(True, [], [], [])

        # Check if related documents exist
        for related_doc in frontmatter['related_docs']:
            # Get the directory of the current document for relative path resolution
            current_doc_dir = str(Path(doc_path).parent.relative_to(self.docs_root))

            # Handle different path formats
            if related_doc.startswith('docs/'):
                # Convert full path to relative path for index lookup
                relative_doc = related_doc[5:]  # Remove 'docs/' prefix
            elif related_doc.startswith('../') or related_doc.startswith('./'):
                # Handle relative paths - resolve from current document directory
                try:
                    base_path = Path(self.docs_root) / current_doc_dir
                    resolved_path = (base_path / related_doc).resolve()
                    relative_doc = str(resolved_path.relative_to(self.docs_root))
                    # Normalize path separators
                    relative_doc = relative_doc.replace('\\', '/')
                except (ValueError, RuntimeError):
                    relative_doc = related_doc
            elif '/' not in related_doc and '\\' not in related_doc:
                # Just a filename - search across all directories
                found = False
                # First try same directory
                if current_doc_dir and current_doc_dir != '.':
                    same_dir_path = f"{current_doc_dir}/{related_doc}"
                    if same_dir_path in self.doc_index:
                        relative_doc = same_dir_path
                        found = True

                # If not found in same directory, search all directories
                if not found:
                    for index_path in self.doc_index.keys():
                        if index_path.endswith(f"/{related_doc}") or index_path == related_doc:
                            relative_doc = index_path
                            found = True
                            break

                # If still not found, use as-is (will fail validation)
                if not found:
                    relative_doc = related_doc
            else:
                # Already a relative path
                relative_doc = related_doc

            if relative_doc not in self.doc_index:
                # Try with .md extension
                if not relative_doc.endswith('.md'):
                    related_doc_with_ext = relative_doc + '.md'
                    if related_doc_with_ext not in self.doc_index:
                        errors.append(f"Related document not found: {related_doc}")
                    else:
                        suggestions.append(f"Consider using full path: {related_doc_with_ext}")
                else:
                    errors.append(f"Related document not found: {related_doc}")

        return ValidationResult(
            len(errors) == 0,
            errors,
            warnings,
            suggestions
        )

class NamingValidator(DocValidator):
    """
    Validates document naming consistency
    """

    def __init__(self, docs_root: str = "docs"):
        super().__init__(docs_root)
        self.naming_patterns = {
            'technical': r'^[A-Z][A-Za-z0-9_]+$',
            'design': r'^[A-Z][A-Za-z0-9_\s]+$',
            'lore': r'^[A-Z][A-Za-z0-9_\s]+$',
            'art': r'^[A-Z][A-Za-z0-9_\s]+$',
            'process': r'^[A-Z][A-Za-z0-9_\s]+$'
        }

    def validate_document(self, doc_path: str) -> ValidationResult:
        """
        Validate document naming consistency
        """
        errors = []
        warnings = []
        suggestions = []

        doc_name = Path(doc_path).stem

        content, frontmatter = self.read_document(doc_path)

        if frontmatter and 'domain' in frontmatter:
            domain = frontmatter['domain']
            if domain in self.naming_patterns:
                pattern = self.naming_patterns[domain]
                if not re.match(pattern, doc_name):
                    errors.append(f"Document name '{doc_name}' doesn't match {domain} naming pattern")
                    suggestions.append(f"Consider renaming to follow pattern: {pattern}")

        return ValidationResult(
            len(errors) == 0,
            errors,
            warnings,
            suggestions
        )

# Utility functions
def get_all_markdown_files(docs_root: str = "../../docs") -> List[Path]:
    """
    Get all markdown files in the docs directory
    """
    docs_path = Path(docs_root)
    return list(docs_path.rglob("*.md"))

def validate_all_documents(docs_root: str = "../../docs") -> Dict[str, ValidationResult]:
    """
    Validate all documents using all validators
    """
    docs_path = Path(docs_root)

    validators = [
        FrontmatterValidator(docs_root),
        CrossReferenceValidator(docs_root),
        NamingValidator(docs_root)
    ]

    # Build cross-reference index
    for validator in validators:
        if isinstance(validator, CrossReferenceValidator):
            validator.build_document_index()

    results = {}

    for md_file in get_all_markdown_files(docs_root):
        if md_file.name.lower() == "readme.md":
            continue

        file_results = []
        for validator in validators:
            result = validator.validate_document(str(md_file))
            file_results.append(result)

        # Combine results
        all_errors = []
        all_warnings = []
        all_suggestions = []

        for result in file_results:
            all_errors.extend(result.errors)
            all_warnings.extend(result.warnings)
            all_suggestions.extend(result.suggestions)

        combined_result = ValidationResult(
            len(all_errors) == 0,
            all_errors,
            all_warnings,
            all_suggestions
        )

        results[str(md_file.relative_to(docs_root))] = combined_result

    return results

if __name__ == "__main__":
    # Quick test of the validation system
    print("Testing Terminal Grounds Documentation Validation System")
    print("=" * 60)

    results = validate_all_documents()

    total_docs = len(results)
    valid_docs = sum(1 for result in results.values() if result.is_valid)
    invalid_docs = total_docs - valid_docs

    print(f"Validation Results:")
    print(f"   Total documents: {total_docs}")
    print(f"   Valid documents: {valid_docs}")
    print(f"   Invalid documents: {invalid_docs}")
    print(f"   Success rate: {(valid_docs/total_docs)*100:.1f}%")

    if invalid_docs > 0:
        print(f"Documents with issues:")
        for doc_path, result in results.items():
            if not result.is_valid:
                print(f"   - {doc_path}")
                for error in result.errors[:2]:  # Show first 2 errors
                    print(f"     * {error}")

    print("Validation system operational!")
    print("Phase 3 automation foundation established!")
