"""Tests for the core TechnicalEventEnv environment."""

import pytest
from env.environment import TechnicalEventEnv, Action, Observation, Reward


class TestEnvironmentSetup:
    """Verify environment initialisation and reset behaviour."""

    def test_reset_returns_observation(self, easy_env):
        obs = easy_env.reset()
        assert isinstance(obs, Observation)
        assert obs.task_id == "easy"
        assert obs.step_count == 0
        assert len(obs.rooms) == 10
        assert len(obs.teams) == 50

    def test_medium_dimensions(self, medium_env):
        obs = medium_env.state()
        assert len(obs.rooms) == 5
        assert len(obs.teams) == 20

    def test_hard_dimensions(self, hard_env):
        obs = hard_env.state()
        assert len(obs.rooms) == 7
        assert len(obs.teams) == 50

    def test_unknown_task_falls_back(self):
        env = TechnicalEventEnv(task_id="nonexistent")
        obs = env.reset()
        assert obs.task_id == "easy"


class TestStepping:
    """Verify step mechanics."""

    def test_step_returns_reward(self, easy_env, sample_assignments):
        action = Action(assignments=sample_assignments)
        obs, reward, done, info = easy_env.step(action)
        assert isinstance(reward, Reward)
        assert 0.0 < reward.score < 1.0
        assert done is True

    def test_empty_assignments_minimal_score(self, easy_env):
        action = Action(assignments={})
        obs, reward, done, _ = easy_env.step(action)
        assert reward.score == 0.01

    def test_step_increments_counter(self, easy_env, sample_assignments):
        action = Action(assignments=sample_assignments)
        obs, _, _, _ = easy_env.step(action)
        assert obs.step_count == 1


class TestScoring:
    """Verify scoring edge cases."""

    def test_perfect_coverage_high_score(self, medium_env):
        rooms = [r["id"] for r in medium_env.rooms]
        teams = [t["id"] for t in medium_env.teams]
        mapping = {tid: rooms[i % len(rooms)] for i, tid in enumerate(teams)}
        action = Action(assignments=mapping)
        _, reward, _, _ = medium_env.step(action)
        assert reward.score >= 0.4

    def test_partial_coverage(self, easy_env):
        teams = [t["id"] for t in easy_env.teams[:5]]
        rooms = [r["id"] for r in easy_env.rooms]
        mapping = {tid: rooms[0] for tid in teams}
        action = Action(assignments=mapping)
        _, reward, _, _ = easy_env.step(action)
        assert reward.score < 0.5

    def test_score_clamped_above_zero(self, easy_env):
        action = Action(assignments={"FAKE": "ROOM"})
        _, reward, _, _ = easy_env.step(action)
        assert reward.score >= 0.01
