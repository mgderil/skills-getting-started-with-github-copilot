import copy
from urllib.parse import quote

import pytest
from fastapi.testclient import TestClient

from src.app import activities, app


client = TestClient(app)


@pytest.fixture(autouse=True)
def restore_activity_state():
    original_state = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(original_state)


def test_root_redirects_to_the_frontend():
    # Arrange

    # Act
    response = client.get("/", follow_redirects=False)

    # Assert
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_the_catalog():
    # Arrange

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    payload = response.json()
    assert "Chess Club" in payload
    assert payload["Chess Club"]["schedule"] == "Fridays, 3:30 PM - 5:00 PM"


def test_get_activities_includes_new_sports_and_arts_programs():
    # Arrange
    expected_activities = {"Tennis Club", "Soccer Team", "Photography Club", "Dance Ensemble"}

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    payload = response.json()
    for activity_name in expected_activities:
        assert activity_name in payload


def test_signup_for_activity_adds_a_participant():
    # Arrange
    activity_name = "Chess Club"
    email = "newstudent@mergington.edu"

    # Act
    response = client.post(f"/activities/{quote(activity_name, safe='')}/signup?email={email}")

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for {activity_name}"
    assert email in activities[activity_name]["participants"]


def test_signup_rejects_duplicate_participants():
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"

    # Act
    response = client.post(f"/activities/{quote(activity_name, safe='')}/signup?email={email}")

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_unregister_participant_removes_the_student():
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"

    # Act
    response = client.delete(f"/activities/{quote(activity_name, safe='')}/participants?email={email}")

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Removed {email} from {activity_name}"
    assert email not in activities[activity_name]["participants"]
