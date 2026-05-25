import copy

import pytest
from fastapi.testclient import TestClient

import src.app as app_module

client = TestClient(app_module.app)
original_activities = copy.deepcopy(app_module.activities)


@pytest.fixture(autouse=True)
def reset_activities():
    # Arrange: restore the in-memory activity database before each test
    app_module.activities = copy.deepcopy(original_activities)
    yield
    app_module.activities = copy.deepcopy(original_activities)


def test_root_redirects_to_static_index():
    # Arrange is handled by fixture

    # Act
    response = client.get("/")

    # Assert
    assert response.status_code == 200
    assert response.url.path == "/static/index.html"


def test_get_activities_returns_available_activities():
    # Arrange is handled by fixture

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    activities = response.json()
    assert "Chess Club" in activities
    assert "Gym Class" in activities
    assert isinstance(activities["Chess Club"]["participants"], list)
    assert activities["Chess Club"]["max_participants"] == 12


def test_signup_adds_new_participant():
    # Arrange
    activity_name = "Chess Club"
    new_email = "test.student@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": new_email})

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {new_email} for {activity_name}"
    assert new_email in app_module.activities[activity_name]["participants"]


def test_duplicate_signup_returns_400():
    # Arrange
    activity_name = "Chess Club"
    existing_email = app_module.activities[activity_name]["participants"][0]

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": existing_email})

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up"


def test_remove_participant():
    # Arrange
    activity_name = "Programming Class"
    participant_email = app_module.activities[activity_name]["participants"][0]

    # Act
    response = client.delete(
        f"/activities/{activity_name}/participants",
        params={"email": participant_email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Removed {participant_email} from {activity_name}"
    assert participant_email not in app_module.activities[activity_name]["participants"]


def test_remove_missing_participant_returns_404():
    # Arrange
    activity_name = "Gym Class"
    missing_email = "missing.student@mergington.edu"

    # Act
    response = client.delete(
        f"/activities/{activity_name}/participants",
        params={"email": missing_email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"
