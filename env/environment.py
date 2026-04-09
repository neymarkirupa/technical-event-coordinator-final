from pydantic import BaseModel
from typing import List, Dict, Any
import random
import math


class Observation(BaseModel):
    rooms: List[Dict[str, Any]]
    teams: List[Dict[str, Any]]
    assignments: Dict[str, str]
    task_id: str
    step_count: int


class Action(BaseModel):
    assignments: Dict[str, str]


class Reward(BaseModel):
    score: float
    reason: str


# mapping of valid room ids per task so we can quickly validate
_ROOM_COUNTS = {"easy": 10, "medium": 5, "hard": 7}
_TEAM_COUNTS = {"easy": 50, "medium": 20, "hard": 50}


def _clamp_score(raw: float) -> float:
    """Pin the score inside the open interval (0, 1).
    The hackathon grader rejects boundary values, so we nudge
    anything that lands on 0.0 or 1.0 slightly inward."""
    clamped = max(0.0, min(1.0, raw))
    if clamped <= 0.0:
        return 0.01
    if clamped >= 1.0:
        return 0.99
    return round(clamped, 4)


class TechnicalEventEnv:
    """Simulates a technical event with room-assignment logistics.

    Three difficulty tiers determine the ratio of teams to rooms
    and how tight the capacity / outlet budgets are.
    """

    def __init__(self, task_id="easy"):
        self.task_id = task_id
        self.step_count = 0
        self.rooms: List[Dict[str, Any]] = []
        self.teams: List[Dict[str, Any]] = []
        self.assignments: Dict[str, str] = {}

    # ---- public API -----------------------------------------------

    def reset(self) -> Observation:
        self.step_count = 0
        self.assignments = {}
        self._build_scenario()
        return self._observe()

    def step(self, action: Action):
        self.step_count += 1
        self.assignments = action.assignments
        obs = self._observe()
        reward = self._score_assignments()
        done = True
        return obs, reward, done, {}

    def state(self) -> Observation:
        return self._observe()

    # ---- scenario generation --------------------------------------

    def _build_scenario(self):
        random.seed(hash(self.task_id) & 0xFFFFFFFF)

        if self.task_id == "easy":
            # 10 rooms with generous capacity, 50 teams
            self.rooms = [
                {
                    "id": f"R{i}",
                    "capacity": random.randint(4, 8),
                    "outlets": random.randint(3, 8),
                }
                for i in range(1, 11)
            ]
            self.teams = [
                {
                    "id": f"T{i}",
                    "size": random.randint(2, 4),
                    "laptops": random.randint(1, 4),
                }
                for i in range(1, 51)
            ]

        elif self.task_id == "medium":
            # 5 rooms, uniform capacity, 20 teams
            self.rooms = [
                {"id": f"R{i}", "capacity": 10, "outlets": 10}
                for i in range(1, 6)
            ]
            self.teams = [
                {"id": f"T{i}", "size": 3, "laptops": 3}
                for i in range(1, 21)
            ]

        elif self.task_id == "hard":
            # 7 rooms with tight capacity, 50 teams -> heavy contention
            self.rooms = [
                {"id": f"R{i}", "capacity": 5, "outlets": 5}
                for i in range(1, 8)
            ]
            self.teams = [
                {"id": f"T{i}", "size": 4, "laptops": 4}
                for i in range(1, 51)
            ]

        else:
            # unknown task_id — fall back to easy
            self.task_id = "easy"
            self._build_scenario()

    # ---- observation helper ---------------------------------------

    def _observe(self) -> Observation:
        return Observation(
            rooms=self.rooms,
            teams=self.teams,
            assignments=self.assignments,
            task_id=self.task_id,
            step_count=self.step_count,
        )

    # ---- scoring logic --------------------------------------------

    def _score_assignments(self) -> Reward:
        if not self.assignments:
            return Reward(score=0.01, reason="No teams were assigned to any room.")

        total_teams = len(self.teams)
        valid_room_ids = {r["id"] for r in self.rooms}
        valid_team_ids = {t["id"] for t in self.teams}

        # how many assignments point to real rooms and real teams?
        good_assignments = {
            tid: rid
            for tid, rid in self.assignments.items()
            if tid in valid_team_ids and rid in valid_room_ids
        }
        assigned_ct = len(good_assignments)

        # 1) coverage component  (weight 0.6)
        coverage_ratio = assigned_ct / total_teams if total_teams else 0
        coverage_part = coverage_ratio * 0.6

        # 2) capacity-overflow penalty  (weight up to -0.2)
        room_team_counts: Dict[str, int] = {}
        for rid in good_assignments.values():
            room_team_counts[rid] = room_team_counts.get(rid, 0) + 1

        overflow_hits = 0
        for room in self.rooms:
            used = room_team_counts.get(room["id"], 0)
            if used > room["capacity"]:
                overflow_hits += 1
        cap_penalty = min(0.2, overflow_hits * 0.05)

        # 3) outlet-overflow penalty  (weight up to -0.15)
        # count total laptops per room
        team_map = {t["id"]: t for t in self.teams}
        room_laptops: Dict[str, int] = {}
        for tid, rid in good_assignments.items():
            laps = team_map.get(tid, {}).get("laptops", 0)
            room_laptops[rid] = room_laptops.get(rid, 0) + laps

        outlet_hits = 0
        for room in self.rooms:
            if room_laptops.get(room["id"], 0) > room["outlets"]:
                outlet_hits += 1
        outlet_penalty = min(0.15, outlet_hits * 0.04)

        # 4) balance bonus  (weight up to +0.15)
        # reward even distribution across rooms using coefficient of variation
        if room_team_counts:
            counts = list(room_team_counts.values())
            mean_ct = sum(counts) / len(counts)
            variance = sum((c - mean_ct) ** 2 for c in counts) / len(counts)
            cv = math.sqrt(variance) / mean_ct if mean_ct > 0 else 1.0
            balance_bonus = max(0.0, 0.15 * (1.0 - cv))
        else:
            balance_bonus = 0.0

        raw = coverage_part + balance_bonus - cap_penalty - outlet_penalty
        final = _clamp_score(raw)

        reason_parts = [
            f"Assigned {assigned_ct}/{total_teams} teams",
            f"coverage={coverage_ratio:.2f}",
            f"cap_penalty={cap_penalty:.2f}",
            f"outlet_penalty={outlet_penalty:.2f}",
            f"balance_bonus={balance_bonus:.2f}",
        ]
        return Reward(score=final, reason=" | ".join(reason_parts))