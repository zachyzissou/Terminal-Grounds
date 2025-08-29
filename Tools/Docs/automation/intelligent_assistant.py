"""
Terminal Grounds Documentation Automation Framework
Phase 4.1.1.2: Intelligent Assistance System

Context-aware template suggestions, content structure guidance,
and real-time validation feedback for guided document creation.
"""

import os
import re
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass, field
from datetime import datetime
from collections import Counter, defaultdict
import logging
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class TemplateSuggestion:
    """Suggestion for document template"""
    template_name: str
    confidence_score: float
    reasoning: str
    domain: str
    estimated_completion_time: int  # minutes
    required_fields: List[str]
    suggested_content: Dict[str, Any]

@dataclass
class ContentGuidance:
    """Guidance for content structure"""
    section_name: str
    description: str
    required: bool
    suggested_content: str
    validation_rules: List[Dict[str, Any]]
    examples: List[str] = field(default_factory=list)

@dataclass
class ValidationFeedback:
    """Real-time validation feedback"""
    field: str
    is_valid: bool
    message: str
    severity: str  # "error", "warning", "info"
    suggestion: Optional[str] = None
    auto_fix_available: bool = False

@dataclass
class DocumentContext:
    """Context information for intelligent assistance"""
    document_type: str
    domain: str
    target_audience: str
    complexity_level: str
    keywords: List[str]
    related_documents: List[str]
    project_context: Dict[str, Any]

