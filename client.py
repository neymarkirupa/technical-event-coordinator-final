"""Thin HTTP client for the Technical Event Coordinator environment.

Wraps the REST API so callers can interact with the server without
hand-crafting requests.  Used by the inference script and benchmark.

Usage:
    from client import TECClient
    c = TECClient("https://your-space.hf.space")
    obs = c.reset("easy")
    result = c.step("easy", {"T1": "R1", "T2": "R3"})
"""

from __future__ import annotations

from typing import Any, Dict, Optional

import requests


class TECClient:
    """HTTP client for the Technical Event Coordinator API."""

    def __init__(self, base_url: str, timeout: int = 30):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self._session = requests.Session()

    # ── core endpoints ─────────────────────────────────────────────

    def health(self) -> dict:
        return self._get("/health")

    def reset(self, task_id: str = "easy") -> dict:
        return self._post("/reset", {"task_id": task_id})

    def step(self, task_id: str, assignments: Dict[str, str]) -> dict:
        return self._post("/step", {
            "task_id": task_id,
            "assignments": assignments,
        })

    def grade(self, task_id: str, assignments: Dict[str, str]) -> dict:
        return self._post("/grade", {
            "task_id": task_id,
            "assignments": assignments,
        })

    def tasks(self) -> list:
        return self._get("/tasks")

    def task_detail(self, task_id: str) -> dict:
        return self._get(f"/tasks/{task_id}")

    def state(self, task_id: str) -> dict:
        return self._get(f"/state/{task_id}")

    # ── internal helpers ───────────────────────────────────────────

    def _get(self, path: str) -> Any:
        url = f"{self.base_url}{path}"
        resp = self._session.get(url, timeout=self.timeout)
        resp.raise_for_status()
        return resp.json()

    def _post(self, path: str, payload: dict) -> Any:
        url = f"{self.base_url}{path}"
        resp = self._session.post(url, json=payload, timeout=self.timeout)
        resp.raise_for_status()
        return resp.json()


if __name__ == "__main__":
    c = TECClient("http://localhost:7860")
    print("Health:", c.health())
    print("Tasks:", c.tasks())
