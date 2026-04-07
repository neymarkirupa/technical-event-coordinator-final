from pydantic import BaseModel
from typing import List, Dict, Any
import random

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

class TechnicalEventEnv:

    def __init__(self, task_id="easy"):
        self.task_id = task_id
        self.step_count = 0
        self.rooms = []
        self.teams = []
        self.assignments = {}

    def reset(self):
        self.step_count = 0
        self.assignments = {}

        if self.task_id == "easy":
            self.rooms = [
                {"id": f"R{i}", "capacity": random.randint(4, 8), "outlets": random.randint(3, 8)}
                for i in range(1, 11)
            ]
            self.teams = [
                {"id": f"T{i}", "size": random.randint(2, 4), "laptops": random.randint(1, 4)}
                for i in range(1, 51)
            ]

        elif self.task_id == "medium":
            self.rooms = [
                {"id": f"R{i}", "capacity": 10, "outlets": 10}
                for i in range(1, 6)
            ]
            self.teams = [
                {"id": f"T{i}", "size": 3, "laptops": 3}
                for i in range(1, 21)
            ]

        elif self.task_id == "hard":
            self.rooms = [
                {"id": f"R{i}", "capacity": 5, "outlets": 5}
                for i in range(1, 8)
            ]
            self.teams = [
                {"id": f"T{i}", "size": 4, "laptops": 4}
                for i in range(1, 51)
            ]

        return self._get_observation()

    def step(self, action: Action):
        self.step_count += 1
        self.assignments = action.assignments
        obs = self._get_observation()
        reward = self._calculate_reward()
        done = True
        return obs, reward, done, {}

    def state(self):
        return self._get_observation()

    def _get_observation(self):
        return Observation(
            rooms=self.rooms,
            teams=self.teams,
            assignments=self.assignments,
            task_id=self.task_id,
            step_count=self.step_count
        )

    def _calculate_reward(self):
        if not self.assignments:
            return Reward(score=0.0, reason="Nothing assigned!")

        total_teams = len(self.teams)
        assigned_count = len(self.assignments)

        
        coverage = assigned_count / total_teams

        
        room_usage = {}
        for team_id, room_id in self.assignments.items():
            room_usage[room_id] = room_usage.get(room_id, 0) + 1

        overflow_penalty = 0
        for room in self.rooms:
            used = room_usage.get(room["id"], 0)
            if used > room["capacity"]:
                overflow_penalty += 0.1

        
        outlet_penalty = 0
        for room in self.rooms:
            used = room_usage.get(room["id"], 0)
            if used > room["outlets"]:
                outlet_penalty += 0.1

        
        score = (coverage * 0.7) - overflow_penalty - outlet_penalty
        score = max(0.0, min(1.0, round(score, 2)))

        return Reward(
            score=score,
            reason=f"Assigned {assigned_count}/{total_teams} teams. Overflow penalty: {overflow_penalty}"
        )