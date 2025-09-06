#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Terminal Grounds Documentation Validator
Phase 5.1 Bold Strategy - Automated Governance

Agent-First Approach: This script should be called via:
/document-control-specialist validation comprehensive

For legacy usage: python Tools/DocumentControl/doc_validator.py
"""

import os
import json
import re
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime
import argparse

@dataclass
class ValidationResult:
    """Documentation validation result structure"""
    file_path: str
    score: int  # 0-100
    issues: List[str]
    recommendations: List[str]
    category: str
    priority: str  # HIGH, MEDIUM, LOW

class DocumentationValidator:
    """
    Comprehensive documentation validation system
    
    Validates:
    - Frontmatter compliance
    - Content quality indicators
    - Link integrity
    - Agent-first approach compliance
    - Phase alignment
    """
    
    def __init__(self, base_path: str = "."):
        self.base_path = Path(base_path)
        self.results: List[ValidationResult] = []
        self.agent_keywords = [
            "/document-control-specialist",
            "/performance-engineer", 
            "/comfyui-concept-designer",
            "/cto-architect",
            "/chief-security-officer",
            "/map-designer",
            "/data-scientist",
            "/devops-engineer",
            "/chief-design-officer",
            "/chief-art-director",
            "/website-prompt-specialist"
        ]
        
    def validate_all_docs(self) -> Dict:
        """Run comprehensive validation on all markdown files"""
        print("Starting comprehensive documentation validation...")
        
        # Find all markdown files (excluding third-party)
        md_files = self._find_project_markdown_files()
        
        print(f"Found {len(md_files)} project markdown files to validate")
        
        # Validate each file
        for file_path in md_files:
            result = self._validate_file(file_path)
            self.results.append(result)
            
        # Generate summary report
        return self._generate_summary_report()
    
    def _find_project_markdown_files(self) -> List[Path]:
        """Find all project markdown files, excluding third-party dependencies"""
        exclude_patterns = [
            "*/node_modules/*",
            "*/Meshroom-2025/*", 
            "*/ComfyUI-API/custom_nodes/*",
            "*/.git/*",
            "*/venv/*",
            "*/__pycache__/*"
        ]
        
        md_files = []
        for file_path in self.base_path.rglob("*.md"):
            # Skip excluded paths
            should_exclude = any(
                file_path.match(pattern) for pattern in exclude_patterns
            )
            if not should_exclude:
                md_files.append(file_path)
                
        return sorted(md_files)
    
    def _validate_file(self, file_path: Path) -> ValidationResult:
        """Validate individual markdown file"""
        try:
            content = file_path.read_text(encoding='utf-8')
        except Exception as e:
            return ValidationResult(
                file_path=str(file_path),
                score=0,
                issues=[f"Cannot read file: {e}"],
                recommendations=["Fix file encoding or permissions"],
                category="ERROR",
                priority="HIGH"
            )
            
        issues = []
        recommendations = []
        score = 100  # Start perfect, deduct for issues
        
        # Check frontmatter
        frontmatter_score, fm_issues, fm_recs = self._check_frontmatter(content)
        score -= (100 - frontmatter_score) * 0.3  # 30% weight
        issues.extend(fm_issues)
        recommendations.extend(fm_recs)
        
        # Check content quality
        content_score, c_issues, c_recs = self._check_content_quality(content)
        score -= (100 - content_score) * 0.4  # 40% weight  
        issues.extend(c_issues)
        recommendations.extend(c_recs)
        
        # Check agent-first compliance
        agent_score, a_issues, a_recs = self._check_agent_compliance(content)
        score -= (100 - agent_score) * 0.2  # 20% weight
        issues.extend(a_issues) 
        recommendations.extend(a_recs)
        
        # Check phase alignment
        phase_score, p_issues, p_recs = self._check_phase_alignment(content)
        score -= (100 - phase_score) * 0.1  # 10% weight
        issues.extend(p_issues)
        recommendations.extend(p_recs)
        
        # Determine category and priority
        category = self._determine_category(file_path)
        priority = self._determine_priority(score, len(issues))
        
        return ValidationResult(
            file_path=str(file_path.relative_to(self.base_path)),
            score=max(0, int(score)),
            issues=issues,
            recommendations=recommendations,
            category=category,
            priority=priority
        )
    
    def _check_frontmatter(self, content: str) -> Tuple[int, List[str], List[str]]:
        """Check frontmatter compliance"""
        issues = []
        recommendations = []
        score = 100
        
        # Check for frontmatter presence
        if not content.startswith('---'):
            score -= 30
            issues.append("Missing YAML frontmatter")
            recommendations.append("Add YAML frontmatter with title, date, status")
            return score, issues, recommendations
            
        # Extract frontmatter
        try:
            end_idx = content.find('---', 3)
            if end_idx == -1:
                score -= 20
                issues.append("Malformed frontmatter (missing closing ---)")
                recommendations.append("Close frontmatter with --- on new line")
        except Exception:
            score -= 30
            issues.append("Cannot parse frontmatter")
            
        return score, issues, recommendations
    
    def _check_content_quality(self, content: str) -> Tuple[int, List[str], List[str]]:
        """Check content quality indicators"""
        issues = []
        recommendations = []
        score = 100
        
        # Check for TODO markers
        todo_count = len(re.findall(r'\bTODO\b', content, re.IGNORECASE))
        if todo_count > 0:
            score -= min(todo_count * 10, 30)  # Max 30 point deduction
            issues.append(f"Contains {todo_count} TODO markers")
            recommendations.append("Complete or remove TODO items")
            
        # Check for placeholder text
        placeholders = ['Lorem ipsum', 'placeholder', 'TBD', 'FIXME']
        for placeholder in placeholders:
            if placeholder.lower() in content.lower():
                score -= 15
                issues.append(f"Contains placeholder text: {placeholder}")
                recommendations.append("Replace placeholder text with actual content")
                
        # Check minimum content length
        word_count = len(content.split())
        if word_count < 50:
            score -= 25
            issues.append(f"Very short content ({word_count} words)")
            recommendations.append("Expand documentation with examples and details")
        elif word_count < 100:
            score -= 10
            issues.append(f"Short content ({word_count} words)")
            recommendations.append("Consider adding more detail and examples")
            
        # Check for proper headings structure
        if '# ' not in content:
            score -= 20
            issues.append("Missing main heading (H1)")
            recommendations.append("Add main heading with # syntax")
            
        return score, issues, recommendations
    
    def _check_agent_compliance(self, content: str) -> Tuple[int, List[str], List[str]]:
        """Check agent-first approach compliance"""
        issues = []
        recommendations = []
        score = 100
        
        # Check for agent usage examples
        agent_mentions = 0
        for keyword in self.agent_keywords:
            agent_mentions += content.count(keyword)
            
        # Check for legacy script patterns
        legacy_patterns = [
            r'python\s+[\w/\\.-]+\.py',
            r'bash\s+[\w/\\.-]+\.sh',
            r'npm\s+run\s+[\w-]+',
            r'git\s+\w+'
        ]
        
        legacy_count = 0
        for pattern in legacy_patterns:
            legacy_count += len(re.findall(pattern, content, re.IGNORECASE))
            
        # Score based on agent vs legacy ratio
        if agent_mentions == 0 and legacy_count > 3:
            score -= 40
            issues.append("No agent usage examples, many legacy commands")
            recommendations.append("Replace legacy commands with agent-first examples")
        elif agent_mentions == 0:
            score -= 20
            issues.append("No agent usage examples")
            recommendations.append("Add agent-first command examples")
        elif legacy_count > agent_mentions * 2:
            score -= 15
            issues.append("More legacy commands than agent examples")
            recommendations.append("Balance agent examples with legacy deprecation")
            
        return score, issues, recommendations
    
    def _check_phase_alignment(self, content: str) -> Tuple[int, List[str], List[str]]:
        """Check alignment with current Phase 5 development"""
        issues = []
        recommendations = []
        score = 100
        
        # Check for outdated phase references
        outdated_patterns = [
            r'Phase\s+[1-4]\s+\(current\)|Phase\s+[1-4]\s+\(in\s+progress\)',
            r'August\s+2025.*current',
            r'92%.*current.*success.*rate'
        ]
        
        for pattern in outdated_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                score -= 15
                issues.append("Contains outdated phase/status information")
                recommendations.append("Update to current Phase 5 status")
                
        # Check for current phase indicators
        if 'Phase 5' in content or 'September 2025' in content:
            score += 5  # Bonus for current content
        
        return score, issues, recommendations
    
    def _determine_category(self, file_path: Path) -> str:
        """Determine documentation category"""
        path_str = str(file_path).lower()
        
        if 'readme' in path_str:
            return 'README'
        elif 'roadmap' in path_str:
            return 'ROADMAP' 
        elif any(x in path_str for x in ['design', 'spec', 'architecture']):
            return 'DESIGN'
        elif any(x in path_str for x in ['tools', 'script', 'automation']):
            return 'TOOLS'
        elif 'claude' in path_str:
            return 'AI_CONTEXT'
        else:
            return 'GENERAL'
    
    def _determine_priority(self, score: int, issue_count: int) -> str:
        """Determine priority based on score and issues"""
        if score < 60 or issue_count >= 5:
            return 'HIGH'
        elif score < 80 or issue_count >= 3:
            return 'MEDIUM'
        else:
            return 'LOW'
    
    def _generate_summary_report(self) -> Dict:
        """Generate comprehensive summary report"""
        total_files = len(self.results)
        if total_files == 0:
            return {"error": "No files validated"}
            
        # Calculate overall health score
        total_score = sum(r.score for r in self.results)
        health_score = total_score / total_files
        
        # Priority distribution
        priority_dist = {
            'HIGH': len([r for r in self.results if r.priority == 'HIGH']),
            'MEDIUM': len([r for r in self.results if r.priority == 'MEDIUM']), 
            'LOW': len([r for r in self.results if r.priority == 'LOW'])
        }
        
        # Category breakdown
        categories = {}
        for result in self.results:
            categories[result.category] = categories.get(result.category, 0) + 1
            
        # Top issues
        all_issues = []
        for result in self.results:
            all_issues.extend(result.issues)
            
        issue_frequency = {}
        for issue in all_issues:
            issue_frequency[issue] = issue_frequency.get(issue, 0) + 1
            
        top_issues = sorted(issue_frequency.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return {
            'timestamp': datetime.now().isoformat(),
            'validation_summary': {
                'total_files': total_files,
                'health_score': round(health_score, 1),
                'target_score': 97.0,
                'improvement_needed': max(0, 97.0 - health_score),
                'files_needing_attention': priority_dist['HIGH'] + priority_dist['MEDIUM']
            },
            'priority_distribution': priority_dist,
            'category_breakdown': categories,
            'top_issues': top_issues,
            'detailed_results': [
                {
                    'file': r.file_path,
                    'score': r.score,
                    'category': r.category,
                    'priority': r.priority,
                    'issues': r.issues,
                    'recommendations': r.recommendations
                }
                for r in sorted(self.results, key=lambda x: x.score)
            ]
        }

def main():
    """Main validation function"""
    parser = argparse.ArgumentParser(description='Terminal Grounds Documentation Validator')
    parser.add_argument('--output', '-o', default='validation_report.json',
                      help='Output file for validation report')
    parser.add_argument('--format', choices=['json', 'summary'], default='json',
                      help='Output format')
    parser.add_argument('--path', default='.',
                      help='Base path to validate')
    
    args = parser.parse_args()
    
    # Initialize validator
    validator = DocumentationValidator(args.path)
    
    # Run validation
    report = validator.validate_all_docs()
    
    # Output results
    if args.format == 'json':
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        print(f"Validation report written to: {args.output}")
    else:
        # Print summary to console
        summary = report['validation_summary']
        print(f"\nDocumentation Health Report")
        print(f"===========================")
        print(f"Files Validated: {summary['total_files']}")
        print(f"Health Score: {summary['health_score']}/100")
        print(f"Target Score: {summary['target_score']}")
        print(f"Improvement Needed: +{summary['improvement_needed']:.1f} points")
        print(f"Files Needing Attention: {summary['files_needing_attention']}")
        
        priorities = report['priority_distribution']
        print(f"\nPriority Distribution:")
        print(f"  HIGH: {priorities['HIGH']} files")
        print(f"  MEDIUM: {priorities['MEDIUM']} files") 
        print(f"  LOW: {priorities['LOW']} files")

if __name__ == '__main__':
    main()