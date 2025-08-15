#!/usr/bin/env python3
"""
artgen_import.py

- Reads Tools/ArtGen/artgen_config.json and batch plan files
- Assumes images already exist at target paths
- Imports into UE via UnrealEditor-Cmd + Python script hooks when run via VS Code task
- As a library: when run directly here, just logs what would be imported and writes UE import intents to Docs/Phase4_Implementation_Log.md
"""
import os, json, datetime
ROOT=os.path.abspath(os.path.join(os.path.dirname(__file__),"..",".."))
os.chdir(ROOT)

LOG_PATH="Docs/Phase4_Implementation_Log.md"

def log(msg:str):
  print(msg)
  os.makedirs(os.path.dirname(LOG_PATH),exist_ok=True)
  with open(LOG_PATH,"a",encoding="utf-8") as f:
    f.write(f"{msg}\n")

def classify_target(target:str)->str:
  t=target.replace("\\","/").lower()
  if "/content/tg/icons/" in t:
    return "ui"
  return "world"

def build_ue_path(target:str)->str:
  p=target.replace("\\","/")
  if p.startswith("Content/"):
    return "/Game/"+p[len("Content/"):].rsplit(".",1)[0]
  # Docs assets are not uassets; skip but log
  return ""

if __name__=="__main__":
  cfg=json.load(open("Tools/ArtGen/artgen_config.json"))
  log(f"## ArtGen Import Intent • {datetime.datetime.now().isoformat()}")
  for batch in cfg.get("batches",[]):
    plan=json.load(open(batch))
    log(f"- Batch: {batch} • model={plan.get('model')} • items={len(plan.get('items',[]))}")
    for it in plan.get("items",[]):
      tgt=it["target"]
      kind=classify_target(tgt)
      ue=build_ue_path(tgt)
      if ue:
        log(f"  - Import {tgt} -> {ue} [{kind}]")
      else:
        log(f"  - Skip import (docs-only) {tgt}")
  print("Wrote import intents to docs log.")
