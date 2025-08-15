"""
Terminal Grounds - Output Monitor
==================================
Standalone script to watch ComfyUI output folder and organize generated assets.
Can be run independently of the main generator.
"""

import os
import time
import shutil
from pathlib import Path
from datetime import datetime
import webbrowser

# Configuration
COMFYUI_OUTPUT = Path(r"C:\Users\Zachg\Documents\ComfyUI\output")
PROJECT_ROOT = Path(r"C:\Users\Zachg\Terminal-Grounds")
REVIEW_DIR = PROJECT_ROOT / "Tools" / "ArtGen" / "outputs" / "review"
APPROVED_DIR = PROJECT_ROOT / "Tools" / "ArtGen" / "outputs" / "approved"

def setup_directories():
    """Create necessary directories"""
    REVIEW_DIR.mkdir(parents=True, exist_ok=True)
    APPROVED_DIR.mkdir(parents=True, exist_ok=True)
    
    for subfolder in ["Emblems", "Posters", "Icons", "Misc"]:
        (REVIEW_DIR / subfolder).mkdir(exist_ok=True)
        (APPROVED_DIR / subfolder).mkdir(exist_ok=True)

def categorize_file(filename):
    """Determine asset category from filename"""
    if "Emblem" in filename:
        return "Emblems"
    elif "Poster" in filename:
        return "Posters"
    elif "Icon" in filename:
        return "Icons"
    else:
        return "Misc"

def generate_dashboard():
    """Generate HTML dashboard for reviewing assets"""
    
    html = """
<!DOCTYPE html>
<html>
<head>
    <title>TG Asset Review</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', Arial, sans-serif;
            background: linear-gradient(135deg, #0a0a0a 0%, #1a1a1a 100%);
            color: #e0e0e0;
            padding: 20px;
            min-height: 100vh;
        }
        .header {
            text-align: center;
            margin-bottom: 30px;
            padding: 20px;
            background: rgba(0,255,0,0.1);
            border: 2px solid #00ff00;
            border-radius: 10px;
        }
        h1 {
            color: #00ff00;
            text-transform: uppercase;
            letter-spacing: 3px;
            font-size: 2.5em;
            margin-bottom: 10px;
            text-shadow: 0 0 20px rgba(0,255,0,0.5);
        }
        .stats {
            display: flex;
            justify-content: center;
            gap: 30px;
            margin: 20px 0;
        }
        .stat {
            background: rgba(255,255,255,0.05);
            padding: 15px 25px;
            border-radius: 8px;
            border: 1px solid rgba(0,255,0,0.3);
        }
        .stat-value {
            font-size: 2em;
            color: #00ff00;
            font-weight: bold;
        }
        .stat-label {
            font-size: 0.9em;
            color: #888;
            text-transform: uppercase;
        }
        .category {
            margin: 40px 0;
            background: rgba(255,255,255,0.02);
            border-radius: 10px;
            padding: 20px;
            border: 1px solid rgba(0,255,0,0.2);
        }
        h2 {
            color: #00ff00;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid rgba(0,255,0,0.3);
        }
        .assets {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
            gap: 25px;
        }
        .asset {
            background: rgba(42,42,42,0.8);
            border: 2px solid #333;
            border-radius: 10px;
            overflow: hidden;
            transition: all 0.3s ease;
            position: relative;
        }
        .asset:hover {
            transform: translateY(-5px);
            border-color: #00ff00;
            box-shadow: 0 10px 30px rgba(0,255,0,0.3);
        }
        .asset img {
            width: 100%;
            height: 250px;
            object-fit: contain;
            background: #000;
            display: block;
        }
        .asset-info {
            padding: 15px;
        }
        .asset-name {
            font-size: 0.85em;
            color: #aaa;
            margin-bottom: 10px;
            word-break: break-all;
            font-family: 'Courier New', monospace;
        }
        .asset-actions {
            display: flex;
            gap: 10px;
        }
        button {
            flex: 1;
            padding: 8px;
            border: 2px solid #00ff00;
            background: transparent;
            color: #00ff00;
            cursor: pointer;
            font-weight: bold;
            text-transform: uppercase;
            transition: all 0.2s;
            border-radius: 5px;
        }
        button:hover {
            background: #00ff00;
            color: #000;
            transform: scale(1.05);
        }
        button.reject {
            border-color: #ff3333;
            color: #ff3333;
        }
        button.reject:hover {
            background: #ff3333;
        }
        .timestamp {
            text-align: center;
            margin-top: 30px;
            color: #666;
            font-size: 0.9em;
        }
        .no-assets {
            text-align: center;
            padding: 40px;
            color: #666;
            font-style: italic;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>⚡ Terminal Grounds Asset Review ⚡</h1>
        <div class="stats">
            <div class="stat">
                <div class="stat-value">{total}</div>
                <div class="stat-label">Total Generated</div>
            </div>
            <div class="stat">
                <div class="stat-value">{pending}</div>
                <div class="stat-label">Pending Review</div>
            </div>
            <div class="stat">
                <div class="stat-value">{approved}</div>
                <div class="stat-label">Approved</div>
            </div>
        </div>
    </div>
"""
    
    total = 0
    pending = 0
    approved = len(list(APPROVED_DIR.glob("**/*.png")))
    
    # Add categories
    for category in ["Emblems", "Posters", "Icons", "Misc"]:
        folder = REVIEW_DIR / category
        if folder.exists():
            assets = list(folder.glob("*.png"))
            pending += len(assets)
            total += len(assets)
            
            html += f"""
    <div class="category">
        <h2>📁 {category} ({len(assets)} items)</h2>
"""
            
            if assets:
                html += '<div class="assets">'
                for asset in sorted(assets, key=lambda x: x.stat().st_mtime, reverse=True):
                    rel_path = asset.relative_to(REVIEW_DIR).as_posix()
                    html += f"""
            <div class="asset">
                <img src="{rel_path}" alt="{asset.name}">
                <div class="asset-info">
                    <div class="asset-name">{asset.name}</div>
                    <div class="asset-actions">
                        <button onclick="approveAsset('{rel_path}')">✓ Approve</button>
                        <button class="reject" onclick="rejectAsset('{rel_path}')">✗ Reject</button>
                    </div>
                </div>
            </div>
"""
                html += '</div>'
            else:
                html += '<div class="no-assets">No assets in this category yet</div>'
                
            html += '</div>'
    
    total += approved
    
    # Add footer and scripts
    html += """
    <div class="timestamp">Last updated: {timestamp}</div>
    
    <script>
        function approveAsset(path) {
            if(confirm('Approve ' + path + '?')) {
                // Move to approved folder
                alert('To approve: Move file from review/' + path + ' to approved/' + path);
            }
        }
        
        function rejectAsset(path) {
            if(confirm('Delete ' + path + '?')) {
                alert('To reject: Delete file from review/' + path);
            }
        }
        
        // Auto-refresh every 5 seconds
        setTimeout(() => location.reload(), 5000);
    </script>
</body>
</html>
""".format(
        total=total,
        pending=pending,
        approved=approved,
        timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )
    
    dashboard_path = REVIEW_DIR / "dashboard.html"
    dashboard_path.write_text(html)
    
    return dashboard_path

