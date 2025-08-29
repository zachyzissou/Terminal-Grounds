"""
Terminal Grounds Documentation Automation Framework
Phase 4.0.1: Enhanced Template System

Dynamic template generation system with context-aware templates,
domain-specific variants, and automated template compliance checking.
"""

import os
import yaml
import json
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
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
class TemplateField:
    """Represents a template field with validation rules"""
    name: str
    type: str
    required: bool
    default: Any
    validation: Optional[Dict[str, Any]] = None
    description: Optional[str] = None

@dataclass
class DocumentTemplate:
    """Complete document template with metadata and fields"""
    name: str
    domain: str
    type: str
    description: str
    fields: List[TemplateField]
    content_structure: Dict[str, Any]
    examples: List[str]

class TemplateAnalysisEngine:
    """
    Analyzes existing documents to understand patterns and generate templates
    """

    def __init__(self, docs_root: str = "../../docs"):
        self.docs_root = Path(docs_root)
        self.analysis_results = {}

    def analyze_document_patterns(self) -> Dict[str, Any]:
        """
        Analyze existing documents to identify common patterns by domain and type
        """
        patterns = {
            'domains': {},
            'types': {},
            'field_usage': {},
            'content_structures': {}
        }

        for md_file in self.docs_root.rglob("*.md"):
            if md_file.name.lower() == "readme.md":
                continue

            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Extract frontmatter
                if content.startswith('---'):
                    parts = content.split('---', 2)
                    if len(parts) >= 3:
                        frontmatter_content = parts[1]
                        body_content = parts[2]

                        try:
                            frontmatter = yaml.safe_load(frontmatter_content)

                            if frontmatter:
                                domain = frontmatter.get('domain', 'unknown')
                                doc_type = frontmatter.get('type', 'unknown')

                                # Track domain patterns
                                if domain not in patterns['domains']:
                                    patterns['domains'][domain] = {
                                        'count': 0,
                                        'types': {},
                                        'common_fields': {},
                                        'tags': set()
                                    }

                                patterns['domains'][domain]['count'] += 1

                                # Track type patterns
                                if doc_type not in patterns['types']:
                                    patterns['types'][doc_type] = {
                                        'count': 0,
                                        'domains': set(),
                                        'common_fields': {}
                                    }

                                patterns['types'][doc_type]['count'] += 1
                                patterns['types'][doc_type]['domains'].add(domain)

                                # Analyze field usage
                                for field, value in frontmatter.items():
                                    if field not in patterns['field_usage']:
                                        patterns['field_usage'][field] = {
                                            'count': 0,
                                            'types': set(),
                                            'domains': set()
                                        }

                                    patterns['field_usage'][field]['count'] += 1
                                    patterns['field_usage'][field]['types'].add(doc_type)
                                    patterns['field_usage'][field]['domains'].add(domain)

                                # Track tags
                                if 'tags' in frontmatter and isinstance(frontmatter['tags'], list):
                                    for tag in frontmatter['tags']:
                                        if tag not in patterns['domains'][domain]['tags']:
                                            patterns['domains'][domain]['tags'].add(tag)

                        except yaml.YAMLError:
                            continue

            except Exception as e:
                logger.warning(f"Error analyzing {md_file}: {e}")
                continue

        self.analysis_results = patterns
        return patterns

    def generate_domain_templates(self) -> Dict[str, DocumentTemplate]:
        """
        Generate templates based on analyzed patterns
        """
        if not self.analysis_results:
            self.analyze_document_patterns()

        templates = {}

        for domain, domain_data in self.analysis_results['domains'].items():
            # Create base template for domain
            template = self._create_domain_template(domain, domain_data)
            if template:
                templates[f"{domain}_base"] = template

            # Create type-specific templates
            for doc_type in domain_data['types']:
                type_template = self._create_type_template(domain, doc_type, domain_data)
                if type_template:
                    templates[f"{domain}_{doc_type}"] = type_template

        return templates

    def _create_domain_template(self, domain: str, domain_data: Dict[str, Any]) -> Optional[DocumentTemplate]:
        """Create a base template for a domain"""
        fields = [
            TemplateField(
                name="title",
                type="string",
                required=True,
                default="",
                description=f"Document title for {domain} domain"
            ),
            TemplateField(
                name="type",
                type="enum",
                required=True,
                default="reference",
                validation={"enum": ["guide", "reference", "process", "spec", "api"]},
                description="Document type"
            ),
            TemplateField(
                name="domain",
                type="string",
                required=True,
                default=domain,
                description="Documentation domain"
            ),
            TemplateField(
                name="status",
                type="enum",
                required=True,
                default="draft",
                validation={"enum": ["draft", "review", "approved", "deprecated"]},
                description="Document status"
            ),
            TemplateField(
                name="last_reviewed",
                type="date",
                required=True,
                default=datetime.now().strftime('%Y-%m-%d'),
                description="Last review date"
            ),
            TemplateField(
                name="maintainer",
                type="string",
                required=True,
                default="Documentation Team",
                description="Document maintainer"
            ),
            TemplateField(
                name="tags",
                type="array",
                required=False,
                default=[domain],
                description="Document tags"
            ),
            TemplateField(
                name="related_docs",
                type="array",
                required=False,
                default=[],
                description="Related documents"
            )
        ]

        return DocumentTemplate(
            name=f"{domain}_base",
            domain=domain,
            type="base",
            description=f"Base template for {domain} domain documents",
            fields=fields,
            content_structure={
                "sections": ["Overview", "Details", "References"],
                "required_sections": ["Overview"]
            },
            examples=[f"Example {domain} document"]
        )

    def _create_type_template(self, domain: str, doc_type: str, domain_data: Dict[str, Any]) -> Optional[DocumentTemplate]:
        """Create a type-specific template"""
        # This would be more sophisticated in a real implementation
        return None  # Placeholder for now

