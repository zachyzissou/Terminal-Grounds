#!/usr/bin/env python3
"""
Quick quality analysis of current TG_PERFECT generation batch
"""
import os
from pathlib import Path

def analyze_current_batch():
    output_dir = Path("C:/Users/Zachg/Terminal-Grounds/Tools/Comfy/ComfyUI-API/output/environments")
    
    # Find TG_PERFECT files with 00001_ pattern
    perfect_files = list(output_dir.glob("TG_PERFECT_*00001_*.png"))
    
    if not perfect_files:
        print("No TG_PERFECT files found with 00001_ pattern")
        return
    
    print(f"CURRENT BATCH QUALITY ANALYSIS")
    print("=" * 50)
    print(f"Found {len(perfect_files)} TG_PERFECT assets")
    print()
    
    # Quality assessment based on file size
    quality_grades = {"MASTERPIECE": 0, "EXCELLENT": 0, "PRODUCTION": 0, "NEEDS_WORK": 0}
    
    for file_path in sorted(perfect_files):
        file_size_mb = file_path.stat().st_size / (1024 * 1024)
        
        # Quality grading based on file size
        if file_size_mb >= 2.0:
            grade = "MASTERPIECE"
        elif file_size_mb >= 1.2:
            grade = "EXCELLENT"
        elif file_size_mb >= 0.8:
            grade = "PRODUCTION"
        else:
            grade = "NEEDS_WORK"
        
        quality_grades[grade] += 1
        
        print(f"{file_path.name}")
        print(f"  Size: {file_size_mb:.2f} MB - {grade}")
        print()
    
    # Calculate success metrics
    total = len(perfect_files)
    aaa_ready = quality_grades["MASTERPIECE"] + quality_grades["EXCELLENT"]
    aaa_percentage = (aaa_ready / total) * 100 if total > 0 else 0
    
    print("QUALITY SUMMARY:")
    print(f"Total Assets: {total}")
    print(f"AAA Ready (1.2MB+): {aaa_ready}/{total} ({aaa_percentage:.1f}%)")
    print(f"Masterpiece (2MB+): {quality_grades['MASTERPIECE']}")
    print(f"Excellent (1.2-2MB): {quality_grades['EXCELLENT']}")
    print(f"Production (0.8-1.2MB): {quality_grades['PRODUCTION']}")
    print(f"Needs Work (<0.8MB): {quality_grades['NEEDS_WORK']}")
    
    mission_status = "SUCCESS" if quality_grades["NEEDS_WORK"] == 0 and aaa_percentage >= 85 else "ITERATION REQUIRED"
    print(f"\n100% AAA MISSION STATUS: {mission_status}")

if __name__ == "__main__":
    analyze_current_batch()