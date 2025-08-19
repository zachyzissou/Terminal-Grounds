#!/usr/bin/env python3
"""
Asset Manager for Terminal Grounds v2.0
=======================================
Comprehensive asset lifecycle management, organization, and discovery system.
"""

import json
import sqlite3
import shutil
import hashlib
from pathlib import Path
from typing import Dict, Any, List, Optional, Union, Tuple, Iterator
from dataclasses import dataclass, field, asdict
from enum import Enum
import time
import logging
from datetime import datetime, timedelta

try:
    from .asset_spec import AssetSpecification, AssetType, FactionCode, QualityLevel
except ImportError:
    from asset_spec import AssetSpecification, AssetType, FactionCode, QualityLevel

logger = logging.getLogger(__name__)

class AssetStatus(Enum):
    DRAFT = "draft"
    REVIEW = "review"
    APPROVED = "approved"
    PUBLISHED = "published"
    ARCHIVED = "archived"
    DEPRECATED = "deprecated"

class AssetVersion(Enum):
    MAJOR = "major"
    MINOR = "minor"
    PATCH = "patch"

@dataclass
class AssetFile:
    """Represents a file associated with an asset"""
    path: Path
    file_type: str  # "source", "final", "preview", "metadata"
    format: str     # "png", "jpg", "json", "uasset"
    size_bytes: int
    checksum: str
    created_at: float
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class AssetRecord:
    """Complete asset record with all associated data"""
    asset_id: str
    asset_spec: AssetSpecification
    status: AssetStatus
    version: str
    created_at: float
    updated_at: float
    files: List[AssetFile] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    quality_score: Optional[float] = None
    usage_count: int = 0
    last_accessed: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def primary_file(self) -> Optional[AssetFile]:
        """Get the primary asset file (usually the final output)"""
        final_files = [f for f in self.files if f.file_type == "final"]
        return final_files[0] if final_files else None
    
    @property
    def preview_file(self) -> Optional[AssetFile]:
        """Get the preview/thumbnail file"""
        preview_files = [f for f in self.files if f.file_type == "preview"]
        return preview_files[0] if preview_files else None

