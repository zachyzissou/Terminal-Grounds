"""
Terminal Grounds Documentation Automation Framework
Phase 4.1.2: Complete Quality Assurance Framework

Integrated system combining proofreading, freshness monitoring,
consistency validation, and quality scoring for comprehensive
documentation quality management.
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Set
from dataclasses import dataclass
from datetime import datetime
import logging

# Add automation directory to path
sys.path.append(str(Path(__file__).parent))

from proofreading_engine import get_proofreading_engine, AutomatedProofreadingEngine
from freshness_monitoring import get_freshness_monitoring_system, ContentFreshnessMonitoringSystem
from consistency_validator import get_consistency_validation_system, ConsistencyValidationSystem
from quality_assessment import get_quality_assessment_system, QualityAssessmentSystem
from regulatory_compliance_framework import get_regulatory_compliance_framework, RegulatoryComplianceFramework
from accessibility_standards_framework import get_accessibility_standards_framework, AccessibilityStandardsFramework
from internationalization_framework import get_internationalization_framework, InternationalizationFramework

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class QualityAssuranceReport:
    """Comprehensive quality assurance report"""
    document_path: str
    assessment_date: datetime
    proofreading_results: Dict[str, Any]
    freshness_metrics: Dict[str, Any]
    consistency_analysis: Dict[str, Any]
    quality_score: Dict[str, Any]
    compliance_results: Dict[str, Any]
    accessibility_results: Dict[str, Any]
    internationalization_results: Dict[str, Any]
    overall_assessment: Dict[str, Any]
    recommendations: List[Dict[str, Any]]

@dataclass
class QualityAssuranceSummary:
    """Summary of quality assurance across all documents"""
    total_documents: int
    assessment_date: datetime
    average_scores: Dict[str, float]
    grade_distribution: Dict[str, int]
    critical_issues: List[Dict[str, Any]]
    improvement_opportunities: List[Dict[str, Any]]
    system_health: Dict[str, Any]

class QualityAssuranceFramework:
    """
    Complete quality assurance framework integrating all quality systems
    """

    def __init__(self, docs_root: str = "docs"):
        self.docs_root = Path(docs_root)

        # Initialize all quality systems
        self.proofreading_engine = AutomatedProofreadingEngine()
        self.freshness_monitor = ContentFreshnessMonitoringSystem(docs_root)
        self.consistency_validator = ConsistencyValidationSystem(docs_root)
        self.quality_assessor = QualityAssessmentSystem(docs_root)
        self.compliance_framework = RegulatoryComplianceFramework()
        self.accessibility_standards_framework = AccessibilityStandardsFramework()
        self.internationalization_framework = InternationalizationFramework()

        self.assessment_cache: Dict[str, QualityAssuranceReport] = {}

        logger.info("Complete Quality Assurance Framework initialized")

    def perform_complete_quality_assessment(self, doc_path: str) -> QualityAssuranceReport:
        """
        Perform complete quality assessment using all systems
        """
        logger.info(f"Starting complete quality assessment for {doc_path}")

        # 1. Proofreading Analysis
        proofreading_result, error = self.proofreading_engine.proofread_document(doc_path)
        if error:
            proofreading_results = {"error": error}
        else:
            proofreading_results = self.proofreading_engine.get_proofreading_summary(proofreading_result)

        # 2. Freshness Analysis
        freshness_metrics = self.freshness_monitor.analyze_document_freshness(doc_path)
        if freshness_metrics:
            freshness_data = {
                "freshness_score": freshness_metrics.freshness_score,
                "staleness_risk": freshness_metrics.staleness_risk,
                "update_priority": freshness_metrics.update_priority,
                "days_since_review": freshness_metrics.days_since_review,
                "days_since_modified": freshness_metrics.days_since_modified
            }
        else:
            freshness_data = {"error": "Failed to analyze freshness"}

        # 3. Consistency Analysis
        consistency_issues = self.consistency_validator.validate_document_consistency(doc_path)
        consistency_data = {
            "total_issues": len(consistency_issues),
            "issues": [
                {
                    "type": issue.issue_type,
                    "severity": issue.severity,
                    "line": issue.line_number,
                    "inconsistent_term": issue.inconsistent_term,
                    "suggested_term": issue.suggested_term
                }
                for issue in consistency_issues
            ]
        }

        # 4. Quality Scoring
        quality_score = self.quality_assessor.assess_document_quality(doc_path)
        quality_data = {
            "overall_score": quality_score.overall_score,
            "grade": quality_score.grade,
            "component_scores": quality_score.component_scores,
            "recommendations": quality_score.recommendations
        }

        # 5. Regulatory Compliance Assessment
        compliance_report = self.compliance_framework.assess_compliance(doc_path)
        compliance_data = {
            "compliance_score": compliance_report.compliance_score if compliance_report else 0,
            "overall_status": compliance_report.overall_status if compliance_report else "unknown",
            "violations_count": len(compliance_report.violations) if compliance_report else 0,
            "violations": [
                {
                    "requirement_id": v.requirement_id,
                    "violation_type": v.violation_type,
                    "severity": v.severity,
                    "description": v.description
                }
                for v in (compliance_report.violations if compliance_report else [])
            ],
            "recommendations": compliance_report.recommendations if compliance_report else []
        }

        # 6. Accessibility Standards Assessment
        accessibility_report = self.accessibility_standards_framework.perform_accessibility_assessment(doc_path)
        accessibility_data = {
            "compliance_score": accessibility_report.overall_score if accessibility_report else 0,
            "issues": [
                {
                    "issue_id": issue.issue_id,
                    "description": issue.description,
                    "severity": issue.severity,
                    "recommendations": issue.remediation_steps
                }
                for issue in (accessibility_report.issues if accessibility_report else [])
            ],
            "recommendations": accessibility_report.recommendations if accessibility_report else []
        }

        # 7. Internationalization Assessment
        internationalization_report = self.internationalization_framework.assess_document_i18n(doc_path)
        internationalization_data = {
            "utf8_valid": internationalization_report.utf8_valid if internationalization_report else False,
            "detected_language": internationalization_report.detected_language if internationalization_report else None,
            "has_multilingual_metadata": internationalization_report.has_multilingual_metadata if internationalization_report else False,
            "issues": [
                {
                    "issue_type": issue.issue_type,
                    "description": issue.description,
                    "severity": issue.severity,
                    "detected_at": issue.detected_at.isoformat() if hasattr(issue, 'detected_at') else None
                }
                for issue in (internationalization_report.issues if internationalization_report else [])
            ],
            "recommendations": internationalization_report.recommendations if internationalization_report else []
        }

        # 8. Generate Overall Assessment
        overall_assessment = self._generate_overall_assessment(
            proofreading_results, freshness_data, consistency_data, quality_data, compliance_data, accessibility_data, internationalization_data
        )

        # 9. Generate Recommendations
        recommendations = self._generate_integrated_recommendations(
            proofreading_results, freshness_data, consistency_data, quality_data, compliance_data, accessibility_data, internationalization_data
        )

        # Create comprehensive report
        report = QualityAssuranceReport(
            document_path=doc_path,
            assessment_date=datetime.now(),
            proofreading_results=proofreading_results,
            freshness_metrics=freshness_data,
            consistency_analysis=consistency_data,
            quality_score=quality_data,
            compliance_results=compliance_data,
            accessibility_results=accessibility_data,
            internationalization_results=internationalization_data,
            overall_assessment=overall_assessment,
            recommendations=recommendations
        )

        # Cache the report
        self.assessment_cache[doc_path] = report

        logger.info(f"Complete quality assessment completed for {doc_path}")

        return report

    def _generate_overall_assessment(self, proofreading: Dict, freshness: Dict,
                                   consistency: Dict, quality: Dict, compliance: Dict = None, accessibility: Dict = None, internationalization: Dict = None) -> Dict[str, Any]:
        """Generate overall quality assessment"""
        assessment = {
            "quality_level": "unknown",
            "critical_issues": 0,
            "improvement_areas": [],
            "strengths": []
        }

        # Determine quality level based on multiple factors
        quality_score = quality.get("overall_score", 0)
        proofreading_score = proofreading.get("overall_quality_score", 0)
        freshness_score = freshness.get("freshness_score", 0)
        consistency_issues = consistency.get("total_issues", 0)
        compliance_score = compliance.get("compliance_score", 100) if compliance else 100
        compliance_status = compliance.get("overall_status", "compliant") if compliance else "compliant"
        accessibility_score = accessibility.get("compliance_score", 100) if accessibility else 100
        internationalization_score = internationalization.get("compliance_score", 100) if internationalization else 100

        # Calculate weighted quality level
        if quality_score >= 85 and proofreading_score >= 80 and consistency_issues <= 2 and compliance_score >= 90 and accessibility_score >= 90 and internationalization_score >= 90:
            assessment["quality_level"] = "excellent"
        elif quality_score >= 75 and proofreading_score >= 70 and consistency_issues <= 5 and compliance_score >= 75 and accessibility_score >= 75 and internationalization_score >= 75:
            assessment["quality_level"] = "good"
        elif quality_score >= 65 and proofreading_score >= 60 and compliance_score >= 60 and accessibility_score >= 60 and internationalization_score >= 60:
            assessment["quality_level"] = "acceptable"
        elif quality_score >= 50 or proofreading_score >= 40:
            assessment["quality_level"] = "needs_improvement"
        else:
            assessment["quality_level"] = "poor"

        # Identify critical issues
        if proofreading.get("errors_count", 0) > 0:
            assessment["critical_issues"] += proofreading["errors_count"]
            assessment["improvement_areas"].append("grammar_errors")

        if freshness.get("staleness_risk") in ["high", "critical"]:
            assessment["critical_issues"] += 1
            assessment["improvement_areas"].append("content_freshness")

        if consistency_issues > 10:
            assessment["critical_issues"] += 1
            assessment["improvement_areas"].append("consistency_issues")

        if compliance_status != "compliant":
            assessment["critical_issues"] += 1
            assessment["improvement_areas"].append("regulatory_compliance")

        if accessibility_score < 80:
            assessment["critical_issues"] += 1
            assessment["improvement_areas"].append("accessibility_standards")

        if internationalization_score < 80:
            assessment["critical_issues"] += 1
            assessment["improvement_areas"].append("internationalization_standards")

        # Identify strengths
        if proofreading_score >= 90:
            assessment["strengths"].append("excellent_proofreading")
        if freshness_score >= 0.9:
            assessment["strengths"].append("very_fresh_content")
        if consistency_issues == 0:
            assessment["strengths"].append("perfect_consistency")
        if compliance_score == 100:
            assessment["strengths"].append("full_compliance")
        if accessibility_score == 100:
            assessment["strengths"].append("full_accessibility")
        if internationalization_score == 100:
            assessment["strengths"].append("full_internationalization")

        return assessment

    def _generate_integrated_recommendations(self, proofreading: Dict, freshness: Dict,
                                          consistency: Dict, quality: Dict, compliance: Dict = None, accessibility: Dict = None, internationalization: Dict = None) -> List[Dict[str, Any]]:
        """Generate integrated recommendations across all quality dimensions"""
        recommendations = []

        # Proofreading recommendations
        if proofreading.get("errors_count", 0) > 0:
            recommendations.append({
                "category": "proofreading",
                "priority": "high",
                "type": "fix_errors",
                "description": f"Fix {proofreading['errors_count']} proofreading errors",
                "estimated_effort": "low",
                "impact": "high"
            })

        if proofreading.get("readability_score", 100) < 60:
            recommendations.append({
                "category": "readability",
                "priority": "medium",
                "type": "improve_readability",
                "description": f"Improve readability (current: {proofreading.get('readability_score', 0):.1f})",
                "estimated_effort": "medium",
                "impact": "medium"
            })

        # Freshness recommendations
        if freshness.get("update_priority") in ["high", "urgent"]:
            recommendations.append({
                "category": "freshness",
                "priority": "high" if freshness.get("update_priority") == "urgent" else "medium",
                "type": "update_content",
                "description": f"Update content - {freshness.get('staleness_risk', 'unknown')} risk",
                "estimated_effort": "high",
                "impact": "high"
            })

        # Consistency recommendations
        if consistency.get("total_issues", 0) > 5:
            recommendations.append({
                "category": "consistency",
                "priority": "medium",
                "type": "fix_consistency",
                "description": f"Address {consistency['total_issues']} consistency issues",
                "estimated_effort": "medium",
                "impact": "medium"
            })

        # Quality recommendations
        if quality.get("overall_score", 100) < 75:
            recommendations.extend(quality.get("recommendations", []))

        # Compliance recommendations
        if compliance:
            if compliance.get("compliance_score", 100) < 75:
                recommendations.append({
                    "category": "compliance",
                    "priority": "high",
                    "type": "address_violations",
                    "description": f"Address compliance issues - {len(compliance.get('violations', []))} violations",
                    "estimated_effort": "high",
                    "impact": "high"
                })

            if compliance.get("overall_status") != "compliant":
                recommendations.append({
                    "category": "compliance",
                    "priority": "high",
                    "type": "achieve_compliance",
                    "description": "Take necessary actions to achieve regulatory compliance",
                    "estimated_effort": "high",
                    "impact": "high"
                })

        # Accessibility recommendations
        if accessibility:
            if accessibility.get("compliance_score", 100) < 75:
                recommendations.append({
                    "category": "accessibility",
                    "priority": "high",
                    "type": "address_accessibility_issues",
                    "description": f"Address accessibility issues - {len(accessibility.get('issues', []))} issues",
                    "estimated_effort": "high",
                    "impact": "high"
                })

            if accessibility.get("compliance_score", 100) < 90:
                recommendations.append({
                    "category": "accessibility",
                    "priority": "medium",
                    "type": "enhance_accessibility",
                    "description": "Enhance accessibility features to meet standards",
                    "estimated_effort": "medium",
                    "impact": "medium"
                })

        # Internationalization recommendations
        if internationalization:
            if internationalization.get("compliance_score", 100) < 75:
                recommendations.append({
                    "category": "internationalization",
                    "priority": "high",
                    "type": "address_internationalization_issues",
                    "description": f"Address internationalization issues - {len(internationalization.get('issues', []))} issues",
                    "estimated_effort": "high",
                    "impact": "high"
                })

            if internationalization.get("compliance_score", 100) < 90:
                recommendations.append({
                    "category": "internationalization",
                    "priority": "medium",
                    "type": "enhance_internationalization",
                    "description": "Enhance internationalization features to meet standards",
                    "estimated_effort": "medium",
                    "impact": "medium"
                })

        # Sort by priority
        priority_order = {"high": 0, "medium": 1, "low": 2}
        recommendations.sort(key=lambda x: priority_order.get(x.get("priority", "low"), 2))

        return recommendations[:10]  # Return top 10 recommendations

    def perform_bulk_quality_assessment(self) -> QualityAssuranceSummary:
        """
        Perform quality assessment across all documents
        """
        logger.info("Starting bulk quality assessment")

        all_reports = []
        quality_scores = []
        grade_counts = {"A": 0, "B": 0, "C": 0, "D": 0, "F": 0}

        # Assess all documents
        for md_file in self.docs_root.rglob("*.md"):
            if md_file.name.lower() == "readme.md":
                continue

            try:
                report = self.perform_complete_quality_assessment(str(md_file))
                all_reports.append(report)

                quality_scores.append(report.quality_score["overall_score"])
                grade_counts[report.quality_score["grade"]] += 1

            except Exception as e:
                logger.error(f"Error assessing {md_file}: {e}")

        # Calculate averages
        average_scores = {
            "overall_quality": sum(quality_scores) / len(quality_scores) if quality_scores else 0.0,
            "proofreading": sum(r.proofreading_results.get("overall_quality_score", 0)
                              for r in all_reports) / len(all_reports) if all_reports else 0.0,
            "freshness": sum(r.freshness_metrics.get("freshness_score", 0)
                           for r in all_reports) / len(all_reports) if all_reports else 0.0,
            "consistency": sum(100 - (r.consistency_analysis.get("total_issues", 0) * 5)
                             for r in all_reports) / len(all_reports) if all_reports else 0.0
        }

        # Identify critical issues
        critical_issues = []
        for report in all_reports:
            if report.overall_assessment.get("critical_issues", 0) > 0:
                critical_issues.append({
                    "document": report.document_path,
                    "critical_issues": report.overall_assessment["critical_issues"],
                    "quality_level": report.overall_assessment["quality_level"],
                    "main_issues": report.overall_assessment.get("improvement_areas", [])
                })

        # Generate improvement opportunities
        improvement_opportunities = self._analyze_improvement_opportunities(all_reports)

        # System health assessment
        system_health = self._assess_system_health(all_reports, average_scores)

        summary = QualityAssuranceSummary(
            total_documents=len(all_reports),
            assessment_date=datetime.now(),
            average_scores=average_scores,
            grade_distribution=grade_counts,
            critical_issues=critical_issues,
            improvement_opportunities=improvement_opportunities,
            system_health=system_health
        )

        logger.info(f"Bulk quality assessment completed for {len(all_reports)} documents")

        return summary

    def _analyze_improvement_opportunities(self, reports: List[QualityAssuranceReport]) -> List[Dict[str, Any]]:
        """Analyze improvement opportunities across all reports"""
        opportunities = []

        # Analyze common issues
        proofreading_issues = sum(len(r.proofreading_results.get("issues", {}).get("errors", [])) +
                                len(r.proofreading_results.get("issues", {}).get("warnings", []))
                                for r in reports)

        freshness_issues = sum(1 for r in reports
                             if r.freshness_metrics.get("staleness_risk") in ["high", "critical"])

        consistency_issues = sum(r.consistency_analysis.get("total_issues", 0) for r in reports)

        if proofreading_issues > len(reports) * 2:  # More than 2 issues per document
            opportunities.append({
                "category": "proofreading_training",
                "description": f"High proofreading error rate ({proofreading_issues} total issues)",
                "impact": "high",
                "recommendation": "Implement proofreading training and automated checks"
            })

        if freshness_issues > len(reports) * 0.3:  # More than 30% stale
            opportunities.append({
                "category": "content_refresh_process",
                "description": f"High stale content rate ({freshness_issues} documents)",
                "impact": "high",
                "recommendation": "Establish regular content review and update process"
            })

        if consistency_issues > len(reports) * 5:  # More than 5 issues per document
            opportunities.append({
                "category": "consistency_standards",
                "description": f"High consistency issue rate ({consistency_issues} total issues)",
                "impact": "medium",
                "recommendation": "Develop and enforce consistency standards and guidelines"
            })

        return opportunities

    def _assess_system_health(self, reports: List[QualityAssuranceReport],
                            average_scores: Dict[str, float]) -> Dict[str, Any]:
        """Assess overall system health"""
        health = {
            "status": "healthy",
            "score": 100,
            "issues": []
        }

        # Check average scores
        if average_scores["overall_quality"] < 70:
            health["issues"].append("Low average quality score")
            health["score"] -= 20

        if average_scores["proofreading"] < 75:
            health["issues"].append("Proofreading quality needs improvement")
            health["score"] -= 15

        if average_scores["freshness"] < 0.7:
            health["issues"].append("Content freshness is concerning")
            health["score"] -= 15

        if average_scores["consistency"] < 80:
            health["issues"].append("Consistency standards need enforcement")
            health["score"] -= 10

        # Check for critical issues
        critical_count = sum(1 for r in reports
                           if r.overall_assessment.get("critical_issues", 0) > 0)

        if critical_count > len(reports) * 0.2:  # More than 20% have critical issues
            health["issues"].append("High number of documents with critical issues")
            health["score"] -= 20

        # Determine status
        if health["score"] >= 90:
            health["status"] = "excellent"
        elif health["score"] >= 75:
            health["status"] = "healthy"
        elif health["score"] >= 60:
            health["status"] = "needs_attention"
        else:
            health["status"] = "critical"

        return health

    def get_quality_assurance_dashboard(self) -> Dict[str, Any]:
        """
        Get comprehensive quality assurance dashboard data
        """
        summary = self.perform_bulk_quality_assessment()

        return {
            "summary": {
                "total_documents": summary.total_documents,
                "assessment_date": summary.assessment_date.isoformat(),
                "average_scores": summary.average_scores,
                "grade_distribution": summary.grade_distribution,
                "system_health": summary.system_health
            },
            "critical_issues": summary.critical_issues[:10],  # Top 10
            "improvement_opportunities": summary.improvement_opportunities,
            "quality_distribution": {
                "excellent": summary.grade_distribution.get("A", 0) + summary.grade_distribution.get("B", 0),
                "good": summary.grade_distribution.get("C", 0),
                "needs_improvement": summary.grade_distribution.get("D", 0) + summary.grade_distribution.get("F", 0)
            },
            "component_scores": {
                "proofreading": summary.average_scores["proofreading"],
                "freshness": summary.average_scores["freshness"] * 100,  # Convert to percentage
                "consistency": summary.average_scores["consistency"]
            }
        }

    def get_document_quality_report(self, doc_path: str) -> Dict[str, Any]:
        """
        Get detailed quality report for a specific document
        """
        if doc_path in self.assessment_cache:
            report = self.assessment_cache[doc_path]
        else:
            report = self.perform_complete_quality_assessment(doc_path)

        return {
            "document_path": report.document_path,
            "assessment_date": report.assessment_date.isoformat(),
            "proofreading": report.proofreading_results,
            "freshness": report.freshness_metrics,
            "consistency": report.consistency_analysis,
            "quality_score": report.quality_score,
            "overall_assessment": report.overall_assessment,
            "recommendations": report.recommendations
        }

    def generate_quality_improvement_plan(self) -> Dict[str, Any]:
        """
        Generate a comprehensive quality improvement plan
        """
        summary = self.perform_bulk_quality_assessment()

        plan = {
            "assessment_date": summary.assessment_date.isoformat(),
            "current_state": {
                "average_quality_score": summary.average_scores["overall_quality"],
                "system_health": summary.system_health["status"],
                "critical_issues_count": len(summary.critical_issues)
            },
            "improvement_priorities": [],
            "action_plan": [],
            "success_metrics": {}
        }

        # Define improvement priorities based on current state
        if summary.average_scores["proofreading"] < 75:
            plan["improvement_priorities"].append({
                "area": "proofreading",
                "current_score": summary.average_scores["proofreading"],
                "target_score": 85.0,
                "priority": "high"
            })

        if summary.average_scores["freshness"] < 0.8:
            plan["improvement_priorities"].append({
                "area": "content_freshness",
                "current_score": summary.average_scores["freshness"] * 100,
                "target_score": 90.0,
                "priority": "high"
            })

        if summary.average_scores["consistency"] < 85:
            plan["improvement_priorities"].append({
                "area": "consistency",
                "current_score": summary.average_scores["consistency"],
                "target_score": 95.0,
                "priority": "medium"
            })

        # Generate action plan
        plan["action_plan"] = self._create_action_plan(summary)

        # Define success metrics
        plan["success_metrics"] = {
            "target_average_score": 85.0,
            "target_fresh_documents": 0.9,  # 90%
            "target_consistency_score": 95.0,
            "critical_issues_target": 0
        }

        return plan

    def _create_action_plan(self, summary: QualityAssuranceSummary) -> List[Dict[str, Any]]:
        """Create detailed action plan for quality improvement"""
        actions = []

        # Immediate actions (Week 1-2)
        if summary.system_health["score"] < 75:
            actions.append({
                "phase": "immediate",
                "timeframe": "Week 1-2",
                "actions": [
                    "Implement automated quality gates in workflow",
                    "Set up quality monitoring alerts",
                    "Conduct quality training for contributors"
                ]
            })

        # Short-term actions (Week 3-4)
        actions.append({
            "phase": "short_term",
            "timeframe": "Week 3-4",
            "actions": [
                "Address critical issues in high-priority documents",
                "Implement automated proofreading checks",
                "Establish content freshness monitoring"
            ]
        })

        # Medium-term actions (Month 2-3)
        actions.append({
            "phase": "medium_term",
            "timeframe": "Month 2-3",
            "actions": [
                "Develop consistency standards and guidelines",
                "Implement quality scoring system",
                "Create quality improvement workflows"
            ]
        })

        # Long-term actions (Month 3-6)
        actions.append({
            "phase": "long_term",
            "timeframe": "Month 3-6",
            "actions": [
                "Achieve target quality scores across all documents",
                "Implement predictive quality analytics",
                "Establish continuous quality improvement process"
            ]
        })

        return actions

# Global quality assurance framework instance
quality_assurance_framework = QualityAssuranceFramework()

def get_quality_assurance_framework() -> QualityAssuranceFramework:
    """Get the global quality assurance framework instance"""
    return quality_assurance_framework

def perform_document_quality_assessment(doc_path: str) -> Dict[str, Any]:
    """
    Perform complete quality assessment for a document
    """
    framework = get_quality_assurance_framework()
    report = framework.get_document_quality_report(doc_path)
    return report

def get_quality_assurance_dashboard() -> Dict[str, Any]:
    """
    Get quality assurance dashboard data
    """
    framework = get_quality_assurance_framework()
    return framework.get_quality_assurance_dashboard()

def generate_quality_improvement_plan() -> Dict[str, Any]:
    """
    Generate comprehensive quality improvement plan
    """
    framework = get_quality_assurance_framework()
    return framework.generate_quality_improvement_plan()

if __name__ == "__main__":
    # Test the complete quality assurance framework
    print("Terminal Grounds Complete Quality Assurance Framework")
    print("=" * 57)

    framework = QualityAssuranceFramework("../../docs")

    print("Performing bulk quality assessment...")
    summary = framework.perform_bulk_quality_assessment()

    print(f"\nQuality Assurance Assessment Results:")
    print(f"Total Documents: {summary.total_documents}")
    print(f"Average Overall Quality: {summary.average_scores['overall_quality']:.1f}")
    print(f"Proofreading Score: {summary.average_scores['proofreading']:.1f}")
    print(f"Freshness Score: {summary.average_scores['freshness']:.2f}")
    print(f"Consistency Score: {summary.average_scores['consistency']:.1f}")

    print(f"\nGrade Distribution:")
    for grade, count in summary.grade_distribution.items():
        print(f"  {grade}: {count} documents")

    print(f"\nSystem Health:")
    health = summary.system_health
    print(f"  Status: {health['status']}")
    print(f"  Score: {health['score']}/100")
    if health['issues']:
        print(f"  Issues: {', '.join(health['issues'])}")

    print(f"\nCritical Issues: {len(summary.critical_issues)} documents")

    print(f"\nImprovement Opportunities:")
    for i, opp in enumerate(summary.improvement_opportunities[:3], 1):
        print(f"  {i}. {opp['category']}: {opp['description']}")

    print("\nComplete Quality Assurance Framework operational!")
    print("Phase 4.1.2 Complete Quality Assurance Framework ready for production use.")
