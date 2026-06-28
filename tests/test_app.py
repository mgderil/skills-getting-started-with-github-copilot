from fastapi.testclient import TestClient

from src.app import app, activities


client = TestClient(app)


def test_unregister_participant_from_activity():
    activity_name = "Chess Club"
    email = "michael@mergington.edu"
    activity = activities[activity_name]
    original_participants = activity["participants"].copy()

    try:
        response = client.delete(f"/activities/{activity_name}/participants?email={email}")

        assert response.status_code == 200
        assert response.json()["message"] == f"Removed {email} from {activity_name}"
        assert email not in activity["participants"]
    finally:
        activity["participants"] = original_participants