class AssetDatabase:
    """SQLite-based asset database for fast querying and organization"""
    
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()
    
    def _init_database(self):
        """Initialize database schema"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS assets (
                    asset_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    asset_type TEXT NOT NULL,
                    faction TEXT NOT NULL,
                    description TEXT,
                    status TEXT NOT NULL,
                    version TEXT NOT NULL,
                    quality_score REAL,
                    usage_count INTEGER DEFAULT 0,
                    created_at REAL NOT NULL,
                    updated_at REAL NOT NULL,
                    last_accessed REAL,
                    asset_spec_json TEXT NOT NULL,
                    metadata_json TEXT
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS asset_files (
                    file_id TEXT PRIMARY KEY,
                    asset_id TEXT NOT NULL,
                    path TEXT NOT NULL,
                    file_type TEXT NOT NULL,
                    format TEXT NOT NULL,
                    size_bytes INTEGER,
                    checksum TEXT,
                    created_at REAL NOT NULL,
                    metadata_json TEXT,
                    FOREIGN KEY (asset_id) REFERENCES assets (asset_id)
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS asset_tags (
                    asset_id TEXT NOT NULL,
                    tag TEXT NOT NULL,
                    PRIMARY KEY (asset_id, tag),
                    FOREIGN KEY (asset_id) REFERENCES assets (asset_id)
                )
            """)
            
            # Create indexes for fast queries
            conn.execute("CREATE INDEX IF NOT EXISTS idx_assets_type ON assets (asset_type)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_assets_faction ON assets (faction)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_assets_status ON assets (status)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_assets_quality ON assets (quality_score)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_assets_created ON assets (created_at)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_tags_tag ON asset_tags (tag)")
            
            conn.commit()
    
    def insert_asset(self, record: AssetRecord) -> bool:
        """Insert new asset record"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Insert main asset record
                conn.execute("""
                    INSERT INTO assets (
                        asset_id, name, asset_type, faction, description, status, version,
                        quality_score, usage_count, created_at, updated_at, last_accessed,
                        asset_spec_json, metadata_json
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    record.asset_id,
                    record.asset_spec.name,
                    record.asset_spec.asset_type,
                    record.asset_spec.faction,
                    record.asset_spec.description,
                    record.status.value,
                    record.version,
                    record.quality_score,
                    record.usage_count,
                    record.created_at,
                    record.updated_at,
                    record.last_accessed,
                    json.dumps(record.asset_spec.to_dict()),
                    json.dumps(record.metadata)
                ))
                
                # Insert files
                for file_record in record.files:
                    file_id = f"{record.asset_id}_{file_record.file_type}_{int(file_record.created_at)}"
                    conn.execute("""
                        INSERT INTO asset_files (
                            file_id, asset_id, path, file_type, format, size_bytes,
                            checksum, created_at, metadata_json
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        file_id,
                        record.asset_id,
                        str(file_record.path),
                        file_record.file_type,
                        file_record.format,
                        file_record.size_bytes,
                        file_record.checksum,
                        file_record.created_at,
                        json.dumps(file_record.metadata)
                    ))
                
                # Insert tags
                for tag in record.tags:
                    conn.execute("""
                        INSERT OR IGNORE INTO asset_tags (asset_id, tag) VALUES (?, ?)
                    """, (record.asset_id, tag))
                
                conn.commit()
                return True
                
        except Exception as e:
            logger.error(f"Failed to insert asset {record.asset_id}: {e}")
            return False
    
    def get_asset(self, asset_id: str) -> Optional[AssetRecord]:
        """Get asset record by ID"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                
                # Get main asset data
                cursor = conn.execute("""
                    SELECT * FROM assets WHERE asset_id = ?
                """, (asset_id,))
                
                row = cursor.fetchone()
                if not row:
                    return None
                
                # Reconstruct asset spec
                asset_spec_data = json.loads(row['asset_spec_json'])
                asset_spec = AssetSpecification.from_dict(asset_spec_data)
                
                # Get files
                file_cursor = conn.execute("""
                    SELECT * FROM asset_files WHERE asset_id = ?
                """, (asset_id,))
                
                files = []
                for file_row in file_cursor.fetchall():
                    file_metadata = json.loads(file_row['metadata_json'] or '{}')
                    asset_file = AssetFile(
                        path=Path(file_row['path']),
                        file_type=file_row['file_type'],
                        format=file_row['format'],
                        size_bytes=file_row['size_bytes'],
                        checksum=file_row['checksum'],
                        created_at=file_row['created_at'],
                        metadata=file_metadata
                    )
                    files.append(asset_file)
                
                # Get tags
                tag_cursor = conn.execute("""
                    SELECT tag FROM asset_tags WHERE asset_id = ?
                """, (asset_id,))
                
                tags = [tag_row[0] for tag_row in tag_cursor.fetchall()]
                
                # Create record
                metadata = json.loads(row['metadata_json'] or '{}')
                record = AssetRecord(
                    asset_id=row['asset_id'],
                    asset_spec=asset_spec,
                    status=AssetStatus(row['status']),
                    version=row['version'],
                    created_at=row['created_at'],
                    updated_at=row['updated_at'],
                    files=files,
                    tags=tags,
                    quality_score=row['quality_score'],
                    usage_count=row['usage_count'],
                    last_accessed=row['last_accessed'],
                    metadata=metadata
                )
                
                return record
                
        except Exception as e:
            logger.error(f"Failed to get asset {asset_id}: {e}")
            return None
    
    def search_assets(self, 
                     asset_type: Optional[AssetType] = None,
                     faction: Optional[FactionCode] = None,
                     status: Optional[AssetStatus] = None,
                     tags: Optional[List[str]] = None,
                     min_quality: Optional[float] = None,
                     max_quality: Optional[float] = None,
                     created_after: Optional[float] = None,
                     created_before: Optional[float] = None,
                     name_pattern: Optional[str] = None,
                     limit: int = 100) -> List[AssetRecord]:
        """Search assets with various filters"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                
                # Build query
                query_parts = ["SELECT DISTINCT a.asset_id FROM assets a"]
                params = []
                where_conditions = []
                
                if tags:
                    query_parts.append("JOIN asset_tags t ON a.asset_id = t.asset_id")
                
                if asset_type:
                    where_conditions.append("a.asset_type = ?")
                    params.append(asset_type)
                
                if faction:
                    where_conditions.append("a.faction = ?")
                    params.append(faction)
                
                if status:
                    where_conditions.append("a.status = ?")
                    params.append(status.value)
                
                if min_quality is not None:
                    where_conditions.append("a.quality_score >= ?")
                    params.append(min_quality)
                
                if max_quality is not None:
                    where_conditions.append("a.quality_score <= ?")
                    params.append(max_quality)
                
                if created_after:
                    where_conditions.append("a.created_at >= ?")
                    params.append(created_after)
                
                if created_before:
                    where_conditions.append("a.created_at <= ?")
                    params.append(created_before)
                
                if name_pattern:
                    where_conditions.append("a.name LIKE ?")
                    params.append(f"%{name_pattern}%")
                
                if tags:
                    tag_placeholders = ",".join("?" * len(tags))
                    where_conditions.append(f"t.tag IN ({tag_placeholders})")
                    params.extend(tags)
                
                if where_conditions:
                    query_parts.append("WHERE " + " AND ".join(where_conditions))
                
                query_parts.append("ORDER BY a.created_at DESC")
                query_parts.append("LIMIT ?")
                params.append(limit)
                
                query = " ".join(query_parts)
                
                cursor = conn.execute(query, params)
                asset_ids = [row[0] for row in cursor.fetchall()]
                
                # Get full records
                records = []
                for asset_id in asset_ids:
                    record = self.get_asset(asset_id)
                    if record:
                        records.append(record)
                
                return records
                
        except Exception as e:
            logger.error(f"Asset search failed: {e}")
            return []
    
    def update_asset_status(self, asset_id: str, status: AssetStatus) -> bool:
        """Update asset status"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    UPDATE assets SET status = ?, updated_at = ? WHERE asset_id = ?
                """, (status.value, time.time(), asset_id))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Failed to update status for {asset_id}: {e}")
            return False
    
    def update_usage_stats(self, asset_id: str) -> bool:
        """Update usage statistics"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    UPDATE assets 
                    SET usage_count = usage_count + 1, last_accessed = ?
                    WHERE asset_id = ?
                """, (time.time(), asset_id))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Failed to update usage stats for {asset_id}: {e}")
            return False
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get database statistics"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("SELECT COUNT(*) FROM assets")
                total_assets = cursor.fetchone()[0]
                
                # Assets by type
                cursor = conn.execute("""
                    SELECT asset_type, COUNT(*) FROM assets GROUP BY asset_type
                """)
                by_type = dict(cursor.fetchall())
                
                # Assets by faction
                cursor = conn.execute("""
                    SELECT faction, COUNT(*) FROM assets GROUP BY faction
                """)
                by_faction = dict(cursor.fetchall())
                
                # Assets by status
                cursor = conn.execute("""
                    SELECT status, COUNT(*) FROM assets GROUP BY status
                """)
                by_status = dict(cursor.fetchall())
                
                # Quality statistics
                cursor = conn.execute("""
                    SELECT AVG(quality_score), MIN(quality_score), MAX(quality_score)
                    FROM assets WHERE quality_score IS NOT NULL
                """)
                quality_stats = cursor.fetchone()
                
                return {
                    "total_assets": total_assets,
                    "by_type": by_type,
                    "by_faction": by_faction,
                    "by_status": by_status,
                    "quality_stats": {
                        "average": quality_stats[0] if quality_stats[0] else 0,
                        "minimum": quality_stats[1] if quality_stats[1] else 0,
                        "maximum": quality_stats[2] if quality_stats[2] else 0
                    }
                }
                
        except Exception as e:
            logger.error(f"Failed to get statistics: {e}")
            return {}

class AssetOrganizer:
    """Handles physical file organization and directory structure"""
    
    def __init__(self, base_path: Path):
        self.base_path = base_path
        self.base_path.mkdir(parents=True, exist_ok=True)
        
        # Standard directory structure
        self.structure = {
            "assets": self.base_path / "assets",
            "previews": self.base_path / "previews", 
            "metadata": self.base_path / "metadata",
            "archive": self.base_path / "archive",
            "temp": self.base_path / "temp"
        }
        
        # Create directories
        for dir_path in self.structure.values():
            dir_path.mkdir(parents=True, exist_ok=True)
    
    def organize_asset_files(self, asset_record: AssetRecord) -> Dict[str, Path]:
        """Organize files for an asset according to standard structure"""
        organized_paths = {}
        
        try:
            # Create asset-specific directory
            asset_dir = self.structure["assets"] / asset_record.asset_spec.faction / asset_record.asset_spec.asset_type
            asset_dir.mkdir(parents=True, exist_ok=True)
            
            preview_dir = self.structure["previews"] / asset_record.asset_spec.faction / asset_record.asset_spec.asset_type
            preview_dir.mkdir(parents=True, exist_ok=True)
            
            metadata_dir = self.structure["metadata"] / asset_record.asset_spec.faction / asset_record.asset_spec.asset_type
            metadata_dir.mkdir(parents=True, exist_ok=True)
            
            for asset_file in asset_record.files:
                if not asset_file.path.exists():
                    logger.warning(f"Source file not found: {asset_file.path}")
                    continue
                
                # Determine destination based on file type
                if asset_file.file_type == "final":
                    dest_dir = asset_dir
                    dest_name = f"{asset_record.asset_spec.name}_v{asset_record.version}.{asset_file.format}"
                elif asset_file.file_type == "preview":
                    dest_dir = preview_dir
                    dest_name = f"{asset_record.asset_spec.name}_preview.{asset_file.format}"
                elif asset_file.file_type == "metadata":
                    dest_dir = metadata_dir
                    dest_name = f"{asset_record.asset_spec.name}_metadata.{asset_file.format}"
                else:
                    dest_dir = asset_dir
                    dest_name = f"{asset_record.asset_spec.name}_{asset_file.file_type}.{asset_file.format}"
                
                dest_path = dest_dir / dest_name
                
                # Copy file if it's not already in the right place
                if asset_file.path != dest_path:
                    shutil.copy2(asset_file.path, dest_path)
                    logger.info(f"Organized: {asset_file.path} -> {dest_path}")
                
                organized_paths[asset_file.file_type] = dest_path
            
            return organized_paths
            
        except Exception as e:
            logger.error(f"Failed to organize files for {asset_record.asset_id}: {e}")
            return {}
    
    def create_asset_preview(self, asset_file: AssetFile, asset_record: AssetRecord) -> Optional[Path]:
        """Create preview/thumbnail for asset"""
        try:
            if asset_file.format.lower() not in ['png', 'jpg', 'jpeg']:
                return None
            
            from PIL import Image
            
            # Load and resize image
            with Image.open(asset_file.path) as img:
                # Create thumbnail
                img.thumbnail((512, 512), Image.Resampling.LANCZOS)
                
                # Save preview
                preview_dir = self.structure["previews"] / asset_record.asset_spec.faction / asset_record.asset_spec.asset_type
                preview_dir.mkdir(parents=True, exist_ok=True)
                
                preview_path = preview_dir / f"{asset_record.asset_spec.name}_preview.jpg"
                img.convert('RGB').save(preview_path, 'JPEG', quality=85)
                
                return preview_path
                
        except Exception as e:
            logger.error(f"Failed to create preview for {asset_file.path}: {e}")
            return None
    
    def archive_asset(self, asset_record: AssetRecord) -> bool:
        """Archive an asset (move to archive directory)"""
        try:
            archive_dir = self.structure["archive"] / asset_record.asset_spec.faction / asset_record.asset_spec.asset_type
            archive_dir.mkdir(parents=True, exist_ok=True)
            
            # Move all files to archive
            for asset_file in asset_record.files:
                if asset_file.path.exists():
                    archive_path = archive_dir / asset_file.path.name
                    shutil.move(asset_file.path, archive_path)
                    logger.info(f"Archived: {asset_file.path} -> {archive_path}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to archive asset {asset_record.asset_id}: {e}")
            return False
    
    def cleanup_temp_files(self, older_than_hours: int = 24) -> int:
        """Clean up temporary files older than specified hours"""
        cleaned_count = 0
        cutoff_time = time.time() - (older_than_hours * 3600)
        
        try:
            temp_dir = self.structure["temp"]
            for file_path in temp_dir.rglob("*"):
                if file_path.is_file() and file_path.stat().st_mtime < cutoff_time:
                    file_path.unlink()
                    cleaned_count += 1
                    
            logger.info(f"Cleaned up {cleaned_count} temporary files")
            return cleaned_count
            
        except Exception as e:
            logger.error(f"Failed to cleanup temp files: {e}")
            return 0

class AssetVersionManager:
    """Handles asset versioning and history"""
    
    def __init__(self, database: AssetDatabase):
        self.database = database
    
    def create_new_version(self, asset_id: str, version_type: AssetVersion = AssetVersion.MINOR) -> str:
        """Create new version string"""
        record = self.database.get_asset(asset_id)
        if not record:
            return "1.0.0"
        
        current_version = record.version
        parts = current_version.split('.')
        
        try:
            major, minor, patch = int(parts[0]), int(parts[1]), int(parts[2] if len(parts) > 2 else 0)
        except ValueError:
            return "1.0.0"
        
        if version_type == AssetVersion.MAJOR:
            return f"{major + 1}.0.0"
        elif version_type == AssetVersion.MINOR:
            return f"{major}.{minor + 1}.0"
        else:  # PATCH
            return f"{major}.{minor}.{patch + 1}"
    
    def get_asset_history(self, base_name: str, faction: FactionCode, asset_type: AssetType) -> List[AssetRecord]:
        """Get version history for an asset"""
        records = self.database.search_assets(
            asset_type=asset_type,
            faction=faction,
            name_pattern=base_name
        )
        
        # Filter and sort by version
        history = [r for r in records if r.asset_spec.name.startswith(base_name)]
        history.sort(key=lambda r: self._version_key(r.version), reverse=True)
        
        return history
    
    def _version_key(self, version: str) -> Tuple[int, int, int]:
        """Convert version string to sortable tuple"""
        try:
            parts = version.split('.')
            return (int(parts[0]), int(parts[1]), int(parts[2] if len(parts) > 2 else 0))
        except (ValueError, IndexError):
            return (0, 0, 0)

class AssetManager:
    """
    Comprehensive asset management system for Terminal Grounds.
    Handles asset storage, organization, discovery, and lifecycle management.
    """
    
    def __init__(self, base_path: Path, db_path: Optional[Path] = None):
        self.base_path = base_path
        self.base_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize components
        self.database = AssetDatabase(db_path or (base_path / "assets.db"))
        self.organizer = AssetOrganizer(base_path)
        self.version_manager = AssetVersionManager(self.database)
        
        logger.info(f"Asset Manager initialized at {base_path}")
    
    def register_asset(self, 
                      asset_spec: AssetSpecification,
                      files: List[Path],
                      quality_score: Optional[float] = None,
                      status: AssetStatus = AssetStatus.DRAFT,
                      tags: Optional[List[str]] = None) -> Optional[AssetRecord]:
        """Register a new asset in the system"""
        
        try:
            # Generate asset ID
            asset_id = self._generate_asset_id(asset_spec)
            
            # Create asset files
            asset_files = []
            for file_path in files:
                if not file_path.exists():
                    logger.warning(f"File not found: {file_path}")
                    continue
                
                # Calculate checksum
                checksum = self._calculate_checksum(file_path)
                
                # Determine file type and format
                file_type = self._determine_file_type(file_path, asset_spec)
                file_format = file_path.suffix.lstrip('.')
                
                asset_file = AssetFile(
                    path=file_path,
                    file_type=file_type,
                    format=file_format,
                    size_bytes=file_path.stat().st_size,
                    checksum=checksum,
                    created_at=time.time()
                )
                asset_files.append(asset_file)
            
            if not asset_files:
                logger.error("No valid files provided for asset registration")
                return None
            
            # Create asset record
            current_time = time.time()
            record = AssetRecord(
                asset_id=asset_id,
                asset_spec=asset_spec,
                status=status,
                version="1.0.0",
                created_at=current_time,
                updated_at=current_time,
                files=asset_files,
                tags=tags or [],
                quality_score=quality_score
            )
            
            # Organize files
            organized_paths = self.organizer.organize_asset_files(record)
            
            # Update file paths to organized locations
            for asset_file in record.files:
                if asset_file.file_type in organized_paths:
                    asset_file.path = organized_paths[asset_file.file_type]
            
            # Create preview if needed
            primary_file = record.primary_file
            if primary_file and primary_file.format.lower() in ['png', 'jpg', 'jpeg']:
                preview_path = self.organizer.create_asset_preview(primary_file, record)
                if preview_path:
                    preview_file = AssetFile(
                        path=preview_path,
                        file_type="preview",
                        format="jpg",
                        size_bytes=preview_path.stat().st_size,
                        checksum=self._calculate_checksum(preview_path),
                        created_at=time.time()
                    )
                    record.files.append(preview_file)
            
            # Save to database
            success = self.database.insert_asset(record)
            if success:
                logger.info(f"Asset registered: {asset_id}")
                return record
            else:
                logger.error(f"Failed to save asset to database: {asset_id}")
                return None
                
        except Exception as e:
            logger.error(f"Failed to register asset: {e}")
            return None
    
    def get_asset(self, asset_id: str) -> Optional[AssetRecord]:
        """Get asset by ID and update usage stats"""
        record = self.database.get_asset(asset_id)
        if record:
            self.database.update_usage_stats(asset_id)
        return record
    
    def search_assets(self, **kwargs) -> List[AssetRecord]:
        """Search assets with filters"""
        return self.database.search_assets(**kwargs)
    
    def update_asset_status(self, asset_id: str, status: AssetStatus) -> bool:
        """Update asset status"""
        return self.database.update_asset_status(asset_id, status)
    
    def create_asset_version(self, asset_id: str, 
                           new_files: List[Path],
                           version_type: AssetVersion = AssetVersion.MINOR,
                           quality_score: Optional[float] = None) -> Optional[AssetRecord]:
        """Create new version of existing asset"""
        
        original_record = self.database.get_asset(asset_id)
        if not original_record:
            logger.error(f"Original asset not found: {asset_id}")
            return None
        
        try:
            # Generate new version
            new_version = self.version_manager.create_new_version(asset_id, version_type)
            new_asset_id = f"{asset_id}_v{new_version.replace('.', '_')}"
            
            # Create new asset record based on original
            new_spec = original_record.asset_spec
            new_spec.version += 1
            
            # Register new version
            new_record = self.register_asset(
                asset_spec=new_spec,
                files=new_files,
                quality_score=quality_score,
                status=AssetStatus.DRAFT,
                tags=original_record.tags.copy()
            )
            
            if new_record:
                new_record.version = new_version
                # Update database with correct version
                self.database.update_asset_status(new_record.asset_id, new_record.status)
                
            return new_record
            
        except Exception as e:
            logger.error(f"Failed to create asset version: {e}")
            return None
    
    def archive_asset(self, asset_id: str) -> bool:
        """Archive an asset"""
        record = self.database.get_asset(asset_id)
        if not record:
            return False
        
        # Move files to archive
        success = self.organizer.archive_asset(record)
        if success:
            # Update status in database
            return self.database.update_asset_status(asset_id, AssetStatus.ARCHIVED)
        
        return False
    
    def get_asset_statistics(self) -> Dict[str, Any]:
        """Get comprehensive asset statistics"""
        db_stats = self.database.get_statistics()
        
        # Add file system statistics
        total_size = 0
        file_count = 0
        
        try:
            for path in self.organizer.structure["assets"].rglob("*"):
                if path.is_file():
                    total_size += path.stat().st_size
                    file_count += 1
        except Exception as e:
            logger.warning(f"Failed to calculate file system stats: {e}")
        
        db_stats.update({
            "file_system": {
                "total_files": file_count,
                "total_size_mb": total_size / (1024 * 1024),
                "total_size_gb": total_size / (1024 * 1024 * 1024)
            }
        })
        
        return db_stats
    
    def cleanup_assets(self, dry_run: bool = True) -> Dict[str, Any]:
        """Clean up orphaned files and optimize storage"""
        cleanup_report = {
            "orphaned_files": [],
            "missing_files": [],
            "temp_files_cleaned": 0,
            "space_freed_mb": 0
        }
        
        try:
            # Clean temporary files
            cleaned_count = self.organizer.cleanup_temp_files()
            cleanup_report["temp_files_cleaned"] = cleaned_count
            
            # Find orphaned files (files not in database)
            db_file_paths = set()
            
            # Get all file paths from database
            all_assets = self.database.search_assets(limit=10000)  # Adjust limit as needed
            for asset in all_assets:
                for asset_file in asset.files:
                    db_file_paths.add(str(asset_file.path))
            
            # Check file system for orphaned files
            for asset_dir in self.organizer.structure["assets"].rglob("*"):
                if asset_dir.is_file():
                    if str(asset_dir) not in db_file_paths:
                        cleanup_report["orphaned_files"].append(str(asset_dir))
                        if not dry_run:
                            size = asset_dir.stat().st_size
                            asset_dir.unlink()
                            cleanup_report["space_freed_mb"] += size / (1024 * 1024)
            
            # Check for missing files (in database but not on disk)
            for file_path in db_file_paths:
                if not Path(file_path).exists():
                    cleanup_report["missing_files"].append(file_path)
            
            logger.info(f"Cleanup report: {cleanup_report}")
            return cleanup_report
            
        except Exception as e:
            logger.error(f"Cleanup failed: {e}")
            return cleanup_report
    
    def export_asset_catalog(self, output_path: Path, format: str = "json") -> bool:
        """Export complete asset catalog"""
        try:
            all_assets = self.database.search_assets(limit=10000)
            
            catalog_data = {
                "export_timestamp": time.time(),
                "total_assets": len(all_assets),
                "assets": []
            }
            
            for asset in all_assets:
                asset_data = {
                    "asset_id": asset.asset_id,
                    "name": asset.asset_spec.name,
                    "type": asset.asset_spec.asset_type,
                    "faction": asset.asset_spec.faction,
                    "description": asset.asset_spec.description,
                    "status": asset.status.value,
                    "version": asset.version,
                    "quality_score": asset.quality_score,
                    "created_at": asset.created_at,
                    "tags": asset.tags,
                    "files": [
                        {
                            "path": str(f.path),
                            "type": f.file_type,
                            "format": f.format,
                            "size_mb": f.size_bytes / (1024 * 1024)
                        }
                        for f in asset.files
                    ]
                }
                catalog_data["assets"].append(asset_data)
            
            # Save catalog
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            if format.lower() == "json":
                with open(output_path, 'w') as f:
                    json.dump(catalog_data, f, indent=2)
            else:
                logger.error(f"Unsupported export format: {format}")
                return False
            
            logger.info(f"Asset catalog exported to {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to export asset catalog: {e}")
            return False
    
    def _generate_asset_id(self, asset_spec: AssetSpecification) -> str:
        """Generate unique asset ID"""
        # Create ID based on faction, type, and name
        base = f"{asset_spec.faction}_{asset_spec.asset_type}_{asset_spec.name}"
        
        # Clean the base string
        import re
        base = re.sub(r'[^a-zA-Z0-9_]', '_', base)
        base = re.sub(r'_+', '_', base).strip('_')
        
        # Add timestamp for uniqueness
        timestamp = int(time.time())
        
        return f"{base}_{timestamp}"
    
    def _calculate_checksum(self, file_path: Path) -> str:
        """Calculate SHA-256 checksum of file"""
        try:
            sha256_hash = hashlib.sha256()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(chunk)
            return sha256_hash.hexdigest()
        except Exception as e:
            logger.warning(f"Failed to calculate checksum for {file_path}: {e}")
            return ""
    
    def _determine_file_type(self, file_path: Path, asset_spec: AssetSpecification) -> str:
        """Determine file type based on path and content"""
        suffix = file_path.suffix.lower()
        name = file_path.stem.lower()
        
        if "preview" in name or "thumb" in name:
            return "preview"
        elif suffix == ".json":
            return "metadata"
        elif suffix in [".png", ".jpg", ".jpeg"]:
            return "final"  # Assume main output unless specified otherwise
        elif suffix in [".uasset", ".umap"]:
            return "ue5_asset"
        else:
            return "source"