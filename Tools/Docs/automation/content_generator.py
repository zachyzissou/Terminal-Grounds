"""
Terminal Grounds Documentation Automation Framework
Phase 4.0.2: Automated Content Generation

AI-powered content assistance for documentation creation and maintenance,
including frontmatter auto-population, cross-reference discovery, and quality enhancement.
"""

import os
import re
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass
from datetime import datetime
import logging
from collections import Counter

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class ContentAnalysis:
    """Analysis results for document content"""
    keywords: List[str]
    topics: List[str]
    entities: List[str]
    complexity_score: float
    readability_score: float
    suggested_tags: List[str]
    related_documents: List[str]

@dataclass
class FrontmatterSuggestion:
    """Suggestions for frontmatter fields"""
    title: Optional[str] = None
    type: Optional[str] = None
    domain: Optional[str] = None
    tags: Optional[List[str]] = None
    related_docs: Optional[List[str]] = None
    maintainer: Optional[str] = None

class ContentAnalyzer:
    """
    Analyzes document content to extract insights and generate suggestions
    """

    def __init__(self, docs_root: str = "../../docs"):
        self.docs_root = Path(docs_root)
        self.stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
            'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
            'should', 'may', 'might', 'must', 'can', 'this', 'that', 'these',
            'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him',
            'her', 'us', 'them', 'my', 'your', 'his', 'its', 'our', 'their'
        }

        # Domain-specific keywords
        self.domain_keywords = {
            'technical': ['api', 'function', 'class', 'method', 'module', 'library', 'framework', 'database', 'server', 'client', 'protocol', 'algorithm'],
            'design': ['ui', 'ux', 'interface', 'user', 'experience', 'visual', 'layout', 'color', 'typography', 'component', 'wireframe', 'mockup'],
            'lore': ['character', 'faction', 'region', 'event', 'history', 'world', 'universe', 'story', 'narrative', 'canon', 'myth', 'legend'],
            'art': ['texture', 'model', 'animation', 'render', 'shader', 'material', 'asset', 'sprite', 'particle', 'effect', 'lighting'],
            'process': ['workflow', 'procedure', 'step', 'guide', 'tutorial', 'how-to', 'best practice', 'standard', 'policy', 'methodology']
        }

    def analyze_content(self, content: str, filename: str = "") -> ContentAnalysis:
        """
        Analyze document content and extract insights
        """
        # Extract keywords
        keywords = self._extract_keywords(content)

        # Identify topics
        topics = self._identify_topics(content, keywords)

        # Extract entities (proper nouns, technical terms)
        entities = self._extract_entities(content)

        # Calculate complexity and readability
        complexity_score = self._calculate_complexity(content)
        readability_score = self._calculate_readability(content)

        # Generate tag suggestions
        suggested_tags = self._generate_tag_suggestions(keywords, topics, entities)

        # Find related documents
        related_documents = self._find_related_documents(keywords, topics, filename)

        return ContentAnalysis(
            keywords=keywords[:20],  # Top 20 keywords
            topics=topics,
            entities=entities[:10],  # Top 10 entities
            complexity_score=complexity_score,
            readability_score=readability_score,
            suggested_tags=suggested_tags,
            related_documents=related_documents
        )

    def _extract_keywords(self, content: str) -> List[str]:
        """Extract important keywords from content"""
        # Clean and tokenize content
        content = content.lower()
        content = re.sub(r'[^\w\s]', ' ', content)
        words = content.split()

        # Remove stop words and short words
        keywords = [word for word in words if len(word) > 3 and word not in self.stop_words]

        # Count frequency
        word_counts = Counter(keywords)

        # Return most common keywords
        return [word for word, count in word_counts.most_common(30)]

    def _identify_topics(self, content: str, keywords: List[str]) -> List[str]:
        """Identify main topics based on keywords and domain patterns"""
        topics = []

        # Check against domain keywords
        for domain, domain_words in self.domain_keywords.items():
            matches = set(keywords) & set(domain_words)
            if len(matches) >= 2:  # At least 2 matches indicate topic relevance
                topics.append(domain)

        # Extract topic-like phrases
        topic_patterns = [
            r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b',  # Title case phrases
            r'\b[a-z]+(?:-[a-z]+)+\b',  # Hyphenated terms
            r'\b[A-Z]{2,}\b'  # Acronyms
        ]

        for pattern in topic_patterns:
            matches = re.findall(pattern, content)
            topics.extend(matches[:5])  # Limit to 5 per pattern

        return list(set(topics))[:10]  # Remove duplicates and limit

    def _extract_entities(self, content: str) -> List[str]:
        """Extract named entities and technical terms"""
        entities = []

        # Extract proper nouns (capitalized words)
        proper_nouns = re.findall(r'\b[A-Z][a-z]+\b', content)
        entities.extend(proper_nouns)

        # Extract technical terms (camelCase, PascalCase)
        technical_terms = re.findall(r'\b[a-z]+[A-Z][a-zA-Z]*\b', content)
        entities.extend(technical_terms)

        # Extract acronyms
        acronyms = re.findall(r'\b[A-Z]{2,}\b', content)
        entities.extend(acronyms)

        # Remove duplicates and common words
        entities = list(set(entities))
        entities = [e for e in entities if len(e) > 2 and e.lower() not in self.stop_words]

        return entities

    def _calculate_complexity(self, content: str) -> float:
        """Calculate content complexity score"""
        sentences = re.split(r'[.!?]+', content)
        words = content.split()

        if not sentences or not words:
            return 0.0

        avg_sentence_length = len(words) / len(sentences)
        avg_word_length = sum(len(word) for word in words) / len(words)

        # Complexity factors
        factors = {
            'sentence_length': min(avg_sentence_length / 20, 1.0),  # Normalize to 0-1
            'word_length': min(avg_word_length / 8, 1.0),  # Normalize to 0-1
            'vocabulary_richness': len(set(words)) / len(words) if words else 0
        }

        # Weighted complexity score
        complexity = (
            factors['sentence_length'] * 0.4 +
            factors['word_length'] * 0.3 +
            factors['vocabulary_richness'] * 0.3
        )

        return round(complexity, 2)

    def _calculate_readability(self, content: str) -> float:
        """Calculate readability score (simplified Flesch reading ease)"""
        sentences = re.split(r'[.!?]+', content)
        words = content.split()
        syllables = sum(self._count_syllables(word) for word in words)

        if not sentences or not words:
            return 0.0

        # Simplified Flesch formula
        readability = 206.835 - 1.015 * (len(words) / len(sentences)) - 84.6 * (syllables / len(words))

        # Normalize to 0-1 scale (Flesch scores typically 0-100)
        normalized_readability = max(0, min(1, readability / 100))

        return round(normalized_readability, 2)

    def _count_syllables(self, word: str) -> int:
        """Count syllables in a word (simplified)"""
        word = word.lower()
        count = 0
        vowels = "aeiouy"

        if word[0] in vowels:
            count += 1

        for i in range(1, len(word)):
            if word[i] in vowels and word[i - 1] not in vowels:
                count += 1

        if word.endswith("e"):
            count -= 1

        return max(1, count)

    def _generate_tag_suggestions(self, keywords: List[str], topics: List[str], entities: List[str]) -> List[str]:
        """Generate tag suggestions based on content analysis"""
        tags = []

        # Add domain-relevant keywords as tags
        for keyword in keywords[:10]:  # Top 10 keywords
            if len(keyword) > 3 and keyword not in self.stop_words:
                tags.append(keyword)

        # Add topics as tags
        tags.extend(topics[:5])  # Top 5 topics

        # Add important entities as tags
        tags.extend(entities[:3])  # Top 3 entities

        # Remove duplicates and clean
        tags = list(set(tags))
        tags = [tag.lower().replace(' ', '-') for tag in tags if len(tag) > 2]

        return tags[:15]  # Limit to 15 tags

    def _find_related_documents(self, keywords: List[str], topics: List[str], current_filename: str = "") -> List[str]:
        """Find related documents based on content similarity"""
        related_docs = []

        # This would be more sophisticated in production
        # For now, return some placeholder suggestions
        if 'api' in keywords:
            related_docs.append("API_REFERENCE.md")
        if 'design' in topics:
            related_docs.append("DESIGN_GUIDELINES.md")
        if 'process' in topics:
            related_docs.append("WORKFLOW_GUIDE.md")

        return related_docs[:5]

