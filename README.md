---
title: Technical Event Coordinator
emoji: 🎯
colorFrom: blue
colorTo: purple
sdk: docker
app_port: 7860
---

# Technical Event Coordinator Environment

## Description
An OpenEnv environment that simulates managing a large-scale technical fest.
The AI agent must handle room assignments, scheduling conflicts, and budget crises.

## Tasks

### Easy — Room Assignment
- Assign 50 teams to 10 rooms
- Constraints: seating capacity and power outlets
- Score: percentage of teams correctly assigned

### Medium — Schedule Conflict Resolution
- Resolve a double-booked VIP judge conflict
- Score: based on conflicts resolved without creating new ones

### Hard — Sponsor Pullout Crisis
- A major sponsor pulled out 24 hours before closing ceremony
- Rewrite prize distribution without going into the red
- Score: based on constraints satisfied and budget maintained

## Action Space
JSON object with team to room assignments:
```json
{
  "assignments": {
    "T1": "R1",
    "T2": "R2"
  }
}
```

## Observation Space
JSON object containing:
- `rooms` — list of rooms with capacity and outlets
- `teams` — list of teams with size and laptops
- `assignments` — current team to room assignments
- `task_id` — current task (easy/medium/hard)
- `step_count` — number of steps taken

## Reward
- Score between 0.0 and 1.0
- Based on percentage of constraints satisfied

## Setup Instructions

### Local Setup
```bash
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 7860
```

### Docker Setup
```bash
docker build -t technical-event-coordinator .
docker run -p 7860:7860 technical-event-coordinator
```

### Run Inference
```bash
export HF_TOKEN=your_token
export MODEL_NAME=meta-llama/Llama-3.3-70B-Instruct
export API_BASE_URL=https://router.huggingface.co/v1
python inference.py
```

## Baseline Scores
| Task | Score |
|------|-------|
| Easy | 0.75 |
| Medium | 0.65 |
| Hard | 0.55 |

## Team
- Team Name: NULL BYTE
- Hackathon: OpenEnv x Scaler Hackathon