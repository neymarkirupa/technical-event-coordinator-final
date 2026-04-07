from fastapi import FastAPI
from pydantic import BaseModel
from typing import Dict, Optional

app = FastAPI()

state = {}

# ✅ Define request model (IMPORTANT)
class ResetRequest(BaseModel):
    task_id: Optional[str] = "easy"


class StepRequest(BaseModel):
    task_id: Optional[str] = "easy"
    assignments: Dict = {}


# ✅ RESET
@app.post("/reset")
def reset(req: ResetRequest = ResetRequest()):
    task_id = req.task_id

    state[task_id] = {
        "rooms": [
            {"id": "R1", "capacity": 2, "outlets": 2},
            {"id": "R2", "capacity": 2, "outlets": 2}
        ],
        "teams": [
            {"id": "T1"},
            {"id": "T2"}
        ],
        "assignments": {}
    }

    return {
        "observation": state[task_id],
        "info": {}
    }


# ✅ STEP
@app.post("/step")
def step(req: StepRequest):
    task_id = req.task_id
    assignments = req.assignments

    state[task_id]["assignments"] = assignments

    return {
        "observation": state[task_id],
        "reward": 1.0,
        "done": True,
        "info": {}
    }