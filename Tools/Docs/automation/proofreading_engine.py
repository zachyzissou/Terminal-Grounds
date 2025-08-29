"""
Terminal Grounds Documentation Automation Framework
Phase 4.1.2.1: Automated Proofreading Engine

Comprehensive automated proofreading system for grammar, style, readability,
and tone consistency validation in documentation.
"""

import os
import re
import string
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Set
from dataclasses import dataclass
from datetime import datetime
import logging
import yaml

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class ProofreadingIssue:
    """Represents a proofreading issue found in text"""
    issue_type: str  # 'grammar', 'style', 'readability', 'tone'
    severity: str    # 'error', 'warning', 'suggestion'
    line_number: int
    column_start: int
    column_end: int
    text: str
    suggestion: str
    explanation: str
    rule_id: str

@dataclass
class ProofreadingResult:
    """Result of proofreading analysis"""
    total_issues: int
    errors: List[ProofreadingIssue]
    warnings: List[ProofreadingIssue]
    suggestions: List[ProofreadingIssue]
    readability_score: float
    grade_level: float
    tone_consistency_score: float
    overall_quality_score: float

@dataclass
class StyleGuideRule:
    """Represents a style guide rule"""
    rule_id: str
    category: str
    description: str
    pattern: str
    suggestion: str
    severity: str
    examples: List[str]

class GrammarValidator:
    """
    Grammar validation engine
    """

    def __init__(self):
        self.common_errors = {
            r'\b(i|we|they|you)\s+(is|are|was|were)\s+not\b': {
                'suggestion': "Use contraction: {word}n't",
                'explanation': "Use contractions for better readability"
            },
            r'\b(can|will|shall|must|should|would|could)\s+not\b': {
                'suggestion': "Use contraction: {word}n't",
                'explanation': "Use contractions for better readability"
            },
            r'\b(it|that|this|these|those)\s+is\s+not\b': {
                'suggestion': "Use contraction: {word}'s not or {word} isn't",
                'explanation': "Use contractions for better readability"
            },
            r'\b(who|what|where|when|why|how)\s+is\s+not\b': {
                'suggestion': "Use contraction: {word} isn't",
                'explanation': "Use contractions for better readability"
            },
            r'\b(a|an)\s+(unique|universal|unanimous|unilateral)\b': {
                'suggestion': "Use 'a' before consonant sounds, 'an' before vowel sounds",
                'explanation': "Incorrect article usage"
            },
            r'\b(an)\s+(historic|historical|hotel|hospital)\b': {
                'suggestion': "Use 'a' before consonant sounds",
                'explanation': "Incorrect article usage"
            }
        }

        self.passive_voice_patterns = [
            r'\b(is|are|was|were|be|been|being)\s+(\w+ed|\w+en)\b',
            r'\b(has|have|had)\s+been\s+(\w+ed|\w+en)\b'
        ]

    def validate_grammar(self, text: str, line_offset: int = 0) -> List[ProofreadingIssue]:
        """
        Validate grammar in text
        """
        issues = []

        lines = text.split('\n')

        for line_num, line in enumerate(lines, 1):
            # Check common grammar errors
            for pattern, rule in self.common_errors.items():
                matches = re.finditer(pattern, line, re.IGNORECASE)
                for match in matches:
                    issues.append(ProofreadingIssue(
                        issue_type='grammar',
                        severity=rule.get('severity', 'warning'),
                        line_number=line_num + line_offset,
                        column_start=match.start(),
                        column_end=match.end(),
                        text=match.group(),
                        suggestion=rule['suggestion'].format(word=match.group(1)),
                        explanation=rule['explanation'],
                        rule_id=f"grammar_{pattern.replace('\\\\', '').replace('b', '')}"
                    ))

            # Check for passive voice (warning, not error)
            for pattern in self.passive_voice_patterns:
                matches = re.finditer(pattern, line, re.IGNORECASE)
                for match in matches:
                    issues.append(ProofreadingIssue(
                        issue_type='style',
                        severity='suggestion',
                        line_number=line_num + line_offset,
                        column_start=match.start(),
                        column_end=match.end(),
                        text=match.group(),
                        suggestion="Consider using active voice",
                        explanation="Passive voice can make writing less engaging",
                        rule_id="passive_voice"
                    ))

        return issues

