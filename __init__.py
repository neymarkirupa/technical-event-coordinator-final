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

from env.environment import TechnicalEventEnv, Action, Observation, Reward
from env.tasks import get_task, get_all_tasks, run_task
from env.grader import grade_task, grade_all_tasks, compute_final_score

__version__ = "1.1.0"
__all__ = ["TechnicalEventEnv", "Action", "Observation", "Reward"]
