#!/usr/bin/env python3
"""
Asset Import Monitor for Terminal Grounds
Watches ComfyUI output directory and triggers UE5 import

Author: CTO Architect
"""

import os
import time
import json
import shutil
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import unreal

class AssetImportHandler(FileSystemEventHandler):
    """Handle new asset files from ComfyUI generation"""
    
    def __init__(self, ue5_content_path, metadata_cache):
        self.ue5_content_path = Path(ue5_content_path)
        self.metadata_cache = metadata_cache
        self.import_tasks = []
        
    def on_created(self, event):
        """Handle new file creation"""
        if event.is_directory:
            return
            
        file_path = Path(event.src_path)
        
        # Only process PNG files from ComfyUI
        if file_path.suffix.lower() != '.png':
            return
            
        print(f"New asset detected: {file_path.name}")
        
        # Look for metadata
        metadata = self.get_asset_metadata(file_path)
        
        # Queue for import
        self.queue_import(file_path, metadata)
        
    def get_asset_metadata(self, file_path):
        """Extract metadata from filename or companion JSON"""
        metadata_file = file_path.with_suffix('.json')
        
        if metadata_file.exists():
            with open(metadata_file, 'r') as f:
                return json.load(f)
                
        # Parse from filename convention: TG_[Faction]_[Type]_[ID].png
        parts = file_path.stem.split('_')
        if len(parts) >= 3 and parts[0] == 'TG':
            return {
                'faction': parts[1],
                'building_type': parts[2],
                'unique_id': parts[3] if len(parts) > 3 else 'default'
            }
            
        return {}
        
    def queue_import(self, source_path, metadata):
        """Queue asset for UE5 import"""
        import_task = {
            'source': source_path,
            'destination': self.build_ue5_path(metadata),
            'metadata': metadata,
            'timestamp': time.time()
        }
        
        self.import_tasks.append(import_task)
        
        # Process immediately in UE5 if available
        if self.is_unreal_available():
            self.process_import_queue()
            
    def build_ue5_path(self, metadata):
        """Build UE5 content path from metadata"""
        faction = metadata.get('faction', 'Generic')
        building_type = metadata.get('building_type', 'Structure')
        
        # Content/TerminalGrounds/Procedural/[Faction]/[Type]/
        return self.ue5_content_path / 'TerminalGrounds' / 'Procedural' / faction / building_type
        
    def is_unreal_available(self):
        """Check if Unreal Python API is available"""
        try:
            import unreal
            return True
        except ImportError:
            return False
            
    def process_import_queue(self):
        """Process pending imports in UE5"""
        if not self.import_tasks:
            return
            
        try:
            import unreal
            
            for task in self.import_tasks:
                self.import_to_unreal(task)
                
            self.import_tasks.clear()
            
        except Exception as e:
            print(f"Error processing imports: {e}")
            
    def import_to_unreal(self, task):
        """Import asset to Unreal Engine"""
        import unreal
        
        # Create import task
        import_task = unreal.AssetImportTask()
        import_task.filename = str(task['source'])
        import_task.destination_path = f"/Game/{task['destination'].relative_to(self.ue5_content_path)}"
        import_task.automated = True
        import_task.save = True
        import_task.replace_existing = True
        
        # Configure texture import settings
        texture_options = unreal.FbxTextureImportData()
        texture_options.material_search_location = unreal.MaterialSearchLocation.LOCAL
        
        # Execute import
        asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
        asset_tools.import_asset_tasks([import_task])
        
        print(f"Imported: {task['source'].name} -> {import_task.destination_path}")
        
        # Update procedural cache
        self.notify_procedural_cache(task)
        
    def notify_procedural_cache(self, task):
        """Notify procedural cache of new asset"""
        cache_update = {
            'type': 'ASSET_IMPORTED',
            'asset_path': task['destination'],
            'metadata': task['metadata']
        }
        
        # Write to cache notification file
        cache_file = Path("Tools/ProceduralBridge/import_notifications.json")
        
        notifications = []
        if cache_file.exists():
            with open(cache_file, 'r') as f:
                notifications = json.load(f)
                
        notifications.append(cache_update)
        
        with open(cache_file, 'w') as f:
            json.dump(notifications, f, indent=2)

class AssetImportMonitor:
    """Main monitor coordinating asset imports"""
    
    def __init__(self, watch_dir, ue5_content_path):
        self.watch_dir = Path(watch_dir)
        self.ue5_content_path = Path(ue5_content_path)
        self.metadata_cache = {}
        
        # Create handler and observer
        self.handler = AssetImportHandler(self.ue5_content_path, self.metadata_cache)
        self.observer = Observer()
        
    def start(self):
        """Start monitoring for new assets"""
        print(f"Monitoring: {self.watch_dir}")
        print(f"UE5 Content: {self.ue5_content_path}")
        
        self.observer.schedule(self.handler, str(self.watch_dir), recursive=False)
        self.observer.start()
        
        try:
            while True:
                time.sleep(1)
                
                # Periodically process import queue if UE5 becomes available
                if self.handler.is_unreal_available():
                    self.handler.process_import_queue()
                    
        except KeyboardInterrupt:
            self.observer.stop()
            print("\nMonitoring stopped")
            
        self.observer.join()

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Asset Import Monitor for Terminal Grounds")
    parser.add_argument(
        '--watch-dir',
        default='Tools/Comfy/ComfyUI-API/output',
        help='Directory to monitor for new assets'
    )
    parser.add_argument(
        '--ue5-content',
        default='Content',
        help='UE5 Content directory path'
    )
    
    args = parser.parse_args()
    
    monitor = AssetImportMonitor(args.watch_dir, args.ue5_content)
    monitor.start()

if __name__ == "__main__":
    main()