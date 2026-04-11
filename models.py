"""Pydantic models for the Technical Event Coordinator environment.

Every data structure exchanged between the server, grader, and inference
script is defined here so validation happens in one place.
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


# ── enums ───────────────────────────────────────────────────────────

class Difficulty(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class ActionType(str, Enum):
    ASSIGN = "assign"
    SWAP = "swap"
    REASSIGN = "reassign"
    SUBMIT = "submit"
    NOOP = "noop"


# ── room / team descriptors ────────────────────────────────────────

class RoomSpec(BaseModel):
    """A single venue room available for the event."""
    id: str
    capacity: int = Field(ge=1, description="Max teams that can sit here")
    outlets: int = Field(ge=0, description="Number of power outlets")
    has_projector: bool = False
    floor: int = 1


class TeamSpec(BaseModel):
    """A single registered team."""
    id: str
    size: int = Field(ge=1, description="Number of members")
    laptops: int = Field(ge=0, description="Laptops that need charging")
    needs_projector: bool = False
    priority: int = Field(default=0, ge=0, le=3, description="0=normal, 3=VIP")


# ── action / observation / reward ──────────────────────────────────

class TECAction(BaseModel):
    """Action that the agent can take inside an episode."""
    action_type: ActionType = ActionType.ASSIGN
    assignments: Dict[str, str] = Field(
        default_factory=dict,
        description="Mapping of team_id -> room_id",
    )
    team_id: Optional[str] = None
    room_id: Optional[str] = None
    reason: Optional[str] = None


class TECObservation(BaseModel):
    """What the agent sees after each step."""
    rooms: List[Dict[str, Any]]
    teams: List[Dict[str, Any]]
    assignments: Dict[str, str]
    task_id: str
    step_count: int
    max_steps: int = 10
    done: bool = False
    reward: float = 0.0
    cumulative_reward: float = 0.0
    message: str = ""
    constraints_violated: List[str] = Field(default_factory=list)


class TECReward(BaseModel):
    """Reward breakdown returned by the grader."""
    score: float = Field(ge=0.0, le=1.0)
    coverage: float = 0.0
    capacity_penalty: float = 0.0
    outlet_penalty: float = 0.0
    balance_bonus: float = 0.0
    reason: str = ""


class EnvironmentState(BaseModel):
    """Lightweight episode metadata (GET /state)."""
    task_id: str = ""
    step_count: int = 0
    max_steps: int = 10
    done: bool = False
    cumulative_reward: float = 0.0
    total_teams: int = 0
    total_rooms: int = 0
    assigned_count: int = 0
    seed: int = 42


class TaskInfo(BaseModel):
    """Returned by GET /tasks."""
    id: str
    name: str
    description: str
    difficulty: str
    num_teams: int = 0
    num_rooms: int = 0
    max_steps: int = 10
    reward_range: List[float] = [0.0, 1.0]


class GraderResult(BaseModel):
    """Returned by POST /grader."""
    task_id: str
    score: float
    breakdown: Dict[str, float] = Field(default_factory=dict)
    feedback: List[str] = Field(default_factory=list)
    steps_used: int = 0
    max_steps: int = 10
    done: bool = False
