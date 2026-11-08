import hashlib

import pytest
from fastapi.testclient import TestClient

from toolkit.api import create_app
from toolkit.config import Settings


@pytest.fixture
def settings(tmp_path):
    keys = {
        hashlib.sha256(role.encode()).hexdigest(): {"id": role, "role": role}
        for role in ("analyst", "operator", "approver")
    }
    return Settings(tmp_path / "test.db", keys)


@pytest.fixture
def client(settings):
    with TestClient(create_app(settings)) as client:
        yield client


@pytest.fixture
def service(client):
    return client.app.state.service


@pytest.fixture
def proposal():
    return {
        "vehicle_id": "EV-006",
        "title": "Review maintenance alerts",
        "description": "Review synthetic alert history before escalation.",
        "priority": "urgent",
    }
