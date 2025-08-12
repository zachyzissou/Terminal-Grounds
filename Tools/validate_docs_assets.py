#!/usr/bin/env python3
import sys,re,glob,os,json
ROOT=os.path.abspath(os.path.join(os.path.dirname(__file__),"..",".."))
os.chdir(ROOT)
FAIL=[r"\bTBD\b",r"\bPLACEHOLDER\b",r"\bNEW_ASSET\b"]
ALLOW=re.compile(r"Screenshot\s+TODO",re.I)
DOCS=["README.md","Docs/**/*.md","Design/**/*.md","World/**/*.md","Tech/**/*.md","Docs/Art/**/*.md","Docs/VFX/**/*.md","Docs/Audio/**/*.md"]
fails=[]
for patt in DOCS:
  for p in glob.glob(patt,recursive=True):
    if not os.path.isfile(p): continue
    for i,line in enumerate(open(p,"r",encoding="utf-8",errors="ignore").read().splitlines(),1):
      if ALLOW.search(line): continue
      if any(re.search(r, line) for r in FAIL): fails.append((p,i,line.strip()))
req=[("Docs/Art/ART_BIBLE.md",r"Content/TG/"),("Docs/VFX/VFX_BIBLE.md",r"\bNS_TG_"),("Docs/Art/UI_STYLE_GUIDE.md",r"\bWBP_TG_")]
for path,rx in req:
  if os.path.isfile(path) and not re.search(rx,open(path,"r",encoding="utf-8",errors="ignore").read()):
    fails.append((path,0,f"Missing required reference: {rx}"))
if os.environ.get("REQUIRE_RENDERS","false").lower() in ("1","true","yes"):
  rend=list(glob.glob("Docs/Concepts/Renders/**/*.*",recursive=True))
  if len([p for p in rend if os.path.isfile(p)])<1:
    fails.append(("Docs/Concepts/Renders",0,"Missing required look-dev renders (REQUIRE_RENDERS)"))
if fails:
  print("❌ Docs Gate failures:"); [print(f" - {p}:{i} :: {t}") for p,i,t in fails]
  os.makedirs("Docs",exist_ok=True); json.dump({"failures":fails},open("Docs/.docs_gate_report.json","w"),indent=2)
  sys.exit(1)
print("✅ Docs Gate passed."); sys.exit(0)
