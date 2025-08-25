#!/usr/bin/env python3
"""
Terminal Grounds Batch Organizer v1.0 - CTO-Directed Output Organization
Advanced batch-based organization system for tracking generation improvements

Organizes outputs by:
- Type (environments, emblems, tests, etc.)
- Batch (v0.9, v1.0, date-based)
- Generation session for quality comparison
"""

import os
import sys
import shutil
from pathlib import Path
from datetime import datetime
import re

# Fix Windows Unicode encoding
if sys.platform.startswith('win'):
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    os.environ['PYTHONUTF8'] = '1'

class BatchOrganizer:
    def __init__(self):
        self.output_dir = Path("C:/Users/Zachg/Terminal-Grounds/Tools/Comfy/ComfyUI-API/output")
        self.today = datetime.now().strftime("%Y-%m-%d")
        
        # Enhanced organization structure
        self.organization_structure = {
            "environments": {
                f"batch_v09_{self.today}": [],
                f"batch_v10_{self.today}": [],
                "archive": []
            },
            "emblems": {
                f"batch_{self.today}": [],
                "archive": []
            },
            "tests": {
                f"batch_{self.today}": [],
                "archive": []
            },
            "debug_versions": {
                f"batch_{self.today}": [],
                "archive": []
            },
            "production": {
                f"batch_{self.today}": [],
                "archive": []
            },
            "archived": {
                "experimental": [],
                "deprecated": []
            }
        }
    
    def analyze_file_metadata(self, filename):
        """Analyze file to determine batch version and classification"""
        metadata = {
            "type": "unknown",
            "version": "unknown",
            "batch_date": self.today,
            "generation_session": "unknown"
        }
        
        # Determine file type
        if "TG_Emblem_" in filename:
            metadata["type"] = "emblems"
        elif any(env in filename for env in ["Metro_", "IEZ_", "Tech_", "Corporate_", "Underground_", "Security_"]):
            metadata["type"] = "environments"
        elif any(test in filename for test in ["Test_", "Debug_", "API_"]):
            metadata["type"] = "tests"
        elif "Debug_" in filename:
            metadata["type"] = "debug_versions"
        elif "Production_" in filename:
            metadata["type"] = "production"
        
        # Determine version based on filename patterns and numbering
        if "00001_" in filename:
            metadata["version"] = "v0.9"  # Original generation
            metadata["generation_session"] = "original"
        elif "00002_" in filename:
            metadata["version"] = "v1.0"  # New lived-in world generation
            metadata["generation_session"] = "lived_in_world"
        elif "00003_" in filename:
            metadata["version"] = "v1.1"  # Future versions
            metadata["generation_session"] = "future"
            
        return metadata
    
    def create_batch_directories(self):
        """Create the enhanced batch-based directory structure"""
        for main_type, batches in self.organization_structure.items():
            main_dir = self.output_dir / main_type
            main_dir.mkdir(exist_ok=True)
            
            for batch_name in batches.keys():
                batch_dir = main_dir / batch_name
                batch_dir.mkdir(exist_ok=True)
                print(f"[+] Created batch directory: {batch_dir}")
    
    def organize_existing_files(self):
        """Organize all existing files into batch-based structure"""
        print(f"[+] Organizing files in: {self.output_dir}")
        
        # Get all PNG files in main output directory
        png_files = list(self.output_dir.glob("*.png"))
        print(f"[+] Found {len(png_files)} PNG files to organize")
        
        organization_stats = {
            "organized": 0,
            "skipped": 0,
            "errors": 0
        }
        
        for png_file in png_files:
            try:
                metadata = self.analyze_file_metadata(png_file.name)
                target_path = self.determine_target_path(metadata, png_file.name)
                
                if target_path and target_path != png_file:
                    # Ensure target directory exists
                    target_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    # Move file to organized location
                    shutil.move(str(png_file), str(target_path))
                    print(f"[+] Moved {png_file.name} -> {target_path.relative_to(self.output_dir)}")
                    organization_stats["organized"] += 1
                else:
                    organization_stats["skipped"] += 1
                    
            except Exception as e:
                print(f"[!] Error organizing {png_file.name}: {e}")
                organization_stats["errors"] += 1
        
        return organization_stats
    
    def determine_target_path(self, metadata, filename):
        """Determine the target path based on metadata"""
        file_type = metadata["type"]
        version = metadata["version"]
        
        if file_type == "unknown":
            return None
            
        # Select appropriate batch directory
        type_dir = self.output_dir / file_type
        
        if file_type == "environments":
            if version == "v1.0":
                batch_dir = type_dir / f"batch_v10_{self.today}"
            elif version == "v0.9":
                batch_dir = type_dir / f"batch_v09_{self.today}"
            else:
                batch_dir = type_dir / "archive"
        else:
            batch_dir = type_dir / f"batch_{self.today}"
            
        return batch_dir / filename
    
    def generate_batch_report(self):
        """Generate a report of organized batches for quality comparison"""
        report = {
            "organization_date": self.today,
            "batch_summary": {},
            "quality_comparison_ready": True
        }
        
        for main_type in self.organization_structure.keys():
            type_dir = self.output_dir / main_type
            if type_dir.exists():
                batches = {}
                for batch_dir in type_dir.iterdir():
                    if batch_dir.is_dir():
                        files = list(batch_dir.glob("*.png"))
                        batches[batch_dir.name] = {
                            "file_count": len(files),
                            "files": [f.name for f in files]
                        }
                report["batch_summary"][main_type] = batches
        
        # Save report
        import json
        report_path = self.output_dir / f"batch_organization_report_{self.today}.json"
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
            
        return report
    
    def organize_all(self):
        """Complete organization workflow"""
        print("=" * 60)
        print("TERMINAL GROUNDS BATCH ORGANIZER v1.0")
        print("CTO-Directed Enhanced Batch Organization")
        print("=" * 60)
        
        # Create directory structure
        self.create_batch_directories()
        print()
        
        # Organize existing files
        print("Organizing existing files...")
        stats = self.organize_existing_files()
        print()
        
        # Generate report
        print("Generating batch report...")
        report = self.generate_batch_report()
        print()
        
        # Summary
        print("ORGANIZATION COMPLETE:")
        print(f"[+] Files organized: {stats['organized']}")
        print(f"[+] Files skipped: {stats['skipped']}")
        print(f"[+] Errors: {stats['errors']}")
        print(f"[+] Batch types created: {len(self.organization_structure)}")
        print(f"[+] Report saved: batch_organization_report_{self.today}.json")
        
        return report

if __name__ == "__main__":
    organizer = BatchOrganizer()
    organizer.organize_all()