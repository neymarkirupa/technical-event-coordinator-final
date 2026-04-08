from fastapi import FastAPI, Request
from pydantic import BaseModel
from typing import Dict, Optional
from env.environment import TechnicalEventEnv, Action
from env.grader import grade_task, grade_all_tasks, compute_final_score
from env.tasks import get_all_tasks, get_task

app = FastAPI(title="Technical Event Coordinator Environment")

# Global environment store
envs: Dict[str, TechnicalEventEnv] = {}

class StepRequest(BaseModel):
    task_id: str
    assignments: Dict[str, str]

# --- Routes ---

@app.get("/")
def root():
    return {"message": "Technical Event Coordinator Environment is running!"}

@app.post("/reset")
async def reset(request: Request):
    """Reset the environment. Accepts empty body or JSON with optional task_id."""
    body = {}
    try:
        body = await request.json()
    except Exception:
        pass

    task_id = "easy"
    if isinstance(body, dict) and body.get("task_id"):
        task_id = body["task_id"]

    env = TechnicalEventEnv(task_id=task_id)
    obs = env.reset()
    envs[task_id] = env
    return obs.model_dump()

@app.get("/state/{task_id}")
def state(task_id: str):
    if task_id not in envs:
        return {"error": "Environment not found! Call /reset first!"}
    return envs[task_id].state().model_dump()

@app.post("/step")
def step(req: StepRequest):
    if req.task_id not in envs:
        return {"error": "Environment not found! Call /reset first!"}
    action = Action(assignments=req.assignments)
    obs, reward, done, info = envs[req.task_id].step(action)
    return {
        "observation": obs.model_dump(),
        "reward": reward.model_dump(),
        "done": done,
    }

@app.get("/tasks")
def tasks():
    return get_all_tasks()

@app.get("/tasks/{task_id}")
def task_detail(task_id: str):
    return get_task(task_id)

@app.post("/grade")
def grade(req: StepRequest):
    result = grade_task(req.task_id, req.assignments)
    return result

@app.get("/health")
def health():
    return {"status": "ok"}

def main():
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)

if __name__ == "__main__":
    main()