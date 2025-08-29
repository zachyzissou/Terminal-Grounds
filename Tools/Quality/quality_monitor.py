#!/usr/bin/env python3
"""
Real-time Quality Monitor for ComfyUI Generations

Monitors output directory for new images and performs immediate quality assessment.
Alerts on blurry generations and maintains quality metrics database.
"""

import time
import json
import cv2
import numpy as np
from pathlib import Path
from datetime import datetime
import sqlite3
from typing import Dict, List, Optional

class QualityMonitor:
    def __init__(self, output_dir: str, db_path: str = "quality_metrics.db"):
        self.output_dir = Path(output_dir)
        self.db_path = Path(db_path)
        self.processed_files = set()
        self.sharpness_threshold = 60.0
        self._init_db()
        self._load_processed()

    def _init_db(self):
        """Initialize SQLite database for quality metrics"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS quality_metrics (
                    id INTEGER PRIMARY KEY,
                    filepath TEXT UNIQUE,
                    timestamp TEXT,
                    width INTEGER,
                    height INTEGER,
                    sharpness REAL,
                    brightness REAL,
                    exposure_clipping REAL,
                    edge_density REAL,
                    category TEXT,
                    decision TEXT,
                    reasons TEXT
                )
            ''')

    def _load_processed(self):
        """Load previously processed files from database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('SELECT filepath FROM quality_metrics')
            self.processed_files = {row[0] for row in cursor.fetchall()}

    def analyze_image(self, image_path: Path) -> Dict:
        """Analyze single image for quality metrics"""
        img = cv2.imread(str(image_path))
        if img is None:
            return {"error": "Failed to load image"}

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        h, w = img.shape[:2]

        # Sharpness (variance of Laplacian)
        sharpness = float(cv2.Laplacian(gray, cv2.CV_64F).var())

        # Brightness
        brightness = float(gray.mean())

        # Exposure clipping
        hist = cv2.calcHist([gray], [0], None, [256], [0, 256]).flatten()
        total = float(hist.sum()) or 1.0
        clipped = float(hist[0] + hist[-1]) / total

        # Edge density
        edges = cv2.Canny(gray, 100, 200)
        edge_density = float((edges > 0).sum()) / float(edges.size)

        # Category detection
        category = "environment"  # Default
        if any(term in str(image_path).lower() for term in ["emblem", "logo", "icon"]):
            category = "logo"

        # Decision logic
        reasons = []
        if sharpness < self.sharpness_threshold:
            reasons.append(f"Low sharpness: {sharpness:.1f}")
        if brightness < 25.0:
            reasons.append(f"Too dark: {brightness:.1f}")
        if brightness > 230.0:
            reasons.append(f"Too bright: {brightness:.1f}")
        if clipped > 0.20:
            reasons.append(f"High exposure clipping: {clipped:.3f}")

        decision = "REJECT" if reasons else "PASS"

        return {
            "filepath": str(image_path),
            "timestamp": datetime.now().isoformat(),
            "width": w,
            "height": h,
            "sharpness": sharpness,
            "brightness": brightness,
            "exposure_clipping": clipped,
            "edge_density": edge_density,
            "category": category,
            "decision": decision,
            "reasons": json.dumps(reasons)
        }

    def save_metrics(self, metrics: Dict):
        """Save quality metrics to database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT OR REPLACE INTO quality_metrics
                (filepath, timestamp, width, height, sharpness, brightness,
                 exposure_clipping, edge_density, category, decision, reasons)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                metrics["filepath"], metrics["timestamp"], metrics["width"],
                metrics["height"], metrics["sharpness"], metrics["brightness"],
                metrics["exposure_clipping"], metrics["edge_density"],
                metrics["category"], metrics["decision"], metrics["reasons"]
            ))

    def monitor(self):
        """Main monitoring loop"""
        print("Starting quality monitor...")

        while True:
            try:
                # Find new PNG files
                for png_file in self.output_dir.rglob("*.png"):
                    if str(png_file) not in self.processed_files:
                        print(f"Analyzing: {png_file.name}")

                        metrics = self.analyze_image(png_file)
                        if "error" not in metrics:
                            self.save_metrics(metrics)
                            self.processed_files.add(str(png_file))

                            # Alert on blurry generations
                            if metrics["decision"] == "REJECT":
                                print(f"🚨 BLURRY GENERATION DETECTED: {png_file.name}")
                                print(f"   Sharpness: {metrics['sharpness']:.1f} (threshold: {self.sharpness_threshold})")
                                if metrics["reasons"]:
                                    reasons = json.loads(metrics["reasons"])
                                    for reason in reasons:
                                        print(f"   - {reason}")

                time.sleep(2)  # Check every 2 seconds

            except KeyboardInterrupt:
                print("Monitor stopped by user")
                break
            except Exception as e:
                print(f"Monitor error: {e}")
                time.sleep(5)

if __name__ == "__main__":
    monitor = QualityMonitor("Tools/Comfy/ComfyUI-API/output")
    monitor.monitor()