class IntelligentAssistant:
    """
    AI-powered assistant for guided document creation
    """

    def __init__(self, docs_root: str = "docs"):
        self.docs_root = Path(docs_root)
        self.template_patterns: Dict[str, Dict[str, Any]] = {}
        self.content_patterns: Dict[str, List[ContentGuidance]] = {}
        self.validation_rules: Dict[str, List[Dict[str, Any]]] = {}
        self.context_analyzer = ContextAnalyzer(docs_root)

        # Load assistance data
        self._load_assistance_data()

    def _load_assistance_data(self):
        """Load template patterns and assistance data"""
        assistance_dir = self.docs_root / ".." / "Tools" / "Docs" / "automation" / "assistance"

        if assistance_dir.exists():
            # Load template patterns
            template_file = assistance_dir / "template_patterns.yaml"
            if template_file.exists():
                try:
                    with open(template_file, 'r', encoding='utf-8') as f:
                        self.template_patterns = yaml.safe_load(f)
                except Exception as e:
                    logger.error(f"Error loading template patterns: {e}")

            # Load content guidance
            content_file = assistance_dir / "content_guidance.yaml"
            if content_file.exists():
                try:
                    with open(content_file, 'r', encoding='utf-8') as f:
                        content_data = yaml.safe_load(f)
                        for doc_type, guidance_list in content_data.items():
                            self.content_patterns[doc_type] = [
                                ContentGuidance(**guidance) for guidance in guidance_list
                            ]
                except Exception as e:
                    logger.error(f"Error loading content guidance: {e}")

            # Load validation rules
            validation_file = assistance_dir / "validation_rules.yaml"
            if validation_file.exists():
                try:
                    with open(validation_file, 'r', encoding='utf-8') as f:
                        self.validation_rules = yaml.safe_load(f)
                except Exception as e:
                    logger.error(f"Error loading validation rules: {e}")

        # Create default assistance data if none exists
        if not self.template_patterns:
            self._create_default_assistance_data()

    def _create_default_assistance_data(self):
        """Create default assistance patterns and rules"""

        # Template patterns for different document types
        self.template_patterns = {
            "technical": {
                "patterns": [
                    {
                        "name": "API Documentation",
                        "keywords": ["api", "endpoint", "request", "response", "authentication"],
                        "confidence_boost": 0.8,
                        "required_fields": ["title", "api_version", "base_url", "authentication"]
                    },
                    {
                        "name": "System Architecture",
                        "keywords": ["architecture", "system", "component", "database", "infrastructure"],
                        "confidence_boost": 0.7,
                        "required_fields": ["title", "overview", "components", "data_flow"]
                    },
                    {
                        "name": "Code Documentation",
                        "keywords": ["function", "class", "method", "parameter", "return"],
                        "confidence_boost": 0.6,
                        "required_fields": ["title", "description", "parameters", "examples"]
                    }
                ]
            },
            "design": {
                "patterns": [
                    {
                        "name": "UI/UX Design",
                        "keywords": ["ui", "ux", "interface", "user", "design", "wireframe"],
                        "confidence_boost": 0.8,
                        "required_fields": ["title", "user_personas", "user_journey", "design_system"]
                    },
                    {
                        "name": "Game Design",
                        "keywords": ["gameplay", "mechanics", "level", "character", "balance"],
                        "confidence_boost": 0.7,
                        "required_fields": ["title", "game_mechanics", "level_design", "character_progression"]
                    }
                ]
            },
            "process": {
                "patterns": [
                    {
                        "name": "Standard Operating Procedure",
                        "keywords": ["procedure", "process", "step", "workflow", "sop"],
                        "confidence_boost": 0.8,
                        "required_fields": ["title", "purpose", "scope", "procedure_steps"]
                    },
                    {
                        "name": "Quality Assurance",
                        "keywords": ["quality", "qa", "testing", "validation", "standards"],
                        "confidence_boost": 0.7,
                        "required_fields": ["title", "quality_criteria", "testing_procedures", "acceptance_criteria"]
                    }
                ]
            }
        }

        # Content guidance patterns
        self.content_patterns = {
            "technical": [
                ContentGuidance(
                    section_name="Overview",
                    description="High-level description of the technical component",
                    required=True,
                    suggested_content="Provide a clear, concise overview of what this component does and its purpose in the system.",
                    validation_rules=[
                        {"min_length": 50, "max_length": 500},
                        {"contains_keywords": ["purpose", "functionality"]}
                    ],
                    examples=[
                        "This API provides authentication services for the Terminal Grounds platform.",
                        "The user management system handles user registration, login, and profile management."
                    ]
                ),
                ContentGuidance(
                    section_name="Architecture",
                    description="System architecture and component relationships",
                    required=True,
                    suggested_content="Describe the system architecture, including components, data flow, and integration points.",
                    validation_rules=[
                        {"contains_sections": ["components", "data_flow"]},
                        {"min_length": 100}
                    ],
                    examples=[
                        "## Components\n- Authentication Service\n- User Database\n- API Gateway",
                        "## Data Flow\n1. User submits credentials\n2. Authentication service validates\n3. Token issued"
                    ]
                ),
                ContentGuidance(
                    section_name="API Reference",
                    description="Detailed API endpoint documentation",
                    required=False,
                    suggested_content="Document all API endpoints with parameters, responses, and examples.",
                    validation_rules=[
                        {"contains_code_blocks": True},
                        {"has_examples": True}
                    ],
                    examples=[
                        "### GET /api/users\nRetrieves user information.\n\n**Parameters:**\n- id: User ID\n\n**Response:**\n```json\n{\"id\": 1, \"name\": \"John\"}```"
                    ]
                )
            ],
            "design": [
                ContentGuidance(
                    section_name="Design Overview",
                    description="Overview of the design concept and goals",
                    required=True,
                    suggested_content="Describe the design concept, target audience, and design goals.",
                    validation_rules=[
                        {"min_length": 100},
                        {"contains_keywords": ["audience", "goals"]}
                    ],
                    examples=[
                        "This UI design targets casual gamers aged 18-35, focusing on intuitive navigation and engaging visuals."
                    ]
                ),
                ContentGuidance(
                    section_name="User Experience",
                    description="User experience design and user journey",
                    required=True,
                    suggested_content="Document the user experience, including user journeys, pain points, and design solutions.",
                    validation_rules=[
                        {"contains_sections": ["user_journey", "pain_points"]},
                        {"min_length": 150}
                    ],
                    examples=[
                        "## User Journey\n1. User discovers game\n2. Downloads and installs\n3. Creates account\n4. Starts first mission"
                    ]
                )
            ]
        }

        # Validation rules
        self.validation_rules = {
            "frontmatter": [
                {
                    "field": "title",
                    "required": True,
                    "type": "string",
                    "min_length": 5,
                    "max_length": 100
                },
                {
                    "field": "type",
                    "required": True,
                    "type": "enum",
                    "values": ["technical", "design", "process", "reference", "lore"]
                },
                {
                    "field": "domain",
                    "required": True,
                    "type": "enum",
                    "values": ["technical", "design", "art", "gameplay", "infrastructure"]
                },
                {
                    "field": "maintainer",
                    "required": True,
                    "type": "string",
                    "pattern": r"^[a-zA-Z\s]+$"
                }
            ],
            "content": [
                {
                    "rule": "heading_hierarchy",
                    "description": "Headings should follow proper hierarchy (H1 -> H2 -> H3)",
                    "severity": "warning"
                },
                {
                    "rule": "minimum_length",
                    "description": "Document should have substantial content",
                    "min_length": 500,
                    "severity": "warning"
                },
                {
                    "rule": "required_sections",
                    "description": "Document should have required sections based on type",
                    "severity": "error"
                }
            ]
        }

    def suggest_templates(self, document_context: DocumentContext) -> List[TemplateSuggestion]:
        """
        Suggest appropriate templates based on document context
        """
        suggestions = []

        # Get patterns for the document type
        patterns = self.template_patterns.get(document_context.document_type, {})

        for pattern in patterns.get("patterns", []):
            confidence = self._calculate_template_confidence(
                pattern, document_context
            )

            if confidence > 0.3:  # Only suggest if confidence is reasonable
                suggestion = TemplateSuggestion(
                    template_name=pattern["name"],
                    confidence_score=confidence,
                    reasoning=self._generate_template_reasoning(pattern, document_context),
                    domain=document_context.domain,
                    estimated_completion_time=self._estimate_completion_time(pattern),
                    required_fields=pattern.get("required_fields", []),
                    suggested_content=self._generate_suggested_content(pattern, document_context)
                )
                suggestions.append(suggestion)

        # Sort by confidence score
        suggestions.sort(key=lambda x: x.confidence_score, reverse=True)

        return suggestions[:5]  # Return top 5 suggestions

    def _calculate_template_confidence(self, pattern: Dict[str, Any],
                                    context: DocumentContext) -> float:
        """Calculate confidence score for template suggestion"""
        confidence = 0.0

        # Keyword matching
        pattern_keywords = set(pattern.get("keywords", []))
        context_keywords = set(context.keywords)

        if pattern_keywords and context_keywords:
            keyword_overlap = len(pattern_keywords.intersection(context_keywords))
            confidence += (keyword_overlap / len(pattern_keywords)) * 0.6

        # Domain matching
        if pattern.get("domain") == context.domain:
            confidence += 0.2

        # Document type matching
        if pattern.get("document_type") == context.document_type:
            confidence += 0.2

        # Apply confidence boost
        confidence *= pattern.get("confidence_boost", 1.0)

        return min(confidence, 1.0)

    def _generate_template_reasoning(self, pattern: Dict[str, Any],
                                   context: DocumentContext) -> str:
        """Generate reasoning for template suggestion"""
        reasons = []

        keywords = pattern.get("keywords", [])
        matching_keywords = [kw for kw in keywords if kw in context.keywords]

        if matching_keywords:
            reasons.append(f"Matches keywords: {', '.join(matching_keywords[:3])}")

        if pattern.get("domain") == context.domain:
            reasons.append(f"Suitable for {context.domain} domain")

        if reasons:
            return ". ".join(reasons)
        else:
            return f"General template suitable for {context.document_type} documents"

    def _estimate_completion_time(self, pattern: Dict[str, Any]) -> int:
        """Estimate completion time for template"""
        base_time = 30  # Base time in minutes
        field_count = len(pattern.get("required_fields", []))
        time_per_field = 5  # Minutes per field

        return base_time + (field_count * time_per_field)

    def _generate_suggested_content(self, pattern: Dict[str, Any],
                                  context: DocumentContext) -> Dict[str, Any]:
        """Generate suggested content structure"""
        return {
            "frontmatter": {
                "title": f"{pattern['name']} - {context.document_type.title()}",
                "type": context.document_type,
                "domain": context.domain,
                "status": "draft",
                "maintainer": "Documentation Team"
            },
            "sections": [
                "Overview",
                "Requirements",
                "Implementation",
                "Testing",
                "References"
            ]
        }

    def get_content_guidance(self, document_type: str, current_content: str = "") -> List[ContentGuidance]:
        """
        Get content structure guidance for document type
        """
        guidance = self.content_patterns.get(document_type, [])

        if current_content:
            # Analyze current content and provide targeted guidance
            guidance = self._prioritize_guidance(guidance, current_content)

        return guidance

    def _prioritize_guidance(self, guidance: List[ContentGuidance],
                           content: str) -> List[ContentGuidance]:
        """Prioritize guidance based on current content"""
        # Check which sections are already present
        present_sections = set()
        lines = content.split('\n')

        for line in lines:
            if line.strip().startswith('#'):
                section_name = line.strip('#').strip().lower()
                present_sections.add(section_name)

        # Prioritize missing required sections
        prioritized = []
        for guide in guidance:
            if guide.required and guide.section_name.lower() not in present_sections:
                prioritized.insert(0, guide)  # Add to front
            else:
                prioritized.append(guide)

        return prioritized

    def validate_content(self, content: str, document_type: str,
                        frontmatter: Dict[str, Any] = None) -> List[ValidationFeedback]:
        """
        Provide real-time validation feedback
        """
        feedback = []

        # Validate frontmatter
        if frontmatter:
            feedback.extend(self._validate_frontmatter(frontmatter))

        # Validate content structure
        feedback.extend(self._validate_content_structure(content, document_type))

        # Validate content quality
        feedback.extend(self._validate_content_quality(content))

        return feedback

    def _validate_frontmatter(self, frontmatter: Dict[str, Any]) -> List[ValidationFeedback]:
        """Validate frontmatter fields"""
        feedback = []

        rules = self.validation_rules.get("frontmatter", [])

        for rule in rules:
            field_name = rule["field"]
            field_value = frontmatter.get(field_name)

            # Check required fields
            if rule.get("required", False) and not field_value:
                feedback.append(ValidationFeedback(
                    field=field_name,
                    is_valid=False,
                    message=f"Required field '{field_name}' is missing",
                    severity="error",
                    suggestion=f"Add {field_name} to frontmatter"
                ))
                continue

            if field_value:
                # Type validation
                if rule.get("type") == "enum" and field_value not in rule.get("values", []):
                    feedback.append(ValidationFeedback(
                        field=field_name,
                        is_valid=False,
                        message=f"Invalid value for '{field_name}'. Must be one of: {', '.join(rule.get('values', []))}",
                        severity="error"
                    ))

                # Length validation
                if rule.get("min_length") and len(str(field_value)) < rule["min_length"]:
                    feedback.append(ValidationFeedback(
                        field=field_name,
                        is_valid=False,
                        message=f"Field '{field_name}' is too short (minimum {rule['min_length']} characters)",
                        severity="warning"
                    ))

                if rule.get("max_length") and len(str(field_value)) > rule["max_length"]:
                    feedback.append(ValidationFeedback(
                        field=field_name,
                        is_valid=False,
                        message=f"Field '{field_name}' is too long (maximum {rule['max_length']} characters)",
                        severity="warning"
                    ))

        return feedback

    def _validate_content_structure(self, content: str, document_type: str) -> List[ValidationFeedback]:
        """Validate content structure"""
        feedback = []

        lines = content.split('\n')
        headings = []

        # Extract headings
        for i, line in enumerate(lines):
            if line.strip().startswith('#'):
                level = len(line) - len(line.lstrip('#'))
                title = line.strip('#').strip()
                headings.append((level, title, i))

        # Check heading hierarchy
        prev_level = 0
        for level, title, line_num in headings:
            if level > prev_level + 1:
                feedback.append(ValidationFeedback(
                    field="content_structure",
                    is_valid=False,
                    message=f"Heading hierarchy violation at line {line_num + 1}: jumped from level {prev_level} to {level}",
                    severity="warning",
                    suggestion="Use proper heading hierarchy (H1 -> H2 -> H3)"
                ))
            prev_level = level

        # Check for required sections
        required_sections = []
        for guidance in self.content_patterns.get(document_type, []):
            if guidance.required:
                required_sections.append(guidance.section_name.lower())

        present_sections = {title.lower() for _, title, _ in headings}

        for required in required_sections:
            if required not in present_sections:
                feedback.append(ValidationFeedback(
                    field="content_structure",
                    is_valid=False,
                    message=f"Required section '{required}' is missing",
                    severity="error",
                    suggestion=f"Add a '{required}' section to your document"
                ))

        return feedback

    def _validate_content_quality(self, content: str) -> List[ValidationFeedback]:
        """Validate content quality"""
        feedback = []

        # Check minimum length
        word_count = len(content.split())
        if word_count < 100:
            feedback.append(ValidationFeedback(
                field="content_quality",
                is_valid=False,
                message=f"Document is too short ({word_count} words). Minimum recommended: 100 words",
                severity="warning",
                suggestion="Add more detailed content and examples"
            ))

        # Check for code blocks if technical content
        if "```" not in content and word_count > 200:
            feedback.append(ValidationFeedback(
                field="content_quality",
                is_valid=False,
                message="Consider adding code examples or technical details",
                severity="info",
                suggestion="Include code blocks or technical examples where appropriate"
            ))

        return feedback

    def get_context_suggestions(self, partial_content: str,
                              document_type: str) -> Dict[str, Any]:
        """
        Get context-aware suggestions for partial content
        """
        suggestions = {
            "next_sections": [],
            "field_suggestions": {},
            "content_examples": [],
            "validation_issues": []
        }

        # Analyze current content
        context = self.context_analyzer.analyze_content(partial_content)

        # Get guidance for next steps
        guidance = self.get_content_guidance(document_type, partial_content)

        # Suggest next sections
        present_sections = set()
        for line in partial_content.split('\n'):
            if line.strip().startswith('#'):
                section = line.strip('#').strip().lower()
                present_sections.add(section)

        for guide in guidance:
            if guide.section_name.lower() not in present_sections:
                suggestions["next_sections"].append({
                    "name": guide.section_name,
                    "description": guide.description,
                    "priority": "high" if guide.required else "medium"
                })

        # Suggest field values based on content
        if context.get("keywords"):
            suggestions["field_suggestions"]["tags"] = context["keywords"][:5]

        # Provide content examples
        for guide in guidance[:3]:  # Top 3 suggestions
            if guide.examples:
                suggestions["content_examples"].extend(guide.examples[:2])

        # Check for validation issues
        validation_feedback = self.validate_content(partial_content, document_type)
        suggestions["validation_issues"] = [
            {
                "field": fb.field,
                "message": fb.message,
                "severity": fb.severity,
                "suggestion": fb.suggestion
            }
            for fb in validation_feedback
        ]

        return suggestions

