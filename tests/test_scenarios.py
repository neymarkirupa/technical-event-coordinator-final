"""Tests for the baseline agent and task scenarios."""

import pytest
from baseline_agent import HeuristicBaselineAgent
from env.environment import TechnicalEventEnv


class TestBaselineAgent:
    def test_solve_returns_mapping(self):
        env = TechnicalEventEnv(task_id="easy")
        env.reset()
        agent = HeuristicBaselineAgent()
        mapping = agent.solve(env.rooms, env.teams)
        assert len(mapping) == 50
        assert all(tid.startswith("T") for tid in mapping.keys())

    def test_reset_clears_history(self):
        agent = HeuristicBaselineAgent()
        env = TechnicalEventEnv(task_id="easy")
        env.reset()
        agent.solve(env.rooms, env.teams)
        assert len(agent._history) == 1
        agent.reset()
        assert len(agent._history) == 0

    def test_quick_score_reasonable(self):
        env = TechnicalEventEnv(task_id="easy")
        env.reset()
        agent = HeuristicBaselineAgent()
        mapping = agent.solve(env.rooms, env.teams)
        score = agent.quick_score(env.rooms, env.teams, mapping)
        assert 0.01 <= score <= 0.99


class TestScenarios:
    """Ensure each difficulty tier produces valid scenarios."""

    @pytest.mark.parametrize("task_id,n_rooms,n_teams", [
        ("easy", 10, 50),
        ("medium", 5, 20),
        ("hard", 7, 50),
    ])
    def test_scenario_dimensions(self, task_id, n_rooms, n_teams):
        env = TechnicalEventEnv(task_id=task_id)
        obs = env.reset()
        assert len(obs.rooms) == n_rooms
        assert len(obs.teams) == n_teams

    def test_rooms_have_required_keys(self):
        env = TechnicalEventEnv(task_id="easy")
        env.reset()
        for room in env.rooms:
            assert "id" in room
            assert "capacity" in room
            assert "outlets" in room