class DynamicTemplateGenerator:
    """
    Generates context-aware templates based on document requirements
    """

    def __init__(self, analysis_engine: TemplateAnalysisEngine):
        self.analysis_engine = analysis_engine
        self.templates = {}

    def generate_template(self, domain: str, doc_type: str, context: Optional[Dict[str, Any]] = None) -> DocumentTemplate:
        """
        Generate a context-aware template
        """
        template_key = f"{domain}_{doc_type}"

        if template_key in self.templates:
            return self.templates[template_key]

        # Generate new template
        template = self._generate_context_template(domain, doc_type, context)
        self.templates[template_key] = template

        return template

    def _generate_context_template(self, domain: str, doc_type: str, context: Optional[Dict[str, Any]]) -> DocumentTemplate:
        """Generate a template based on context"""
        # Base fields for all documents
        fields = [
            TemplateField("title", "string", True, "", "Document title"),
            TemplateField("type", "string", True, doc_type, "Document type"),
            TemplateField("domain", "string", True, domain, "Documentation domain"),
            TemplateField("status", "enum", True, "draft", {"enum": ["draft", "review", "approved", "deprecated"]}),
            TemplateField("last_reviewed", "date", True, datetime.now().strftime('%Y-%m-%d')),
            TemplateField("maintainer", "string", True, "Documentation Team"),
            TemplateField("tags", "array", False, [domain]),
            TemplateField("related_docs", "array", False, [])
        ]

        # Add domain-specific fields
        if domain == "technical":
            fields.extend([
                TemplateField("api_version", "string", False, "1.0.0", "API version if applicable"),
                TemplateField("dependencies", "array", False, [], "Technical dependencies")
            ])
        elif domain == "design":
            fields.extend([
                TemplateField("design_system", "string", False, "", "Design system used"),
                TemplateField("platforms", "array", False, [], "Target platforms")
            ])

        # Add type-specific fields
        if doc_type == "api":
            fields.extend([
                TemplateField("endpoint", "string", False, "", "API endpoint"),
                TemplateField("method", "enum", False, "GET", {"enum": ["GET", "POST", "PUT", "DELETE"]})
            ])

        return DocumentTemplate(
            name=f"{domain}_{doc_type}",
            domain=domain,
            type=doc_type,
            description=f"Dynamic template for {domain} {doc_type} documents",
            fields=fields,
            content_structure=self._get_content_structure(doc_type),
            examples=[f"Example {domain} {doc_type} document"]
        )

    def _get_content_structure(self, doc_type: str) -> Dict[str, Any]:
        """Get content structure based on document type"""
        structures = {
            "guide": {
                "sections": ["Overview", "Prerequisites", "Steps", "Examples", "Troubleshooting"],
                "required_sections": ["Overview", "Steps"]
            },
            "reference": {
                "sections": ["Overview", "API Reference", "Examples", "See Also"],
                "required_sections": ["Overview"]
            },
            "process": {
                "sections": ["Overview", "Process Flow", "Roles & Responsibilities", "Checklist"],
                "required_sections": ["Overview", "Process Flow"]
            },
            "spec": {
                "sections": ["Overview", "Requirements", "Implementation", "Testing"],
                "required_sections": ["Overview", "Requirements"]
            }
        }

        return structures.get(doc_type, {
            "sections": ["Overview", "Details"],
            "required_sections": ["Overview"]
        })