class ContextAnalyzer:
    """
    Analyzes document content to extract context and insights
    """

    def __init__(self, docs_root: str = "docs"):
        self.docs_root = Path(docs_root)
        self.stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
            'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
            'should', 'may', 'might', 'must', 'can', 'this', 'that', 'these',
            'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him',
            'her', 'us', 'them'
        }

    def analyze_content(self, content: str) -> Dict[str, Any]:
        """Analyze document content for context and insights"""
        # Extract keywords
        words = re.findall(r'\b\w+\b', content.lower())
        filtered_words = [word for word in words if word not in self.stop_words and len(word) > 2]

        keyword_counts = Counter(filtered_words)
        keywords = [word for word, count in keyword_counts.most_common(10) if count > 1]

        # Extract potential topics
        topics = self._extract_topics(content)

        # Estimate complexity
        complexity = self._estimate_complexity(content)

        # Find related documents (placeholder - would integrate with search)
        related_docs = []

        return {
            "keywords": keywords,
            "topics": topics,
            "complexity": complexity,
            "word_count": len(words),
            "sentence_count": len(re.split(r'[.!?]+', content)),
            "related_documents": related_docs
        }

    def _extract_topics(self, content: str) -> List[str]:
        """Extract potential topics from content"""
        topics = []

        # Look for technical terms
        tech_patterns = [
            r'\bAPI\b', r'\bdatabase\b', r'\bserver\b', r'\bclient\b',
            r'\bauthentication\b', r'\bauthorization\b', r'\bencryption\b',
            r'\bUI\b', r'\bUX\b', r'\bdesign\b', r'\bgameplay\b'
        ]

        for pattern in tech_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                topic = pattern.strip(r'\b').title()
                topics.append(topic)

        return topics[:5]

    def _estimate_complexity(self, content: str) -> str:
        """Estimate content complexity"""
        word_count = len(content.split())
        sentence_count = len(re.split(r'[.!?]+', content))
        avg_sentence_length = word_count / max(sentence_count, 1)

        # Technical terms indicator
        tech_terms = len(re.findall(r'\b(API|database|server|authentication|encryption|algorithm)\b', content, re.IGNORECASE))

        if word_count > 2000 or avg_sentence_length > 25 or tech_terms > 10:
            return "high"
        elif word_count > 500 or avg_sentence_length > 15 or tech_terms > 3:
            return "medium"
        else:
            return "low"

