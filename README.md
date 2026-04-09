---
title: Technical Event Coordinator
emoji: 🎯
colorFrom: blue
colorTo: purple
sdk: docker
app_port: 7860
---

# Technical Event Coordinator — OpenEnv Environment

An interactive simulation of a large-scale technical fest.  The AI agent
must deal with the messy realities of room assignments, scheduling overlaps,
and last-minute budget shocks — all through a simple REST API.

## Problem Statement

Managing a college hackathon sounds easy until 50 teams show up and only
10 rooms have power outlets.  This environment formalises the logistical
nightmare into three graded tasks so an LLM can tackle it programmatically.

## Tasks

| Difficulty | Name | What the agent must do |
|------------|------|------------------------|
| **Easy** | Room Assignment | Assign 50 teams to 10 rooms subject to seating + outlet limits |
| **Medium** | Schedule Conflict | Resolve a VIP-judge double-booking without cascading conflicts |
| **Hard** | Sponsor Pullout | Re-distribute prizes after a sponsor withdraws, staying in budget |

## API

### `POST /reset`
Reset the environment.  Accepts `{"task_id": "easy"}`.

### `POST /step`
Submit assignments:
```json
{
  "task_id": "easy",
  "assignments": {"T1": "R1", "T2": "R3"}
}
```
Returns `observation`, `reward` (with `score` and `reason`), and `done`.

### `POST /grade`
Stateless grading — same schema as `/step`.

### `GET /tasks`
List available tasks with descriptions.

### `GET /health`
Returns `{"status": "ok"}`.

## Scoring

Every task yields a score in the open interval **(0, 1)**.  The score
reflects coverage of teams, capacity-overflow penalties, outlet-overflow
penalties, and a balance bonus for even distribution.

## Running Locally

```bash
pip install -r requirements.txt
uvicorn server.app:app --host 0.0.0.0 --port 7860
```

### Docker

```bash
docker build -t tec .
docker run -p 7860:7860 tec
```

### Inference

```bash
export API_BASE_URL=https://router.huggingface.co/v1
export API_KEY=<your-token>
python inference.py
```

## Approach

The inference agent uses a two-tier strategy:

1. **LLM planner** — sends the room/team data to GPT-4o-mini and asks
   for a constraint-aware mapping.
2. **Greedy bin-packing fallback** — if the LLM call fails, teams are
   sorted by laptop count (descending) and packed into the room with
   the most remaining capacity headroom.

This hybrid approach ensures we always produce a valid assignment even
when the LLM produces malformed output.

## Baseline Scores

| Task   | Score |
|--------|-------|
| Easy   | ~0.75 |
| Medium | ~0.65 |
| Hard   | ~0.45 |

## Team

- **Team Name:** NULL BYTE
- **Hackathon:** Meta Hackathon × Scaler — OpenEnv Track