class TemplateManager:
    """
    Manages template lifecycle, validation, and usage analytics
    """

    def __init__(self, templates_dir: str = "../../Tools/Docs/templates"):
        self.templates_dir = Path(templates_dir)
        self.templates_dir.mkdir(exist_ok=True)
        self.templates = {}
        self.usage_stats = {}

    def save_template(self, template: DocumentTemplate) -> bool:
        """Save template to disk"""
        try:
            template_data = {
                "name": template.name,
                "domain": template.domain,
                "type": template.type,
                "description": template.description,
                "fields": [
                    {
                        "name": field.name,
                        "type": field.type,
                        "required": field.required,
                        "default": field.default,
                        "validation": field.validation,
                        "description": field.description
                    }
                    for field in template.fields
                ],
                "content_structure": template.content_structure,
                "examples": template.examples
            }

            template_file = self.templates_dir / f"{template.name}.json"
            with open(template_file, 'w', encoding='utf-8') as f:
                json.dump(template_data, f, indent=2, default=str)

            self.templates[template.name] = template
            return True

        except Exception as e:
            logger.error(f"Error saving template {template.name}: {e}")
            return False

    def load_template(self, template_name: str) -> Optional[DocumentTemplate]:
        """Load template from disk"""
        template_file = self.templates_dir / f"{template_name}.json"

        if not template_file.exists():
            return None

        try:
            with open(template_file, 'r', encoding='utf-8') as f:
                template_data = json.load(f)

            fields = [
                TemplateField(**field_data)
                for field_data in template_data["fields"]
            ]

            template = DocumentTemplate(
                name=template_data["name"],
                domain=template_data["domain"],
                type=template_data["type"],
                description=template_data["description"],
                fields=fields,
                content_structure=template_data["content_structure"],
                examples=template_data["examples"]
            )

            self.templates[template_name] = template
            return template

        except Exception as e:
            logger.error(f"Error loading template {template_name}: {e}")
            return None

    def validate_template_compliance(self, template: DocumentTemplate) -> Dict[str, Any]:
        """Validate template compliance with standards"""
        issues = []

        # Check required fields
        required_fields = ["title", "type", "domain", "status", "last_reviewed", "maintainer"]
        field_names = [field.name for field in template.fields]

        for required_field in required_fields:
            if required_field not in field_names:
                issues.append(f"Missing required field: {required_field}")

        # Check field types
        valid_types = ["string", "enum", "array", "date", "number", "boolean"]
        for field in template.fields:
            if field.type not in valid_types:
                issues.append(f"Invalid field type '{field.type}' for field '{field.name}'")

        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "field_count": len(template.fields),
            "required_fields": len([f for f in template.fields if f.required])
        }

    def get_usage_stats(self) -> Dict[str, Any]:
        """Get template usage statistics"""
        return {
            "total_templates": len(self.templates),
            "templates_by_domain": self._group_templates_by("domain"),
            "templates_by_type": self._group_templates_by("type"),
            "usage_stats": self.usage_stats
        }

    def _group_templates_by(self, attribute: str) -> Dict[str, int]:
        """Group templates by attribute"""
        groups = {}
        for template in self.templates.values():
            key = getattr(template, attribute)
            groups[key] = groups.get(key, 0) + 1
        return groups

def main():
    """Main function for template system demonstration"""
    print("Terminal Grounds Enhanced Template System")
    print("=" * 50)

    # Initialize components
    analysis_engine = TemplateAnalysisEngine()
    template_generator = DynamicTemplateGenerator(analysis_engine)
    template_manager = TemplateManager()

    # Analyze existing documents
    print("Analyzing existing document patterns...")
    patterns = analysis_engine.analyze_document_patterns()

    print(f"Found {len(patterns['domains'])} domains and {len(patterns['types'])} types")
    print(f"Analyzed {sum(d['count'] for d in patterns['domains'].values())} documents")

    # Generate templates
    print("\nGenerating dynamic templates...")
    templates = analysis_engine.generate_domain_templates()

    # Save and validate templates
    for template_name, template in templates.items():
        print(f"Processing template: {template_name}")

        # Save template
        if template_manager.save_template(template):
            print(f"  ✓ Saved template: {template_name}")

            # Validate template
            validation = template_manager.validate_template_compliance(template)
            if validation["valid"]:
                print(f"  ✓ Template validation passed")
            else:
                print(f"  ⚠ Template validation issues: {validation['issues']}")
        else:
            print(f"  ✗ Failed to save template: {template_name}")

    # Generate example templates
    print("\nGenerating example context-aware templates...")
    example_template = template_generator.generate_template("technical", "api")
    print(f"Generated example template: {example_template.name}")

    # Display usage statistics
    stats = template_manager.get_usage_stats()
    print(f"\nTemplate System Statistics:")
    print(f"  Total Templates: {stats['total_templates']}")
    print(f"  By Domain: {stats['templates_by_domain']}")
    print(f"  By Type: {stats['templates_by_type']}")

    print("\nEnhanced Template System operational!")
    print("Phase 4.0.1: Template System Enhancement complete!")

if __name__ == "__main__":
    main()