# Global assistant instance
intelligent_assistant = IntelligentAssistant()

def get_intelligent_assistant() -> IntelligentAssistant:
    """Get the global intelligent assistant instance"""
    return intelligent_assistant

if __name__ == "__main__":
    # Test the intelligent assistance system
    print("Testing Terminal Grounds Intelligent Assistance System")
    print("=" * 60)

    assistant = get_intelligent_assistant()

    # Test context analysis
    test_content = """
    This API provides user authentication services for the Terminal Grounds platform.
    It handles login, registration, and password reset functionality.
    The system uses JWT tokens for secure authentication.
    """

    context = assistant.context_analyzer.analyze_content(test_content)
    print("Content Analysis:")
    print(f"  Keywords: {context['keywords']}")
    print(f"  Topics: {context['topics']}")
    print(f"  Complexity: {context['complexity']}")

    # Test template suggestions
    doc_context = DocumentContext(
        document_type="technical",
        domain="technical",
        target_audience="developers",
        complexity_level="medium",
        keywords=["api", "authentication", "jwt"],
        related_documents=[],
        project_context={}
    )

    suggestions = assistant.suggest_templates(doc_context)
    print(f"\nTemplate Suggestions ({len(suggestions)}):")
    for suggestion in suggestions[:3]:
        print(f"  - {suggestion.template_name}: {suggestion.confidence_score:.2f} confidence")

    # Test content guidance
    guidance = assistant.get_content_guidance("technical", test_content)
    print(f"\nContent Guidance ({len(guidance)} items):")
    for guide in guidance[:3]:
        print(f"  - {guide.section_name}: {'Required' if guide.required else 'Optional'}")

    print("\nIntelligent assistance system operational!")
    print("Phase 4.1.1.2 Intelligent Assistance System ready for implementation.")
