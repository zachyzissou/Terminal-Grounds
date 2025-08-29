"""
Terminal Grounds Documentation Automation Framework
Phase 4.1.3.2: Accessibility Standards Framework

Comprehensive accessibility standards implementation for documentation,
including screen reader compatibility, semantic validation, and remediation.
"""

import os
import sys
import re
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Set, Union
from dataclasses import dataclass, field
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class AccessibilityIssue:
    """Represents an accessibility issue found in documentation"""
    issue_id: str
    file_path: str
    line_number: Optional[int]
    issue_type: str
    wcag_guideline: str
    description: str
    severity: str  # 'critical', 'high', 'medium', 'low'
    impact: str  # 'blocking', 'serious', 'moderate', 'minor'
    remediation_steps: List[str]
    detected_at: datetime
    status: str = "open"  # 'open', 'resolved', 'acknowledged'

@dataclass
class AccessibilityAssessment:
    """Results from comprehensive accessibility assessment"""
    file_path: str
    wcag_version: str
    conformance_level: str  # 'A', 'AA', 'AAA'
    overall_score: float
    issues: List[AccessibilityIssue]
    recommendations: List[str]
    assessed_at: datetime

@dataclass
class ScreenReaderCompatibility:
    """Screen reader compatibility assessment results"""
    file_path: str
    screen_reader_friendly: bool
    issues: List[AccessibilityIssue]
    compatibility_score: float
    recommendations: List[str]
    tested_at: datetime

