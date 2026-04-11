"""Heuristic baseline agent for Technical Event Coordinator.

This agent runs locally without an LLM.  It uses a combination of
first-fit-decreasing bin packing and simple priority rules to produce
reasonable (but not optimal) team-to-room assignments.

Usage:
    from baseline_agent import HeuristicBaselineAgent
    agent = HeuristicBaselineAgent()
    mapping = agent.solve(rooms, teams)
"""

from __future__ import annotations

import math
import random
from typing import Any, Dict, List, Optional


class HeuristicBaselineAgent:
    """Greedy heuristic that assigns teams to rooms without an LLM."""

    def __init__(self, seed: int = 42):
        self._rng = random.Random(seed)
        self._history: List[Dict[str, str]] = []

    def reset(self, seed: int | None = None) -> None:
        """Clear internal state for a fresh episode."""
        if seed is not None:
            self._rng = random.Random(seed)
        self._history.clear()

    # ── core solver ─────────────────────────────────────────────────

    def solve(
        self,
        rooms: List[Dict[str, Any]],
        teams: List[Dict[str, Any]],
    ) -> Dict[str, str]:
        """Return a team→room mapping using first-fit-decreasing.

        Steps:
        1. Sort teams by laptop count descending (ties broken by size).
        2. Sort rooms by capacity descending.
        3. For each team, pick the room with the most remaining headroom
           that can still satisfy both capacity and outlet constraints.
        4. If no perfect fit, assign to the room with the largest capacity.
        """
        buckets = self._init_buckets(rooms)
        ordered = self._rank_teams(teams)
        result: Dict[str, str] = {}

        for team in ordered:
            tid = team["id"]
            laps = team.get("laptops", 0)
            chosen = self._pick_room(buckets, laps)
            result[tid] = chosen["id"]
            chosen["cap_left"] -= 1
            chosen["out_left"] -= laps

        self._history.append(result)
        return result

    # alias used by the /baseline endpoint
    def next_action(self, obs: dict) -> dict:
        """Convenience wrapper: extract rooms+teams from an observation dict
        and return an action payload ready for POST /step."""
        inner = obs.get("observation", obs)
        rooms = inner.get("rooms", [])
        teams = inner.get("teams", [])
        mapping = self.solve(rooms, teams)
        return {"assignments": mapping}

    # ── internal helpers ────────────────────────────────────────────

    @staticmethod
    def _init_buckets(rooms: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        return [
            {
                "id": r["id"],
                "cap_left": r["capacity"],
                "out_left": r["outlets"],
                "capacity": r["capacity"],
            }
            for r in rooms
        ]

    @staticmethod
    def _rank_teams(teams: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        return sorted(
            teams,
            key=lambda t: (t.get("laptops", 0), t.get("size", 1)),
            reverse=True,
        )

    @staticmethod
    def _pick_room(
        buckets: List[Dict[str, Any]],
        laptops_needed: int,
    ) -> Dict[str, Any]:
        best: Optional[Dict[str, Any]] = None
        best_slack = -999

        for b in buckets:
            slack = min(b["cap_left"], b["out_left"] - laptops_needed)
            if slack > best_slack:
                best_slack = slack
                best = b

        return best if best is not None else buckets[0]

    # ── scoring helper (mirrors env grader) ─────────────────────────

    @staticmethod
    def quick_score(
        rooms: List[Dict[str, Any]],
        teams: List[Dict[str, Any]],
        assignments: Dict[str, str],
    ) -> float:
        """Approximate score without running the full environment."""
        valid_rooms = {r["id"] for r in rooms}
        valid_teams = {t["id"] for t in teams}
        total = len(teams)
        if total == 0:
            return 0.01

        good = {
            tid: rid
            for tid, rid in assignments.items()
            if tid in valid_teams and rid in valid_rooms
        }
        coverage = len(good) / total

        counts: Dict[str, int] = {}
        team_map = {t["id"]: t for t in teams}
        room_laps: Dict[str, int] = {}

        for tid, rid in good.items():
            counts[rid] = counts.get(rid, 0) + 1
            laps = team_map.get(tid, {}).get("laptops", 0)
            room_laps[rid] = room_laps.get(rid, 0) + laps

        cap_hits = sum(
            1 for r in rooms if counts.get(r["id"], 0) > r["capacity"]
        )
        out_hits = sum(
            1 for r in rooms if room_laps.get(r["id"], 0) > r["outlets"]
        )

        raw = (
            coverage * 0.6
            - min(0.2, cap_hits * 0.05)
            - min(0.15, out_hits * 0.04)
        )

        if counts:
            vals = list(counts.values())
            mu = sum(vals) / len(vals)
            var = sum((v - mu) ** 2 for v in vals) / len(vals)
            cv = math.sqrt(var) / mu if mu > 0 else 1.0
            raw += max(0.0, 0.15 * (1.0 - cv))

        return max(0.01, min(0.99, round(raw, 4)))


# ── CLI entry point ────────────────────────────────────────────────

def main():
    """Run the baseline agent against the local server."""
    import requests

    url = "http://localhost:7860"
    tasks = ["easy", "medium", "hard"]

    for tid in tasks:
        obs = requests.post(f"{url}/reset", json={"task_id": tid}).json()
        inner = obs.get("observation", obs)
        agent = HeuristicBaselineAgent()
        mapping = agent.solve(inner.get("rooms", []), inner.get("teams", []))
        result = requests.post(
            f"{url}/step",
            json={"task_id": tid, "assignments": mapping},
        ).json()
        score = result.get("reward", {}).get("score", 0)
        print(f"Task {tid}: score={score}")


if __name__ == "__main__":
    main()
