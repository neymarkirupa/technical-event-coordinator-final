import os
import requests
from openai import OpenAI

API_BASE_URL = os.getenv("API_BASE_URL", "https://router.huggingface.co/v1")
API_KEY = os.getenv("HF_TOKEN") or os.getenv("API_KEY")
MODEL_NAME = os.getenv("MODEL_NAME", "meta-llama/Llama-3.3-70B-Instruct")

ENV_URL = "http://localhost:7860"

client = OpenAI(base_url=API_BASE_URL, api_key=API_KEY)

def reset_env(task_id: str):
    res = requests.post(f"{ENV_URL}/reset", json={"task_id": task_id})
    return res.json()

def get_state(task_id: str):
    res = requests.get(f"{ENV_URL}/state/{task_id}")
    return res.json()

def step_env(task_id: str, assignments: dict):
    res = requests.post(f"{ENV_URL}/step", json={
        "task_id": task_id,
        "assignments": assignments
    })
    return res.json()

def ask_llm(observation: dict, task_id: str) -> dict:
    prompt = f"""
You are managing a technical fest.
Task: {task_id}
Current situation:
- Rooms: {observation.get('rooms', [])}
- Teams: {observation.get('teams', [])}
- Current assignments: {observation.get('assignments', {})}

Your job: Assign teams to rooms.
Rules:
- Each team must go to exactly one room
- Don't exceed room capacity
- Don't exceed room outlets

Reply ONLY with a JSON object like this:
{{"assignments": {{"T1": "R1", "T2": "R2"}}}}
"""
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": "You are a fest management AI. Reply only with valid JSON."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=1000,
        temperature=0.2,
    )

    import json
    text = response.choices[0].message.content
    text = text.strip().replace("```json", "").replace("```", "")
    parsed = json.loads(text)
    return parsed.get("assignments", {})

def run_task(task_id: str):
    print(f"\n{'='*40}")
    print(f"Running Task: {task_id.upper()}")
    print(f"{'='*40}")

    obs = reset_env(task_id)
    print(f"Environment reset!")

    assignments = ask_llm(obs, task_id)
    print(f"AI assignments: {assignments}")

    result = step_env(task_id, assignments)
    score = result.get("reward", {}).get("score", 0.0)
    reason = result.get("reward", {}).get("reason", "")

    print(f"Score: {score}")
    print(f"Reason: {reason}")
    return score

def main():
    scores = {}
    for task_id in ["easy", "medium", "hard"]:
        scores[task_id] = run_task(task_id)

    print(f"\n{'='*40}")
    print("FINAL SCORES:")
    for task_id, score in scores.items():
        print(f"{task_id.upper()}: {score}")
    avg = sum(scores.values()) / len(scores)
    print(f"AVERAGE SCORE: {avg:.2f}")
    print(f"{'='*40}")

if __name__ == "__main__":
    main()