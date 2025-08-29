"""
Terminal Grounds LoreBook Migration Script
Phase 3.2: Convert LoreBook files to standard frontmatter format
"""

import os
import yaml
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

class LoreBookMigrator:
    """
    Migrates LoreBook files from custom format to standard Phase 2 frontmatter
    """

    def __init__(self, lorebook_root: str = "../../docs/Lore/LoreBook"):
        self.lorebook_root = Path(lorebook_root)
        self.migration_stats = {
            'processed': 0,
            'successful': 0,
            'failed': 0,
            'skipped': 0
        }

    def get_domain_from_path(self, file_path: Path) -> str:
        """Determine domain based on file path"""
        path_parts = file_path.parts

        if 'characters' in path_parts:
            return 'lore'
        elif 'factions' in path_parts:
            return 'lore'
        elif 'pois' in path_parts:
            return 'lore'
        elif 'regions' in path_parts:
            return 'lore'
        elif 'events' in path_parts:
            return 'lore'
        elif 'technology' in path_parts:
            return 'lore'
        else:
            return 'lore'  # Default to lore for LoreBook

    def get_type_from_content(self, custom_frontmatter: Dict[str, Any]) -> str:
        """Determine document type from custom frontmatter"""
        if 'type' in custom_frontmatter:
            custom_type = custom_frontmatter['type']
            if custom_type == 'character':
                return 'reference'
            elif custom_type == 'faction':
                return 'reference'
            elif custom_type == 'poi':
                return 'reference'
            elif custom_type == 'region':
                return 'reference'
            elif custom_type == 'event':
                return 'reference'
            elif custom_type == 'technology':
                return 'reference'

        return 'reference'  # Default type

    def extract_title_from_custom(self, custom_frontmatter: Dict[str, Any], filename: str) -> str:
        """Extract or generate title from custom frontmatter"""
        if 'name' in custom_frontmatter:
            return custom_frontmatter['name']
        elif 'id' in custom_frontmatter:
            # Convert ID to readable title
            id_name = custom_frontmatter['id']
            # Remove prefix and convert to title case
            if '_' in id_name:
                parts = id_name.split('_', 2)  # Split into prefix and name parts
                if len(parts) >= 3:
                    name_part = parts[2].replace('_', ' ').title()
                    return f"{name_part}"
            return id_name.replace('_', ' ').title()
        else:
            # Fallback to filename
            return filename.replace('_', ' ').replace('.md', '').title()

    def generate_tags_from_custom(self, custom_frontmatter: Dict[str, Any]) -> list:
        """Generate standard tags from custom frontmatter"""
        tags = []

        if 'tags' in custom_frontmatter:
            tags.extend(custom_frontmatter['tags'])

        if 'relationships' in custom_frontmatter:
            rel = custom_frontmatter['relationships']
            if 'faction' in rel:
                tags.append(f"faction:{rel['faction']}")

        # Add lore tag if not present
        if 'lore' not in tags:
            tags.append('lore')

        return tags

    def migrate_file(self, file_path: Path) -> bool:
        """Migrate a single LoreBook file to standard format"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Extract custom frontmatter
            if not content.startswith('---'):
                self.migration_stats['skipped'] += 1
                print(f"Skipped {file_path.name}: No frontmatter found")
                return False

            parts = content.split('---', 2)
            if len(parts) < 3:
                self.migration_stats['skipped'] += 1
                print(f"Skipped {file_path.name}: Invalid frontmatter format")
                return False

            custom_frontmatter_content = parts[1]
            body_content = parts[2]

            try:
                custom_frontmatter = yaml.safe_load(custom_frontmatter_content)
            except yaml.YAMLError as e:
                print(f"Failed to parse YAML in {file_path.name}: {e}")
                self.migration_stats['failed'] += 1
                return False

            # Generate standard frontmatter
            standard_frontmatter = {
                'title': self.extract_title_from_custom(custom_frontmatter, file_path.stem),
                'type': self.get_type_from_content(custom_frontmatter),
                'domain': self.get_domain_from_path(file_path),
                'status': 'approved',  # LoreBook content is canonical
                'last_reviewed': datetime.now().strftime('%Y-%m-%d'),
                'maintainer': 'Narrative Team',
                'tags': self.generate_tags_from_custom(custom_frontmatter),
                'related_docs': []  # Will be populated based on relationships
            }

            # Add related docs based on relationships
            if 'relationships' in custom_frontmatter:
                rel = custom_frontmatter['relationships']
                related_docs = []

                if 'faction' in rel:
                    # Add faction reference
                    faction_file = f"factions/{rel['faction']}.md"
                    if (self.lorebook_root / faction_file).exists():
                        related_docs.append(f"LoreBook/{faction_file}")

                if related_docs:
                    standard_frontmatter['related_docs'] = related_docs

            # Generate new content
            standard_frontmatter_yaml = yaml.dump(standard_frontmatter, default_flow_style=False, sort_keys=False)
            new_content = f"---\n{standard_frontmatter_yaml}---\n{body_content}"

            # Write back to file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)

            self.migration_stats['successful'] += 1
            print(f"Successfully migrated {file_path.name}")
            return True

        except Exception as e:
            print(f"Failed to migrate {file_path.name}: {e}")
            self.migration_stats['failed'] += 1
            return False

    def migrate_all_files(self) -> Dict[str, int]:
        """Migrate all LoreBook files"""
        print("Starting LoreBook migration to standard frontmatter format...")
        print("=" * 60)

        # Find all .md files in LoreBook directory
        for md_file in self.lorebook_root.rglob("*.md"):
            if md_file.name.lower() == "readme.md":
                continue

            self.migration_stats['processed'] += 1
            self.migrate_file(md_file)

        print("Migration completed!")
        print(f"Processed: {self.migration_stats['processed']}")
        print(f"Successful: {self.migration_stats['successful']}")
        print(f"Failed: {self.migration_stats['failed']}")
        print(f"Skipped: {self.migration_stats['skipped']}")

        return self.migration_stats

def main():
    """Main migration function"""
    migrator = LoreBookMigrator()
    stats = migrator.migrate_all_files()

    success_rate = (stats['successful'] / stats['processed']) * 100 if stats['processed'] > 0 else 0
    print(f"Success rate: {success_rate:.1f}%")
    if stats['failed'] == 0 and stats['skipped'] == 0:
        print("✅ LoreBook migration completed successfully!")
        print("Phase 3.2: LoreBook standardization achieved!")
    else:
        print("⚠️  Migration completed with some issues. Manual review recommended.")

if __name__ == "__main__":
    main()
