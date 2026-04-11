"""Benchmark runner for Technical Event Coordinator.

Runs the baseline agent across all difficulty tiers, collects scores,
and prints a summary table.  Useful for validating that the server
and grader are working before submitting.

Usage:
    python benchmark.py                    # default: local server
    python benchmark.py --url https://...  # remote HF Space
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from typing import Dict, List

import requests

from baseline_agent import HeuristicBaselineAgent

TASKS = ["easy", "medium", "hard"]


def run_benchmark(
    base_url: str,
    tasks: List[str] | None = None,
    seeds: List[int] | None = None,
    verbose: bool = False,
) -> Dict[str, float]:
    """Run the baseline agent across tasks and return {task_id: score}."""

    tasks = tasks or TASKS
    seeds = seeds or [42]

    agent = HeuristicBaselineAgent()
    results: Dict[str, float] = {}

    for tid in tasks:
        task_scores: List[float] = []

        for seed in seeds:
            agent.reset(seed)

            # reset environment
            resp = requests.post(
                f"{base_url}/reset",
                json={"task_id": tid},
                timeout=30,
            )
            resp.raise_for_status()
            obs = resp.json()

            inner = obs.get("observation", obs)
            rooms = inner.get("rooms", [])
            teams = inner.get("teams", [])

            mapping = agent.solve(rooms, teams)

            # submit
            resp = requests.post(
                f"{base_url}/step",
                json={"task_id": tid, "assignments": mapping},
                timeout=30,
            )
            resp.raise_for_status()
            result = resp.json()

            reward = result.get("reward", {})
            score = reward.get("score", 0) if isinstance(reward, dict) else float(reward)
            task_scores.append(score)

            if verbose:
                print(f"  {tid} seed={seed} score={score:.4f}")

        avg = sum(task_scores) / len(task_scores) if task_scores else 0
        results[tid] = round(avg, 4)

    return results


def print_table(results: Dict[str, float]) -> None:
    """Pretty-print a results table."""
    header = f"{'Task':<12} | {'Score':>8}"
    sep = "-" * len(header)
    print(sep)
    print(header)
    print(sep)
    for tid, score in results.items():
        print(f"{tid:<12} | {score:>8.4f}")
    print(sep)

    avg = sum(results.values()) / len(results) if results else 0
    print(f"{'AVERAGE':<12} | {avg:>8.4f}")
    print(sep)


def main():
    parser = argparse.ArgumentParser(description="Benchmark runner")
    parser.add_argument(
        "--url",
        default="http://localhost:7860",
        help="Base URL of the running server",
    )
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    print(f"Benchmarking against {args.url} ...")
    t0 = time.time()
    results = run_benchmark(args.url, verbose=args.verbose)
    elapsed = time.time() - t0

    print_table(results)
    print(f"\nCompleted in {elapsed:.1f}s")


if __name__ == "__main__":
    main()