class SemanticValidator:
    """Validates semantic structure and markup in documentation"""

    def __init__(self):
        self.semantic_patterns = {
            'heading_hierarchy': re.compile(r'^(#{1,6})\s+(.+)$', re.MULTILINE),
            'code_blocks': re.compile(r'```[\s\S]*?```', re.MULTILINE),
            'inline_code': re.compile(r'`[^`]+`'),
            'emphasis': re.compile(r'\*([^*]+)\*|_([^_]+)_'),
            'strong': re.compile(r'\*\*([^*]+)\*\*|__([^_]+)__'),
            'links': re.compile(r'\[([^\]]+)\]\(([^)]+)\)'),
            'images': re.compile(r'!\[([^\]]*)\]\(([^)]+)\)'),
            'lists': re.compile(r'^[\s]*[-*+]\s+', re.MULTILINE),
            'numbered_lists': re.compile(r'^[\s]*\d+\.\s+', re.MULTILINE),
            'blockquotes': re.compile(r'^>\s+', re.MULTILINE),
            'tables': re.compile(r'\|[^\n]*\|[\s]*\n\|[\s\-\|:]+\|', re.MULTILINE)
        }

    def validate_semantic_structure(self, file_path: str, content: str) -> List[AccessibilityIssue]:
        """Validate semantic structure of markdown content"""
        issues = []

        # Check for proper heading hierarchy
        heading_issues = self._validate_heading_hierarchy(content)
        issues.extend(heading_issues)

        # Check for semantic markup usage
        markup_issues = self._validate_semantic_markup(content)
        issues.extend(markup_issues)

        # Check for proper list structure
        list_issues = self._validate_list_structure(content)
        issues.extend(list_issues)

        # Check for table accessibility
        table_issues = self._validate_table_accessibility(content)
        issues.extend(table_issues)

        return issues

    def _validate_heading_hierarchy(self, content: str) -> List[AccessibilityIssue]:
        """Validate heading hierarchy follows proper structure"""
        issues = []
        lines = content.split('\n')
        heading_levels = []
        previous_level = 0

        for i, line in enumerate(lines, 1):
            match = self.semantic_patterns['heading_hierarchy'].match(line.strip())
            if match:
                level = len(match.group(1))
                heading_levels.append((level, i, match.group(2).strip()))

                # Check for proper hierarchy (shouldn't skip levels)
                if level > previous_level + 1 and previous_level > 0:
                    issues.append(AccessibilityIssue(
                        issue_id=f"HEADING_HIERARCHY_{i}",
                        file_path="",
                        line_number=i,
                        issue_type="heading_hierarchy",
                        wcag_guideline="WCAG_1_3_1",
                        description=f"Heading level {level} skips from level {previous_level}",
                        severity="high",
                        impact="serious",
                        remediation_steps=[
                            f"Add missing heading level {previous_level + 1} before this heading",
                            "Ensure logical heading hierarchy (H1 > H2 > H3, etc.)",
                            "Review document structure for proper organization"
                        ],
                        detected_at=datetime.now()
                    ))

                previous_level = level

        # Check if document starts with H1
        if heading_levels and heading_levels[0][0] != 1:
            issues.append(AccessibilityIssue(
                issue_id="MISSING_H1",
                file_path="",
                line_number=heading_levels[0][1],
                issue_type="missing_h1",
                wcag_guideline="WCAG_2_4_2",
                description="Document does not start with H1 heading",
                severity="high",
                impact="serious",
                remediation_steps=[
                    "Add a main H1 heading at the beginning of the document",
                    "Ensure the H1 describes the document's primary topic",
                    "Use descriptive headings that clearly indicate content purpose"
                ],
                detected_at=datetime.now()
            ))

        return issues

    def _validate_semantic_markup(self, content: str) -> List[AccessibilityIssue]:
        """Validate proper use of semantic markup"""
        issues = []

        # Check for images without alt text
        images = self.semantic_patterns['images'].findall(content)
        for alt_text, url in images:
            if not alt_text.strip():
                issues.append(AccessibilityIssue(
                    issue_id=f"IMAGE_ALT_{len(issues)}",
                    file_path="",
                    line_number=None,  # Would need more complex line finding
                    issue_type="missing_alt_text",
                    wcag_guideline="WCAG_1_1_1",
                    description="Image found without alternative text",
                    severity="critical",
                    impact="blocking",
                    remediation_steps=[
                        "Add descriptive alt text to the image",
                        "Describe the image's purpose or content",
                        "If decorative, use empty alt attribute: ![decorative image]()",
                        "Ensure alt text is meaningful to screen reader users"
                    ],
                    detected_at=datetime.now()
                ))

        # Check for links with generic text
        links = self.semantic_patterns['links'].findall(content)
        generic_link_texts = ['click here', 'here', 'read more', 'more', 'link', 'this']

        for link_text, url in links:
            if link_text.lower().strip() in generic_link_texts:
                issues.append(AccessibilityIssue(
                    issue_id=f"LINK_TEXT_{len(issues)}",
                    file_path="",
                    line_number=None,
                    issue_type="generic_link_text",
                    wcag_guideline="WCAG_2_4_4",
                    description=f"Link uses generic text: '{link_text}'",
                    severity="high",
                    impact="serious",
                    remediation_steps=[
                        "Use descriptive link text that indicates destination",
                        "Include relevant keywords in link text",
                        "Avoid generic phrases like 'click here' or 'read more'",
                        "Make link text meaningful out of context"
                    ],
                    detected_at=datetime.now()
                ))

        return issues

    def _validate_list_structure(self, content: str) -> List[AccessibilityIssue]:
        """Validate proper list structure and nesting"""
        issues = []

        # Check for proper list formatting
        lines = content.split('\n')
        in_list = False
        list_indent_levels = []

        for i, line in enumerate(lines, 1):
            stripped = line.strip()

            # Check for list items
            if self.semantic_patterns['lists'].match(line) or self.semantic_patterns['numbered_lists'].match(line):
                if not in_list:
                    in_list = True
                    list_indent_levels = []

                # Check indentation consistency
                indent = len(line) - len(line.lstrip())
                if list_indent_levels and indent > list_indent_levels[-1] + 2:
                    issues.append(AccessibilityIssue(
                        issue_id=f"LIST_INDENT_{i}",
                        file_path="",
                        line_number=i,
                        issue_type="list_indentation",
                        wcag_guideline="WCAG_1_3_1",
                        description="Inconsistent list indentation may confuse screen readers",
                        severity="medium",
                        impact="moderate",
                        remediation_steps=[
                            "Use consistent indentation for nested lists",
                            "Use 2 spaces or 4 spaces consistently",
                            "Ensure proper list hierarchy is maintained",
                            "Test list navigation with screen readers"
                        ],
                        detected_at=datetime.now()
                    ))

                list_indent_levels.append(indent)
            elif stripped and in_list and not line.startswith(' ') and not line.startswith('\t'):
                # End of list
                in_list = False
                list_indent_levels = []

        return issues

    def _validate_table_accessibility(self, content: str) -> List[AccessibilityIssue]:
        """Validate table accessibility features"""
        issues = []

        # Find tables in content
        table_matches = self.semantic_patterns['tables'].findall(content)

        for i, table_content in enumerate(table_matches):
            # Check for table headers
            lines = table_content.split('\n')
            if len(lines) >= 3:
                header_row = lines[0].strip()
                separator_row = lines[1].strip()

                # Check if separator row indicates headers
                if not re.search(r':*\|:*', separator_row):
                    issues.append(AccessibilityIssue(
                        issue_id=f"TABLE_HEADERS_{i}",
                        file_path="",
                        line_number=None,
                        issue_type="table_headers",
                        wcag_guideline="WCAG_1_3_1",
                        description="Table may be missing proper header structure",
                        severity="high",
                        impact="serious",
                        remediation_steps=[
                            "Add table headers using markdown table syntax",
                            "Use |---| or |:---| to indicate header rows",
                            "Ensure first row contains meaningful headers",
                            "Consider using HTML tables for complex structures"
                        ],
                        detected_at=datetime.now()
                    ))

        return issues

