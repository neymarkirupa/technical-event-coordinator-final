import os
import requests
import json
from openai import OpenAI

ENV_URL = "https://kirubakaransl-technical-event-coordinator.hf.space"

# Use the hackathon-provided LLM proxy
API_BASE_URL = os.environ.get("API_BASE_URL", "")
API_KEY = os.environ.get("API_KEY", "")

client = OpenAI(
    base_url=API_BASE_URL,
    api_key=API_KEY,
)

def reset_env(task_id):
    res = requests.post(f"{ENV_URL}/reset", json={"task_id": task_id})
    return res.json()

def step_env(task_id, assignments):
    res = requests.post(f"{ENV_URL}/step", json={
        "task_id": task_id,
        "assignments": assignments
    })
    return res.json()

def llm_agent(observation, task_id):
    """Use the LLM proxy to decide room assignments."""
    teams = observation.get("observation", {}).get("teams", [])
    rooms = observation.get("observation", {}).get("rooms", [])
    if not teams or not rooms:
        teams = observation.get("teams", [])
        rooms = observation.get("rooms", [])

    prompt = f"""You are a technical event coordinator. Assign teams to rooms optimally.

ROOMS:
{json.dumps(rooms, indent=2)}

TEAMS:
{json.dumps(teams, indent=2)}

RULES:
- Each team must be assigned to exactly one room.
- Try not to exceed room capacity (number of teams in a room should not exceed room capacity).
- Try not to exceed room outlets (total laptops in a room should not exceed outlets).
- Maximize the number of teams assigned.
- Distribute teams as evenly as possible across rooms.

Return ONLY a valid JSON object mapping team IDs to room IDs, like:
{{"T1": "R1", "T2": "R2", ...}}

Return ONLY the JSON, no other text."""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that outputs only valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
            max_tokens=4096,
        )
        
        content = response.choices[0].message.content.strip()
        # Clean up markdown code blocks if present
        if content.startswith("```"):
            content = content.split("\n", 1)[1] if "\n" in content else content[3:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()
        
        assignments = json.loads(content)
        print(f"[LLM] Got assignments for {len(assignments)} teams", flush=True)
        return assignments
    except Exception as e:
        print(f"[LLM ERROR] {e}, falling back to heuristic", flush=True)
        # Fallback: simple round-robin
        assignments = {}
        for i, team in enumerate(teams):
            room = rooms[i % len(rooms)]
            assignments[team["id"]] = room["id"]
        return assignments

def run_task(task_id):
    print(f"[START] task={task_id}", flush=True)
    
    try:
        obs = reset_env(task_id)
        assignments = llm_agent(obs, task_id)
        result = step_env(task_id, assignments)
        
        # reward can be a dict like {"score": 0.7, "reason": "..."} or a float
        reward = result.get("reward", 0.0)
        if isinstance(reward, dict):
            reward = float(reward.get("score", 0.0))
        else:
            reward = float(reward)
        
        done = result.get("done", False)
        
        print(f"[STEP] step=1 reward={reward}", flush=True)
        print(f"[END] task={task_id} score={reward} steps=1", flush=True)
        
        return reward
    except Exception as e:
        print(f"[ERROR] task={task_id} error={e}", flush=True)
        print(f"[END] task={task_id} score=0.0 steps=1", flush=True)
        return 0.0

def main():
    tasks = ["easy", "medium", "hard"]
    scores = {}
    
    for task_id in tasks:
        score = run_task(task_id)
        scores[task_id] = float(score)
    
    avg = sum(scores.values()) / len(scores)
    print(f"\nFINAL SCORES: {scores}", flush=True)
    print(f"AVERAGE: {avg:.2f}", flush=True)

if __name__ == "__main__":
    main()