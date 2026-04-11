"""
Technical Event Coordinator
============================
OpenEnv-compliant environment for simulating technical-fest logistics.

Public API:
    TechnicalEventEnv  — core environment (used by server)
    Action             — action model (what the agent sends)
    Observation        — observation model (what the agent receives)
    Reward             — reward breakdown model

Quick start:
    from env.environment import TechnicalEventEnv, Action
    env = TechnicalEventEnv(task_id="easy")
    obs = env.reset()
    obs, reward, done, info = env.step(Action(assignments={"T1": "R1"}))
"""

from env.environment import TechnicalEventEnv  # noqa: F401
from env.environment import Action  # noqa: F401
from env.environment import Observation  # noqa: F401
from env.environment import Reward  # noqa: F401
from env.tasks import get_task  # noqa: F401
from env.tasks import get_all_tasks  # noqa: F401
from env.tasks import run_task  # noqa: F401
from env.grader import grade_task  # noqa: F401
from env.grader import grade_all_tasks  # noqa: F401
from env.grader import compute_final_score  # noqa: F401

__version__ = "1.1.0"
__all__ = [
    "TechnicalEventEnv", "Action", "Observation", "Reward",
    "get_task", "get_all_tasks", "run_task",
    "grade_task", "grade_all_tasks", "compute_final_score",
]