class FrontmatterAutoPopulator:
    """
    Automatically suggests and populates frontmatter fields
    """

    def __init__(self, content_analyzer: ContentAnalyzer):
        self.content_analyzer = content_analyzer

    def generate_suggestions(self, content: str, filename: str = "", existing_frontmatter: Optional[Dict[str, Any]] = None) -> FrontmatterSuggestion:
        """
        Generate frontmatter suggestions based on content analysis
        """
        # Analyze content
        analysis = self.content_analyzer.analyze_content(content, filename)

        suggestions = FrontmatterSuggestion()

        # Suggest title if not present
        if not existing_frontmatter or 'title' not in existing_frontmatter:
            suggestions.title = self._suggest_title(content, filename)

        # Suggest type based on content patterns
        if not existing_frontmatter or 'type' not in existing_frontmatter:
            suggestions.type = self._suggest_type(analysis)

        # Suggest domain based on keywords and topics
        if not existing_frontmatter or 'domain' not in existing_frontmatter:
            suggestions.domain = self._suggest_domain(analysis)

        # Suggest tags
        if not existing_frontmatter or 'tags' not in existing_frontmatter or not existing_frontmatter['tags']:
            suggestions.tags = analysis.suggested_tags

        # Suggest related documents
        if not existing_frontmatter or 'related_docs' not in existing_frontmatter or not existing_frontmatter['related_docs']:
            suggestions.related_docs = analysis.related_documents

        # Suggest maintainer (could be enhanced with team analysis)
        if not existing_frontmatter or 'maintainer' not in existing_frontmatter:
            suggestions.maintainer = "Documentation Team"

        return suggestions

    def _suggest_title(self, content: str, filename: str) -> str:
        """Suggest a title based on content and filename"""
        # Try to extract from first heading
        heading_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        if heading_match:
            return heading_match.group(1).strip()

        # Fallback to filename
        if filename:
            name = Path(filename).stem.replace('_', ' ').replace('-', ' ').title()
            return name

        return "Document Title"

    def _suggest_type(self, analysis: ContentAnalysis) -> str:
        """Suggest document type based on content analysis"""
        # Type indicators
        type_indicators = {
            'guide': ['tutorial', 'how-to', 'step-by-step', 'guide', 'walkthrough'],
            'reference': ['api', 'reference', 'documentation', 'specification', 'manual'],
            'process': ['workflow', 'process', 'procedure', 'methodology', 'standard'],
            'spec': ['specification', 'requirements', 'design', 'architecture']
        }

        # Check keywords and topics for type indicators
        all_terms = set(analysis.keywords + analysis.topics)

        for doc_type, indicators in type_indicators.items():
            if any(indicator in term.lower() for term in all_terms for indicator in indicators):
                return doc_type

        return 'reference'  # Default type

    def _suggest_domain(self, analysis: ContentAnalysis) -> str:
        """Suggest domain based on content analysis"""
        # Count domain keyword matches
        domain_scores = {}

        for domain, keywords in self.content_analyzer.domain_keywords.items():
            matches = set(analysis.keywords) & set(keywords)
            domain_scores[domain] = len(matches)

        # Return domain with highest score
        if domain_scores:
            best_domain = max(domain_scores, key=domain_scores.get)
            if domain_scores[best_domain] >= 2:  # At least 2 matches
                return best_domain

        return 'technical'  # Default domain

