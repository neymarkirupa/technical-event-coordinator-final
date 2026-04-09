from env.environment import TechnicalEventEnv, Action, _clamp_score

TASKS = {
    "easy": {
        "id": "easy",
        "name": "Room Assignment",
        "description": (
            "Assign 50 registered teams to 10 rooms based on "
            "seating capacity and power-outlet constraints."
        ),
        "difficulty": "easy",
    },
    "medium": {
        "id": "medium",
        "name": "Schedule Conflict Resolution",
        "description": (
            "Resolve a double-booked VIP judge conflict "
            "without introducing new scheduling overlaps."
        ),
        "difficulty": "medium",
    },
    "hard": {
        "id": "hard",
        "name": "Sponsor Pullout Crisis",
        "description": (
            "A major sponsor withdrew 24 h before the closing ceremony. "
            "Re-allocate prize distribution to stay within budget."
        ),
        "difficulty": "hard",
    },
}


def get_task(task_id: str) -> dict:
    return TASKS.get(task_id, TASKS["easy"])


def get_all_tasks() -> list:
    return list(TASKS.values())


def run_task(task_id: str, assignments: dict) -> dict:
    """Execute a single task end-to-end and return the graded result."""
    env = TechnicalEventEnv(task_id=task_id)
    env.reset()
    action = Action(assignments=assignments)
    _obs, reward, done, _info = env.step(action)

    safe_score = _clamp_score(reward.score)
    return {
        "task_id": task_id,
        "score": safe_score,
        "reason": reward.reason,
        "done": done,
    }