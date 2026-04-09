"""Inference script — talks to the deployed HF Space environment
and uses the hackathon-provided LLM proxy to solve each task.

The agent follows a straightforward loop for every task:
  1. POST /reset  → get the initial observation (rooms + teams)
  2. Build a prompt that describes the constraint-satisfaction problem
  3. Ask the LLM to produce a team→room JSON mapping
  4. POST /step   → submit assignments, receive the reward

Scores are printed to stdout so the evaluation harness can parse them.
"""

import os
import sys
import json
import math
import requests
from openai import OpenAI

# ── configuration ──────────────────────────────────────────────────
ENV_URL = "https://kirubakaransl-technical-event-coordinator.hf.space"

API_BASE_URL = os.environ.get("API_BASE_URL", "")
API_KEY = os.environ.get("API_KEY", "")

_llm = OpenAI(base_url=API_BASE_URL, api_key=API_KEY)

TASKS = ["easy", "medium", "hard"]


# ── environment helpers ────────────────────────────────────────────

def _post(endpoint: str, payload: dict) -> dict:
    """Fire a POST request to the HF Space and return parsed JSON."""
    url = f"{ENV_URL}/{endpoint.lstrip('/')}"
    resp = requests.post(url, json=payload, timeout=30)
    resp.raise_for_status()
    return resp.json()


def reset_task(task_id: str) -> dict:
    return _post("reset", {"task_id": task_id})


def submit_assignments(task_id: str, mapping: dict) -> dict:
    return _post("step", {"task_id": task_id, "assignments": mapping})


# ── heuristic solver (fallback) ───────────────────────────────────

def _heuristic_assign(rooms, teams):
    """Greedy bin-packing: sort teams by laptop count descending,
    try to fit each team into the room with the most remaining
    capacity and outlets.  Not optimal, but a solid baseline."""

    # mutable copies so we can track remaining capacity
    buckets = []
    for r in rooms:
        buckets.append({
            "id": r["id"],
            "cap_left": r["capacity"],
            "out_left": r["outlets"],
        })

    sorted_teams = sorted(teams, key=lambda t: t.get("laptops", 0), reverse=True)
    result = {}

    for team in sorted_teams:
        tid = team["id"]
        need_laps = team.get("laptops", 0)

        # pick the room with the best remaining headroom
        best_room = None
        best_slack = -999
        for b in buckets:
            slack = min(b["cap_left"], b["out_left"] - need_laps)
            if slack > best_slack:
                best_slack = slack
                best_room = b

        if best_room is None:
            best_room = buckets[0]

        result[tid] = best_room["id"]
        best_room["cap_left"] -= 1
        best_room["out_left"] -= need_laps

    return result


# ── LLM-based solver ─────────────────────────────────────────────

def _build_prompt(rooms, teams):
    """Construct an instruction prompt describing the assignment problem."""
    lines = [
        "You are an expert event logistics planner.",
        "Given the rooms and teams below, produce an optimal assignment",
        "of teams to rooms.",
        "",
        "### Rooms",
        json.dumps(rooms, indent=2),
        "",
        "### Teams",
        json.dumps(teams, indent=2),
        "",
        "### Constraints (in priority order)",
        "1. Every team must be assigned to exactly one room.",
        "2. The number of teams in a room must not exceed its capacity.",
        "3. The total laptops in a room must not exceed its outlet count.",
        "4. Spread teams across rooms as evenly as possible.",
        "",
        "Return ONLY a JSON object mapping team IDs to room IDs.",
        'Example: {"T1": "R1", "T2": "R3", ...}',
        "Do not include any explanation or markdown fences.",
    ]
    return "\n".join(lines)


def _strip_fences(text: str) -> str:
    """Remove markdown code fences the LLM sometimes wraps around JSON."""
    text = text.strip()
    if text.startswith("```"):
        # drop the opening fence line
        first_nl = text.find("\n")
        text = text[first_nl + 1:] if first_nl != -1 else text[3:]
    if text.endswith("```"):
        text = text[:-3]
    return text.strip()


def llm_solve(rooms, teams, task_id: str) -> dict:
    """Ask the LLM proxy for an assignment; fall back to heuristic on error."""
    prompt = _build_prompt(rooms, teams)

    try:
        completion = _llm.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a constraint-satisfaction solver. "
                        "Reply with valid JSON only, no commentary."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.15,
            max_tokens=4096,
        )
        raw = completion.choices[0].message.content
        cleaned = _strip_fences(raw)
        mapping = json.loads(cleaned)
        print(f"  [llm] produced {len(mapping)} assignments", flush=True)
        return mapping

    except Exception as exc:
        print(f"  [llm-fallback] {exc}", flush=True)
        return _heuristic_assign(rooms, teams)


# ── main loop ─────────────────────────────────────────────────────

def _safe_score(raw) -> float:
    """Extract a numeric score and clamp it to the open interval (0, 1)."""
    if isinstance(raw, dict):
        val = float(raw.get("score", 0))
    else:
        val = float(raw)
    # the grader rejects exact 0.0 and 1.0
    if val <= 0.0:
        return 0.01
    if val >= 1.0:
        return 0.99
    return round(val, 4)


def run_single_task(task_id: str) -> float:
    print(f"[task:{task_id}] resetting environment …", flush=True)
    obs = reset_task(task_id)

    # unpack teams + rooms from either nesting format
    inner = obs.get("observation", obs)
    teams = inner.get("teams", [])
    rooms = inner.get("rooms", [])

    assignments = llm_solve(rooms, teams, task_id)
    result = submit_assignments(task_id, assignments)

    score = _safe_score(result.get("reward", 0))
    print(f"[task:{task_id}] score = {score}", flush=True)
    return score


def main():
    scores = {}
    for tid in TASKS:
        try:
            scores[tid] = run_single_task(tid)
        except Exception as err:
            print(f"[task:{tid}] FAILED — {err}", flush=True)
            scores[tid] = 0.01          # safe fallback

    avg = sum(scores.values()) / len(scores) if scores else 0.01
    print(f"\nPer-task scores : {scores}", flush=True)
    print(f"Average score   : {avg:.4f}", flush=True)


if __name__ == "__main__":
    main()