class QualityEnhancer:
    """
    Enhances document quality through automated proofreading and suggestions
    """

    def __init__(self):
        self.common_issues = {
            'spelling': [],
            'grammar': [],
            'style': []
        }

    def enhance_quality(self, content: str) -> Dict[str, Any]:
        """
        Analyze and suggest quality improvements
        """
        issues = []
        suggestions = []

        # Check for common issues
        lines = content.split('\n')

        for i, line in enumerate(lines, 1):
            # Check for trailing whitespace
            if line.rstrip() != line:
                issues.append({
                    'type': 'style',
                    'line': i,
                    'message': 'Trailing whitespace found',
                    'suggestion': 'Remove trailing spaces'
                })

            # Check for multiple consecutive blank lines
            if i > 1 and not line.strip() and not lines[i-2].strip():
                issues.append({
                    'type': 'style',
                    'line': i,
                    'message': 'Multiple consecutive blank lines',
                    'suggestion': 'Use single blank line between sections'
                })

            # Check for inconsistent heading styles
            if line.startswith('#'):
                heading_level = len(line) - len(line.lstrip('#'))
                if heading_level > 6:
                    issues.append({
                        'type': 'style',
                        'line': i,
                        'message': f'Heading level {heading_level} is too deep',
                        'suggestion': 'Use heading levels 1-6 only'
                    })

        # Generate quality score
        quality_score = self._calculate_quality_score(content, issues)

        return {
            'issues': issues,
            'suggestions': suggestions,
            'quality_score': quality_score,
            'improvement_areas': self._identify_improvement_areas(content)
        }

    def _calculate_quality_score(self, content: str, issues: List[Dict[str, Any]]) -> float:
        """Calculate overall quality score"""
        base_score = 100

        # Deduct points for issues
        issue_penalties = {
            'style': 2,
            'grammar': 5,
            'spelling': 3
        }

        for issue in issues:
            penalty = issue_penalties.get(issue['type'], 1)
            base_score -= penalty

        # Bonus for good practices
        if '---' in content[:500]:  # Has frontmatter
            base_score += 5

        if re.search(r'^# .+', content, re.MULTILINE):  # Has title
            base_score += 5

        # Normalize to 0-100
        return max(0, min(100, base_score))

    def _identify_improvement_areas(self, content: str) -> List[str]:
        """Identify areas for improvement"""
        areas = []

        # Check content length
        word_count = len(content.split())
        if word_count < 100:
            areas.append("Content appears brief - consider adding more detail")
        elif word_count > 2000:
            areas.append("Content is quite long - consider breaking into sections")

        # Check for code blocks
        if '```' in content:
            areas.append("Good: Includes code examples")
        else:
            areas.append("Consider adding code examples or illustrations")

        # Check for lists
        if re.search(r'^[-*+]\s', content, re.MULTILINE):
            areas.append("Good: Uses lists for organization")

        # Check for links
        if '[' in content and ']' in content:
            areas.append("Good: Includes references or links")

        return areas

