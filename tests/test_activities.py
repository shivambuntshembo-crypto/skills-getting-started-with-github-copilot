def test_get_activities_returns_list_payload(client):
    response = client.get("/activities")

    assert response.status_code == 200
    payload = response.json()

    assert "activities" in payload
    assert isinstance(payload["activities"], list)
    assert len(payload["activities"]) >= 6


def test_get_activities_can_filter_by_college(client):
    response = client.get("/activities", params={"college_id": "northbridge"})
    assert response.status_code == 200

    activities = response.json()["activities"]
    assert activities
    assert all(activity["college_id"] == "northbridge" for activity in activities)


def test_get_colleges_lists_available_colleges(client):
    response = client.get("/colleges")
    assert response.status_code == 200

    colleges = response.json()["colleges"]
    assert len(colleges) >= 3
    college_ids = {college["id"] for college in colleges}
    assert "northbridge" in college_ids
