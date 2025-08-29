"""
Terminal Grounds Documentation Automation Framework
Phase 4.1.2.2: Content Freshness Monitoring System

Intelligent content aging analysis, freshness tracking, and automated
update prioritization for documentation maintenance.
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
class ContentFreshnessMetrics:
    """Metrics for content freshness analysis"""
    document_path: str
    last_reviewed: datetime
    last_modified: datetime
    days_since_review: int
    days_since_modified: int
    freshness_score: float  # 0.0 = stale, 1.0 = fresh
    staleness_risk: str     # 'low', 'medium', 'high', 'critical'
    update_priority: str    # 'low', 'medium', 'high', 'urgent'
    aging_factors: Dict[str, float]

@dataclass
class ContentUpdateRecommendation:
    """Recommendation for content updates"""
    document_path: str
    recommendation_type: str  # 'review', 'update', 'archive', 'deprecate'
    priority: str
    reason: str
    suggested_actions: List[str]
    estimated_effort: str  # 'low', 'medium', 'high'
    business_impact: str

@dataclass
class FreshnessAnalysisResult:
    """Complete freshness analysis result"""
    total_documents: int
    fresh_documents: int
    stale_documents: int
    critical_documents: int
    average_freshness_score: float
    documents_by_priority: Dict[str, List[str]]
    recommendations: List[ContentUpdateRecommendation]
    aging_trends: Dict[str, Any]

class ContentAgingAnalyzer:
    """
    Analyzes content aging patterns and freshness
    """

    def __init__(self):
        self.aging_factors = {
            'time_since_review': {
                'weight': 0.4,
                'thresholds': {'low': 30, 'medium': 90, 'high': 180, 'critical': 365}
            },
            'time_since_modified': {
                'weight': 0.3,
                'thresholds': {'low': 60, 'medium': 180, 'high': 365, 'critical': 730}
            },
            'content_volatility': {
                'weight': 0.2,
                'indicators': ['api', 'version', 'release', 'update', 'change']
            },
            'reference_freshness': {
                'weight': 0.1,
                'patterns': [r'\b(v\d+\.\d+)', r'\b(\d{4}-\d{2}-\d{2})', r'\b(api|version|release)\b']
            }
        }

    def analyze_document_freshness(self, doc_path: str, frontmatter: Dict[str, Any],
                                 file_modified_time: datetime) -> ContentFreshnessMetrics:
        """
        Analyze freshness of a single document
        """
        # Parse last_reviewed date
        last_reviewed = self._parse_date(frontmatter.get('last_reviewed'))
        if not last_reviewed:
            last_reviewed = file_modified_time  # Fallback to file modification time

        now = datetime.now()
        days_since_review = (now - last_reviewed).days
        days_since_modified = (now - file_modified_time).days

        # Calculate aging factors
        aging_factors = {}

        # Time since review factor
        review_factor = self._calculate_time_factor(
            days_since_review,
            self.aging_factors['time_since_review']['thresholds']
        )
        aging_factors['time_since_review'] = review_factor

        # Time since modified factor
        modified_factor = self._calculate_time_factor(
            days_since_modified,
            self.aging_factors['time_since_modified']['thresholds']
        )
        aging_factors['time_since_modified'] = modified_factor

        # Content volatility factor
        volatility_factor = self._analyze_content_volatility(doc_path)
        aging_factors['content_volatility'] = volatility_factor

        # Reference freshness factor
        reference_factor = self._analyze_reference_freshness(doc_path)
        aging_factors['reference_freshness'] = reference_factor

        # Calculate overall freshness score
        freshness_score = self._calculate_freshness_score(aging_factors)

        # Determine staleness risk and update priority
        staleness_risk = self._determine_staleness_risk(freshness_score, days_since_review)
        update_priority = self._determine_update_priority(staleness_risk, aging_factors)

        return ContentFreshnessMetrics(
            document_path=doc_path,
            last_reviewed=last_reviewed,
            last_modified=file_modified_time,
            days_since_review=days_since_review,
            days_since_modified=days_since_modified,
            freshness_score=freshness_score,
            staleness_risk=staleness_risk,
            update_priority=update_priority,
            aging_factors=aging_factors
        )

    def _parse_date(self, date_str: Optional[str]) -> Optional[datetime]:
        """Parse date string to datetime object"""
        if not date_str:
            return None

        try:
            return datetime.strptime(date_str, '%Y-%m-%d')
        except ValueError:
            try:
                return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            except ValueError:
                logger.warning(f"Could not parse date: {date_str}")
                return None

    def _calculate_time_factor(self, days: int, thresholds: Dict[str, int]) -> float:
        """Calculate time-based aging factor (0.0 = fresh, 1.0 = stale)"""
        if days <= thresholds['low']:
            return 0.0
        elif days <= thresholds['medium']:
            return 0.3
        elif days <= thresholds['high']:
            return 0.7
        else:
            return 1.0

    def _analyze_content_volatility(self, doc_path: str) -> float:
        """Analyze content volatility based on keywords"""
        try:
            with open(doc_path, 'r', encoding='utf-8') as f:
                content = f.read().lower()

            indicators = self.aging_factors['content_volatility']['indicators']
            matches = sum(1 for indicator in indicators if indicator in content)

            # Normalize to 0-1 scale
            return min(1.0, matches / len(indicators))

        except Exception as e:
            logger.error(f"Error analyzing content volatility for {doc_path}: {e}")
            return 0.5  # Default medium volatility

    def _analyze_reference_freshness(self, doc_path: str) -> float:
        """Analyze freshness of references and dates in content"""
        try:
            with open(doc_path, 'r', encoding='utf-8') as f:
                content = f.read()

            patterns = self.aging_factors['reference_freshness']['patterns']
            total_matches = 0

            for pattern in patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                total_matches += len(matches)

            # Higher reference density = higher freshness monitoring need
            return min(1.0, total_matches / 10)  # Normalize

        except Exception as e:
            logger.error(f"Error analyzing reference freshness for {doc_path}: {e}")
            return 0.5

    def _calculate_freshness_score(self, aging_factors: Dict[str, float]) -> float:
        """Calculate overall freshness score"""
        total_weight = sum(factor['weight'] for factor in self.aging_factors.values())
        weighted_score = 0.0

        for factor_name, factor_config in self.aging_factors.items():
            if factor_name in aging_factors:
                weight = factor_config['weight']
                factor_value = aging_factors[factor_name]
                weighted_score += weight * factor_value

        # Convert to freshness score (1.0 = fresh, 0.0 = stale)
        return 1.0 - (weighted_score / total_weight)

    def _determine_staleness_risk(self, freshness_score: float, days_since_review: int) -> str:
        """Determine staleness risk level"""
        if freshness_score >= 0.8:
            return 'low'
        elif freshness_score >= 0.6:
            return 'medium'
        elif freshness_score >= 0.4 or days_since_review > 180:
            return 'high'
        else:
            return 'critical'

    def _determine_update_priority(self, staleness_risk: str, aging_factors: Dict[str, float]) -> str:
        """Determine update priority based on risk and factors"""
        if staleness_risk == 'critical':
            return 'urgent'
        elif staleness_risk == 'high':
            return 'high'
        elif staleness_risk == 'medium':
            # Check for high volatility content
            if aging_factors.get('content_volatility', 0) > 0.7:
                return 'high'
            else:
                return 'medium'
        else:
            return 'low'

class UpdateRecommendationEngine:
    """
    Generates intelligent update recommendations
    """

    def __init__(self):
        self.recommendation_rules = {
            'critical': {
                'review': 'Immediate review required - content may be outdated',
                'update': 'Urgent update needed - critical information stale',
                'archive': 'Consider archiving - content no longer relevant',
                'deprecate': 'Deprecation candidate - significantly outdated'
            },
            'high': {
                'review': 'Review recommended within 30 days',
                'update': 'Update recommended within 60 days',
                'archive': 'Consider archiving if no longer relevant',
                'deprecate': 'Monitor for deprecation'
            },
            'medium': {
                'review': 'Review recommended within 90 days',
                'update': 'Update when convenient',
                'archive': 'Monitor usage before archiving',
                'deprecate': 'Not a deprecation candidate yet'
            },
            'low': {
                'review': 'Review during next content audit',
                'update': 'Update during major revisions',
                'archive': 'Stable content - archive only if obsolete',
                'deprecate': 'Not a deprecation candidate'
            }
        }

    def generate_recommendations(self, freshness_metrics: List[ContentFreshnessMetrics]
                               ) -> List[ContentUpdateRecommendation]:
        """
        Generate update recommendations for documents
        """
        recommendations = []

        for metrics in freshness_metrics:
            if metrics.staleness_risk in ['critical', 'high']:
                # Generate specific recommendations based on aging factors
                recs = self._generate_specific_recommendations(metrics)
                recommendations.extend(recs)
            elif metrics.staleness_risk == 'medium':
                # Generate review recommendations
                recommendations.append(self._create_review_recommendation(metrics))
            # Low risk documents don't need recommendations

        return recommendations

    def _generate_specific_recommendations(self, metrics: ContentFreshnessMetrics
                                        ) -> List[ContentUpdateRecommendation]:
        """Generate specific recommendations based on aging factors"""
        recommendations = []

        # Check for high content volatility
        if metrics.aging_factors.get('content_volatility', 0) > 0.7:
            recommendations.append(ContentUpdateRecommendation(
                document_path=metrics.document_path,
                recommendation_type='update',
                priority=metrics.update_priority,
                reason='High content volatility - frequent updates needed',
                suggested_actions=[
                    'Review API versions and references',
                    'Check for recent changes in related systems',
                    'Update version numbers and dates'
                ],
                estimated_effort='medium',
                business_impact='high'
            ))

        # Check for stale references
        if metrics.aging_factors.get('reference_freshness', 0) > 0.7:
            recommendations.append(ContentUpdateRecommendation(
                document_path=metrics.document_path,
                recommendation_type='review',
                priority=metrics.update_priority,
                reason='Contains dated references that may need updating',
                suggested_actions=[
                    'Review and update version references',
                    'Check dates for currency',
                    'Verify API endpoints and links'
                ],
                estimated_effort='low',
                business_impact='medium'
            ))

        # Check for long time since review
        if metrics.days_since_review > 365:
            recommendations.append(ContentUpdateRecommendation(
                document_path=metrics.document_path,
                recommendation_type='review',
                priority='urgent',
                reason=f'Not reviewed for {metrics.days_since_review} days',
                suggested_actions=[
                    'Conduct comprehensive content review',
                    'Verify accuracy of all information',
                    'Update last_reviewed date'
                ],
                estimated_effort='high',
                business_impact='high'
            ))

        return recommendations

    def _create_review_recommendation(self, metrics: ContentFreshnessMetrics
                                    ) -> ContentUpdateRecommendation:
        """Create a standard review recommendation"""
        return ContentUpdateRecommendation(
            document_path=metrics.document_path,
            recommendation_type='review',
            priority=metrics.update_priority,
            reason=f'Medium staleness risk - freshness score: {metrics.freshness_score:.2f}',
            suggested_actions=[
                'Review content for accuracy',
                'Check for outdated information',
                'Update last_reviewed date'
            ],
            estimated_effort='low',
            business_impact='low'
        )

class ContentFreshnessMonitoringSystem:
    """
    Complete content freshness monitoring and analysis system
    """

    def __init__(self, docs_root: str = "docs"):
        self.docs_root = Path(docs_root)
        self.aging_analyzer = ContentAgingAnalyzer()
        self.recommendation_engine = UpdateRecommendationEngine()

        logger.info("Content Freshness Monitoring System initialized")

    def analyze_document_freshness(self, doc_path: str) -> Optional[ContentFreshnessMetrics]:
        """
        Analyze freshness of a single document
        """
        try:
            # Read document and extract frontmatter
            with open(doc_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Extract frontmatter
            frontmatter = {}
            if content.startswith('---'):
                parts = content.split('---', 2)
                if len(parts) >= 3:
                    try:
                        import yaml
                        frontmatter = yaml.safe_load(parts[1]) or {}
                    except ImportError:
                        logger.warning("YAML not available, skipping frontmatter parsing")
                    except Exception as e:
                        logger.warning(f"Error parsing frontmatter: {e}")

            # Get file modification time
            file_modified_time = datetime.fromtimestamp(os.path.getmtime(doc_path))

            # Analyze freshness
            metrics = self.aging_analyzer.analyze_document_freshness(
                doc_path, frontmatter, file_modified_time
            )

            return metrics

        except Exception as e:
            logger.error(f"Error analyzing document freshness for {doc_path}: {e}")
            return None

    def analyze_all_documents(self) -> FreshnessAnalysisResult:
        """
        Analyze freshness of all documents in the repository
        """
        all_metrics = []
        documents_by_priority = {'urgent': [], 'high': [], 'medium': [], 'low': []}

        # Find all markdown files
        for md_file in self.docs_root.rglob("*.md"):
            if md_file.name.lower() == "readme.md":
                continue

            metrics = self.analyze_document_freshness(str(md_file))
            if metrics:
                all_metrics.append(metrics)
                documents_by_priority[metrics.update_priority].append(str(md_file))

        # Calculate summary statistics
        total_documents = len(all_metrics)
        fresh_documents = len([m for m in all_metrics if m.freshness_score >= 0.8])
        stale_documents = len([m for m in all_metrics if m.freshness_score < 0.6])
        critical_documents = len([m for m in all_metrics if m.staleness_risk == 'critical'])

        average_freshness_score = (
            sum(m.freshness_score for m in all_metrics) / total_documents
            if total_documents > 0 else 0.0
        )

        # Generate recommendations
        recommendations = self.recommendation_engine.generate_recommendations(all_metrics)

        # Analyze aging trends
        aging_trends = self._analyze_aging_trends(all_metrics)

        return FreshnessAnalysisResult(
            total_documents=total_documents,
            fresh_documents=fresh_documents,
            stale_documents=stale_documents,
            critical_documents=critical_documents,
            average_freshness_score=average_freshness_score,
            documents_by_priority=documents_by_priority,
            recommendations=recommendations,
            aging_trends=aging_trends
        )

    def _analyze_aging_trends(self, metrics: List[ContentFreshnessMetrics]) -> Dict[str, Any]:
        """Analyze aging trends across all documents"""
        trends = {
            'average_days_since_review': 0,
            'average_days_since_modified': 0,
            'staleness_distribution': {'low': 0, 'medium': 0, 'high': 0, 'critical': 0},
            'priority_distribution': {'urgent': 0, 'high': 0, 'medium': 0, 'low': 0},
            'aging_rate': 0.0  # Documents becoming stale per month
        }

        if not metrics:
            return trends

        # Calculate averages
        trends['average_days_since_review'] = sum(m.days_since_review for m in metrics) / len(metrics)
        trends['average_days_since_modified'] = sum(m.days_since_modified for m in metrics) / len(metrics)

        # Count distributions
        for metric in metrics:
            trends['staleness_distribution'][metric.staleness_risk] += 1
            trends['priority_distribution'][metric.update_priority] += 1

        # Calculate aging rate (simplified)
        stale_count = trends['staleness_distribution']['high'] + trends['staleness_distribution']['critical']
        trends['aging_rate'] = stale_count / len(metrics) if len(metrics) > 0 else 0.0

        return trends

    def get_freshness_dashboard_data(self) -> Dict[str, Any]:
        """
        Get data for freshness monitoring dashboard
        """
        analysis = self.analyze_all_documents()

        return {
            'summary': {
                'total_documents': analysis.total_documents,
                'fresh_documents': analysis.fresh_documents,
                'stale_documents': analysis.stale_documents,
                'critical_documents': analysis.critical_documents,
                'average_freshness_score': analysis.average_freshness_score,
                'freshness_percentage': (analysis.fresh_documents / analysis.total_documents * 100)
                                      if analysis.total_documents > 0 else 0
            },
            'distributions': {
                'by_priority': analysis.documents_by_priority,
                'by_risk': analysis.aging_trends['staleness_distribution']
            },
            'trends': analysis.aging_trends,
            'recommendations': [
                {
                    'document': rec.document_path,
                    'type': rec.recommendation_type,
                    'priority': rec.priority,
                    'reason': rec.reason,
                    'effort': rec.estimated_effort,
                    'impact': rec.business_impact
                }
                for rec in analysis.recommendations[:10]  # Top 10 recommendations
            ]
        }

    def get_documents_needing_attention(self, priority: str = 'high') -> List[Dict[str, Any]]:
        """
        Get list of documents needing attention at specified priority level
        """
        analysis = self.analyze_all_documents()
        attention_docs = []

        priority_levels = {
            'urgent': ['urgent'],
            'high': ['urgent', 'high'],
            'medium': ['urgent', 'high', 'medium'],
            'all': ['urgent', 'high', 'medium', 'low']
        }

        target_priorities = priority_levels.get(priority, ['urgent', 'high'])

        for rec in analysis.recommendations:
            if rec.priority in target_priorities:
                attention_docs.append({
                    'document_path': rec.document_path,
                    'priority': rec.priority,
                    'recommendation_type': rec.recommendation_type,
                    'reason': rec.reason,
                    'suggested_actions': rec.suggested_actions,
                    'estimated_effort': rec.estimated_effort,
                    'business_impact': rec.business_impact
                })

        return attention_docs

# Global freshness monitoring system instance
freshness_monitoring_system = ContentFreshnessMonitoringSystem()

def get_freshness_monitoring_system() -> ContentFreshnessMonitoringSystem:
    """Get the global freshness monitoring system instance"""
    return freshness_monitoring_system

def analyze_document_freshness(doc_path: str) -> Dict[str, Any]:
    """
    Analyze freshness of a single document
    """
    system = get_freshness_monitoring_system()
    metrics = system.analyze_document_freshness(doc_path)

    if not metrics:
        return {"error": "Failed to analyze document freshness"}

    return {
        "document_path": metrics.document_path,
        "freshness_score": metrics.freshness_score,
        "staleness_risk": metrics.staleness_risk,
        "update_priority": metrics.update_priority,
        "days_since_review": metrics.days_since_review,
        "days_since_modified": metrics.days_since_modified,
        "aging_factors": metrics.aging_factors
    }

def get_freshness_dashboard() -> Dict[str, Any]:
    """
    Get freshness monitoring dashboard data
    """
    system = get_freshness_monitoring_system()
    return system.get_freshness_dashboard_data()

if __name__ == "__main__":
    # Test the freshness monitoring system
    print("Terminal Grounds Content Freshness Monitoring System")
    print("=" * 55)

    system = get_freshness_monitoring_system()

    print("Analyzing document freshness...")
    analysis = system.analyze_all_documents()

    print(f"\nFreshness Analysis Results:")
    print(f"Total Documents: {analysis.total_documents}")
    print(f"Fresh Documents: {analysis.fresh_documents}")
    print(f"Stale Documents: {analysis.stale_documents}")
    print(f"Critical Documents: {analysis.critical_documents}")
    print(f"Average Freshness Score: {analysis.average_freshness_score:.2f}")
    print(f"Freshness Rate: {(analysis.fresh_documents/analysis.total_documents*100):.1f}%"
          if analysis.total_documents > 0 else "0.0%")

    print(f"\nDocuments by Priority:")
    for priority, docs in analysis.documents_by_priority.items():
        print(f"  {priority.capitalize()}: {len(docs)} documents")

    print(f"\nTop Recommendations:")
    for i, rec in enumerate(analysis.recommendations[:5], 1):
        print(f"  {i}. {rec.document_path} - {rec.priority} priority")
        print(f"     {rec.reason}")

    print("\nContent Freshness Monitoring System operational!")
    print("Phase 4.1.2.2 Content Freshness Monitoring System ready for integration.")