class ScreenReaderValidator:
    """Validates content compatibility with screen readers"""

    def __init__(self):
        self.screen_reader_patterns = {
            'abbreviations': re.compile(r'\b[A-Z]{2,}\b'),
            'acronyms': re.compile(r'\b([A-Z]\.){2,}'),
            'technical_terms': re.compile(r'\b[A-Z][a-z]+[A-Z][a-z]+\b'),  # CamelCase
            'code_snippets': re.compile(r'`[^`]{10,}`'),  # Long inline code
            'file_paths': re.compile(r'[a-zA-Z]:\\[^\s]+|/[^\s]+/[^\s]+'),  # Windows/Unix paths
            'urls': re.compile(r'https?://[^\s]+'),
            'email_addresses': re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
        }

    def assess_screen_reader_compatibility(self, file_path: str, content: str) -> ScreenReaderCompatibility:
        """Assess content compatibility with screen readers"""
        issues = []

        # Check for abbreviations that need expansion
        abbreviations = self.screen_reader_patterns['abbreviations'].findall(content)
        for abbr in set(abbreviations):
            if len(abbr) > 2 and abbr not in ['API', 'URL', 'HTTP', 'HTTPS', 'HTML', 'CSS', 'JS', 'JSON', 'XML']:
                issues.append(AccessibilityIssue(
                    issue_id=f"ABBREVIATION_{abbr}",
                    file_path=file_path,
                    line_number=None,
                    issue_type="abbreviation",
                    wcag_guideline="WCAG_3_1_4",
                    description=f"Abbreviation '{abbr}' may need expansion for screen readers",
                    severity="medium",
                    impact="moderate",
                    remediation_steps=[
                        f"Expand abbreviation '{abbr}' on first use",
                        "Use <abbr> tag if HTML is supported",
                        "Provide pronunciation guidance for complex terms",
                        "Consider if abbreviation is necessary"
                    ],
                    detected_at=datetime.now()
                ))

        # Check for complex technical terms
        technical_terms = self.screen_reader_patterns['technical_terms'].findall(content)
        for term in set(technical_terms[:5]):  # Limit to first 5 to avoid spam
            issues.append(AccessibilityIssue(
                issue_id=f"TECHNICAL_TERM_{term}",
                file_path=file_path,
                line_number=None,
                issue_type="technical_term",
                wcag_guideline="WCAG_3_1_3",
                description=f"Complex technical term '{term}' may need explanation",
                severity="low",
                impact="minor",
                remediation_steps=[
                    f"Define or explain '{term}' when first used",
                    "Consider providing a glossary",
                    "Use simpler language where possible",
                    "Ensure context makes meaning clear"
                ],
                detected_at=datetime.now()
            ))

        # Check for long code snippets that might be hard to follow
        long_code = self.screen_reader_patterns['code_snippets'].findall(content)
        if len(long_code) > 0:
            issues.append(AccessibilityIssue(
                issue_id="LONG_CODE_SNIPPETS",
                file_path=file_path,
                line_number=None,
                issue_type="long_code",
                wcag_guideline="WCAG_1_3_1",
                description=f"Found {len(long_code)} long code snippets that may be difficult for screen readers",
                severity="medium",
                impact="moderate",
                remediation_steps=[
                    "Break long code snippets into smaller, manageable pieces",
                    "Add comments to explain complex code sections",
                    "Provide text descriptions of what the code does",
                    "Consider alternative formats for code presentation"
                ],
                detected_at=datetime.now()
            ))

        # Calculate compatibility score
        base_score = 100
        penalty_per_issue = {
            'critical': 20,
            'high': 10,
            'medium': 5,
            'low': 2
        }

        for issue in issues:
            base_score -= penalty_per_issue.get(issue.severity, 0)

        compatibility_score = max(0, base_score)

        # Generate recommendations
        recommendations = []
        if issues:
            recommendations.append("Review content for screen reader compatibility")
            recommendations.append("Test with actual screen reader software")
            recommendations.append("Consider providing alternative formats")

        if compatibility_score < 70:
            recommendations.append("Significant accessibility improvements needed")
        elif compatibility_score < 90:
            recommendations.append("Minor accessibility enhancements recommended")

        return ScreenReaderCompatibility(
            file_path=file_path,
            screen_reader_friendly=compatibility_score >= 80,
            issues=issues,
            compatibility_score=compatibility_score,
            recommendations=recommendations,
            tested_at=datetime.now()
        )

