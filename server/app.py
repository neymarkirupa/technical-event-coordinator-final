"""FastAPI server powering the Technical Event Coordinator environment.

Exposes REST endpoints so that an external LLM agent (inference.py)
can interact with the simulated environment: reset a task, submit
assignments, get grading feedback, etc.
"""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Dict, Optional

from env.environment import TechnicalEventEnv, Action
from env.grader import grade_task, grade_all_tasks, compute_final_score
from env.tasks import get_all_tasks, get_task

app = FastAPI(
    title="Technical Event Coordinator Environment",
    version="1.1.0",
    description="Simulated technical-fest logistics for the OpenEnv hackathon.",
)

# keep one env instance per task so an agent can reset + step independently
_active_envs: Dict[str, TechnicalEventEnv] = {}


# ---------- request schemas -------------------------------------------------

class StepRequest(BaseModel):
    task_id: str
    assignments: Dict[str, str]


# ---------- routes ----------------------------------------------------------

@app.get("/")
def landing():
    """Health-check landing page returned on GET /."""
    return {
        "service": "Technical Event Coordinator",
        "version": "1.1.0",
        "endpoints": ["/reset", "/step", "/grade", "/tasks", "/health"],
    }


@app.post("/reset")
async def reset_env(request: Request):
    """Reset (or create) the environment for a given task_id."""
    body: dict = {}
    try:
        body = await request.json()
    except Exception:
        pass

    task_id = "easy"
    if isinstance(body, dict) and body.get("task_id"):
        task_id = body["task_id"]

    env = TechnicalEventEnv(task_id=task_id)
    obs = env.reset()
    _active_envs[task_id] = env
    return obs.model_dump()


@app.get("/state/{task_id}")
def get_state(task_id: str):
    """Return current observation without advancing the step counter."""
    if task_id not in _active_envs:
        return JSONResponse(
            status_code=400,
            content={"error": "Environment not initialised — call /reset first."},
        )
    return _active_envs[task_id].state().model_dump()


@app.post("/step")
def perform_step(req: StepRequest):
    """Submit team→room assignments and get back the reward."""
    if req.task_id not in _active_envs:
        return JSONResponse(
            status_code=400,
            content={"error": "Environment not initialised — call /reset first."},
        )
    action = Action(assignments=req.assignments)
    obs, reward, done, _info = _active_envs[req.task_id].step(action)
    return {
        "observation": obs.model_dump(),
        "reward": reward.model_dump(),
        "done": done,
    }


@app.get("/tasks")
def list_tasks():
    """Return metadata for every available task."""
    return get_all_tasks()


@app.get("/tasks/{task_id}")
def task_detail(task_id: str):
    """Return metadata for a single task."""
    return get_task(task_id)


@app.post("/grade")
def grade(req: StepRequest):
    """Grade a set of assignments for a given task (stateless)."""
    result = grade_task(req.task_id, req.assignments)
    return result


@app.get("/health")
def health_check():
    return {"status": "ok"}


# ---------- CLI entry point -------------------------------------------------

def main():
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)


if __name__ == "__main__":
    main()