class AutomatedContentGenerator:
    """
    Main interface for automated content generation and enhancement
    """

    def __init__(self, docs_root: str = "../../docs"):
        self.content_analyzer = ContentAnalyzer(docs_root)
        self.frontmatter_populator = FrontmatterAutoPopulator(self.content_analyzer)
        self.quality_enhancer = QualityEnhancer()

    def process_document(self, content: str, filename: str = "", existing_frontmatter: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Process a document and generate comprehensive suggestions
        """
        # Analyze content
        analysis = self.content_analyzer.analyze_content(content, filename)

        # Generate frontmatter suggestions
        frontmatter_suggestions = self.frontmatter_populator.generate_suggestions(
            content, filename, existing_frontmatter
        )

        # Enhance quality
        quality_report = self.quality_enhancer.enhance_quality(content)

        # Generate comprehensive report
        report = {
            'analysis': {
                'keywords': analysis.keywords,
                'topics': analysis.topics,
                'entities': analysis.entities,
                'complexity_score': analysis.complexity_score,
                'readability_score': analysis.readability_score
            },
            'frontmatter_suggestions': {
                'title': frontmatter_suggestions.title,
                'type': frontmatter_suggestions.type,
                'domain': frontmatter_suggestions.domain,
                'tags': frontmatter_suggestions.tags,
                'related_docs': frontmatter_suggestions.related_docs,
                'maintainer': frontmatter_suggestions.maintainer
            },
            'quality_report': quality_report,
            'content_insights': {
                'word_count': len(content.split()),
                'sentence_count': len(re.split(r'[.!?]+', content)),
                'paragraph_count': len([p for p in content.split('\n\n') if p.strip()]),
                'has_frontmatter': '---' in content[:500],
                'has_headings': bool(re.search(r'^#', content, re.MULTILINE))
            }
        }

        return report

    def generate_document_template(self, domain: str, doc_type: str, title: str) -> str:
        """
        Generate a complete document template with suggested content
        """
        # Generate frontmatter
        frontmatter = {
            'title': title,
            'type': doc_type,
            'domain': domain,
            'status': 'draft',
            'last_reviewed': datetime.now().strftime('%Y-%m-%d'),
            'maintainer': 'Documentation Team',
            'tags': [domain, doc_type],
            'related_docs': []
        }

        # Generate basic content structure
        content_structure = self._get_content_structure(doc_type)

        # Create document
        frontmatter_yaml = yaml.dump(frontmatter, default_flow_style=False, sort_keys=False)
        document = f"---\n{frontmatter_yaml}---\n\n{content_structure}"

        return document

    def _get_content_structure(self, doc_type: str) -> str:
        """Get basic content structure for document type"""
        structures = {
            'guide': f"""# {doc_type.title()} Guide

## Overview

Brief description of what this guide covers.

## Prerequisites

What readers should know or have before starting.

## Steps

1. First step
2. Second step
3. Continue with detailed steps...

## Examples

```bash
# Example command or code
echo "Hello, World!"
```

## Troubleshooting

Common issues and solutions.

## Next Steps

What to do after completing this guide.
""",
            'reference': f"""# {doc_type.title()} Reference

## Overview

Comprehensive reference for [topic].

## API Reference

### Functions

#### `function_name(parameters)`
Description of the function.

**Parameters:**
- `param1` (type): Description
- `param2` (type): Description

**Returns:** Return type and description

**Example:**
```python
result = function_name("example")
```

## Data Structures

### ClassName
Description of the class.

**Properties:**
- `property1` (type): Description
- `property2` (type): Description

## Examples

See [Examples](#examples) section.

## See Also

- Related documentation
- External references
""",
            'process': f"""# {doc_type.title()} Process

## Overview

Description of this process and its purpose.

## Process Flow

1. **Step 1:** Description
   - Sub-step details
   - Required inputs
   - Expected outputs

2. **Step 2:** Description
   - Continue with process steps...

## Roles & Responsibilities

### Role 1
- Responsibility description
- Required skills
- Time commitment

### Role 2
- Responsibility description
- Required skills
- Time commitment

## Checklist

- [ ] Prerequisite verification
- [ ] Process step 1 completion
- [ ] Process step 2 completion
- [ ] Quality assurance
- [ ] Documentation update

## Metrics

How to measure process success.

## Continuous Improvement

Areas for process optimization.
"""
        }

        return structures.get(doc_type, f"""# {doc_type.title()} Document

## Overview

Document overview and purpose.

## Details

Detailed content goes here.

## Examples

Code examples or illustrations.

## References

Related documentation and resources.
""")

def main():
    """Main function for automated content generation demonstration"""
    print("Terminal Grounds Automated Content Generation")
    print("=" * 55)

    # Initialize system
    generator = AutomatedContentGenerator()

    # Example document processing
    sample_content = """
# API Documentation Guide

This guide covers how to document APIs effectively.

## Best Practices

1. Use clear, descriptive names
2. Include examples for all endpoints
3. Document error responses
4. Keep documentation up to date

## Tools

- Swagger/OpenAPI for specification
- Postman for testing
- ReadMe for hosting documentation

## Example

```javascript
// GET /api/users
app.get('/api/users', (req, res) => {
  res.json({ users: [] });
});
```
"""

    print("Processing sample document...")
    report = generator.process_document(sample_content, "api_guide.md")

    print(f"\n📊 Content Analysis:")
    print(f"  Keywords: {', '.join(report['analysis']['keywords'][:5])}")
    print(f"  Topics: {', '.join(report['analysis']['topics'][:3])}")
    print(f"  Complexity Score: {report['analysis']['complexity_score']}")
    print(f"  Readability Score: {report['analysis']['readability_score']}")

    print(f"\n📝 Frontmatter Suggestions:")
    for field, value in report['frontmatter_suggestions'].items():
        if value:
            if isinstance(value, list):
                print(f"  {field}: {', '.join(value[:3])}")
            else:
                print(f"  {field}: {value}")

    print(f"\n⭐ Quality Report:")
    print(f"  Quality Score: {report['quality_report']['quality_score']}/100")
    print(f"  Issues Found: {len(report['quality_report']['issues'])}")
    print(f"  Improvement Areas: {len(report['quality_report']['improvement_areas'])}")

    print(f"\n📄 Content Insights:")
    for key, value in report['content_insights'].items():
        print(f"  {key.replace('_', ' ').title()}: {value}")

    # Generate a sample document
    print(f"\n🔧 Generating Sample Document...")
    sample_doc = generator.generate_document_template("technical", "guide", "New API Guide")
    print("Generated document template:")
    print("-" * 40)
    print(sample_doc[:500] + "..." if len(sample_doc) > 500 else sample_doc)

    print("\n✅ Automated Content Generation operational!")
    print("Phase 4.0.2: Automated Content Generation complete!")

if __name__ == "__main__":
    main()