class StyleValidator:
    """
    Style and consistency validation engine
    """

    def __init__(self):
        self.style_rules = self._load_style_rules()

    def _load_style_rules(self) -> List[StyleGuideRule]:
        """Load style guide rules"""
        return [
            StyleGuideRule(
                rule_id="heading_case",
                category="formatting",
                description="Use sentence case for headings",
                pattern=r'^#{1,6}\s+[A-Z][^A-Z]*$',
                suggestion="Use sentence case: capitalize first word and proper nouns only",
                severity="warning",
                examples=["# This Is Wrong", "# This is correct"]
            ),
            StyleGuideRule(
                rule_id="multiple_spaces",
                category="formatting",
                description="Avoid multiple consecutive spaces",
                pattern=r'\s{2,}',
                suggestion="Use single space between words",
                severity="warning",
                examples=["word1  word2", "word1 word2"]
            ),
            StyleGuideRule(
                rule_id="trailing_space",
                category="formatting",
                description="Remove trailing whitespace",
                pattern=r'\s+$',
                suggestion="Remove trailing spaces",
                severity="warning",
                examples=["text ", "text"]
            ),
            StyleGuideRule(
                rule_id="oxford_comma",
                category="punctuation",
                description="Use Oxford comma in lists",
                pattern=r'\b(and|or)\s+\w+\s*,?\s*\w+\s*$',
                suggestion="Use Oxford comma: item1, item2, and item3",
                severity="suggestion",
                examples=["apples, oranges and bananas", "apples, oranges, and bananas"]
            ),
            StyleGuideRule(
                rule_id="first_person",
                category="voice",
                description="Avoid first person in technical documentation",
                pattern=r'\b(I|we|our|us|my)\b',
                suggestion="Use second person or passive voice",
                severity="suggestion",
                examples=["I recommend using", "It is recommended to use"]
            )
        ]

    def validate_style(self, text: str, line_offset: int = 0) -> List[ProofreadingIssue]:
        """
        Validate style consistency
        """
        issues = []
        lines = text.split('\n')

        for line_num, line in enumerate(lines, 1):
            for rule in self.style_rules:
                matches = re.finditer(rule.pattern, line)
                for match in matches:
                    issues.append(ProofreadingIssue(
                        issue_type='style',
                        severity=rule.severity,
                        line_number=line_num + line_offset,
                        column_start=match.start(),
                        column_end=match.end(),
                        text=match.group(),
                        suggestion=rule.suggestion,
                        explanation=rule.description,
                        rule_id=rule.rule_id
                    ))

        return issues

class ReadabilityAnalyzer:
    """
    Readability and complexity analysis engine
    """

    def __init__(self):
        self.syllable_words = self._load_syllable_dictionary()

    def _load_syllable_dictionary(self) -> Dict[str, int]:
        """Load syllable count dictionary for common words"""
        return {
            'the': 1, 'a': 1, 'an': 1, 'and': 1, 'or': 1, 'but': 1, 'in': 1, 'on': 1, 'at': 1, 'to': 1, 'for': 1, 'of': 1, 'with': 1, 'by': 1,
            'documentation': 5, 'implementation': 6, 'configuration': 6, 'development': 5, 'application': 5, 'functionality': 6,
            'requirements': 4, 'specifications': 5, 'architecture': 5, 'integration': 5, 'validation': 5, 'automation': 5
        }

    def analyze_readability(self, text: str) -> Tuple[float, float]:
        """
        Analyze text readability using Flesch-Kincaid metrics
        Returns: (readability_score, grade_level)
        """
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]

        if not sentences:
            return 0.0, 0.0

        total_words = 0
        total_syllables = 0
        total_sentences = len(sentences)

        for sentence in sentences:
            words = re.findall(r'\b\w+\b', sentence)
            total_words += len(words)

            for word in words:
                word_lower = word.lower()
                if word_lower in self.syllable_words:
                    total_syllables += self.syllable_words[word_lower]
                else:
                    # Estimate syllables for unknown words
                    total_syllables += max(1, len(re.findall(r'[aeiouy]+', word_lower)))

        if total_words == 0 or total_sentences == 0:
            return 0.0, 0.0

        # Flesch Reading Ease Score
        readability_score = 206.835 - 1.015 * (total_words / total_sentences) - 84.6 * (total_syllables / total_words)

        # Flesch-Kincaid Grade Level
        grade_level = 0.39 * (total_words / total_sentences) + 11.8 * (total_syllables / total_words) - 15.59

        return max(0, min(100, readability_score)), max(0, grade_level)

    def get_readability_issues(self, text: str, readability_score: float,
                             grade_level: float, line_offset: int = 0) -> List[ProofreadingIssue]:
        """
        Generate readability-related issues
        """
        issues = []

        # Check readability score
        if readability_score < 30:
            issues.append(ProofreadingIssue(
                issue_type='readability',
                severity='warning',
                line_number=1,
                column_start=0,
                column_end=len(text.split('\n')[0]) if text.split('\n') else 0,
                text="Low readability score",
                suggestion="Simplify language and sentence structure",
                explanation=f"Readability score is {readability_score:.1f}/100. Aim for 60+ for general audience",
                rule_id="readability_score"
            ))

        # Check grade level
        if grade_level > 12:
            issues.append(ProofreadingIssue(
                issue_type='readability',
                severity='warning',
                line_number=1,
                column_start=0,
                column_end=len(text.split('\n')[0]) if text.split('\n') else 0,
                text="High grade level",
                suggestion="Use simpler words and shorter sentences",
                explanation=f"Grade level is {grade_level:.1f}. Consider grade 8-10 for technical documentation",
                rule_id="grade_level"
            ))

        # Check for long sentences
        sentences = re.split(r'[.!?]+', text)
        for i, sentence in enumerate(sentences):
            words = re.findall(r'\b\w+\b', sentence)
            if len(words) > 25:
                issues.append(ProofreadingIssue(
                    issue_type='readability',
                    severity='suggestion',
                    line_number=i + 1,
                    column_start=0,
                    column_end=len(sentence),
                    text=f"Long sentence ({len(words)} words)",
                    suggestion="Break into shorter sentences",
                    explanation="Sentences over 25 words are hard to read",
                    rule_id="long_sentence"
                ))

        return issues

