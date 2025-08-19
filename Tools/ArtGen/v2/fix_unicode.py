#!/usr/bin/env python3
"""Fix Unicode characters in terminal_grounds_pipeline.py for Windows compatibility"""

import re

def fix_unicode_in_file(file_path):
    """Replace Unicode emojis with ASCII equivalents"""
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Define replacements
    replacements = [
        ('🚀', '[INIT]'),
        ('✅', '[OK]'),
        ('❌', '[ERROR]'),
        ('🛑', '[STOP]'),
        ('🎨', '[GEN]'),
        ('📊', '[BATCH]'),
        ('🏛️', '[FACTION]'),
        ('✨', '[ENHANCE]'),
        ('🎮', '[UE5]'),
        ('🔍', '[SEARCH]'),
        ('📋', '[STATUS]'),
        ('🧪', '[TEST]'),
        ('🎯', '[INTER]'),
        ('⚠️', '[WARN]'),
        ('⚪', '[INFO]'),
        ('👋', '[BYE]'),
        ('🎉', '[SUCCESS]'),
        ('⭐', '[QUALITY]'),
        ('🖥️', '[CLIENT]'),
        ('⏳', '[WAIT]'),
        ('📈', '[PROGRESS]'),
        ('⏰', '[TIMEOUT]'),
        ('🔧', '[HEALTH]'),
    ]
    
    # Apply replacements
    for emoji, replacement in replacements:
        content = content.replace(emoji, replacement)
    
    # Write back
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Fixed Unicode characters in {file_path}")

if __name__ == "__main__":
    fix_unicode_in_file("terminal_grounds_pipeline.py")