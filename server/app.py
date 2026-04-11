"""FastAPI server powering the Technical Event Coordinator environment.

Exposes REST endpoints so that an external LLM agent (inference.py)
can interact with the simulated environment: reset a task, submit
assignments, get grading feedback, etc.
"""

import logging
import threading
from contextlib import asynccontextmanager
from typing import Dict, Optional

from fastapi import FastAPI, Request, Body, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
from pydantic import BaseModel

from env.environment import TechnicalEventEnv, Action
from env.grader import grade_task, grade_all_tasks, compute_final_score
from env.tasks import get_all_tasks, get_task
from server.landing_ui import UI_HTML

logger = logging.getLogger(__name__)

# keep one env instance per task so an agent can reset + step independently
_active_envs: Dict[str, TechnicalEventEnv] = {}
_env_lock = threading.Lock()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialise default environment on startup."""
    logger.info("Technical Event Coordinator starting up")
    yield


app = FastAPI(
    title="Technical Event Coordinator",
    version="1.1.0",
    description=(
        "OpenEnv-compliant environment simulating a large-scale technical fest. "
        "An AI agent must handle room assignments, scheduling overlaps, and "
        "last-minute budget shocks — all through a simple REST API."
    ),
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "Authorization"],
)


# ---------- request schemas -------------------------------------------------

class StepRequest(BaseModel):
    task_id: str
    assignments: Dict[str, str]


# ---------- HTML landing page -----------------------------------------------

@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def root():
    """Primary Space landing page with interactive dashboard."""
    return UI_HTML


@app.get("/ui", response_class=HTMLResponse, include_in_schema=False)
def ui():
    """Alternative path to the dashboard UI."""
    return UI_HTML


# ---------- core routes -----------------------------------------------------

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

    with _env_lock:
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
    with _env_lock:
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
    """Liveness check — returns 200 when server is running."""
    return {"status": "ok", "version": "1.1.0", "env": "technical-event-coordinator"}


@app.get("/metadata")
def metadata():
    """Environment metadata (OpenEnv runtime spec)."""
    return {
        "name": "technical-event-coordinator",
        "version": "1.1.0",
        "description": (
            "An OpenEnv environment that simulates managing a large-scale "
            "technical fest. The agent must handle room assignments, "
            "scheduling conflicts, and budget crises."
        ),
        "tasks": ["easy", "medium", "hard"],
        "author": "NULL BYTE",
        "tags": ["openenv", "scheduling", "resource-allocation", "budget-management", "real-world"],
    }


# ---------- CLI entry point -------------------------------------------------

def main():
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)


if __name__ == "__main__":
    main()