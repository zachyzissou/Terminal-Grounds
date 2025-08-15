#!/usr/bin/env python3
"""
artgen_plan_from_placeholder_report.py

Reads Docs/.placeholder_report.json and drafts a batch plan JSON focused on:
- UI icons (icon class) -> 1024x1024
- Concept art (concept class) -> 2048x2048
Skips any paths that already have a high-res sibling (e.g., *_1024.* or *_2048.*).
"""
import os, json
ROOT=os.path.abspath(os.path.join(os.path.dirname(__file__),"..",".."))
os.chdir(ROOT)

report_path="Docs/.placeholder_report.json"
plan_out="Tools/ArtGen/outputs/batch_from_report.plan.json"

if not os.path.isfile(report_path):
  raise SystemExit("No placeholder report found. Run Tools/validate_placeholders.py first.")

r=json.load(open(report_path))
items=[]
for it in r.get("items",[]):
  p=it.get("path","")
  klass=it.get("class")
  if not klass: continue
  base,ext=os.path.splitext(p)
  if klass=="icon":
    # Skip if a 1024 sibling exists already
    if os.path.isfile(f"{base}_1024.png"): continue
    items.append({
      "category":"ui-icon",
      "target": f"{base}_1024.png",
      "prompt": "Terminal Grounds UI icon, clean vector-like glyph matching filename semantics, bold silhouette, high contrast, no text, flat shading, dark sci-fi UI kit",
      "negative": "photo, 3d scene, text, watermark"
    })
  elif klass=="concept":
    # Docs concept -> write a new 2048 sibling in same folder with _2048 suffix
    if os.path.isfile(f"{base}_2048.png"): continue
    items.append({
      "category":"concept",
      "target": f"{base}_2048.png",
      "prompt": "Terminal Grounds concept art, painterly sci-fi consistent with lore and style guide, high detail, atmospheric lighting, 2048x2048",
      "negative": "text, logo, watermark, UI"
    })

plan={"batch":"auto-from-report","model":"flux-1-schnell","defaults":{"steps":6,"width":1024,"height":1024},"items":items}
os.makedirs(os.path.dirname(plan_out),exist_ok=True)
json.dump(plan,open(plan_out,"w"),indent=2)
print(f"Drafted {len(items)} items to {plan_out}")
