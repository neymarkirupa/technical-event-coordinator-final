"""Shared fixtures for Technical Event Coordinator tests."""

import pytest
from env.environment import TechnicalEventEnv, Action


@pytest.fixture
def easy_env():
    """Pre-built environment for the easy task."""
    env = TechnicalEventEnv(task_id="easy")
    env.reset()
    return env


@pytest.fixture
def medium_env():
    """Pre-built environment for the medium task."""
    env = TechnicalEventEnv(task_id="medium")
    env.reset()
    return env


@pytest.fixture
def hard_env():
    """Pre-built environment for the hard task."""
    env = TechnicalEventEnv(task_id="hard")
    env.reset()
    return env


@pytest.fixture
def sample_assignments(easy_env):
    """A naive 1-to-1 assignment for the first 10 teams."""
    rooms = [r["id"] for r in easy_env.rooms]
    teams = [t["id"] for t in easy_env.teams]
    mapping = {}
    for i, tid in enumerate(teams):
        mapping[tid] = rooms[i % len(rooms)]
    return mapping
