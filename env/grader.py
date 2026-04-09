from env.environment import TechnicalEventEnv, Action, _clamp_score


def grade_task(task_id: str, assignments: dict) -> dict:
    """Run one task through the environment and return its graded result."""
    env = TechnicalEventEnv(task_id=task_id)
    env.reset()
    action = Action(assignments=assignments)
    _obs, reward, _done, _info = env.step(action)

    # safety net — make absolutely sure output stays in (0, 1)
    safe_score = _clamp_score(reward.score)
    return {
        "task_id": task_id,
        "score": safe_score,
        "reason": reward.reason,
    }


def grade_all_tasks(assignments_per_task: dict) -> dict:
    """Grade every task in the provided mapping and return per-task results."""
    results = {}
    for tid, assigns in assignments_per_task.items():
        results[tid] = grade_task(tid, assigns)
    return results


def compute_final_score(results: dict) -> float:
    """Average the per-task scores, clamped to avoid boundary values."""
    scores = [r["score"] for r in results.values()]
    if not scores:
        return 0.01
    avg = sum(scores) / len(scores)
    return _clamp_score(avg)