class ToneConsistencyAnalyzer:
    """
    Tone and voice consistency analysis
    """

    def __init__(self):
        self.formal_indicators = {
            'words': {'utilize', 'implement', 'facilitate', 'leverage', 'optimize', 'streamline'},
            'phrases': {'it is recommended', 'please note', 'important to note', 'should be noted'}
        }

        self.informal_indicators = {
            'words': {'stuff', 'thing', 'like', 'really', 'just', 'okay', 'cool'},
            'contractions': {'don\'t', 'can\'t', 'won\'t', 'shouldn\'t', 'wouldn\'t'}
        }

    def analyze_tone_consistency(self, text: str) -> float:
        """
        Analyze tone consistency (0.0 = inconsistent, 1.0 = consistent)
        """
        formal_score = 0
        informal_score = 0

        words = re.findall(r'\b\w+\b', text.lower())

        # Count formal indicators
        for word in words:
            if word in self.formal_indicators['words']:
                formal_score += 1

        # Count informal indicators
        for word in words:
            if word in self.informal_indicators['words']:
                informal_score += 1

        # Count contractions
        contractions = len(re.findall(r'\b\w+\'\w+\b', text))
        informal_score += contractions

        # Count formal phrases
        for phrase in self.formal_indicators['phrases']:
            formal_score += text.lower().count(phrase)

        total_indicators = formal_score + informal_score

        if total_indicators == 0:
            return 1.0  # Neutral is considered consistent

        # Calculate consistency (lower mixed indicators = higher consistency)
        if formal_score > informal_score:
            consistency = 1 - (informal_score / total_indicators)
        else:
            consistency = 1 - (formal_score / total_indicators)

        return max(0.0, min(1.0, consistency))

    def get_tone_issues(self, text: str, consistency_score: float,
                       line_offset: int = 0) -> List[ProofreadingIssue]:
        """
        Generate tone consistency issues
        """
        issues = []

        if consistency_score < 0.7:
            issues.append(ProofreadingIssue(
                issue_type='tone',
                severity='warning',
                line_number=1,
                column_start=0,
                column_end=len(text.split('\n')[0]) if text.split('\n') else 0,
                text="Inconsistent tone",
                suggestion="Maintain consistent formal or informal tone throughout",
                explanation=f"Tone consistency score: {consistency_score:.2f}/1.0",
                rule_id="tone_consistency"
            ))

        return issues

