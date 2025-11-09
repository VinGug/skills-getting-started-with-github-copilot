import pytest
from fastapi.testclient import TestClient
from urllib.parse import quote

from src.app import app, activities

client = TestClient(app)


def test_get_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    # Basic sanity checks
    assert isinstance(data, dict)
    assert "Chess Club" in data


def test_root_redirects_to_index():
    resp = client.get("/", follow_redirects=True)
    assert resp.status_code == 200
    # index.html contains the school heading
    assert "Mergington High School" in resp.text


def test_signup_and_unregister_flow():
    activity = "Chess Club"
    email = "tester@example.com"

    # Ensure clean state for this test
    if email in activities[activity]["participants"]:
        activities[activity]["participants"].remove(email)

    # Sign up
    signup_resp = client.post(f"/activities/{quote(activity)}/signup?email={quote(email)}")
    assert signup_resp.status_code == 200
    assert f"Signed up {email}" in signup_resp.json().get("message", "")

    # Verify participant present
    activities_resp = client.get("/activities")
    assert activities_resp.status_code == 200
    assert email in activities_resp.json()[activity]["participants"]

    # Signing up again should fail (duplicate)
    dup_resp = client.post(f"/activities/{quote(activity)}/signup?email={quote(email)}")
    assert dup_resp.status_code == 400

    # Unregister
    unregister_resp = client.post(f"/activities/{quote(activity)}/unregister?email={quote(email)}")
    assert unregister_resp.status_code == 200
    assert f"Unregistered {email}" in unregister_resp.json().get("message", "")

    # Verify removed
    activities_resp = client.get("/activities")
    assert email not in activities_resp.json()[activity]["participants"]
