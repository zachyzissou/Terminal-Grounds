#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Terminal Grounds Documentation Graph Database
AI-Powered Documentation Control System with Graph Relationships
"""

import os
import json
import sqlite3
import hashlib
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Set
import networkx as nx
from collections import defaultdict, Counter

class DocumentGraphDatabase:
    """Graph-based documentation management with AI analysis capabilities"""
    
    def __init__(self, project_root: str = "C:/Users/Zachg/Terminal-Grounds"):
        self.project_root = Path(project_root)
        self.db_path = self.project_root / "Tools/DocumentControl/doc_graph.db"
        self.graph = nx.DiGraph()
        self.doc_metadata = {}
        self.quality_scores = {}
        self.init_database()
        
    def init_database(self):
        """Initialize SQLite database for persistent storage"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Documents table with comprehensive metadata
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                path TEXT UNIQUE NOT NULL,
                title TEXT,
                category TEXT,
                priority INTEGER DEFAULT 3,
                status TEXT DEFAULT 'active',
                owner TEXT,
                last_updated TIMESTAMP,
                content_hash TEXT,
                word_count INTEGER,
                quality_score REAL,
                completeness_score REAL,
                consistency_score REAL,
                doc_references TEXT,
                dependencies TEXT,
                tags TEXT,
                ai_summary TEXT,
                improvement_suggestions TEXT
            )
        ''')
        
        # Document relationships table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS relationships (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_doc_id INTEGER,
                target_doc_id INTEGER,
                relationship_type TEXT,
                strength REAL,
                auto_detected BOOLEAN DEFAULT 1,
                FOREIGN KEY (source_doc_id) REFERENCES documents (id),
                FOREIGN KEY (target_doc_id) REFERENCES documents (id)
            )
        ''')
        
        # Quality metrics table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS quality_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                doc_id INTEGER,
                metric_name TEXT,
                metric_value REAL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (doc_id) REFERENCES documents (id)
            )
        ''')
        
        # Duplicate detection table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS duplicates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                doc1_id INTEGER,
                doc2_id INTEGER,
                similarity_score REAL,
                detection_method TEXT,
                suggested_action TEXT,
                FOREIGN KEY (doc1_id) REFERENCES documents (id),
                FOREIGN KEY (doc2_id) REFERENCES documents (id)
            )
        ''')
        
        conn.commit()
        conn.close()
        
    def scan_documentation(self) -> Dict[str, int]:
        """Scan project for all markdown files and build graph"""
        stats = {
            'total_files': 0,
            'new_files': 0,
            'updated_files': 0,
            'relationships_found': 0,
            'duplicates_found': 0
        }
        
        # Find all markdown files
        md_files = list(self.project_root.rglob('*.md'))
        stats['total_files'] = len(md_files)
        
        for md_file in md_files:
            if self.process_document(md_file):
                stats['new_files'] += 1
            else:
                stats['updated_files'] += 1
                
        # Build relationship graph
        stats['relationships_found'] = self.detect_relationships()
        
        # Find duplicates
        stats['duplicates_found'] = self.detect_duplicates()
        
        return stats
        
    def process_document(self, file_path: Path) -> bool:
        """Process a single document and extract metadata"""
        relative_path = file_path.relative_to(self.project_root)
        
        try:
            content = file_path.read_text(encoding='utf-8')
        except Exception:
            return False
            
        # Calculate content hash
        content_hash = hashlib.md5(content.encode()).hexdigest()
        
        # Extract metadata
        metadata = self.extract_metadata(content, file_path)
        metadata['path'] = str(relative_path)
        metadata['content_hash'] = content_hash
        metadata['last_updated'] = datetime.fromtimestamp(file_path.stat().st_mtime)
        
        # Calculate quality scores
        scores = self.calculate_quality_scores(content, metadata)
        metadata.update(scores)
        
        # Store in database
        return self.store_document(metadata)
        
    def extract_metadata(self, content: str, file_path: Path) -> Dict:
        """Extract metadata from document content"""
        metadata = {
            'title': None,
            'category': self.infer_category(file_path),
            'word_count': len(content.split()),
            'references': [],
            'tags': []
        }
        
        # Extract title from first heading
        title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        if title_match:
            metadata['title'] = title_match.group(1)
        else:
            metadata['title'] = file_path.stem.replace('_', ' ').title()
            
        # Extract references (links to other docs)
        ref_pattern = r'\[([^\]]+)\]\(([^)]+\.md)\)'
        references = re.findall(ref_pattern, content)
        metadata['references'] = [ref[1] for ref in references]
        
        # Extract tags (if present)
        tag_match = re.search(r'^Tags?:\s*(.+)$', content, re.MULTILINE | re.IGNORECASE)
        if tag_match:
            metadata['tags'] = [t.strip() for t in tag_match.group(1).split(',')]
            
        return metadata
        
    def infer_category(self, file_path: Path) -> str:
        """Infer document category from path"""
        parts = file_path.parts
        
        if 'docs' in parts or 'Docs' in parts:
            if 'Design' in parts:
                return 'design'
            elif 'Lore' in parts:
                return 'lore'
            elif 'technical' in parts:
                return 'technical'
            elif 'guides' in parts:
                return 'guide'
        elif 'Tools' in parts:
            return 'tooling'
        elif 'Content' in parts:
            return 'content'
            
        return 'general'
        
    def calculate_quality_scores(self, content: str, metadata: Dict) -> Dict:
        """Calculate comprehensive quality scores for a document"""
        scores = {
            'quality_score': 0.0,
            'completeness_score': 0.0,
            'consistency_score': 0.0
        }
        
        # Completeness check
        completeness_factors = [
            len(content) > 100,  # Not empty
            metadata['title'] is not None,  # Has title
            '## ' in content,  # Has sections
            metadata['word_count'] > 50,  # Meaningful content
            len(metadata['references']) > 0 or metadata['category'] == 'general',  # Has refs or standalone
        ]
        scores['completeness_score'] = sum(completeness_factors) / len(completeness_factors) * 100
        
        # Consistency check
        consistency_factors = [
            bool(re.search(r'^#\s+', content, re.MULTILINE)),  # Has proper heading
            content.count('```') % 2 == 0,  # Code blocks are closed
            not bool(re.search(r'\[TODO\]|\[WIP\]|XXX|FIXME', content, re.IGNORECASE)),  # No TODOs
            not bool(re.search(r'\d{4}-\d{2}-\d{2}', content)),  # No hardcoded dates
        ]
        scores['consistency_score'] = sum(consistency_factors) / len(consistency_factors) * 100
        
        # Overall quality score
        scores['quality_score'] = (scores['completeness_score'] + scores['consistency_score']) / 2
        
        return scores
        
    def detect_relationships(self) -> int:
        """Detect relationships between documents"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get all documents
        cursor.execute('SELECT id, path, doc_references FROM documents')
        docs = cursor.fetchall()
        
        relationship_count = 0
        
        for doc_id, doc_path, references_json in docs:
            if references_json:
                references = json.loads(references_json) if references_json else []
                
                for ref in references:
                    # Find target document
                    cursor.execute('SELECT id FROM documents WHERE path LIKE ?', (f'%{ref}',))
                    target = cursor.fetchone()
                    
                    if target:
                        # Add relationship
                        cursor.execute('''
                            INSERT OR REPLACE INTO relationships 
                            (source_doc_id, target_doc_id, relationship_type, strength)
                            VALUES (?, ?, ?, ?)
                        ''', (doc_id, target[0], 'references', 1.0))
                        relationship_count += 1
                        
                        # Add to graph
                        self.graph.add_edge(doc_path, ref, type='reference')
                        
        conn.commit()
        conn.close()
        
        return relationship_count
        
    def detect_duplicates(self) -> int:
        """Detect potential duplicate documents"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get all documents
        cursor.execute('SELECT id, path, title, content_hash FROM documents')
        docs = cursor.fetchall()
        
        duplicates_found = 0
        
        for i, (id1, path1, title1, hash1) in enumerate(docs):
            for id2, path2, title2, hash2 in docs[i+1:]:
                similarity = 0.0
                action = None
                
                # Check for identical content
                if hash1 == hash2:
                    similarity = 1.0
                    action = 'merge'
                # Check for similar titles
                elif title1 and title2 and self.similar_strings(title1, title2) > 0.8:
                    similarity = 0.8
                    action = 'review'
                # Check for similar paths
                elif self.similar_strings(Path(path1).stem, Path(path2).stem) > 0.7:
                    similarity = 0.7
                    action = 'review'
                    
                if similarity > 0.6:
                    cursor.execute('''
                        INSERT OR REPLACE INTO duplicates
                        (doc1_id, doc2_id, similarity_score, detection_method, suggested_action)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (id1, id2, similarity, 'content_hash' if similarity == 1.0 else 'title_similarity', action))
                    duplicates_found += 1
                    
        conn.commit()
        conn.close()
        
        return duplicates_found
        
    def similar_strings(self, s1: str, s2: str) -> float:
        """Calculate string similarity using Jaccard coefficient"""
        s1_words = set(s1.lower().split())
        s2_words = set(s2.lower().split())
        
        if not s1_words or not s2_words:
            return 0.0
            
        intersection = s1_words & s2_words
        union = s1_words | s2_words
        
        return len(intersection) / len(union)
        
    def store_document(self, metadata: Dict) -> bool:
        """Store or update document in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check if document exists
        cursor.execute('SELECT id, content_hash FROM documents WHERE path = ?', (metadata['path'],))
        existing = cursor.fetchone()
        
        is_new = existing is None
        
        if is_new:
            # Insert new document
            cursor.execute('''
                INSERT INTO documents (
                    path, title, category, word_count, content_hash,
                    last_updated, quality_score, completeness_score,
                    consistency_score, doc_references, tags
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                metadata['path'], metadata['title'], metadata['category'],
                metadata['word_count'], metadata['content_hash'],
                metadata['last_updated'], metadata['quality_score'],
                metadata['completeness_score'], metadata['consistency_score'],
                json.dumps(metadata['references']), json.dumps(metadata['tags'])
            ))
        else:
            # Update if content changed
            if existing[1] != metadata['content_hash']:
                cursor.execute('''
                    UPDATE documents SET
                        title = ?, category = ?, word_count = ?,
                        content_hash = ?, last_updated = ?,
                        quality_score = ?, completeness_score = ?,
                        consistency_score = ?, doc_references = ?, tags = ?
                    WHERE path = ?
                ''', (
                    metadata['title'], metadata['category'], metadata['word_count'],
                    metadata['content_hash'], metadata['last_updated'],
                    metadata['quality_score'], metadata['completeness_score'],
                    metadata['consistency_score'], json.dumps(metadata['references']),
                    json.dumps(metadata['tags']), metadata['path']
                ))
                
        conn.commit()
        conn.close()
        
        return is_new
        
    def get_documentation_stats(self) -> Dict:
        """Get comprehensive documentation statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        stats = {}
        
        # Total documents by category
        cursor.execute('''
            SELECT category, COUNT(*) FROM documents
            GROUP BY category
        ''')
        stats['by_category'] = dict(cursor.fetchall())
        
        # Quality distribution
        cursor.execute('''
            SELECT 
                COUNT(CASE WHEN quality_score >= 85 THEN 1 END) as excellent,
                COUNT(CASE WHEN quality_score >= 70 AND quality_score < 85 THEN 1 END) as good,
                COUNT(CASE WHEN quality_score >= 50 AND quality_score < 70 THEN 1 END) as fair,
                COUNT(CASE WHEN quality_score < 50 THEN 1 END) as poor
            FROM documents
        ''')
        quality = cursor.fetchone()
        stats['quality_distribution'] = {
            'excellent': quality[0],
            'good': quality[1],
            'fair': quality[2],
            'poor': quality[3]
        }
        
        # Duplicates
        cursor.execute('SELECT COUNT(*) FROM duplicates')
        stats['duplicate_pairs'] = cursor.fetchone()[0]
        
        # Relationships
        cursor.execute('SELECT COUNT(*) FROM relationships')
        stats['relationships'] = cursor.fetchone()[0]
        
        # Average scores
        cursor.execute('''
            SELECT 
                AVG(quality_score) as avg_quality,
                AVG(completeness_score) as avg_completeness,
                AVG(consistency_score) as avg_consistency
            FROM documents
        ''')
        scores = cursor.fetchone()
        stats['average_scores'] = {
            'quality': round(scores[0], 2) if scores[0] else 0,
            'completeness': round(scores[1], 2) if scores[1] else 0,
            'consistency': round(scores[2], 2) if scores[2] else 0
        }
        
        conn.close()
        
        return stats
        
    def find_conflicting_documents(self) -> List[Tuple[str, str, str]]:
        """Find documents with potentially conflicting information"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        conflicts = []
        
        # Find documents with similar titles but different categories
        cursor.execute('''
            SELECT d1.path, d2.path, 'title_conflict'
            FROM documents d1, documents d2
            WHERE d1.id < d2.id
            AND d1.title = d2.title
            AND d1.category != d2.category
        ''')
        conflicts.extend(cursor.fetchall())
        
        # Find high-similarity duplicates
        cursor.execute('''
            SELECT 
                (SELECT path FROM documents WHERE id = doc1_id) as path1,
                (SELECT path FROM documents WHERE id = doc2_id) as path2,
                'high_similarity'
            FROM duplicates
            WHERE similarity_score > 0.8
        ''')
        conflicts.extend(cursor.fetchall())
        
        conn.close()
        
        return conflicts
        
    def generate_consolidation_plan(self) -> Dict:
        """Generate intelligent consolidation recommendations"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        plan = {
            'immediate_actions': [],
            'review_required': [],
            'archive_candidates': [],
            'merge_opportunities': []
        }
        
        # Find identical duplicates for immediate merging
        cursor.execute('''
            SELECT 
                (SELECT path FROM documents WHERE id = doc1_id) as path1,
                (SELECT path FROM documents WHERE id = doc2_id) as path2
            FROM duplicates
            WHERE similarity_score = 1.0
        ''')
        for path1, path2 in cursor.fetchall():
            plan['immediate_actions'].append({
                'action': 'merge',
                'files': [path1, path2],
                'reason': 'Identical content'
            })
            
        # Find low-quality documents for archival
        cursor.execute('''
            SELECT path, quality_score, word_count
            FROM documents
            WHERE quality_score < 50 OR word_count < 20
        ''')
        for path, score, words in cursor.fetchall():
            plan['archive_candidates'].append({
                'file': path,
                'reason': f'Low quality (score: {score:.1f}) or minimal content ({words} words)'
            })
            
        # Find similar documents for review
        cursor.execute('''
            SELECT 
                (SELECT path FROM documents WHERE id = doc1_id) as path1,
                (SELECT path FROM documents WHERE id = doc2_id) as path2,
                similarity_score
            FROM duplicates
            WHERE similarity_score >= 0.7 AND similarity_score < 1.0
        ''')
        for path1, path2, score in cursor.fetchall():
            plan['review_required'].append({
                'files': [path1, path2],
                'similarity': score,
                'suggested_action': 'consolidate' if score > 0.85 else 'review'
            })
            
        conn.close()
        
        return plan

if __name__ == '__main__':
    # Initialize the documentation graph database
    print("Initializing Terminal Grounds Documentation Graph Database...")
    doc_db = DocumentGraphDatabase()
    
    print("\nScanning documentation...")
    stats = doc_db.scan_documentation()
    
    print(f"\nScan Complete:")
    print(f"  Total Files: {stats['total_files']}")
    print(f"  New Files: {stats['new_files']}")
    print(f"  Updated Files: {stats['updated_files']}")
    print(f"  Relationships Found: {stats['relationships_found']}")
    print(f"  Duplicates Found: {stats['duplicates_found']}")
    
    print("\nDocumentation Statistics:")
    doc_stats = doc_db.get_documentation_stats()
    print(f"  Categories: {doc_stats['by_category']}")
    print(f"  Quality Distribution: {doc_stats['quality_distribution']}")
    print(f"  Average Scores: {doc_stats['average_scores']}")
    
    print("\nGenerating Consolidation Plan...")
    plan = doc_db.generate_consolidation_plan()
    print(f"  Immediate Merges: {len(plan['immediate_actions'])}")
    print(f"  Files Needing Review: {len(plan['review_required'])}")
    print(f"  Archive Candidates: {len(plan['archive_candidates'])}")