class AutomatedProofreadingEngine:
    """
    Complete automated proofreading system
    """

    def __init__(self):
        self.grammar_validator = GrammarValidator()
        self.style_validator = StyleValidator()
        self.readability_analyzer = ReadabilityAnalyzer()
        self.tone_analyzer = ToneConsistencyAnalyzer()

        logger.info("Automated Proofreading Engine initialized")

    def proofread_text(self, text: str, line_offset: int = 0) -> ProofreadingResult:
        """
        Complete proofreading analysis of text
        """
        all_issues = []

        # Grammar validation
        grammar_issues = self.grammar_validator.validate_grammar(text, line_offset)
        all_issues.extend(grammar_issues)

        # Style validation
        style_issues = self.style_validator.validate_style(text, line_offset)
        all_issues.extend(style_issues)

        # Readability analysis
        readability_score, grade_level = self.readability_analyzer.analyze_readability(text)
        readability_issues = self.readability_analyzer.get_readability_issues(
            text, readability_score, grade_level, line_offset
        )
        all_issues.extend(readability_issues)

        # Tone consistency analysis
        tone_consistency_score = self.tone_analyzer.analyze_tone_consistency(text)
        tone_issues = self.tone_analyzer.get_tone_issues(
            text, tone_consistency_score, line_offset
        )
        all_issues.extend(tone_issues)

        # Categorize issues
        errors = [issue for issue in all_issues if issue.severity == 'error']
        warnings = [issue for issue in all_issues if issue.severity == 'warning']
        suggestions = [issue for issue in all_issues if issue.severity == 'suggestion']

        # Calculate overall quality score
        overall_quality_score = self._calculate_overall_quality_score(
            errors, warnings, suggestions, readability_score, tone_consistency_score
        )

        return ProofreadingResult(
            total_issues=len(all_issues),
            errors=errors,
            warnings=warnings,
            suggestions=suggestions,
            readability_score=readability_score,
            grade_level=grade_level,
            tone_consistency_score=tone_consistency_score,
            overall_quality_score=overall_quality_score
        )

    def _calculate_overall_quality_score(self, errors: List[ProofreadingIssue],
                                       warnings: List[ProofreadingIssue],
                                       suggestions: List[ProofreadingIssue],
                                       readability_score: float,
                                       tone_consistency_score: float) -> float:
        """
        Calculate overall quality score (0-100)
        """
        # Base score from readability (weighted 40%)
        readability_component = (readability_score / 100) * 40

        # Tone consistency (weighted 20%)
        tone_component = tone_consistency_score * 20

        # Issue penalties (weighted 40%)
        total_issues = len(errors) + len(warnings) + len(suggestions)
        issue_penalty = min(40, total_issues * 2)  # Max 40 point penalty

        quality_score = readability_component + tone_component + (40 - issue_penalty)

        return max(0.0, min(100.0, quality_score))

    def proofread_document(self, doc_path: str) -> Tuple[Optional[ProofreadingResult], Optional[str]]:
        """
        Proofread a markdown document
        """
        try:
            with open(doc_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Extract body content (skip frontmatter)
            if content.startswith('---'):
                parts = content.split('---', 2)
                if len(parts) >= 3:
                    body_content = parts[2].strip()
                else:
                    body_content = content
            else:
                body_content = content

            result = self.proofread_text(body_content)

            return result, None

        except Exception as e:
            logger.error(f"Error proofreading document {doc_path}: {e}")
            return None, str(e)

    def get_proofreading_summary(self, result: ProofreadingResult) -> Dict[str, Any]:
        """
        Get summary of proofreading results
        """
        return {
            "total_issues": result.total_issues,
            "errors_count": len(result.errors),
            "warnings_count": len(result.warnings),
            "suggestions_count": len(result.suggestions),
            "readability_score": result.readability_score,
            "grade_level": result.grade_level,
            "tone_consistency_score": result.tone_consistency_score,
            "overall_quality_score": result.overall_quality_score,
            "quality_grade": self._get_quality_grade(result.overall_quality_score),
            "issues_by_type": {
                "grammar": len([i for i in result.errors + result.warnings + result.suggestions
                               if i.issue_type == 'grammar']),
                "style": len([i for i in result.errors + result.warnings + result.suggestions
                             if i.issue_type == 'style']),
                "readability": len([i for i in result.errors + result.warnings + result.suggestions
                                   if i.issue_type == 'readability']),
                "tone": len([i for i in result.errors + result.warnings + result.suggestions
                            if i.issue_type == 'tone'])
            }
        }

    def _get_quality_grade(self, score: float) -> str:
        """Convert quality score to letter grade"""
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

    def generate_correction_suggestions(self, result: ProofreadingResult) -> List[Dict[str, Any]]:
        """
        Generate actionable correction suggestions
        """
        suggestions = []

        # Group issues by type and severity
        issue_groups = {}
        for issue in result.errors + result.warnings + result.suggestions:
            key = (issue.issue_type, issue.severity)
            if key not in issue_groups:
                issue_groups[key] = []
            issue_groups[key].append(issue)

        # Generate suggestions for each group
        for (issue_type, severity), issues in issue_groups.items():
            suggestions.append({
                "category": f"{issue_type}_{severity}",
                "count": len(issues),
                "description": f"Address {len(issues)} {severity} {issue_type} issues",
                "priority": "high" if severity == "error" else "medium" if severity == "warning" else "low",
                "examples": [issue.text for issue in issues[:3]],  # Show first 3 examples
                "action_items": self._get_action_items_for_issue_type(issue_type, severity)
            })

        return suggestions

    def _get_action_items_for_issue_type(self, issue_type: str, severity: str) -> List[str]:
        """Get action items for specific issue types"""
        action_map = {
            ("grammar", "error"): [
                "Review grammar rules and common errors",
                "Use grammar checking tools during writing",
                "Have content reviewed by another writer"
            ],
            ("style", "warning"): [
                "Follow established style guide consistently",
                "Use automated formatting tools",
                "Review style rules before publishing"
            ],
            ("readability", "warning"): [
                "Simplify complex sentences",
                "Use shorter paragraphs",
                "Replace technical jargon with simpler terms"
            ],
            ("tone", "warning"): [
                "Establish consistent voice guidelines",
                "Review content for tone consistency",
                "Use style guides for tone reference"
            ]
        }

        return action_map.get((issue_type, severity), [
            "Review and correct identified issues",
            "Establish quality standards",
            "Implement automated checking"
        ])

# Global proofreading engine instance
proofreading_engine = AutomatedProofreadingEngine()

def get_proofreading_engine() -> AutomatedProofreadingEngine:
    """Get the global proofreading engine instance"""
    return proofreading_engine

def proofread_document_file(file_path: str) -> Dict[str, Any]:
    """
    Proofread a document file and return results
    """
    engine = get_proofreading_engine()
    result, error = engine.proofread_document(file_path)

    if error:
        return {"error": error}

    if not result:
        return {"error": "Failed to proofread document"}

    summary = engine.get_proofreading_summary(result)
    suggestions = engine.generate_correction_suggestions(result)

    return {
        "success": True,
        "summary": summary,
        "suggestions": suggestions,
        "issues": {
            "errors": [{"line": i.line_number, "text": i.text, "suggestion": i.suggestion}
                      for i in result.errors],
            "warnings": [{"line": i.line_number, "text": i.text, "suggestion": i.suggestion}
                        for i in result.warnings],
            "suggestions": [{"line": i.line_number, "text": i.text, "suggestion": i.suggestion}
                           for i in result.suggestions]
        }
    }

if __name__ == "__main__":
    # Test the proofreading engine
    print("Terminal Grounds Automated Proofreading Engine")
    print("=" * 50)

    engine = get_proofreading_engine()

    # Test with sample text
    test_text = """
    This is a test document. It contains some grammar errors and style issues.
    The documentation should be easy to read and understand.
    We utilize multiple tools to achieve our goals.
    The implementation is complex and requires careful consideration.
    It is recommended to follow these guidelines when writing technical documentation.
    """

    print("Testing proofreading engine...")
    result = engine.proofread_text(test_text)

    print(f"\nProofreading Results:")
    print(f"Total Issues: {result.total_issues}")
    print(f"Errors: {len(result.errors)}")
    print(f"Warnings: {len(result.warnings)}")
    print(f"Suggestions: {len(result.suggestions)}")
    print(f"Readability Score: {result.readability_score:.1f}/100")
    print(f"Grade Level: {result.grade_level:.1f}")
    print(f"Tone Consistency: {result.tone_consistency_score:.2f}/1.0")
    print(f"Overall Quality: {result.overall_quality_score:.1f}/100")

    summary = engine.get_proofreading_summary(result)
    print(f"\nQuality Grade: {summary['quality_grade']}")

    print("\nAutomated Proofreading Engine operational!")
    print("Phase 4.1.2.1 Automated Proofreading Engine ready for integration.")
