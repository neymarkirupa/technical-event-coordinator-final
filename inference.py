from fastapi import FastAPI

app = FastAPI()

# Simple in-memory state
state = {}

@app.post("/reset")
def reset(data: dict):
    task_id = data.get("task_id", "easy")

    # Example environment state
    state[task_id] = {
        "rooms": ["R1", "R2"],
        "teams": ["T1", "T2"],
        "assignments": {}
    }

    return {
        "observation": state[task_id],
        "info": {}
    }


@app.post("/step")
def step(data: dict):
    task_id = data.get("task_id", "easy")
    assignments = data.get("assignments", {})

    state[task_id]["assignments"] = assignments

    return {
        "observation": state[task_id],
        "reward": 1.0,
        "done": True,
        "info": {"message": "Step successful"}
    }