"""Minimal ComfyUI API client."""

from __future__ import annotations

import json
import pathlib
import time
import uuid
from typing import Any, Dict, Optional

import requests


class ComfyClient:
    """Client for interacting with a ComfyUI server."""

    def __init__(self, base_url: str = "http://127.0.0.1:8000") -> None:
        self.base = base_url.rstrip("/")

    def _post(self, path: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        resp = requests.post(f"{self.base}{path}", json=payload, timeout=120)
        resp.raise_for_status()
        return resp.json()

    def queue_workflow(self, api_workflow: Dict[str, Any]) -> str:
        """Queue a workflow and return its prompt identifier."""
        resp = self._post("/prompt", {"prompt": api_workflow})
        return resp.get("prompt_id") or resp.get("node_id") or str(uuid.uuid4())

    def wait_for_images(
        self,
        history_id: str,
        out_dir: pathlib.Path,
        poll: float = 1.0,
        timeout: float = 600,
    ) -> tuple[list[Dict[str, Any]], Dict[str, Any]]:
        """Poll the history endpoint until images are ready and download them."""
        start = time.time()
        out_dir.mkdir(parents=True, exist_ok=True)
        last: Optional[Dict[str, Any]] = None
        while time.time() - start < timeout:
            hist = requests.get(f"{self.base}/history/{history_id}", timeout=30)
            if hist.status_code == 200 and hist.json():
                last = hist.json()
                images = self._collect_images_from_history(last)
                if images:
                    self._download_images(images, out_dir)
                    return images, last
            time.sleep(poll)
        raise TimeoutError("Comfy job timed out")

    def _collect_images_from_history(
        self, hist_json: Dict[str, Any]
    ) -> list[Dict[str, Any]]:
        images: list[Dict[str, Any]] = []
        for node in hist_json.values():
            if isinstance(node, dict):
                for output in node.get("outputs", {}).values():
                    images.extend(output.get("images", []))
        return images

    def _download_images(self, images: list[Dict[str, Any]], out_dir: pathlib.Path) -> None:
        for img in images:
            url = (
                f'{self.base}/view?filename={img["filename"]}&subfolder={img.get("subfolder", "")}'
                "&type=output"
            )
            data = requests.get(url, timeout=60).content
            (out_dir / img["filename"]).write_bytes(data)


def inject_params(api_workflow: Dict[str, Any], params: Dict[str, Any]) -> Dict[str, Any]:
    """Inject prompt parameters into an API workflow template."""
    workflow = json.loads(json.dumps(api_workflow))
    # TODO: map specific node IDs to workflow inputs
    return workflow

