"""
Terminal Grounds Documentation Automation Framework
Phase 4.1.2.4: Quality Scoring Implementation

Comprehensive quality scoring system that combines proofreading, freshness,
consistency, and other quality metrics into unified quality assessments.
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Set
from dataclasses import dataclass
from datetime import datetime, timedelta
import logging
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class QualityScore:
    """Comprehensive quality score for a document"""
    document_path: str
    overall_score: float  # 0-100
    grade: str  # A, B, C, D, F
    component_scores: Dict[str, float]
    weighted_factors: Dict[str, float]
    assessment_date: datetime
    recommendations: List[Dict[str, Any]]

@dataclass
class QualityBenchmark:
    """Quality benchmark for different document types"""
    document_type: str
    minimum_score: float
    target_score: float
    critical_threshold: float
    quality_factors: Dict[str, float]

@dataclass
class QualityTrend:
    """Quality trend analysis"""
    document_path: str
    score_history: List[Tuple[datetime, float]]
    trend_direction: str  # 'improving', 'declining', 'stable'
    trend_rate: float
    predictions: Dict[str, Any]

class QualityScoringEngine:
    """
    Engine for calculating comprehensive quality scores
    """

    def __init__(self):
        self.quality_benchmarks = self._load_quality_benchmarks()
        self.scoring_weights = {
            'proofreading': 0.25,    # Grammar, style, readability, tone
            'freshness': 0.20,       # Content age and updates
            'consistency': 0.25,     # Terminology, references, format, metadata
            'completeness': 0.15,    # Content coverage and structure
            'compliance': 0.15       # Standards and policy adherence
        }

        logger.info("Quality Scoring Engine initialized")

    def _load_quality_benchmarks(self) -> Dict[str, QualityBenchmark]:
        """Load quality benchmarks for different document types"""
        return {
            'guide': QualityBenchmark(
                document_type='guide',
                minimum_score=70.0,
                target_score=85.0,
                critical_threshold=60.0,
                quality_factors={
                    'proofreading': 0.3,
                    'freshness': 0.2,
                    'consistency': 0.25,
                    'completeness': 0.15,
                    'compliance': 0.1
                }
            ),
            'reference': QualityBenchmark(
                document_type='reference',
                minimum_score=75.0,
                target_score=90.0,
                critical_threshold=65.0,
                quality_factors={
                    'proofreading': 0.25,
                    'freshness': 0.15,
                    'consistency': 0.3,
                    'completeness': 0.2,
                    'compliance': 0.1
                }
            ),
            'process': QualityBenchmark(
                document_type='process',
                minimum_score=80.0,
                target_score=95.0,
                critical_threshold=70.0,
                quality_factors={
                    'proofreading': 0.2,
                    'freshness': 0.25,
                    'consistency': 0.2,
                    'completeness': 0.2,
                    'compliance': 0.15
                }
            ),
            'spec': QualityBenchmark(
                document_type='spec',
                minimum_score=85.0,
                target_score=95.0,
                critical_threshold=75.0,
                quality_factors={
                    'proofreading': 0.15,
                    'freshness': 0.2,
                    'consistency': 0.25,
                    'completeness': 0.25,
                    'compliance': 0.15
                }
            ),
            'api': QualityBenchmark(
                document_type='api',
                minimum_score=85.0,
                target_score=95.0,
                critical_threshold=75.0,
                quality_factors={
                    'proofreading': 0.2,
                    'freshness': 0.15,
                    'consistency': 0.3,
                    'completeness': 0.2,
                    'compliance': 0.15
                }
            )
        }

    def calculate_document_quality_score(self, doc_path: str,
                                       proofreading_result: Optional[Any] = None,
                                       freshness_metrics: Optional[Any] = None,
                                       consistency_issues: Optional[List] = None,
                                       frontmatter: Optional[Dict[str, Any]] = None) -> QualityScore:
        """
        Calculate comprehensive quality score for a document
        """
        component_scores = {}

        # Proofreading score (0-100)
        if proofreading_result:
            component_scores['proofreading'] = proofreading_result.overall_quality_score
        else:
            component_scores['proofreading'] = self._estimate_proofreading_score(doc_path)

        # Freshness score (0-100)
        if freshness_metrics:
            component_scores['freshness'] = freshness_metrics.freshness_score * 100
        else:
            component_scores['freshness'] = self._estimate_freshness_score(doc_path)

        # Consistency score (0-100)
        if consistency_issues is not None:
            component_scores['consistency'] = self._calculate_consistency_score(consistency_issues)
        else:
            component_scores['consistency'] = self._estimate_consistency_score(doc_path)

        # Completeness score (0-100)
        component_scores['completeness'] = self._calculate_completeness_score(doc_path, frontmatter)

        # Compliance score (0-100)
        component_scores['compliance'] = self._calculate_compliance_score(doc_path, frontmatter)

        # Get document type for benchmark
        doc_type = frontmatter.get('type', 'guide') if frontmatter else 'guide'
        benchmark = self.quality_benchmarks.get(doc_type, self.quality_benchmarks['guide'])

        # Calculate weighted overall score
        overall_score = 0.0
        weighted_factors = {}

        for factor, weight in self.scoring_weights.items():
            if factor in component_scores:
                score = component_scores[factor]
                weighted_score = score * weight
                overall_score += weighted_score
                weighted_factors[factor] = weighted_score

        # Generate grade
        grade = self._calculate_grade(overall_score)

        # Generate recommendations
        recommendations = self._generate_quality_recommendations(
            component_scores, benchmark, doc_type
        )

        return QualityScore(
            document_path=doc_path,
            overall_score=overall_score,
            grade=grade,
            component_scores=component_scores,
            weighted_factors=weighted_factors,
            assessment_date=datetime.now(),
            recommendations=recommendations
        )

    def _estimate_proofreading_score(self, doc_path: str) -> float:
        """Estimate proofreading score when detailed analysis not available"""
        try:
            with open(doc_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Simple heuristics for estimation
            score = 100.0

            # Check for obvious issues
            if re.search(r'\s{2,}', content):  # Multiple spaces
                score -= 5
            if re.search(r'\s+$', content, re.MULTILINE):  # Trailing spaces
                score -= 5
            if content.lower().count('dont') > 0:  # Contractions
                score -= 3

            # Length-based adjustment (longer docs tend to have more issues)
            lines = content.split('\n')
            if len(lines) > 100:
                score -= 5

            return max(0.0, min(100.0, score))

        except Exception:
            return 50.0  # Default neutral score

    def _estimate_freshness_score(self, doc_path: str) -> float:
        """Estimate freshness score based on file modification time"""
        try:
            file_modified = datetime.fromtimestamp(os.path.getmtime(doc_path))
            days_since_modified = (datetime.now() - file_modified).days

            # Simple freshness calculation
            if days_since_modified <= 30:
                return 100.0
            elif days_since_modified <= 90:
                return 80.0
            elif days_since_modified <= 180:
                return 60.0
            elif days_since_modified <= 365:
                return 40.0
            else:
                return 20.0

        except Exception:
            return 50.0

    def _estimate_consistency_score(self, doc_path: str) -> float:
        """Estimate consistency score"""
        try:
            with open(doc_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Simple consistency checks
            score = 100.0

            # Check for mixed heading styles
            if re.search(r'^#+\s', content, re.MULTILINE):
                atx_headings = len(re.findall(r'^#+\s', content, re.MULTILINE))
                if atx_headings > 0:
                    # Assume some inconsistency if we have ATX headings
                    score -= 10

            # Check for inconsistent list markers
            list_markers = re.findall(r'^[\s]*[-*+]\s', content, re.MULTILINE)
            if len(set(list_markers)) > 1:
                score -= 5

            return max(0.0, min(100.0, score))

        except Exception:
            return 50.0

    def _calculate_consistency_score(self, consistency_issues: List) -> float:
        """Calculate consistency score from issues"""
        if not consistency_issues:
            return 100.0

        # Penalize based on issue count and severity
        error_count = len([i for i in consistency_issues if i.severity == 'error'])
        warning_count = len([i for i in consistency_issues if i.severity == 'warning'])
        suggestion_count = len([i for i in consistency_issues if i.severity == 'suggestion'])

        penalty = (error_count * 10) + (warning_count * 5) + (suggestion_count * 2)

        return max(0.0, 100.0 - penalty)

    def _calculate_completeness_score(self, doc_path: str, frontmatter: Optional[Dict[str, Any]]) -> float:
        """Calculate completeness score"""
        score = 100.0

        if not frontmatter:
            score -= 30
            return score

        # Required fields check
        required_fields = ['title', 'type', 'domain', 'status', 'last_reviewed', 'maintainer']
        missing_fields = [f for f in required_fields if f not in frontmatter or not frontmatter[f]]
        score -= len(missing_fields) * 5

        # Content structure check
        try:
            with open(doc_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Check for basic structure elements
            if not re.search(r'^#{1,6}\s', content, re.MULTILINE):
                score -= 10  # No headings

            if not re.search(r'\[.*\]\(.*\)', content):
                score -= 5  # No links

            lines = content.split('\n')
            if len(lines) < 10:
                score -= 10  # Too short

        except Exception:
            score -= 20

        return max(0.0, min(100.0, score))

    def _calculate_compliance_score(self, doc_path: str, frontmatter: Optional[Dict[str, Any]]) -> float:
        """Calculate compliance score"""
        score = 100.0

        if not frontmatter:
            score -= 50
            return score

        # Check field values against standards
        valid_types = ['guide', 'reference', 'process', 'spec', 'api']
        valid_domains = ['technical', 'design', 'lore', 'art', 'process']
        valid_statuses = ['draft', 'review', 'approved', 'deprecated']

        if frontmatter.get('type') and frontmatter['type'] not in valid_types:
            score -= 10
        if frontmatter.get('domain') and frontmatter['domain'] not in valid_domains:
            score -= 10
        if frontmatter.get('status') and frontmatter['status'] not in valid_statuses:
            score -= 10

        # Check date format
        if frontmatter.get('last_reviewed'):
            try:
                datetime.strptime(frontmatter['last_reviewed'], '%Y-%m-%d')
            except ValueError:
                score -= 10

        return max(0.0, min(100.0, score))

    def _calculate_grade(self, score: float) -> str:
        """Convert score to letter grade"""
        if score >= 90:
            return "A"
        elif score >= 80:
            return "B"
        elif score >= 70:
            return "C"
        elif score >= 60:
            return "D"
        else:
            return "F"

    def _generate_quality_recommendations(self, component_scores: Dict[str, float],
                                        benchmark: QualityBenchmark,
                                        doc_type: str) -> List[Dict[str, Any]]:
        """Generate quality improvement recommendations"""
        recommendations = []

        # Check against benchmark
        if component_scores['proofreading'] < 80:
            recommendations.append({
                'category': 'proofreading',
                'priority': 'high',
                'description': 'Improve grammar, style, and readability',
                'current_score': component_scores['proofreading'],
                'target_score': 85.0
            })

        if component_scores['freshness'] < benchmark.minimum_score:
            recommendations.append({
                'category': 'freshness',
                'priority': 'high',
                'description': 'Update content to improve freshness score',
                'current_score': component_scores['freshness'],
                'target_score': benchmark.minimum_score
            })

        if component_scores['consistency'] < 80:
            recommendations.append({
                'category': 'consistency',
                'priority': 'medium',
                'description': 'Address consistency issues in terminology and formatting',
                'current_score': component_scores['consistency'],
                'target_score': 85.0
            })

        if component_scores['completeness'] < benchmark.minimum_score:
            recommendations.append({
                'category': 'completeness',
                'priority': 'medium',
                'description': 'Improve content structure and required metadata',
                'current_score': component_scores['completeness'],
                'target_score': benchmark.minimum_score
            })

        return recommendations

class QualityTrendAnalyzer:
    """
    Analyzes quality trends over time
    """

    def __init__(self):
        self.score_history: Dict[str, List[Tuple[datetime, float]]] = {}
        self.trend_window_days = 90

    def record_quality_score(self, doc_path: str, score: float):
        """Record a quality score for trend analysis"""
        if doc_path not in self.score_history:
            self.score_history[doc_path] = []

        self.score_history[doc_path].append((datetime.now(), score))

        # Keep only recent history
        cutoff_date = datetime.now() - timedelta(days=self.trend_window_days)
        self.score_history[doc_path] = [
            (date, s) for date, s in self.score_history[doc_path]
            if date > cutoff_date
        ]

    def analyze_quality_trend(self, doc_path: str) -> Optional[QualityTrend]:
        """Analyze quality trend for a document"""
        if doc_path not in self.score_history or len(self.score_history[doc_path]) < 2:
            return None

        history = sorted(self.score_history[doc_path])
        scores = [score for _, score in history]

        # Calculate trend
        if len(scores) >= 2:
            first_score = scores[0]
            last_score = scores[-1]
            trend_rate = (last_score - first_score) / len(scores)

            if trend_rate > 0.5:
                trend_direction = 'improving'
            elif trend_rate < -0.5:
                trend_direction = 'declining'
            else:
                trend_direction = 'stable'

            # Simple prediction
            predicted_score = last_score + (trend_rate * 7)  # 7-day prediction
            predicted_score = max(0.0, min(100.0, predicted_score))

            return QualityTrend(
                document_path=doc_path,
                score_history=history,
                trend_direction=trend_direction,
                trend_rate=trend_rate,
                predictions={
                    '7_day_score': predicted_score,
                    'trend_confidence': min(1.0, len(scores) / 10)  # More data = higher confidence
                }
            )

        return None

class QualityAssessmentSystem:
    """
    Complete quality assessment and scoring system
    """

    def __init__(self, docs_root: str = "docs"):
        self.docs_root = Path(docs_root)
        self.scoring_engine = QualityScoringEngine()
        self.trend_analyzer = QualityTrendAnalyzer()

        logger.info("Quality Assessment System initialized")

    def assess_document_quality(self, doc_path: str) -> QualityScore:
        """
        Perform complete quality assessment of a document
        """
        try:
            # Read document and extract frontmatter
            with open(doc_path, 'r', encoding='utf-8') as f:
                content = f.read()

            frontmatter = self._extract_frontmatter(content)

            # Get quality components (simplified - in practice would integrate with other systems)
            proofreading_score = self.scoring_engine._estimate_proofreading_score(doc_path)
            freshness_score = self.scoring_engine._estimate_freshness_score(doc_path)
            consistency_score = self.scoring_engine._estimate_consistency_score(doc_path)

            # Create mock objects for scoring
            class MockProofreadingResult:
                def __init__(self, score):
                    self.overall_quality_score = score

            class MockFreshnessMetrics:
                def __init__(self, score):
                    self.freshness_score = score

            proofreading_result = MockProofreadingResult(proofreading_score / 100)
            freshness_metrics = MockFreshnessMetrics(freshness_score / 100)

            # Calculate quality score
            quality_score = self.scoring_engine.calculate_document_quality_score(
                doc_path=doc_path,
                proofreading_result=proofreading_result,
                freshness_metrics=freshness_metrics,
                consistency_issues=[],  # Would be populated from consistency validator
                frontmatter=frontmatter
            )

            # Record for trend analysis
            self.trend_analyzer.record_quality_score(doc_path, quality_score.overall_score)

            return quality_score

        except Exception as e:
            logger.error(f"Error assessing document quality for {doc_path}: {e}")
            # Return minimal quality score
            return QualityScore(
                document_path=doc_path,
                overall_score=0.0,
                grade="F",
                component_scores={},
                weighted_factors={},
                assessment_date=datetime.now(),
                recommendations=[{
                    'category': 'error',
                    'priority': 'high',
                    'description': f'Quality assessment failed: {str(e)}'
                }]
            )

    def assess_all_documents_quality(self) -> Dict[str, Any]:
        """
        Assess quality of all documents
        """
        quality_scores = {}
        grade_distribution = {'A': 0, 'B': 0, 'C': 0, 'D': 0, 'F': 0}

        for md_file in self.docs_root.rglob("*.md"):
            if md_file.name.lower() == "readme.md":
                continue

            quality_score = self.assess_document_quality(str(md_file))
            quality_scores[str(md_file)] = quality_score
            grade_distribution[quality_score.grade] += 1

        # Calculate summary statistics
        scores = [qs.overall_score for qs in quality_scores.values()]
        average_score = sum(scores) / len(scores) if scores else 0.0

        return {
            'quality_scores': quality_scores,
            'summary': {
                'total_documents': len(quality_scores),
                'average_score': average_score,
                'grade_distribution': grade_distribution,
                'quality_grade': self.scoring_engine._calculate_grade(average_score)
            },
            'trends': self._analyze_quality_trends(quality_scores)
        }

    def _analyze_quality_trends(self, quality_scores: Dict[str, QualityScore]) -> Dict[str, Any]:
        """Analyze quality trends across all documents"""
        trends = {}

        for doc_path, quality_score in quality_scores.items():
            trend = self.trend_analyzer.analyze_quality_trend(doc_path)
            if trend:
                trends[doc_path] = {
                    'direction': trend.trend_direction,
                    'rate': trend.trend_rate,
                    'prediction': trend.predictions.get('7_day_score')
                }

        # Calculate overall trends
        improving_count = sum(1 for t in trends.values() if t['direction'] == 'improving')
        declining_count = sum(1 for t in trends.values() if t['direction'] == 'declining')

        return {
            'document_trends': trends,
            'overall_trends': {
                'improving_documents': improving_count,
                'declining_documents': declining_count,
                'stable_documents': len(trends) - improving_count - declining_count,
                'trend_health_score': (improving_count - declining_count) / len(trends) if trends else 0.0
            }
        }

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

    def get_quality_dashboard_data(self) -> Dict[str, Any]:
        """
        Get data for quality monitoring dashboard
        """
        assessment = self.assess_all_documents_quality()

        return {
            'summary': assessment['summary'],
            'grade_distribution': assessment['summary']['grade_distribution'],
            'quality_distribution': {
                'excellent': assessment['summary']['grade_distribution']['A'],
                'good': assessment['summary']['grade_distribution']['B'],
                'needs_improvement': assessment['summary']['grade_distribution']['C'],
                'poor': assessment['summary']['grade_distribution']['D'] +
                       assessment['summary']['grade_distribution']['F']
            },
            'trends': assessment['trends']['overall_trends'],
            'top_issues': self._get_top_quality_issues(assessment['quality_scores']),
            'recommendations': self._generate_system_recommendations(assessment)
        }

    def _get_top_quality_issues(self, quality_scores: Dict[str, QualityScore]) -> List[Dict[str, Any]]:
        """Get top quality issues across all documents"""
        issues = []

        for doc_path, quality_score in quality_scores.items():
            if quality_score.overall_score < 70:  # Below C grade
                issues.append({
                    'document': doc_path,
                    'score': quality_score.overall_score,
                    'grade': quality_score.grade,
                    'issues': [rec['description'] for rec in quality_score.recommendations[:2]]
                })

        # Sort by score (worst first) and return top 10
        issues.sort(key=lambda x: x['score'])
        return issues[:10]

    def _generate_system_recommendations(self, assessment: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate system-wide quality improvement recommendations"""
        recommendations = []

        summary = assessment['summary']
        trends = assessment['trends']['overall_trends']

        if summary['average_score'] < 75:
            recommendations.append({
                'category': 'overall_quality',
                'priority': 'high',
                'description': f'Improve overall documentation quality (current: {summary["average_score"]:.1f})',
                'action_items': [
                    'Implement automated quality checks in workflow',
                    'Provide quality training for contributors',
                    'Establish quality review processes'
                ]
            })

        if trends['declining_documents'] > trends['improving_documents']:
            recommendations.append({
                'category': 'quality_trends',
                'priority': 'medium',
                'description': 'Address declining quality trends',
                'action_items': [
                    'Identify root causes of quality decline',
                    'Implement quality monitoring alerts',
                    'Review and update quality standards'
                ]
            })

        poor_docs = summary['grade_distribution']['D'] + summary['grade_distribution']['F']
        if poor_docs > summary['total_documents'] * 0.2:  # More than 20% poor quality
            recommendations.append({
                'category': 'quality_backlog',
                'priority': 'high',
                'description': f'Address {poor_docs} documents with poor quality',
                'action_items': [
                    'Prioritize quality improvements for low-scoring documents',
                    'Implement quality gates to prevent poor quality',
                    'Allocate resources for quality remediation'
                ]
            })

        return recommendations

    def get_documents_needing_attention(self, priority: str = 'high') -> List[Dict[str, Any]]:
        """
        Get documents needing quality attention
        """
        assessment = self.assess_all_documents_quality()
        attention_docs = []

        score_thresholds = {
            'urgent': 50,
            'high': 70,
            'medium': 80,
            'all': 100
        }

        threshold = score_thresholds.get(priority, 70)

        for doc_path, quality_score in assessment['quality_scores'].items():
            if quality_score.overall_score < threshold:
                attention_docs.append({
                    'document_path': doc_path,
                    'quality_score': quality_score.overall_score,
                    'grade': quality_score.grade,
                    'recommendations': quality_score.recommendations,
                    'component_scores': quality_score.component_scores
                })

        # Sort by score (worst first)
        attention_docs.sort(key=lambda x: x['quality_score'])

        return attention_docs

