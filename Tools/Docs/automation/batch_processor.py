"""
Terminal Grounds Documentation Automation Framework
Phase 4.0.3: Batch Processing System

Efficient bulk operations for large-scale documentation management,
including parallel processing, incremental updates, and intelligent caching.
"""

import os
import time
import yaml
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable, Tuple
from dataclasses import dataclass
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging
from queue import Queue
import threading

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class ProcessingResult:
    """Result of processing a single document"""
    file_path: str
    success: bool
    operation: str
    changes_made: bool
    error_message: Optional[str] = None
    processing_time: float = 0.0
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class BatchOperation:
    """Definition of a batch operation"""
    name: str
    description: str
    operation_func: Callable
    requires_frontmatter: bool = True
    modifies_content: bool = False
    parallel_safe: bool = True

class DocumentCache:
    """
    Intelligent caching system for document processing
    """

    def __init__(self, cache_dir: str = "../../Tools/Docs/cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.cache_index = {}
        self._load_cache_index()

    def _load_cache_index(self):
        """Load cache index from disk"""
        index_file = self.cache_dir / "cache_index.json"
        if index_file.exists():
            try:
                with open(index_file, 'r', encoding='utf-8') as f:
                    import json
                    self.cache_index = json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load cache index: {e}")
                self.cache_index = {}

    def _save_cache_index(self):
        """Save cache index to disk"""
        index_file = self.cache_dir / "cache_index.json"
        try:
            import json
            with open(index_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache_index, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save cache index: {e}")

    def get_file_hash(self, file_path: str) -> str:
        """Calculate file hash for change detection"""
        try:
            with open(file_path, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()
        except Exception:
            return ""

    def is_file_changed(self, file_path: str) -> bool:
        """Check if file has changed since last processing"""
        current_hash = self.get_file_hash(file_path)
        cached_hash = self.cache_index.get(file_path, {}).get('hash', '')

        return current_hash != cached_hash

    def update_cache(self, file_path: str, metadata: Optional[Dict[str, Any]] = None):
        """Update cache entry for file"""
        current_hash = self.get_file_hash(file_path)
        file_stat = os.stat(file_path)

        self.cache_index[file_path] = {
            'hash': current_hash,
            'modified_time': file_stat.st_mtime,
            'size': file_stat.st_size,
            'last_processed': datetime.now().isoformat(),
            'metadata': metadata or {}
        }

        self._save_cache_index()

    def get_cached_metadata(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Get cached metadata for file"""
        return self.cache_index.get(file_path, {}).get('metadata')

    def clear_cache(self, pattern: Optional[str] = None):
        """Clear cache entries"""
        if pattern:
            # Remove entries matching pattern
            keys_to_remove = [k for k in self.cache_index.keys() if pattern in k]
            for key in keys_to_remove:
                del self.cache_index[key]
        else:
            # Clear all cache
            self.cache_index = {}

        self._save_cache_index()

class ParallelProcessor:
    """
    Parallel processing engine for bulk document operations
    """

    def __init__(self, max_workers: int = 4):
        self.max_workers = max_workers
        self.executor = ThreadPoolExecutor(max_workers=max_workers)

    def process_batch(self, files: List[str], operation: BatchOperation,
                     progress_callback: Optional[Callable] = None) -> List[ProcessingResult]:
        """
        Process a batch of files with the given operation
        """
        results = []
        futures = {}

        # Submit all tasks
        for file_path in files:
            if operation.parallel_safe:
                future = self.executor.submit(self._process_single_file, file_path, operation)
                futures[future] = file_path
            else:
                # Process sequentially for non-parallel-safe operations
                result = self._process_single_file(file_path, operation)
                results.append(result)

                if progress_callback:
                    progress_callback(len(results), len(files), result)

        # Collect parallel results
        for future in as_completed(futures):
            file_path = futures[future]
            try:
                result = future.result()
                results.append(result)

                if progress_callback:
                    progress_callback(len(results), len(files), result)

            except Exception as e:
                logger.error(f"Error processing {file_path}: {e}")
                results.append(ProcessingResult(
                    file_path=file_path,
                    success=False,
                    operation=operation.name,
                    changes_made=False,
                    error_message=str(e)
                ))

        return results

    def _process_single_file(self, file_path: str, operation: BatchOperation) -> ProcessingResult:
        """Process a single file with the given operation"""
        start_time = time.time()

        try:
            # Read document
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Extract frontmatter if required
            frontmatter = None
            body_content = content

            if operation.requires_frontmatter and content.startswith('---'):
                parts = content.split('---', 2)
                if len(parts) >= 3:
                    try:
                        frontmatter = yaml.safe_load(parts[1])
                        body_content = parts[2]
                    except yaml.YAMLError:
                        pass

            # Execute operation
            result_data = operation.operation_func(file_path, content, frontmatter, body_content)

            # Handle result
            if isinstance(result_data, dict):
                success = result_data.get('success', True)
                changes_made = result_data.get('changes_made', False)
                new_content = result_data.get('new_content')
                metadata = result_data.get('metadata', {})

                # Write changes if needed
                if changes_made and new_content and operation.modifies_content:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(new_content)
            else:
                success = True
                changes_made = False
                metadata = {}

            processing_time = time.time() - start_time

            return ProcessingResult(
                file_path=file_path,
                success=success,
                operation=operation.name,
                changes_made=changes_made,
                processing_time=processing_time,
                metadata=metadata
            )

        except Exception as e:
            processing_time = time.time() - start_time
            return ProcessingResult(
                file_path=file_path,
                success=False,
                operation=operation.name,
                changes_made=False,
                error_message=str(e),
                processing_time=processing_time
            )

class BatchOperationsManager:
    """
    Manager for batch operations with caching and progress tracking
    """

    def __init__(self, docs_root: str = "../../docs", max_workers: int = 4):
        self.docs_root = Path(docs_root)
        self.cache = DocumentCache()
        self.processor = ParallelProcessor(max_workers)
        self.operations = self._define_operations()

    def _define_operations(self) -> Dict[str, BatchOperation]:
        """Define available batch operations"""
        return {
            'validate_frontmatter': BatchOperation(
                name='validate_frontmatter',
                description='Validate frontmatter compliance',
                operation_func=self._validate_frontmatter_operation,
                requires_frontmatter=True,
                modifies_content=False,
                parallel_safe=True
            ),
            'update_dates': BatchOperation(
                name='update_dates',
                description='Update last_reviewed dates',
                operation_func=self._update_dates_operation,
                requires_frontmatter=True,
                modifies_content=True,
                parallel_safe=True
            ),
            'fix_formatting': BatchOperation(
                name='fix_formatting',
                description='Fix common formatting issues',
                operation_func=self._fix_formatting_operation,
                requires_frontmatter=False,
                modifies_content=True,
                parallel_safe=True
            ),
            'add_missing_fields': BatchOperation(
                name='add_missing_fields',
                description='Add missing required frontmatter fields',
                operation_func=self._add_missing_fields_operation,
                requires_frontmatter=True,
                modifies_content=True,
                parallel_safe=True
            ),
            'generate_cross_references': BatchOperation(
                name='generate_cross_references',
                description='Auto-generate related document suggestions',
                operation_func=self._generate_cross_references_operation,
                requires_frontmatter=True,
                modifies_content=True,
                parallel_safe=True
            ),
            'bulk_rename': BatchOperation(
                name='bulk_rename',
                description='Rename files to follow naming conventions',
                operation_func=self._bulk_rename_operation,
                requires_frontmatter=True,
                modifies_content=False,
                parallel_safe=False  # File system operations
            )
        }

    def execute_batch_operation(self, operation_name: str, file_pattern: str = "*.md",
                               use_cache: bool = True, progress_callback: Optional[Callable] = None) -> Dict[str, Any]:
        """
        Execute a batch operation on matching files
        """
        if operation_name not in self.operations:
            raise ValueError(f"Unknown operation: {operation_name}")

        operation = self.operations[operation_name]

        # Find matching files
        files = []
        for pattern in file_pattern.split(','):
            pattern = pattern.strip()
            if '**' in pattern:
                files.extend([str(f) for f in self.docs_root.rglob(pattern)])
            else:
                files.extend([str(f) for f in self.docs_root.glob(pattern)])

        # Remove duplicates
        files = list(set(files))

        # Filter out non-markdown files and special files
        files = [f for f in files if f.endswith('.md') and not f.endswith('README.md')]

        logger.info(f"Found {len(files)} files for batch operation: {operation_name}")

        # Filter files based on cache if enabled
        if use_cache:
            changed_files = []
            for file_path in files:
                if self.cache.is_file_changed(file_path):
                    changed_files.append(file_path)
                else:
                    logger.debug(f"Skipping unchanged file: {file_path}")

            files = changed_files
            logger.info(f"Processing {len(files)} changed files (cache enabled)")

        if not files:
            return {
                'success': True,
                'message': 'No files to process',
                'results': [],
                'summary': {'total': 0, 'successful': 0, 'failed': 0, 'changed': 0}
            }

        # Execute operation
        start_time = time.time()
        results = self.processor.process_batch(files, operation, progress_callback)

        # Update cache for processed files
        for result in results:
            if result.success:
                self.cache.update_cache(result.file_path, result.metadata)

        # Calculate summary
        total_time = time.time() - start_time
        successful = sum(1 for r in results if r.success)
        changed = sum(1 for r in results if r.changes_made)

        summary = {
            'total': len(results),
            'successful': successful,
            'failed': len(results) - successful,
            'changed': changed,
            'total_time': round(total_time, 2),
            'avg_time_per_file': round(total_time / len(results), 3) if results else 0
        }

        logger.info(f"Batch operation completed: {summary}")

        return {
            'success': True,
            'message': f'Processed {len(results)} files in {summary["total_time"]}s',
            'results': results,
            'summary': summary
        }

    # Operation implementations
    def _validate_frontmatter_operation(self, file_path: str, content: str,
                                       frontmatter: Optional[Dict], body: str) -> Dict[str, Any]:
        """Validate frontmatter compliance"""
        if not frontmatter:
            return {'success': False, 'error': 'Missing frontmatter'}

        required_fields = ['title', 'type', 'domain', 'status', 'last_reviewed', 'maintainer']
        missing_fields = [f for f in required_fields if f not in frontmatter]

        if missing_fields:
            return {
                'success': False,
                'error': f'Missing fields: {missing_fields}',
                'metadata': {'missing_fields': missing_fields}
            }

        return {'success': True, 'metadata': {'valid': True}}

    def _update_dates_operation(self, file_path: str, content: str,
                               frontmatter: Optional[Dict], body: str) -> Dict[str, Any]:
        """Update last_reviewed dates"""
        if not frontmatter:
            return {'success': False, 'error': 'Missing frontmatter'}

        today = datetime.now().strftime('%Y-%m-%d')
        frontmatter['last_reviewed'] = today

        new_frontmatter_yaml = yaml.dump(frontmatter, default_flow_style=False, sort_keys=False)
        new_content = f"---\n{new_frontmatter_yaml}---\n{body}"

        return {
            'success': True,
            'changes_made': True,
            'new_content': new_content,
            'metadata': {'updated_date': today}
        }

    def _fix_formatting_operation(self, file_path: str, content: str,
                                 frontmatter: Optional[Dict], body: str) -> Dict[str, Any]:
        """Fix common formatting issues"""
        lines = content.split('\n')
        fixed_lines = []
        changes_made = False

        for line in lines:
            original_line = line

            # Remove trailing whitespace
            line = line.rstrip()

            # Fix multiple consecutive blank lines
            if fixed_lines and not line.strip() and not fixed_lines[-1].strip():
                continue  # Skip this blank line

            fixed_lines.append(line)

            if line != original_line:
                changes_made = True

        new_content = '\n'.join(fixed_lines)

        return {
            'success': True,
            'changes_made': changes_made,
            'new_content': new_content if changes_made else None,
            'metadata': {'formatting_fixed': changes_made}
        }

    def _add_missing_fields_operation(self, file_path: str, content: str,
                                     frontmatter: Optional[Dict], body: str) -> Dict[str, Any]:
        """Add missing required frontmatter fields"""
        if not frontmatter:
            return {'success': False, 'error': 'Missing frontmatter'}

        required_fields = {
            'title': Path(file_path).stem.replace('_', ' ').title(),
            'type': 'reference',
            'domain': 'technical',
            'status': 'draft',
            'last_reviewed': datetime.now().strftime('%Y-%m-%d'),
            'maintainer': 'Documentation Team',
            'tags': [],
            'related_docs': []
        }

        changes_made = False
        for field, default_value in required_fields.items():
            if field not in frontmatter:
                frontmatter[field] = default_value
                changes_made = True

        if changes_made:
            new_frontmatter_yaml = yaml.dump(frontmatter, default_flow_style=False, sort_keys=False)
            new_content = f"---\n{new_frontmatter_yaml}---\n{body}"

            return {
                'success': True,
                'changes_made': True,
                'new_content': new_content,
                'metadata': {'fields_added': [f for f in required_fields.keys() if f not in frontmatter]}
            }

        return {'success': True, 'changes_made': False}

    def _generate_cross_references_operation(self, file_path: str, content: str,
                                            frontmatter: Optional[Dict], body: str) -> Dict[str, Any]:
        """Generate cross-reference suggestions"""
        if not frontmatter:
            return {'success': False, 'error': 'Missing frontmatter'}

        # Simple cross-reference generation based on keywords
        keywords = []
        if 'tags' in frontmatter and frontmatter['tags']:
            keywords.extend(frontmatter['tags'])

        # Extract keywords from content
        words = body.lower().split()
        common_keywords = ['api', 'guide', 'reference', 'process', 'design']
        found_keywords = [w for w in words if w in common_keywords]

        keywords.extend(found_keywords)
        keywords = list(set(keywords))  # Remove duplicates

        # Generate related docs based on keywords
        related_docs = []
        if 'api' in keywords:
            related_docs.append("API_REFERENCE.md")
        if 'design' in keywords:
            related_docs.append("DESIGN_GUIDELINES.md")
        if 'process' in keywords:
            related_docs.append("WORKFLOW_GUIDE.md")

        if related_docs and 'related_docs' not in frontmatter:
            frontmatter['related_docs'] = related_docs

            new_frontmatter_yaml = yaml.dump(frontmatter, default_flow_style=False, sort_keys=False)
            new_content = f"---\n{new_frontmatter_yaml}---\n{body}"

            return {
                'success': True,
                'changes_made': True,
                'new_content': new_content,
                'metadata': {'related_docs_added': related_docs}
            }

        return {'success': True, 'changes_made': False}

    def _bulk_rename_operation(self, file_path: str, content: str,
                              frontmatter: Optional[Dict], body: str) -> Dict[str, Any]:
        """Rename files to follow naming conventions"""
        if not frontmatter:
            return {'success': False, 'error': 'Missing frontmatter'}

        current_path = Path(file_path)
        domain = frontmatter.get('domain', 'technical')

        # Generate new filename based on domain and title
        title = frontmatter.get('title', current_path.stem)
        new_filename = title.replace(' ', '_').replace('-', '_') + '.md'

        # Apply domain-specific patterns
        if domain == 'process':
            new_filename = new_filename  # Already in PascalCase format
        elif domain == 'technical':
            new_filename = new_filename  # Keep as-is for technical
        else:
            new_filename = new_filename  # General case

        new_path = current_path.parent / new_filename

        if new_path != current_path and not new_path.exists():
            try:
                current_path.rename(new_path)
                return {
                    'success': True,
                    'changes_made': True,
                    'metadata': {
                        'old_path': str(current_path),
                        'new_path': str(new_path)
                    }
                }
            except Exception as e:
                return {'success': False, 'error': str(e)}

        return {'success': True, 'changes_made': False}

def main():
    """Main function for batch processing system demonstration"""
    print("Terminal Grounds Batch Processing System")
    print("=" * 45)

    # Initialize batch processor
    batch_manager = BatchOperationsManager()

    print(f"Available operations: {list(batch_manager.operations.keys())}")

    # Example: Update dates for all documents
    print(f"\n🔄 Executing batch operation: update_dates")

    def progress_callback(processed, total, result):
        if processed % 10 == 0 or processed == total:
            print(f"  Progress: {processed}/{total} files processed")

    result = batch_manager.execute_batch_operation(
        'update_dates',
        file_pattern='*.md',
        use_cache=True,
        progress_callback=progress_callback
    )

    print(f"\n📊 Batch Operation Results:")
    print(f"  Success: {result['success']}")
    print(f"  Message: {result['message']}")
    print(f"  Summary: {result['summary']}")

    # Example: Validate frontmatter
    print(f"\n✅ Executing batch operation: validate_frontmatter")
    validation_result = batch_manager.execute_batch_operation(
        'validate_frontmatter',
        file_pattern='*.md',
        use_cache=False
    )

    print(f"\n📊 Validation Results:")
    print(f"  Total files: {validation_result['summary']['total']}")
    print(f"  Successful: {validation_result['summary']['successful']}")
    print(f"  Failed: {validation_result['summary']['failed']}")

    if validation_result['summary']['failed'] > 0:
        print("  Failed files:")
        for r in validation_result['results']:
            if not r.success:
                print(f"    - {r.file_path}: {r.error_message}")

    # Cache statistics
    print(f"\n💾 Cache Statistics:")
    cache_stats = batch_manager.cache.cache_index
    print(f"  Cached files: {len(cache_stats)}")
    if cache_stats:
        total_size = sum(entry.get('size', 0) for entry in cache_stats.values())
        print(f"  Total cached size: {total_size} bytes")

    print("\n🚀 Batch Processing System operational!")
    print("Phase 4.0.3: Batch Processing System complete!")
    print("Phase 4.0: Advanced Automation Foundation - COMPLETE!")

if __name__ == "__main__":
    main()
