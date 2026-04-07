from env.environment import TechnicalEventEnv, Action

TASKS = {
    "easy": {
        "id": "easy",
        "name": "Room Assignment",
        "description": "Assign 50 registered teams to 10 rooms based on seating and power outlet constraints.",
        "difficulty": "easy",
    },
    "medium": {
        "id": "medium",
        "name": "Schedule Conflict Resolution",
        "description": "Resolve a double-booked VIP judge conflict without creating new conflicts.",
        "difficulty": "medium",
    },
    "hard": {
        "id": "hard",
        "name": "Sponsor Pullout Crisis",
        "description": "A major sponsor pulled out. Rewrite prize distribution without going into the red.",
        "difficulty": "hard",
    },
}

def get_task(task_id: str):
    return TASKS.get(task_id, TASKS["easy"])

def get_all_tasks():
    return list(TASKS.values())

def run_task(task_id: str, assignments: dict):
    env = TechnicalEventEnv(task_id=task_id)
    env.reset()
    action = Action(assignments=assignments)
    obs, reward, done, info = env.step(action)
    return {
        "task_id": task_id,
        "score": reward.score,
        "reason": reward.reason,
        "done": done,
    }