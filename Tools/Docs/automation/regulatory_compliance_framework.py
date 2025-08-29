"""
Terminal Grounds Documentation Automation Framework
Phase 4.1.3.1: Regulatory Compliance Framework

Comprehensive regulatory compliance system for documentation governance,
including accessibility standards, compliance tracking, and audit trails.
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
import hashlib

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class ComplianceRequirement:
    """Represents a specific compliance requirement"""
    requirement_id: str
    category: str  # 'accessibility', 'regulatory', 'internationalization'
    standard: str  # 'WCAG_2_1_AA', 'GDPR', 'ISO_27001', etc.
    description: str
    severity: str  # 'critical', 'high', 'medium', 'low'
    automated_check: bool
    manual_review_required: bool
    remediation_guidance: str

@dataclass
class ComplianceViolation:
    """Represents a compliance violation found in documentation"""
    requirement_id: str
    file_path: str
    line_number: Optional[int]
    violation_type: str
    description: str
    severity: str
    remediation_steps: List[str]
    detected_at: datetime
    status: str = "open"  # 'open', 'resolved', 'acknowledged'

@dataclass
class AccessibilityValidationResult:
    """Results from accessibility validation"""
    file_path: str
    wcag_compliance_level: str
    violations: List[ComplianceViolation]
    score: float
    recommendations: List[str]
    validated_at: datetime

@dataclass
class ComplianceReport:
    """Comprehensive compliance report"""
    document_path: str
    assessment_date: datetime
    compliance_requirements: List[ComplianceRequirement]
    violations: List[ComplianceViolation]
    compliance_score: float
    overall_status: str  # 'compliant', 'non_compliant', 'partial'
    audit_trail: List[Dict[str, Any]]
    recommendations: List[str]

class AccessibilityValidator:
    """WCAG 2.1 AA Accessibility Validator"""

    def __init__(self):
        self.wcag_requirements = self._load_wcag_requirements()

    def _load_wcag_requirements(self) -> List[ComplianceRequirement]:
        """Load WCAG 2.1 AA requirements"""
        return [
            ComplianceRequirement(
                requirement_id="WCAG_1_1_1",
                category="accessibility",
                standard="WCAG_2_1_AA",
                description="Non-text Content - All non-text content has text alternatives",
                severity="critical",
                automated_check=True,
                manual_review_required=True,
                remediation_guidance="Add alt text to images, provide text descriptions for complex graphics"
            ),
            ComplianceRequirement(
                requirement_id="WCAG_1_3_1",
                category="accessibility",
                standard="WCAG_2_1_AA",
                description="Info and Relationships - Information and relationships conveyed through presentation are preserved in text",
                severity="high",
                automated_check=True,
                manual_review_required=False,
                remediation_guidance="Use proper heading hierarchy, semantic markup, and table structures"
            ),
            ComplianceRequirement(
                requirement_id="WCAG_1_4_3",
                category="accessibility",
                standard="WCAG_2_1_AA",
                description="Contrast (Minimum) - Text has sufficient contrast ratio",
                severity="high",
                automated_check=False,
                manual_review_required=True,
                remediation_guidance="Ensure text contrast ratio is at least 4.5:1 for normal text, 3:1 for large text"
            ),
            ComplianceRequirement(
                requirement_id="WCAG_2_1_1",
                category="accessibility",
                standard="WCAG_2_1_AA",
                description="Keyboard - All functionality is available from a keyboard",
                severity="critical",
                automated_check=False,
                manual_review_required=True,
                remediation_guidance="Ensure all interactive elements are keyboard accessible"
            ),
            ComplianceRequirement(
                requirement_id="WCAG_2_4_2",
                category="accessibility",
                standard="WCAG_2_1_AA",
                description="Page Titled - Web pages have titles that describe topic or purpose",
                severity="high",
                automated_check=True,
                manual_review_required=False,
                remediation_guidance="Add descriptive titles to all documentation pages"
            ),
            ComplianceRequirement(
                requirement_id="WCAG_3_1_1",
                category="accessibility",
                standard="WCAG_2_1_AA",
                description="Language of Page - Language of the page is identified",
                severity="medium",
                automated_check=True,
                manual_review_required=False,
                remediation_guidance="Specify document language in metadata or HTML lang attribute"
            ),
            ComplianceRequirement(
                requirement_id="WCAG_4_1_2",
                category="accessibility",
                standard="WCAG_2_1_AA",
                description="Name, Role, Value - Name and role can be programmatically determined",
                severity="high",
                automated_check=True,
                manual_review_required=False,
                remediation_guidance="Use semantic HTML elements and proper ARIA attributes"
            )
        ]

    def validate_accessibility(self, file_path: str, content: str) -> AccessibilityValidationResult:
        """Validate accessibility compliance for a document"""
        violations = []
        recommendations = []

        # Check for images without alt text
        image_pattern = r'!\[([^\]]*)\]\([^)]+\)'
        images = re.findall(image_pattern, content)

        for i, alt_text in enumerate(images):
            if not alt_text.strip():
                violations.append(ComplianceViolation(
                    requirement_id="WCAG_1_1_1",
                    file_path=file_path,
                    line_number=self._find_line_number(content, f'![{alt_text}]'),
                    violation_type="missing_alt_text",
                    description="Image found without alternative text",
                    severity="critical",
                    remediation_steps=[
                        "Add descriptive alt text to the image",
                        "If image is decorative, use empty alt attribute: ![decorative image]()",
                        "Ensure alt text describes the image's purpose or content"
                    ],
                    detected_at=datetime.now()
                ))

        # Check heading hierarchy
        heading_pattern = r'^(#{1,6})\s+(.+)$'
        headings = re.findall(heading_pattern, content, re.MULTILINE)

        if not headings:
            violations.append(ComplianceViolation(
                requirement_id="WCAG_1_3_1",
                file_path=file_path,
                line_number=1,
                violation_type="missing_headings",
                description="No headings found in document",
                severity="high",
                remediation_steps=[
                    "Add a main heading (H1) at the beginning of the document",
                    "Use proper heading hierarchy (H1 > H2 > H3, etc.)",
                    "Ensure headings accurately describe document sections"
                ],
                detected_at=datetime.now()
            ))
        else:
            # Check for proper heading hierarchy
            heading_levels = [len(level) for level, _ in headings]
            if 1 not in heading_levels:
                violations.append(ComplianceViolation(
                    requirement_id="WCAG_1_3_1",
                    file_path=file_path,
                    line_number=1,
                    violation_type="missing_h1",
                    description="Document missing main heading (H1)",
                    severity="high",
                    remediation_steps=[
                        "Add a main heading (H1) at the beginning of the document",
                        "Ensure the H1 describes the document's primary topic"
                    ],
                    detected_at=datetime.now()
                ))

        # Check for language specification
        if not re.search(r'lang\s*[:=]\s*[a-z]{2}', content, re.IGNORECASE):
            violations.append(ComplianceViolation(
                requirement_id="WCAG_3_1_1",
                file_path=file_path,
                line_number=1,
                violation_type="missing_language",
                description="Document language not specified",
                severity="medium",
                remediation_steps=[
                    "Add language specification in document metadata",
                    "Use ISO language codes (e.g., 'en' for English)",
                    "Include language in frontmatter or document header"
                ],
                detected_at=datetime.now()
            ))

        # Check for descriptive title
        lines = content.split('\n')
        first_heading = None
        for line in lines[:10]:  # Check first 10 lines
            if line.startswith('#'):
                first_heading = line.lstrip('#').strip()
                break

        if not first_heading or len(first_heading) < 5:
            violations.append(ComplianceViolation(
                requirement_id="WCAG_2_4_2",
                file_path=file_path,
                line_number=1,
                violation_type="poor_title",
                description="Document title is too short or missing",
                severity="high",
                remediation_steps=[
                    "Add a descriptive main heading that clearly describes the document's purpose",
                    "Ensure the title is at least 5 characters long",
                    "Make the title specific and meaningful to users"
                ],
                detected_at=datetime.now()
            ))

        # Calculate compliance score
        total_requirements = len(self.wcag_requirements)
        critical_violations = len([v for v in violations if v.severity == "critical"])
        high_violations = len([v for v in violations if v.severity == "high"])

        # Scoring algorithm: 100 - (critical * 20) - (high * 10) - (medium * 5) - (low * 2)
        score = max(0, 100 - (critical_violations * 20) - (high_violations * 10))

        # Generate recommendations
        if violations:
            recommendations.append("Review and fix all accessibility violations")
            recommendations.append("Consider manual accessibility testing for complex content")
            recommendations.append("Validate with automated accessibility tools")

        return AccessibilityValidationResult(
            file_path=file_path,
            wcag_compliance_level="WCAG_2_1_AA",
            violations=violations,
            score=score,
            recommendations=recommendations,
            validated_at=datetime.now()
        )

    def _find_line_number(self, content: str, search_text: str) -> Optional[int]:
        """Find the line number of specific text in content"""
        lines = content.split('\n')
        for i, line in enumerate(lines, 1):
            if search_text in line:
                return i
        return None

class ComplianceMetadataValidator:
    """Validator for compliance-related metadata"""

    def __init__(self):
        self.required_fields = {
            'title': 'Document title',
            'description': 'Document description',
            'last_reviewed': 'Date of last review',
            'review_frequency': 'How often document should be reviewed',
            'compliance_requirements': 'List of applicable compliance requirements'
        }

    def validate_metadata(self, file_path: str, metadata: Dict[str, Any]) -> List[ComplianceViolation]:
        """Validate compliance metadata"""
        violations = []

        # Check required fields
        for field, description in self.required_fields.items():
            if field not in metadata:
                violations.append(ComplianceViolation(
                    requirement_id="COMPLIANCE_METADATA",
                    file_path=file_path,
                    line_number=1,
                    violation_type="missing_metadata",
                    description=f"Missing required compliance metadata: {field}",
                    severity="high",
                    remediation_steps=[
                        f"Add '{field}' to document frontmatter",
                        f"Provide appropriate value for: {description}",
                        "Ensure all required compliance metadata is present"
                    ],
                    detected_at=datetime.now()
                ))

        # Validate date formats
        if 'last_reviewed' in metadata:
            try:
                datetime.fromisoformat(metadata['last_reviewed'].replace('Z', '+00:00'))
            except (ValueError, AttributeError):
                violations.append(ComplianceViolation(
                    requirement_id="COMPLIANCE_METADATA",
                    file_path=file_path,
                    line_number=1,
                    violation_type="invalid_date_format",
                    description="Invalid date format for last_reviewed",
                    severity="medium",
                    remediation_steps=[
                        "Use ISO format for dates (YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS)",
                        "Example: last_reviewed: 2025-08-28",
                        "Ensure date is parseable and valid"
                    ],
                    detected_at=datetime.now()
                ))

        # Validate review frequency
        if 'review_frequency' in metadata:
            valid_frequencies = ['daily', 'weekly', 'monthly', 'quarterly', 'annually', 'biannually']
            if metadata['review_frequency'].lower() not in valid_frequencies:
                violations.append(ComplianceViolation(
                    requirement_id="COMPLIANCE_METADATA",
                    file_path=file_path,
                    line_number=1,
                    violation_type="invalid_review_frequency",
                    description="Invalid review frequency specified",
                    severity="medium",
                    remediation_steps=[
                        f"Use one of: {', '.join(valid_frequencies)}",
                        "Specify how often the document should be reviewed",
                        "Align review frequency with document criticality"
                    ],
                    detected_at=datetime.now()
                ))

        return violations

class RegulatoryComplianceFramework:
    """Main regulatory compliance framework"""

    def __init__(self):
        self.accessibility_validator = AccessibilityValidator()
        self.metadata_validator = ComplianceMetadataValidator()
        self.audit_trail = []
        self.compliance_reports = {}

    def assess_compliance(self, file_path: str, content: str = None,
                         metadata: Dict[str, Any] = None) -> ComplianceReport:
        """Perform comprehensive compliance assessment"""
        if content is None:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            except Exception as e:
                logger.error(f"Error reading file {file_path}: {e}")
                return None

        if metadata is None:
            metadata = self._extract_metadata(content)

        # Perform accessibility validation
        accessibility_result = self.accessibility_validator.validate_accessibility(file_path, content)

        # Validate compliance metadata
        metadata_violations = self.metadata_validator.validate_metadata(file_path, metadata)

        # Combine all violations
        all_violations = accessibility_result.violations + metadata_violations

        # Calculate overall compliance score
        compliance_score = self._calculate_compliance_score(all_violations)

        # Determine overall status
        if compliance_score >= 90:
            overall_status = "compliant"
        elif compliance_score >= 70:
            overall_status = "partial"
        else:
            overall_status = "non_compliant"

        # Generate recommendations
        recommendations = self._generate_recommendations(all_violations, compliance_score)

        # Create audit entry
        audit_entry = {
            'timestamp': datetime.now().isoformat(),
            'file_path': file_path,
            'action': 'compliance_assessment',
            'score': compliance_score,
            'violations_count': len(all_violations),
            'status': overall_status
        }
        self.audit_trail.append(audit_entry)

        report = ComplianceReport(
            document_path=file_path,
            assessment_date=datetime.now(),
            compliance_requirements=self.accessibility_validator.wcag_requirements,
            violations=all_violations,
            compliance_score=compliance_score,
            overall_status=overall_status,
            audit_trail=[audit_entry],
            recommendations=recommendations
        )

        # Store report
        self.compliance_reports[file_path] = report

        return report

    def _extract_metadata(self, content: str) -> Dict[str, Any]:
        """Extract metadata from document frontmatter"""
        metadata = {}

        # Look for YAML frontmatter
        if content.startswith('---'):
            lines = content.split('\n')
            frontmatter_end = -1
            for i, line in enumerate(lines[1:], 1):
                if line.strip() == '---':
                    frontmatter_end = i
                    break

            if frontmatter_end > 0:
                frontmatter_content = '\n'.join(lines[1:frontmatter_end])
                try:
                    # Simple YAML parsing (could be enhanced with pyyaml if available)
                    for line in frontmatter_content.split('\n'):
                        if ':' in line:
                            key, value = line.split(':', 1)
                            metadata[key.strip()] = value.strip()
                except Exception as e:
                    logger.warning(f"Error parsing frontmatter: {e}")

        return metadata

    def _calculate_compliance_score(self, violations: List[ComplianceViolation]) -> float:
        """Calculate overall compliance score"""
        if not violations:
            return 100.0

        # Weight violations by severity
        weights = {
            'critical': 20,
            'high': 10,
            'medium': 5,
            'low': 2
        }

        total_penalty = sum(weights.get(v.severity, 0) for v in violations)
        score = max(0, 100 - total_penalty)

        return score

    def _generate_recommendations(self, violations: List[ComplianceViolation],
                                score: float) -> List[str]:
        """Generate compliance recommendations"""
        recommendations = []

        if score >= 90:
            recommendations.append("Document meets high compliance standards")
            recommendations.append("Continue regular compliance reviews")
        elif score >= 70:
            recommendations.append("Address remaining violations to improve compliance")
            recommendations.append("Consider manual accessibility testing")
        else:
            recommendations.append("Immediate attention required for critical violations")
            recommendations.append("Comprehensive compliance review recommended")

        # Add specific recommendations based on violation types
        violation_types = set(v.violation_type for v in violations)

        if 'missing_alt_text' in violation_types:
            recommendations.append("Add alternative text to all images")

        if 'missing_headings' in violation_types or 'missing_h1' in violation_types:
            recommendations.append("Implement proper heading hierarchy")

        if 'missing_language' in violation_types:
            recommendations.append("Specify document language in metadata")

        if 'missing_metadata' in violation_types:
            recommendations.append("Complete all required compliance metadata fields")

        return recommendations

    def generate_compliance_report(self, output_path: str = None) -> str:
        """Generate comprehensive compliance report"""
        if not self.compliance_reports:
            return "No compliance assessments have been performed yet."

        report_lines = []
        report_lines.append("# Regulatory Compliance Report")
        report_lines.append(f"Generated: {datetime.now().isoformat()}")
        report_lines.append("")

        # Summary statistics
        total_files = len(self.compliance_reports)
        compliant_files = len([r for r in self.compliance_reports.values()
                              if r.overall_status == "compliant"])
        partial_files = len([r for r in self.compliance_reports.values()
                            if r.overall_status == "partial"])
        non_compliant_files = len([r for r in self.compliance_reports.values()
                                  if r.overall_status == "non_compliant"])

        report_lines.append("## Summary Statistics")
        report_lines.append(f"- Total Files Assessed: {total_files}")
        report_lines.append(f"- Compliant: {compliant_files}")
        report_lines.append(f"- Partially Compliant: {partial_files}")
        report_lines.append(f"- Non-Compliant: {non_compliant_files}")
        report_lines.append("")

        # Average scores
        avg_score = sum(r.compliance_score for r in self.compliance_reports.values()) / total_files
        report_lines.append(f"Average Compliance Score: {avg_score:.1f}%")
        report_lines.append("")

        # Detailed results
        report_lines.append("## Detailed Results")
        for file_path, report in self.compliance_reports.items():
            report_lines.append(f"### {Path(file_path).name}")
            report_lines.append(f"- **Status:** {report.overall_status.title()}")
            report_lines.append(f"- **Score:** {report.compliance_score:.1f}%")
            report_lines.append(f"- **Violations:** {len(report.violations)}")

            if report.violations:
                report_lines.append("- **Issues:**")
                for violation in report.violations[:5]:  # Show first 5 violations
                    report_lines.append(f"  - {violation.description} ({violation.severity})")
                if len(report.violations) > 5:
                    report_lines.append(f"  - ... and {len(report.violations) - 5} more")

            report_lines.append("")

        # Recommendations
        all_recommendations = set()
        for report in self.compliance_reports.values():
            all_recommendations.update(report.recommendations)

        if all_recommendations:
            report_lines.append("## Recommendations")
            for rec in sorted(all_recommendations):
                report_lines.append(f"- {rec}")
            report_lines.append("")

        report_content = '\n'.join(report_lines)

        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(report_content)
            logger.info(f"Compliance report saved to: {output_path}")

        return report_content

    def get_audit_trail(self) -> List[Dict[str, Any]]:
        """Get the complete audit trail"""
        return self.audit_trail.copy()

# Global instance for easy access
_compliance_framework = None

def get_regulatory_compliance_framework() -> RegulatoryComplianceFramework:
    """Get or create the global regulatory compliance framework instance"""
    global _compliance_framework
    if _compliance_framework is None:
        _compliance_framework = RegulatoryComplianceFramework()
    return _compliance_framework

# Pseudocode generated by codewrx.ai