# Global quality assessment system instance
quality_assessment_system = QualityAssessmentSystem()

def get_quality_assessment_system() -> QualityAssessmentSystem:
    """Get the global quality assessment system instance"""
    return quality_assessment_system

def assess_document_quality(doc_path: str) -> Dict[str, Any]:
    """
    Assess quality of a single document
    """
    system = get_quality_assessment_system()
    quality_score = system.assess_document_quality(doc_path)

    return {
        "document_path": quality_score.document_path,
        "overall_score": quality_score.overall_score,
        "grade": quality_score.grade,
        "component_scores": quality_score.component_scores,
        "recommendations": quality_score.recommendations
    }

def get_quality_dashboard() -> Dict[str, Any]:
    """
    Get quality assessment dashboard data
    """
    system = get_quality_assessment_system()
    return system.get_quality_dashboard_data()

if __name__ == "__main__":
    # Test the quality assessment system
    print("Terminal Grounds Quality Assessment System")
    print("=" * 44)

    system = QualityAssessmentSystem("../../docs")

    print("Assessing document quality...")
    assessment = system.assess_all_documents_quality()

    print(f"\nQuality Assessment Results:")
    print(f"Total Documents: {assessment['summary']['total_documents']}")
    print(f"Average Score: {assessment['summary']['average_score']:.1f}")
    print(f"Overall Grade: {assessment['summary']['quality_grade']}")

    print(f"\nGrade Distribution:")
    for grade, count in assessment['summary']['grade_distribution'].items():
        print(f"  {grade}: {count} documents")

    print(f"\nQuality Trends:")
    trends = assessment['trends']['overall_trends']
    print(f"  Improving: {trends['improving_documents']} documents")
    print(f"  Declining: {trends['declining_documents']} documents")
    print(f"  Stable: {trends['stable_documents']} documents")

    print(f"\nTop Recommendations:")
    for i, rec in enumerate(assessment.get('recommendations', [])[:3], 1):
        print(f"  {i}. {rec['category']} - {rec['priority']} priority")
        print(f"     {rec['description']}")

    print("\nQuality Assessment System operational!")
    print("Phase 4.1.2.4 Quality Scoring Implementation ready for integration.")
