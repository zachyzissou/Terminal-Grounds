"""
Terminal Grounds Documentation Automation Framework
Phase 4.1.2.3: Consistency Validation System

Automated validation of terminology consistency, reference integrity,
format consistency, and metadata standardization across documentation.
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Set
from dataclasses import dataclass
from datetime import datetime
import logging
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class ConsistencyIssue:
    """Represents a consistency issue found across documents"""
    issue_type: str  # 'terminology', 'reference', 'format', 'metadata'
    severity: str    # 'error', 'warning', 'info'
    document_path: str
    line_number: int
    inconsistent_term: str
    suggested_term: str
    context: str
    related_documents: List[str]

@dataclass
class TerminologyStandard:
    """Standard terminology definition"""
    preferred_term: str
    alternatives: List[str]
    category: str
    description: str
    examples: List[str]

@dataclass
class ConsistencyValidationResult:
    """Result of consistency validation"""
    total_issues: int
    issues_by_type: Dict[str, List[ConsistencyIssue]]
    terminology_coverage: float
    reference_integrity_score: float
    format_consistency_score: float
    metadata_consistency_score: float
    overall_consistency_score: float
    recommendations: List[Dict[str, Any]]

class TerminologyConsistencyValidator:
    """
    Validates terminology consistency across documents
    """

    def __init__(self):
        self.terminology_standards = self._load_terminology_standards()
        self.term_usage_patterns = {}

    def _load_terminology_standards(self) -> Dict[str, TerminologyStandard]:
        """Load terminology standards"""
        return {
            # Technical terms
            'api': TerminologyStandard(
                preferred_term='API',
                alternatives=['api', 'Api', 'application programming interface'],
                category='technical',
                description='Application Programming Interface',
                examples=['REST API', 'API documentation', 'API endpoint']
            ),
            'frontend': TerminologyStandard(
                preferred_term='frontend',
                alternatives=['front-end', 'front end', 'Frontend'],
                category='technical',
                description='User interface and client-side components',
                examples=['frontend development', 'frontend framework']
            ),
            'backend': TerminologyStandard(
                preferred_term='backend',
                alternatives=['back-end', 'back end', 'Backend'],
                category='technical',
                description='Server-side components and logic',
                examples=['backend services', 'backend API']
            ),
            'database': TerminologyStandard(
                preferred_term='database',
                alternatives=['Database', 'DB', 'data store'],
                category='technical',
                description='Data storage system',
                examples=['database schema', 'database connection']
            ),
            # Project-specific terms
            'terminal grounds': TerminologyStandard(
                preferred_term='Terminal Grounds',
                alternatives=['terminal-grounds', 'Terminal-Grounds', 'terminal grounds'],
                category='project',
                description='Project name - always capitalize both words',
                examples=['Terminal Grounds project', 'Terminal Grounds documentation']
            ),
            'unreal engine': TerminologyStandard(
                preferred_term='Unreal Engine',
                alternatives=['unreal-engine', 'Unreal-Engine', 'unreal engine'],
                category='project',
                description='Game engine - always capitalize both words',
                examples=['Unreal Engine 5', 'Unreal Engine project']
            ),
            # Common documentation terms
            'github': TerminologyStandard(
                preferred_term='GitHub',
                alternatives=['github', 'Github', 'git hub'],
                category='platform',
                description='Version control platform',
                examples=['GitHub repository', 'GitHub Actions']
            ),
            'markdown': TerminologyStandard(
                preferred_term='Markdown',
                alternatives=['markdown', 'MARKDOWN'],
                category='format',
                description='Markup language for documentation',
                examples=['Markdown file', 'Markdown syntax']
            )
        }

    def validate_document_terminology(self, doc_path: str, content: str,
                                    line_offset: int = 0) -> List[ConsistencyIssue]:
        """
        Validate terminology consistency in a document
        """
        issues = []

        lines = content.split('\n')

        for line_num, line in enumerate(lines, 1):
            for standard in self.terminology_standards.values():
                # Check for alternative terms that should be standardized
                for alternative in standard.alternatives:
                    if alternative.lower() in line.lower():
                        # Check if it's not already the preferred term
                        if standard.preferred_term.lower() not in line.lower():
                            issues.append(ConsistencyIssue(
                                issue_type='terminology',
                                severity='warning',
                                document_path=doc_path,
                                line_number=line_num + line_offset,
                                inconsistent_term=alternative,
                                suggested_term=standard.preferred_term,
                                context=line.strip(),
                                related_documents=[]  # Will be populated later
                            ))

        return issues

    def analyze_terminology_usage(self, documents: Dict[str, str]) -> Dict[str, Any]:
        """
        Analyze terminology usage across all documents
        """
        usage_analysis = {}

        for term_key, standard in self.terminology_standards.items():
            usage_analysis[term_key] = {
                'preferred_term': standard.preferred_term,
                'usage_count': 0,
                'inconsistent_usage': 0,
                'documents_affected': []
            }

        for doc_path, content in documents.items():
            for term_key, standard in self.terminology_standards.items():
                # Count preferred term usage
                preferred_count = content.lower().count(standard.preferred_term.lower())
                usage_analysis[term_key]['usage_count'] += preferred_count

                # Count inconsistent usage
                inconsistent_count = 0
                for alternative in standard.alternatives:
                    alt_count = content.lower().count(alternative.lower())
                    inconsistent_count += alt_count

                if inconsistent_count > 0:
                    usage_analysis[term_key]['inconsistent_usage'] += inconsistent_count
                    usage_analysis[term_key]['documents_affected'].append(doc_path)

        return usage_analysis

class ReferenceIntegrityValidator:
    """
    Validates reference integrity across documents
    """

    def __init__(self):
        self.reference_patterns = [
            (r'\[([^\]]+)\]\(([^)]+)\)', 'markdown_link'),  # [text](url)
            (r'<([^>]+)>', 'url'),  # <url>
            (r'`([^`]+)`', 'code_reference'),  # `code`
            (r'\b([A-Z][a-z]+(?:[A-Z][a-z]+)+)\b', 'pascal_case'),  # PascalCase
            (r'\b([a-z]+(?:_[a-z]+)+)\b', 'snake_case'),  # snake_case
        ]

    def validate_document_references(self, doc_path: str, content: str,
                                   all_documents: Dict[str, str],
                                   line_offset: int = 0) -> List[ConsistencyIssue]:
        """
        Validate reference integrity in a document
        """
        issues = []
        lines = content.split('\n')

        for line_num, line in enumerate(lines, 1):
            for pattern, ref_type in self.reference_patterns:
                matches = re.finditer(pattern, line)
                for match in matches:
                    reference = match.group(1)

                    if ref_type == 'markdown_link':
                        # Validate markdown links
                        url = match.group(2)
                        if self._is_internal_link(url):
                            issues.extend(self._validate_internal_link(
                                url, doc_path, all_documents, line_num + line_offset, line
                            ))
                    elif ref_type in ['pascal_case', 'snake_case']:
                        # Validate code references
                        issues.extend(self._validate_code_reference(
                            reference, ref_type, doc_path, all_documents, line_num + line_offset, line
                        ))

        return issues

    def _is_internal_link(self, url: str) -> bool:
        """Check if URL is an internal link"""
        return not url.startswith(('http://', 'https://', 'mailto:', '#'))

    def _validate_internal_link(self, url: str, doc_path: str,
                              all_documents: Dict[str, str], line_num: int,
                              context: str) -> List[ConsistencyIssue]:
        """Validate internal link exists"""
        issues = []

        # Convert relative path to absolute
        doc_dir = Path(doc_path).parent
        try:
            target_path = (doc_dir / url).resolve()
            target_path_str = str(target_path)

            # Check if target exists in our document collection
            if target_path_str not in all_documents:
                # Try with .md extension
                if not target_path_str.endswith('.md'):
                    target_with_md = target_path_str + '.md'
                    if target_with_md not in all_documents:
                        issues.append(ConsistencyIssue(
                            issue_type='reference',
                            severity='error',
                            document_path=doc_path,
                            line_number=line_num,
                            inconsistent_term=url,
                            suggested_term=f"Check if {url} exists or update link",
                            context=context,
                            related_documents=[]
                        ))
        except Exception:
            issues.append(ConsistencyIssue(
                issue_type='reference',
                severity='warning',
                document_path=doc_path,
                line_number=line_num,
                inconsistent_term=url,
                suggested_term="Verify link path is correct",
                context=context,
                related_documents=[]
            ))

        return issues

    def _validate_code_reference(self, reference: str, ref_type: str,
                               doc_path: str, all_documents: Dict[str, str],
                               line_num: int, context: str) -> List[ConsistencyIssue]:
        """Validate code references for consistency"""
        issues = []

        # This is a simplified validation - in practice, you'd check against
        # actual code symbols, API references, etc.

        # Check for common inconsistencies in naming conventions
        if ref_type == 'pascal_case':
            # Check if it should be snake_case in certain contexts
            if any(word in context.lower() for word in ['function', 'variable', 'method']):
                issues.append(ConsistencyIssue(
                    issue_type='reference',
                    severity='suggestion',
                    document_path=doc_path,
                    line_number=line_num,
                    inconsistent_term=reference,
                    suggested_term=reference.lower().replace(' ', '_'),
                    context=context,
                    related_documents=[]
                ))

        return issues

class FormatConsistencyValidator:
    """
    Validates format consistency across documents
    """

    def __init__(self):
        self.format_rules = {
            'heading_style': {
                'pattern': r'^#{1,6}\s+',
                'description': 'Use ATX-style headings (# ## ###)',
                'severity': 'warning'
            },
            'list_consistency': {
                'patterns': [r'^\s*[-*+]\s+', r'^\s*\d+\.\s+'],
                'description': 'Maintain consistent list markers',
                'severity': 'suggestion'
            },
            'code_block_style': {
                'pattern': r'```[\w]*',
                'description': 'Use fenced code blocks with language specification',
                'severity': 'suggestion'
            },
            'trailing_whitespace': {
                'pattern': r'\s+$',
                'description': 'Remove trailing whitespace',
                'severity': 'warning'
            }
        }

    def validate_document_format(self, doc_path: str, content: str,
                               line_offset: int = 0) -> List[ConsistencyIssue]:
        """
        Validate format consistency in a document
        """
        issues = []
        lines = content.split('\n')

        for line_num, line in enumerate(lines, 1):
            # Check trailing whitespace
            if re.search(self.format_rules['trailing_whitespace']['pattern'], line):
                issues.append(ConsistencyIssue(
                    issue_type='format',
                    severity=self.format_rules['trailing_whitespace']['severity'],
                    document_path=doc_path,
                    line_number=line_num + line_offset,
                    inconsistent_term='trailing whitespace',
                    suggested_term='Remove trailing spaces',
                    context=line,
                    related_documents=[]
                ))

            # Check heading style
            if line.startswith('#'):
                if not re.match(self.format_rules['heading_style']['pattern'], line):
                    issues.append(ConsistencyIssue(
                        issue_type='format',
                        severity=self.format_rules['heading_style']['severity'],
                        document_path=doc_path,
                        line_number=line_num + line_offset,
                        inconsistent_term=line.split()[0] if line.split() else '#',
                        suggested_term='# (ATX-style)',
                        context=line,
                        related_documents=[]
                    ))

        return issues

class MetadataConsistencyValidator:
    """
    Validates metadata consistency across documents
    """

    def __init__(self):
        self.required_fields = ['title', 'type', 'domain', 'status', 'last_reviewed', 'maintainer']
        self.valid_values = {
            'type': ['guide', 'reference', 'process', 'spec', 'api'],
            'domain': ['technical', 'design', 'lore', 'art', 'process'],
            'status': ['draft', 'review', 'approved', 'deprecated']
        }

    def validate_document_metadata(self, doc_path: str, frontmatter: Dict[str, Any],
                                 line_offset: int = 0) -> List[ConsistencyIssue]:
        """
        Validate metadata consistency
        """
        issues = []

        if not frontmatter:
            issues.append(ConsistencyIssue(
                issue_type='metadata',
                severity='error',
                document_path=doc_path,
                line_number=1,
                inconsistent_term='missing frontmatter',
                suggested_term='Add frontmatter with required fields',
                context='Document missing frontmatter',
                related_documents=[]
            ))
            return issues

        # Check required fields
        for field in self.required_fields:
            if field not in frontmatter:
                issues.append(ConsistencyIssue(
                    issue_type='metadata',
                    severity='error',
                    document_path=doc_path,
                    line_number=1,
                    inconsistent_term=f'missing {field}',
                    suggested_term=f'Add {field} field',
                    context=f'Frontmatter missing required field: {field}',
                    related_documents=[]
                ))
            elif not frontmatter[field]:
                issues.append(ConsistencyIssue(
                    issue_type='metadata',
                    severity='warning',
                    document_path=doc_path,
                    line_number=1,
                    inconsistent_term=f'empty {field}',
                    suggested_term=f'Provide value for {field}',
                    context=f'Frontmatter field {field} is empty',
                    related_documents=[]
                ))

        # Validate field values
        for field, valid_values in self.valid_values.items():
            if field in frontmatter and frontmatter[field] not in valid_values:
                issues.append(ConsistencyIssue(
                    issue_type='metadata',
                    severity='warning',
                    document_path=doc_path,
                    line_number=1,
                    inconsistent_term=frontmatter[field],
                    suggested_term=f"One of: {', '.join(valid_values)}",
                    context=f'Invalid value for {field}: {frontmatter[field]}',
                    related_documents=[]
                ))

        # Validate date format
        if 'last_reviewed' in frontmatter:
            try:
                datetime.strptime(frontmatter['last_reviewed'], '%Y-%m-%d')
            except ValueError:
                issues.append(ConsistencyIssue(
                    issue_type='metadata',
                    severity='warning',
                    document_path=doc_path,
                    line_number=1,
                    inconsistent_term=frontmatter['last_reviewed'],
                    suggested_term='YYYY-MM-DD format',
                    context=f'Invalid date format for last_reviewed: {frontmatter["last_reviewed"]}',
                    related_documents=[]
                ))

        return issues

class ConsistencyValidationSystem:
    """
    Complete consistency validation system
    """

    def __init__(self, docs_root: str = "docs"):
        self.docs_root = Path(docs_root)
        self.terminology_validator = TerminologyConsistencyValidator()
        self.reference_validator = ReferenceIntegrityValidator()
        self.format_validator = FormatConsistencyValidator()
        self.metadata_validator = MetadataConsistencyValidator()

        logger.info("Consistency Validation System initialized")

    def validate_document_consistency(self, doc_path: str) -> List[ConsistencyIssue]:
        """
        Validate consistency for a single document
        """
        issues = []

        try:
            # Read document
            with open(doc_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Extract frontmatter
            frontmatter = self._extract_frontmatter(content)
            body_content = self._extract_body_content(content)

            # Validate terminology
            issues.extend(self.terminology_validator.validate_document_terminology(
                doc_path, body_content
            ))

            # Validate format
            issues.extend(self.format_validator.validate_document_format(
                doc_path, content
            ))

            # Validate metadata
            issues.extend(self.metadata_validator.validate_document_metadata(
                doc_path, frontmatter
            ))

            # Note: Reference validation requires all documents, so it's done separately

        except Exception as e:
            logger.error(f"Error validating document consistency for {doc_path}: {e}")

        return issues

    def validate_all_consistency(self) -> ConsistencyValidationResult:
        """
        Validate consistency across all documents
        """
        all_issues = []
        documents = {}

        # Load all documents
        for md_file in self.docs_root.rglob("*.md"):
            if md_file.name.lower() == "readme.md":
                continue

            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                documents[str(md_file)] = content
            except Exception as e:
                logger.error(f"Error reading document {md_file}: {e}")

        # Validate each document
        for doc_path, content in documents.items():
            # Extract content for validation
            frontmatter = self._extract_frontmatter(content)
            body_content = self._extract_body_content(content)

            # Terminology validation
            all_issues.extend(self.terminology_validator.validate_document_terminology(
                doc_path, body_content
            ))

            # Format validation
            all_issues.extend(self.format_validator.validate_document_format(
                doc_path, content
            ))

            # Metadata validation
            all_issues.extend(self.metadata_validator.validate_document_metadata(
                doc_path, frontmatter
            ))

            # Reference validation (requires all documents)
            all_issues.extend(self.reference_validator.validate_document_references(
                doc_path, content, documents
            ))

        # Analyze terminology usage
        terminology_analysis = self.terminology_validator.analyze_terminology_usage(documents)

        # Categorize issues
        issues_by_type = {
            'terminology': [i for i in all_issues if i.issue_type == 'terminology'],
            'reference': [i for i in all_issues if i.issue_type == 'reference'],
            'format': [i for i in all_issues if i.issue_type == 'format'],
            'metadata': [i for i in all_issues if i.issue_type == 'metadata']
        }

        # Calculate scores
        terminology_coverage = self._calculate_terminology_coverage(terminology_analysis)
        reference_integrity_score = self._calculate_reference_integrity_score(issues_by_type['reference'])
        format_consistency_score = self._calculate_format_consistency_score(issues_by_type['format'])
        metadata_consistency_score = self._calculate_metadata_consistency_score(issues_by_type['metadata'])

        overall_consistency_score = (
            terminology_coverage * 0.3 +
            reference_integrity_score * 0.3 +
            format_consistency_score * 0.2 +
            metadata_consistency_score * 0.2
        )

        # Generate recommendations
        recommendations = self._generate_consistency_recommendations(
            issues_by_type, terminology_analysis
        )

        return ConsistencyValidationResult(
            total_issues=len(all_issues),
            issues_by_type=issues_by_type,
            terminology_coverage=terminology_coverage,
            reference_integrity_score=reference_integrity_score,
            format_consistency_score=format_consistency_score,
            metadata_consistency_score=metadata_consistency_score,
            overall_consistency_score=overall_consistency_score,
            recommendations=recommendations
        )

    def _extract_frontmatter(self, content: str) -> Dict[str, Any]:
        """Extract frontmatter from document content"""
        if not content.startswith('---'):
            return {}

        parts = content.split('---', 2)
        if len(parts) < 3:
            return {}

        try:
            import yaml
            return yaml.safe_load(parts[1]) or {}
        except ImportError:
            logger.warning("YAML not available, skipping frontmatter parsing")
            return {}
        except Exception as e:
            logger.warning(f"Error parsing frontmatter: {e}")
            return {}

    def _extract_body_content(self, content: str) -> str:
        """Extract body content (without frontmatter)"""
        if not content.startswith('---'):
            return content

        parts = content.split('---', 2)
        if len(parts) >= 3:
            return parts[2].strip()
        return content

    def _calculate_terminology_coverage(self, terminology_analysis: Dict[str, Any]) -> float:
        """Calculate terminology consistency coverage"""
        if not terminology_analysis:
            return 0.0

        total_terms = len(terminology_analysis)
        consistent_terms = sum(1 for term_data in terminology_analysis.values()
                             if term_data['inconsistent_usage'] == 0)

        return consistent_terms / total_terms if total_terms > 0 else 0.0

    def _calculate_reference_integrity_score(self, reference_issues: List[ConsistencyIssue]) -> float:
        """Calculate reference integrity score"""
        # Simplified scoring - in practice, you'd track total references vs broken ones
        error_count = len([i for i in reference_issues if i.severity == 'error'])
        return max(0.0, 1.0 - (error_count * 0.1))

    def _calculate_format_consistency_score(self, format_issues: List[ConsistencyIssue]) -> float:
        """Calculate format consistency score"""
        # Simplified scoring based on issue count
        issue_count = len(format_issues)
        return max(0.0, 1.0 - (issue_count * 0.05))

    def _calculate_metadata_consistency_score(self, metadata_issues: List[ConsistencyIssue]) -> float:
        """Calculate metadata consistency score"""
        error_count = len([i for i in metadata_issues if i.severity == 'error'])
        return max(0.0, 1.0 - (error_count * 0.2))

    def _generate_consistency_recommendations(self, issues_by_type: Dict[str, List[ConsistencyIssue]],
                                           terminology_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate consistency improvement recommendations"""
        recommendations = []

        # Terminology recommendations
        inconsistent_terms = [term for term, data in terminology_analysis.items()
                            if data['inconsistent_usage'] > 0]
        if inconsistent_terms:
            recommendations.append({
                'category': 'terminology',
                'priority': 'high',
                'description': f'Standardize {len(inconsistent_terms)} inconsistent terms',
                'action_items': [
                    'Create terminology style guide',
                    'Update documents to use preferred terms',
                    'Add automated terminology checking to workflow'
                ]
            })

        # Reference recommendations
        if issues_by_type['reference']:
            recommendations.append({
                'category': 'references',
                'priority': 'high',
                'description': f'Fix {len(issues_by_type["reference"])} broken or inconsistent references',
                'action_items': [
                    'Validate all internal links',
                    'Update outdated references',
                    'Implement automated link checking'
                ]
            })

        # Format recommendations
        if issues_by_type['format']:
            recommendations.append({
                'category': 'format',
                'priority': 'medium',
                'description': f'Standardize formatting across {len(issues_by_type["format"])} issues',
                'action_items': [
                    'Create formatting style guide',
                    'Use automated formatting tools',
                    'Implement format validation in workflow'
                ]
            })

        # Metadata recommendations
        if issues_by_type['metadata']:
            recommendations.append({
                'category': 'metadata',
                'priority': 'high',
                'description': f'Fix {len(issues_by_type["metadata"])} metadata consistency issues',
                'action_items': [
                    'Ensure all documents have required frontmatter',
                    'Validate metadata values',
                    'Automate metadata population'
                ]
            })

        return recommendations

    def get_consistency_dashboard_data(self) -> Dict[str, Any]:
        """
        Get data for consistency monitoring dashboard
        """
        result = self.validate_all_consistency()

        return {
            'summary': {
                'total_issues': result.total_issues,
                'overall_consistency_score': result.overall_consistency_score,
                'terminology_coverage': result.terminology_coverage,
                'reference_integrity_score': result.reference_integrity_score,
                'format_consistency_score': result.format_consistency_score,
                'metadata_consistency_score': result.metadata_consistency_score
            },
            'issues_by_type': {
                issue_type: len(issues)
                for issue_type, issues in result.issues_by_type.items()
            },
            'recommendations': result.recommendations,
            'top_issues': [
                {
                    'type': issue.issue_type,
                    'severity': issue.severity,
                    'document': issue.document_path,
                    'description': f"{issue.inconsistent_term} -> {issue.suggested_term}"
                }
                for issues in result.issues_by_type.values()
                for issue in issues[:5]  # Top 5 per type
            ]
        }