class AccessibilityChecklist:
    """Automated accessibility checklist generation and validation"""

    def __init__(self):
        self.checklist_items = {
            'WCAG_1_1_1': {
                'guideline': 'Non-text Content',
                'description': 'All non-text content has text alternatives',
                'check_type': 'automated',
                'priority': 'critical'
            },
            'WCAG_1_3_1': {
                'guideline': 'Info and Relationships',
                'description': 'Information and relationships conveyed through presentation are preserved',
                'check_type': 'automated',
                'priority': 'high'
            },
            'WCAG_1_4_3': {
                'guideline': 'Contrast (Minimum)',
                'description': 'Text has sufficient contrast ratio',
                'check_type': 'manual',
                'priority': 'high'
            },
            'WCAG_2_1_1': {
                'guideline': 'Keyboard',
                'description': 'All functionality is available from a keyboard',
                'check_type': 'manual',
                'priority': 'critical'
            },
            'WCAG_2_4_2': {
                'guideline': 'Page Titled',
                'description': 'Web pages have titles that describe topic or purpose',
                'check_type': 'automated',
                'priority': 'high'
            },
            'WCAG_3_1_1': {
                'guideline': 'Language of Page',
                'description': 'Language of the page is identified',
                'check_type': 'automated',
                'priority': 'medium'
            },
            'WCAG_4_1_2': {
                'guideline': 'Name, Role, Value',
                'description': 'Name and role can be programmatically determined',
                'check_type': 'automated',
                'priority': 'high'
            }
        }

    def generate_checklist(self, file_path: str, content: str) -> Dict[str, Any]:
        """Generate accessibility checklist for a document"""
        checklist = {
            'file_path': file_path,
            'generated_at': datetime.now(),
            'wcag_version': '2.1',
            'conformance_level': 'AA',
            'items': []
        }

        for guideline_id, item in self.checklist_items.items():
            checklist_item = {
                'guideline_id': guideline_id,
                'guideline': item['guideline'],
                'description': item['description'],
                'check_type': item['check_type'],
                'priority': item['priority'],
                'status': 'pending',
                'notes': '',
                'remediation_required': False
            }

            checklist['items'].append(checklist_item)

        return checklist

    def validate_checklist_completion(self, checklist: Dict[str, Any]) -> Dict[str, Any]:
        """Validate completion status of accessibility checklist"""
        completed_items = 0
        total_items = len(checklist['items'])

        for item in checklist['items']:
            if item['status'] in ['passed', 'failed']:
                completed_items += 1

        completion_rate = (completed_items / total_items) * 100 if total_items > 0 else 0

        return {
            'completion_rate': completion_rate,
            'completed_items': completed_items,
            'total_items': total_items,
            'status': 'complete' if completion_rate == 100 else 'in_progress'
        }