def watch_output():
    """Main watching loop"""
    
    print("""
╔══════════════════════════════════════════════════════════╗
║        TERMINAL GROUNDS - OUTPUT MONITOR v1.0           ║
╚══════════════════════════════════════════════════════════╝
    """)
    
    setup_directories()
    
    print(f"📁 Watching: {COMFYUI_OUTPUT}")
    print(f"📂 Review folder: {REVIEW_DIR}")
    print(f"✅ Approved folder: {APPROVED_DIR}")
    print()
    
    # Check if output folder exists
    if not COMFYUI_OUTPUT.exists():
        print(f"⚠️ Output folder not found: {COMFYUI_OUTPUT}")
        print("Please update the COMFYUI_OUTPUT path in this script")
        return
    
    # Initial scan
    known_files = set(os.listdir(COMFYUI_OUTPUT))
    print(f"Found {len(known_files)} existing files")
    
    # Generate initial dashboard
    dashboard = generate_dashboard()
    print(f"\n📊 Dashboard created: {dashboard}")
    print("\nPress Ctrl+C to stop monitoring")
    print("-" * 60)
    
    # Open dashboard in browser
    webbrowser.open(str(dashboard))
    
    try:
        while True:
            current_files = set(os.listdir(COMFYUI_OUTPUT))
            new_files = current_files - known_files
            
            for filename in new_files:
                if filename.startswith("TG_") and filename.endswith(".png"):
                    source = COMFYUI_OUTPUT / filename
                    category = categorize_file(filename)
                    dest = REVIEW_DIR / category / filename
                    
                    try:
                        shutil.copy2(source, dest)
                        print(f"✅ New asset: {filename} -> {category}/")
                        
                        # Update dashboard
                        generate_dashboard()
                        
                    except Exception as e:
                        print(f"❌ Error copying {filename}: {e}")
            
            known_files = current_files
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n\n👋 Monitoring stopped")
        print(f"📊 Review your assets at: {dashboard}")

if __name__ == "__main__":
    watch_output()
