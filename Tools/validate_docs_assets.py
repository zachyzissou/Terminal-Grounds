#!/usr/bin/env python3
import sys,re,glob,os,json
ROOT=os.path.abspath(os.path.join(os.path.dirname(__file__),"..",".."))
os.chdir(ROOT)
FAIL=[
  r"\bTBD\b",
  r"\bPLACEHOLDER\b",
  r"\bNEW_ASSET\b",
  # Canon banned terms (see Lore Bible Glossary)
  r"(?i)Industrial\s+Exclusion\s+Zone",
]
ALLOW=re.compile(r"Screenshot\s+TODO",re.I)
DOCS=[
  "README.md",
  "Docs/**/*.md",
  "Design/**/*.md",
  "World/**/*.md",
  "Tech/**/*.md",
  "Docs/Art/**/*.md",
  "Docs/VFX/**/*.md",
  "Docs/Audio/**/*.md"
]
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

# Optional canon consistency checks (non-breaking; enable via env)
if os.environ.get("DOCS_CANON_CHECK","true").lower() in ("1","true","yes"):  # default on
  # 1) Faction art guides must reference canonical Lore Bible
  for guide in glob.glob("Docs/Art/Factions/**/*.md", recursive=True):
    if not os.path.isfile(guide):
      continue
    txt=open(guide,"r",encoding="utf-8",errors="ignore").read()
    if ("Lore Reference" not in txt) or ("LORE_BIBLE.md#factions" not in txt):
      fails.append((guide,0,"Missing Lore Reference to canon (docs/Lore/LORE_BIBLE.md#factions)"))

  # 2) POI flavor must declare IDs
  poi_flavor="Docs/Lore/POIs_Flavor.md"
  if os.path.isfile(poi_flavor):
    txt=open(poi_flavor,"r",encoding="utf-8",errors="ignore").read()
    if "ID: POI_" not in txt:
      fails.append((poi_flavor,0,"POIs_Flavor.md missing POI ID declarations (ID: POI_*)"))

  # 3) POI concepts should reference canonical flavor for lore lines
  poi_concepts="Docs/Concepts/POIs/locations.md"
  if os.path.isfile(poi_concepts):
    for i,line in enumerate(open(poi_concepts,"r",encoding="utf-8",errors="ignore").read().splitlines(),1):
      if line.strip().startswith("- **Lore**:") and ("POIs_Flavor.md#" not in line):
        fails.append((poi_concepts,i,"Lore line should link to docs/Lore/POIs_Flavor.md#<anchor>"))
if fails:
  print("❌ Docs Gate failures:"); [print(f" - {p}:{i} :: {t}") for p,i,t in fails]
  os.makedirs("Docs",exist_ok=True); json.dump({"failures":fails},open("Docs/.docs_gate_report.json","w"),indent=2)
  sys.exit(1)
print("✅ Docs Gate passed."); sys.exit(0)
