#!/usr/bin/env python3
import os,glob,json,hashlib,datetime,re
ROOT=os.path.abspath(os.path.join(os.path.dirname(__file__),"..",".."))
os.chdir(ROOT)

def gather(patts):
  out=[]
  [out.extend([p.replace("\\","/") for p in glob.glob(pt,recursive=True) if os.path.isfile(p)]) for pt in patts]
  return sorted(out)

def h(paths):
  m=hashlib.sha256()
  [m.update(open(p,"rb").read(4096)) for p in paths if os.path.isfile(p)]
  return m.hexdigest()[:12]

emblems=gather(["Content/TG/Decals/Factions/**/*.*"])
posters=gather(["Content/TG/Decals/Posters/**/*.*","Docs/Concepts/Posters/**/*.png"])
icons=gather(["Content/TG/Icons/**/*.*"])
palettes=gather(["Docs/Concepts/Palettes/**/*.png"])
renders=gather(["Docs/Concepts/Renders/**/*.*"])
style_tiles=gather(["Docs/Concepts/StyleTiles/**/*.png"])

uepaths=[]
log="Docs/Phase4_Implementation_Log.md"
if os.path.isfile(log):
  uepaths=sorted(set(re.findall(r"(/Game/TG/[^\s)]+)", open(log,encoding="utf-8",errors="ignore").read())))
manifest={
 "generated_at":datetime.datetime.utcnow().isoformat()+"Z",
 "counts":{"emblems":len(emblems),"posters":len(posters),"icons":len(icons),"palettes":len(palettes),"renders":len(renders),"style_tiles":len(style_tiles),"ue_paths_logged":len(uepaths)},
 "files":{"emblems":emblems,"posters":posters,"icons":icons,"palettes":palettes,"renders":renders,"style_tiles":style_tiles},
 "ue_paths":uepaths,"hash":h(emblems+posters+icons+palettes+renders+style_tiles)
}
os.makedirs("Docs/Concepts",exist_ok=True)
json.dump(manifest,open("Docs/Concepts/ASSET_MANIFEST.json","w"),indent=2)
open("Docs/Concepts/ASSET_MANIFEST.md","w").write("# Asset Manifest (auto)\n\n"+"\n".join([f"- **{k}**: {v}" for k,v in manifest["counts"].items()])+f"\n\nHash `{manifest['hash']}` • {manifest['generated_at']}\n")
print("Manifest built.")
