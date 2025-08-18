"""Generate concept art via ComfyUI using prompt packs."""

from __future__ import annotations

import csv
import json
import pathlib
import time

from comfy_client.comfy_client import ComfyClient, inject_params


ROOT = pathlib.Path(__file__).resolve().parents[2]
WORKFLOW = json.loads((ROOT / "Tools/ArtGen/workflows/concept_art.api.json").read_text())
OUT_BASE = ROOT / "Docs/Concepts/Weapons/AI"


def load_pack(faction_slug: str) -> dict:
    path = ROOT / f"Tools/ArtGen/prompt_packs/factions/{faction_slug}.json"
    return json.loads(path.read_text())


def run() -> None:
    cc = ComfyClient()
    with open(ROOT / "Data/Tables/Weapons.csv", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            faction = row.get("Faction")
            pack = load_pack(faction)
            params = {
                "prompt": f'{pack["positive"][0]}, {row["Name"]}, {row.get("Tags", "")}',
                "negative": ", ".join(pack["negative"]),
                "seed": int(pack["defaults"]["seed"]) + int(row.get("SeedOffset", 0)),
                "model": pack["defaults"]["model"],
                "loras": pack["defaults"]["loras"],
                "width": pack["defaults"]["width"],
                "height": pack["defaults"]["height"],
            }
            wf = inject_params(WORKFLOW, params)
            job_id = cc.queue_workflow(wf)
            out_dir = OUT_BASE / row["Slug"]
            images, _hist = cc.wait_for_images(job_id, out_dir)
            for img in images:
                sidecar = out_dir / f'{img["filename"]}.json'
                sidecar.write_text(
                    json.dumps(
                        {
                            **params,
                            "workflow": "concept_art.api.json",
                            "faction": faction,
                            "category": "Weapons",
                            "generated_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                        },
                        indent=2,
                    )
                )


if __name__ == "__main__":
    run()

