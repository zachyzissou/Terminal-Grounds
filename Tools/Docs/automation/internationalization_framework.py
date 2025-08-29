"""
Terminal Grounds Documentation Automation Framework
Phase 4.1.3.3: Internationalization Support (Safe Approach)

Lightweight internationalization validation and metadata support:
- UTF-8 encoding validation
- Multi-language frontmatter metadata extraction
- Simple language detection (frontmatter or heuristics)
- Review frequency and locale validation
"""

import os
import sys
import re
from pathlib import Path
from typing import Dict, List, Optional, Any
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
class I18nIssue:
    file_path: str
    issue_type: str
    description: str
    severity: str  # 'critical','high','medium','low'
    detected_at: datetime

@dataclass
class I18nAssessment:
    file_path: str
    utf8_valid: bool
    detected_language: Optional[str]
    has_multilingual_metadata: bool
    issues: List[I18nIssue]
    recommendations: List[str]
    assessed_at: datetime

class InternationalizationFramework:
    """Simple internationalization validation and metadata utilities"""

    def __init__(self):
        # Common ISO language codes pattern (simple)
        self.lang_pattern = re.compile(r"^[a-z]{2}(?:-[A-Z]{2})?$")
        logger.info("Internationalization Framework initialized")

    def validate_file_encoding(self, file_path: str) -> bool:
        """Ensure file is UTF-8 encoded"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                _ = f.read()
            return True
        except UnicodeDecodeError:
            return False
        except Exception as e:
            logger.warning(f"Encoding check error for {file_path}: {e}")
            return False

    def extract_multilang_metadata(self, content: str) -> Dict[str, Any]:
        """Extract multilingual metadata from YAML frontmatter if present.
        Supports keys like title.en, title.fr, description.en, lang, etc.
        """
        metadata = {}
        if content.startswith('---'):
            lines = content.split('\n')
            fm_end = -1
            for i, line in enumerate(lines[1:], 1):
                if line.strip() == '---':
                    fm_end = i
                    break
            if fm_end > 0:
                fm = '\n'.join(lines[1:fm_end])
                for line in fm.split('\n'):
                    if ':' in line:
                        key, val = line.split(':', 1)
                        metadata[key.strip()] = val.strip()
        # detect multilanguage keys
        multilang = any('.' in k for k in metadata.keys())
        metadata['_has_multilang'] = multilang
        return metadata

    def detect_language(self, content: str, metadata: Dict[str, Any]) -> Optional[str]:
        """Detect language using metadata first, then simple heuristics (stopwords)"""
        # Check metadata 'lang' or 'language' fields
        lang = metadata.get('lang') or metadata.get('language')
        if lang and isinstance(lang, str) and self.lang_pattern.match(lang.strip()):
            return lang.strip()

        # Heuristic: check for presence of common stopwords for languages
        sample = content[:2000].lower()
        stopwords = {
            'en': [' the ', ' and ', ' is ', ' of '],
            'fr': [' le ', ' la ', ' et ', ' est '],
            'es': [' el ', ' la ', ' y ', ' es '],
            'de': [' der ', ' die ', ' und ', ' ist ']
        }
        scores = {k: sample.count(w) for k, words in stopwords.items() for w in words}
        # aggregate counts
        agg = {k: sum(sample.count(w) for w in words) for k, words in stopwords.items()}
        best = max(agg.items(), key=lambda x: x[1]) if agg else (None, 0)
        if best[1] > 3:
            return best[0]
        return None

    def validate_review_frequency_locale(self, metadata: Dict[str, Any]) -> Optional[I18nIssue]:
        """Validate review frequency and locale fields in metadata"""
        if 'review_frequency' in metadata:
            freq = metadata['review_frequency'].lower()
            valid = ['daily', 'weekly', 'monthly', 'quarterly', 'annually', 'biannually']
            if freq not in valid:
                return I18nIssue(
                    file_path=metadata.get('file_path', ''),
                    issue_type='invalid_review_frequency',
                    description=f"Invalid review frequency: {metadata.get('review_frequency')}",
                    severity='medium',
                    detected_at=datetime.now()
                )
        # Validate locale if present
        locale = metadata.get('locale') or metadata.get('lang') or metadata.get('language')
        if locale and not self.lang_pattern.match(locale):
            return I18nIssue(
                file_path=metadata.get('file_path', ''),
                issue_type='invalid_locale',
                description=f"Invalid locale/language code: {locale}",
                severity='medium',
                detected_at=datetime.now()
            )
        return None

    def assess_document_i18n(self, file_path: str, content: str = None) -> I18nAssessment:
        """Perform basic internationalization assessment for a document"""
        if content is None:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            except Exception as e:
                logger.error(f"Error reading file {file_path}: {e}")
                return I18nAssessment(
                    file_path=file_path,
                    utf8_valid=False,
                    detected_language=None,
                    has_multilingual_metadata=False,
                    issues=[I18nIssue(file_path, 'read_error', str(e), 'critical', datetime.now())],
                    recommendations=["Fix read/encoding error"],
                    assessed_at=datetime.now()
                )

        utf8_ok = self.validate_file_encoding(file_path)
        metadata = self.extract_multilang_metadata(content)
        metadata['file_path'] = file_path
        has_multi = metadata.get('_has_multilang', False)
        lang = self.detect_language(content, metadata)

        issues: List[I18nIssue] = []
        recs: List[str] = []

        if not utf8_ok:
            issues.append(I18nIssue(file_path, 'invalid_encoding', 'File is not UTF-8 encoded', 'critical', datetime.now()))
            recs.append('Convert file to UTF-8 encoding')
        if not lang:
            issues.append(I18nIssue(file_path, 'undetected_language', 'Language not detected from metadata or content', 'medium', datetime.now()))
            recs.append('Add language metadata (lang: en) or include language in frontmatter')
        if not has_multi:
            recs.append('Consider adding multilingual metadata (e.g., title.en, title.fr) for multi-language support')

        freq_issue = self.validate_review_frequency_locale(metadata)
        if freq_issue:
            issues.append(freq_issue)
            recs.append('Fix review_frequency or locale metadata to valid values')

        assessment = I18nAssessment(
            file_path=file_path,
            utf8_valid=utf8_ok,
            detected_language=lang,
            has_multilingual_metadata=has_multi,
            issues=issues,
            recommendations=recs,
            assessed_at=datetime.now()
        )

        return assessment

# Global instance
_i18n_framework: Optional[InternationalizationFramework] = None

def get_internationalization_framework() -> InternationalizationFramework:
    global _i18n_framework
    if _i18n_framework is None:
        _i18n_framework = InternationalizationFramework()
    return _i18n_framework
