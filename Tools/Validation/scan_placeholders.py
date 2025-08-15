"""
Placeholder Asset Scanner for Terminal Grounds
Scans repository for placeholder/temp assets and generates report
"""
import os
import json
import shutil
import re
from pathlib import Path
from datetime import datetime
from PIL import Image
import argparse

class PlaceholderScanner:
    def __init__(self, repo_root):
        self.repo_root = Path(repo_root)
        self.placeholders = []
        
        # Define minimum sizes per asset class
        self.min_sizes = {
            'icon': (512, 512),
            'emblem': (512, 512),
            'poster': (1024, 1536),
            'concept': (1280, 720),
            'mood': (1280, 720)
        }
        
        # Placeholder patterns
        self.placeholder_patterns = [
            r'temp', r'placeholder', r'dummy', r'wip', 
            r'sample', r'stock', r'todo', r'untitled', 
            r'draft', r'lowres', r'test'
        ]
        self.pattern_regex = re.compile('|'.join(self.placeholder_patterns), re.IGNORECASE)
        
    def classify_asset(self, path):
        """Classify asset based on path and name"""
        path_str = str(path).lower()
        name = path.stem.lower()
        
        if 'icon' in path_str or 'icon' in name:
            return 'icon'
        elif 'emblem' in path_str or 'faction' in path_str:
            return 'emblem'
        elif 'poster' in path_str:
            return 'poster'
        elif 'concept' in path_str:
            return 'concept'
        elif 'mood' in path_str or 'render' in path_str:
            return 'mood'
        else:
            return 'general'
    
    def check_image(self, file_path):
        """Check if image is a placeholder"""
        flags = []
        path = Path(file_path)
        
        # Check filename for placeholder patterns
        if self.pattern_regex.search(path.stem):
            flags.append('name_match')
        
        # Try to get image dimensions
        try:
            with Image.open(file_path) as img:
                width, height = img.size
                asset_class = self.classify_asset(path)
                
                # Check minimum size requirements
                if asset_class in self.min_sizes:
                    min_w, min_h = self.min_sizes[asset_class]
                    if width < min_w or height < min_h:
                        flags.append(f'below_min_size_{asset_class}')
                
                # Icons/Emblems must be square
                if asset_class in ['icon', 'emblem'] and width != height:
                    flags.append('not_square')
                    
                return {
                    'path': str(path.relative_to(self.repo_root)),
                    'class': asset_class,
                    'width': width,
                    'height': height,
                    'flags': flags
                }
        except Exception as e:
            flags.append(f'error_reading: {str(e)}')
            return {
                'path': str(path.relative_to(self.repo_root)),
                'class': 'unknown',
                'width': 0,
                'height': 0,
                'flags': flags
            }
        
        return None
    
    def scan(self, paths_to_scan=None):
        """Scan for placeholder assets"""
        if paths_to_scan is None:
            paths_to_scan = [
                self.repo_root / 'Content' / 'TG',
                self.repo_root / 'Docs' / 'Concepts'
            ]
        
        extensions = {'.png', '.jpg', '.jpeg', '.tga', '.webp', '.bmp', '.svg'}
        
        for scan_path in paths_to_scan:
            if not scan_path.exists():
                continue
                
            for ext in extensions:
                for file_path in scan_path.rglob(f'*{ext}'):
                    result = self.check_image(file_path)
                    if result and result['flags']:
                        self.placeholders.append(result)
        
        return self.placeholders
    
    def generate_report(self, output_path=None):
        """Generate JSON report"""
        if output_path is None:
            output_path = self.repo_root / 'Docs' / '.placeholder_report.json'
        
        report = {
            'scan_date': datetime.now().isoformat(),
            'total_placeholders': len(self.placeholders),
            'by_class': {},
            'items': self.placeholders
        }
        
        # Count by class
        for item in self.placeholders:
            cls = item['class']
            report['by_class'][cls] = report['by_class'].get(cls, 0) + 1
        
        # Ensure Docs directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        return report
    
    def quarantine(self, dry_run=False):
        """Move placeholder files to quarantine folder"""
        quarantine_dir = self.repo_root / '_Placeholders'
        quarantine_dir.mkdir(exist_ok=True)
        
        moved = []
        for item in self.placeholders:
            src = self.repo_root / item['path']
            
            # Maintain directory structure in quarantine
            rel_path = Path(item['path'])
            dst_dir = quarantine_dir / rel_path.parent
            dst_dir.mkdir(parents=True, exist_ok=True)
            dst = dst_dir / rel_path.name
            
            if not dry_run and src.exists():
                shutil.move(str(src), str(dst))
                moved.append({
                    'from': str(src),
                    'to': str(dst)
                })
                print(f"Quarantined: {item['path']}")
            elif dry_run:
                print(f"Would quarantine: {item['path']}")
        
        return moved


def main():
    parser = argparse.ArgumentParser(description='Scan for placeholder assets')
    parser.add_argument('--root', default=r'C:\Users\Zachg\Terminal-Grounds',
                      help='Repository root path')
    parser.add_argument('--quarantine', action='store_true',
                      help='Move placeholders to quarantine folder')
    parser.add_argument('--dry-run', action='store_true',
                      help='Show what would be quarantined without moving')
    
    args = parser.parse_args()
    
    scanner = PlaceholderScanner(args.root)
    placeholders = scanner.scan()
    
    print(f"\n📊 Scan Results:")
    print(f"Found {len(placeholders)} placeholder assets")
    
    # Generate report
    report = scanner.generate_report()
    print(f"\n📄 Report saved to: Docs/.placeholder_report.json")
    
    # Show breakdown
    print("\n🏷️ By Class:")
    for cls, count in report['by_class'].items():
        print(f"  {cls}: {count}")
    
    # Show sample issues
    if placeholders:
        print("\n⚠️ Sample Issues (first 5):")
        for item in placeholders[:5]:
            print(f"  {item['path']}")
            print(f"    Class: {item['class']}, Size: {item['width']}x{item['height']}")
            print(f"    Flags: {', '.join(item['flags'])}")
    
    # Quarantine if requested
    if args.quarantine or args.dry_run:
        print(f"\n{'🔍 DRY RUN - ' if args.dry_run else ''}📦 Quarantine Mode:")
        moved = scanner.quarantine(dry_run=args.dry_run)
        if not args.dry_run:
            print(f"Moved {len(moved)} files to _Placeholders/")


if __name__ == '__main__':
    main()