class AccessibilityStandardsFramework:
    """Main accessibility standards framework"""

    def __init__(self):
        self.semantic_validator = SemanticValidator()
        self.screen_reader_validator = ScreenReaderValidator()
        self.checklist_generator = AccessibilityChecklist()
        self.assessment_cache = {}

    def perform_accessibility_assessment(self, file_path: str, content: str = None) -> AccessibilityAssessment:
        """Perform comprehensive accessibility assessment"""
        if content is None:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            except Exception as e:
                logger.error(f"Error reading file {file_path}: {e}")
                return None

        logger.info(f"Starting accessibility assessment for {file_path}")

        # Perform semantic validation
        semantic_issues = self.semantic_validator.validate_semantic_structure(file_path, content)

        # Perform screen reader compatibility assessment
        screen_reader_result = self.screen_reader_validator.assess_screen_reader_compatibility(file_path, content)

        # Combine all issues
        all_issues = semantic_issues + screen_reader_result.issues

        # Calculate overall accessibility score
        score = self._calculate_accessibility_score(all_issues)

        # Generate recommendations
        recommendations = self._generate_accessibility_recommendations(all_issues, score)

        assessment = AccessibilityAssessment(
            file_path=file_path,
            wcag_version="2.1",
            conformance_level="AA",
            overall_score=score,
            issues=all_issues,
            recommendations=recommendations,
            assessed_at=datetime.now()
        )

        # Cache the assessment
        self.assessment_cache[file_path] = assessment

        logger.info(f"Accessibility assessment completed for {file_path} - Score: {score:.1f}%")

        return assessment

    def generate_accessibility_checklist(self, file_path: str, content: str = None) -> Dict[str, Any]:
        """Generate accessibility checklist for a document"""
        if content is None:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            except Exception as e:
                logger.error(f"Error reading file {file_path}: {e}")
                return None

        return self.checklist_generator.generate_checklist(file_path, content)

    def _calculate_accessibility_score(self, issues: List[AccessibilityIssue]) -> float:
        """Calculate overall accessibility score"""
        if not issues:
            return 100.0

        # Weight issues by severity and impact
        weights = {
            'critical': 20,
            'high': 15,
            'medium': 10,
            'low': 5
        }

        impact_multipliers = {
            'blocking': 1.5,
            'serious': 1.2,
            'moderate': 1.0,
            'minor': 0.8
        }

        total_penalty = 0
        for issue in issues:
            base_penalty = weights.get(issue.severity, 5)
            impact_multiplier = impact_multipliers.get(issue.impact, 1.0)
            total_penalty += base_penalty * impact_multiplier

        score = max(0, 100 - total_penalty)
        return score

    def _generate_accessibility_recommendations(self, issues: List[AccessibilityIssue],
                                              score: float) -> List[str]:
        """Generate accessibility recommendations"""
        recommendations = []

        if score >= 90:
            recommendations.append("Document meets high accessibility standards")
            recommendations.append("Continue regular accessibility reviews")
        elif score >= 75:
            recommendations.append("Address remaining accessibility issues to improve compliance")
            recommendations.append("Consider manual accessibility testing")
        else:
            recommendations.append("Significant accessibility improvements required")
            recommendations.append("Comprehensive accessibility review recommended")

        # Add specific recommendations based on issue types
        issue_types = set(issue.issue_type for issue in issues)

        if 'missing_alt_text' in issue_types:
            recommendations.append("Add alternative text to all images")

        if 'heading_hierarchy' in issue_types or 'missing_h1' in issue_types:
            recommendations.append("Fix heading hierarchy and add missing H1")

        if 'generic_link_text' in issue_types:
            recommendations.append("Use descriptive link text instead of generic phrases")

        if 'table_headers' in issue_types:
            recommendations.append("Add proper table headers for accessibility")

        if 'abbreviation' in issue_types:
            recommendations.append("Expand abbreviations on first use")

        if 'long_code' in issue_types:
            recommendations.append("Break long code snippets into manageable pieces")

        return recommendations

    def generate_accessibility_report(self, assessments: List[AccessibilityAssessment] = None) -> str:
        """Generate comprehensive accessibility report"""
        if assessments is None:
            assessments = list(self.assessment_cache.values())

        if not assessments:
            return "No accessibility assessments have been performed yet."

        report_lines = []
        report_lines.append("# Accessibility Standards Report")
        report_lines.append(f"Generated: {datetime.now().isoformat()}")
        report_lines.append("")

        # Summary statistics
        total_files = len(assessments)
        avg_score = sum(a.overall_score for a in assessments) / total_files if total_files > 0 else 0
        total_issues = sum(len(a.issues) for a in assessments)

        report_lines.append("## Summary Statistics")
        report_lines.append(f"- Total Files Assessed: {total_files}")
        report_lines.append(f"- Average Accessibility Score: {avg_score:.1f}%")
        report_lines.append(f"- Total Accessibility Issues: {total_issues}")
        report_lines.append("")

        # Detailed results
        report_lines.append("## Detailed Results")
        for assessment in assessments:
            report_lines.append(f"### {Path(assessment.file_path).name}")
            report_lines.append(f"- **Score:** {assessment.overall_score:.1f}%")
            report_lines.append(f"- **WCAG Version:** {assessment.wcag_version}")
            report_lines.append(f"- **Conformance Level:** {assessment.conformance_level}")
            report_lines.append(f"- **Issues Found:** {len(assessment.issues)}")

            if assessment.issues:
                report_lines.append("- **Top Issues:**")
                for issue in assessment.issues[:5]:  # Show first 5 issues
                    report_lines.append(f"  - {issue.description} ({issue.severity} - {issue.impact})")
                if len(assessment.issues) > 5:
                    report_lines.append(f"  - ... and {len(assessment.issues) - 5} more")

            report_lines.append("")

        # Recommendations
        all_recommendations = set()
        for assessment in assessments:
            all_recommendations.update(assessment.recommendations)

        if all_recommendations:
            report_lines.append("## Recommendations")
            for rec in sorted(all_recommendations):
                report_lines.append(f"- {rec}")
            report_lines.append("")

        return '\n'.join(report_lines)

# Global instance for easy access
_accessibility_framework = None

def get_accessibility_standards_framework() -> AccessibilityStandardsFramework:
    """Get or create the global accessibility standards framework instance"""
    global _accessibility_framework
    if _accessibility_framework is None:
        _accessibility_framework = AccessibilityStandardsFramework()
    return _accessibility_framework

# Pseudocode generated by codewrx.ai
