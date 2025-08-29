---
title: Documentation Standards
type: reference
domain: process
status: draft
last_reviewed: '2025-08-28'
maintainer: Documentation Team
tags: []
related_docs: []
---


# Documentation Standards Template

## Frontmatter Requirements

All documentation must include standardized frontmatter:

```yaml
---
title: "Document Title"
type: "documentation_type" # guide|reference|process|spec|api
domain: "domain_name" # technical|design|lore|art|process
status: "status" # draft|review|approved|deprecated
last_reviewed: "2025-08-28"
maintainer: "team_or_person"
tags: [tag1, tag2]
related_docs: [doc1.md, doc2.md]
---
```

## File Naming Convention

- Use PascalCase for document names: `DesignOverview.md`
- Include domain prefix for organization: `TECH_API_Reference.md`
- Use underscores for multi-word files: `Asset_Pipeline_Guide.md`

## Content Standards

- Maximum 2000 words per document
- Include table of contents for documents >500 words
- Use consistent heading hierarchy (H1 → H2 → H3)
- Cross-reference related documents
- Include last modified date and author
