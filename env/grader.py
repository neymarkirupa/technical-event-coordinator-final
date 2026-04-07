from env.environment import TechnicalEventEnv, Action

def grade_task(task_id: str, assignments: dict) -> dict:
    env = TechnicalEventEnv(task_id=task_id)
    env.reset()
    action = Action(assignments=assignments)
    obs, reward, done, info = env.step(action)
    return {
        "task_id": task_id,
        "score": reward.score,
        "reason": reward.reason,
    }

def grade_all_tasks(assignments_per_task: dict) -> dict:
    results = {}
    for task_id, assignments in assignments_per_task.items():
        results[task_id] = grade_task(task_id, assignments)
    return results

def compute_final_score(results: dict) -> float:
    scores = [r["score"] for r in results.values()]
    if not scores:
        return 0.0
    return round(sum(scores) / len(scores), 2)