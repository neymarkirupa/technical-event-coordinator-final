import os
import requests
import json

ENV_URL = "https://kirubakaransl-technical-event-coordinator.hf.space"

def reset_env(task_id):
    res = requests.post(f"{ENV_URL}/reset", json={"task_id": task_id})
    return res.json()

def step_env(task_id, assignments):
    res = requests.post(f"{ENV_URL}/step", json={
        "task_id": task_id,
        "assignments": assignments
    })
    return res.json()

def simple_agent(observation, task_id):
    teams = observation.get("observation", {}).get("teams", [])
    rooms = observation.get("observation", {}).get("rooms", [])
    assignments = {}
    for i, team in enumerate(teams):
        room = rooms[i % len(rooms)]
        assignments[team["id"]] = room["id"]
    return assignments

def run_task(task_id):
    print(f"[START] task={task_id}", flush=True)
    
    obs = reset_env(task_id)
    assignments = simple_agent(obs, task_id)
    result = step_env(task_id, assignments)
    
    reward = result.get("reward", 0.0)
    done = result.get("done", False)
    
    print(f"[STEP] step=1 reward={reward}", flush=True)
    print(f"[END] task={task_id} score={reward} steps=1", flush=True)
    
    return reward

def main():
    tasks = ["easy", "medium", "hard"]
    scores = {}
    
    for task_id in tasks:
        score = run_task(task_id)
        scores[task_id] = score
    
    avg = sum(scores.values()) / len(scores)
    print(f"\nFINAL SCORES: {scores}", flush=True)
    print(f"AVERAGE: {avg:.2f}", flush=True)

if __name__ == "__main__":
    main()