# Global consistency validation system instance
consistency_validation_system = ConsistencyValidationSystem()

def get_consistency_validation_system() -> ConsistencyValidationSystem:
    """Get the global consistency validation system instance"""
    return consistency_validation_system

def validate_document_consistency(doc_path: str) -> Dict[str, Any]:
    """
    Validate consistency of a single document
    """
    system = get_consistency_validation_system()
    issues = system.validate_document_consistency(doc_path)

    return {
        "document_path": doc_path,
        "total_issues": len(issues),
        "issues": [
            {
                "type": issue.issue_type,
                "severity": issue.severity,
                "line": issue.line_number,
                "inconsistent_term": issue.inconsistent_term,
                "suggested_term": issue.suggested_term,
                "context": issue.context
            }
            for issue in issues
        ]
    }

def get_consistency_dashboard() -> Dict[str, Any]:
    """
    Get consistency validation dashboard data
    """
    system = get_consistency_validation_system()
    return system.get_consistency_dashboard_data()

if __name__ == "__main__":
    # Test the consistency validation system
    print("Terminal Grounds Consistency Validation System")
    print("=" * 48)

    system = ConsistencyValidationSystem("../../docs")

    print("Analyzing document consistency...")
    result = system.validate_all_consistency()

    print(f"\nConsistency Analysis Results:")
    print(f"Total Issues: {result.total_issues}")
    print(f"Overall Consistency Score: {result.overall_consistency_score:.2f}")
    print(f"Terminology Coverage: {result.terminology_coverage:.2f}")
    print(f"Reference Integrity Score: {result.reference_integrity_score:.2f}")
    print(f"Format Consistency Score: {result.format_consistency_score:.2f}")
    print(f"Metadata Consistency Score: {result.metadata_consistency_score:.2f}")

    print(f"\nIssues by Type:")
    for issue_type, issues in result.issues_by_type.items():
        print(f"  {issue_type.capitalize()}: {len(issues)} issues")

    print(f"\nTop Recommendations:")
    for i, rec in enumerate(result.recommendations[:3], 1):
        print(f"  {i}. {rec['category']} - {rec['priority']} priority")
        print(f"     {rec['description']}")

    print("\nConsistency Validation System operational!")
    print("Phase 4.1.2.3 Consistency Validation System ready for integration.")
