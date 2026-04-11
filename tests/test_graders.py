"""Tests for the grading module."""

import pytest
from env.grader import grade_task, grade_all_tasks, compute_final_score


class TestGradeTask:
    def test_easy_full_assignment(self):
        # build a round-robin assignment
        mapping = {f"T{i}": f"R{(i % 10) + 1}" for i in range(1, 51)}
        result = grade_task("easy", mapping)
        assert "score" in result
        assert 0.0 < result["score"] < 1.0
        assert "reason" in result

    def test_empty_assignment_returns_min(self):
        result = grade_task("easy", {})
        assert result["score"] == 0.01

    def test_medium_valid(self):
        mapping = {f"T{i}": f"R{(i % 5) + 1}" for i in range(1, 21)}
        result = grade_task("medium", mapping)
        assert result["score"] > 0.3


class TestGradeAll:
    def test_grade_all_returns_dict(self):
        assignments = {
            "easy": {f"T{i}": f"R{(i % 10) + 1}" for i in range(1, 51)},
            "medium": {f"T{i}": f"R{(i % 5) + 1}" for i in range(1, 21)},
        }
        results = grade_all_tasks(assignments)
        assert "easy" in results
        assert "medium" in results


class TestFinalScore:
    def test_compute_average(self):
        results = {
            "easy": {"score": 0.8, "reason": "ok"},
            "medium": {"score": 0.6, "reason": "ok"},
        }
        avg = compute_final_score(results)
        assert 0.5 < avg < 0.9

    def test_empty_returns_min(self):
        assert compute_final_score({}) == 0.01
