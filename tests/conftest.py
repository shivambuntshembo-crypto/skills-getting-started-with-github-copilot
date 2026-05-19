import copy

import pytest
from fastapi.testclient import TestClient

from src.app import activities, app, colleges, registrations, users


@pytest.fixture
def client():
    original_colleges = copy.deepcopy(colleges)
    original_activities = copy.deepcopy(activities)
    original_users = copy.deepcopy(users)
    original_registrations = copy.deepcopy(registrations)
    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        colleges.clear()
        colleges.update(original_colleges)
        activities.clear()
        activities.update(original_activities)
        users.clear()
        users.update(original_users)
        registrations.clear()
        registrations.update(original_registrations)
