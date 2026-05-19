def test_delete_registration_removes_participant(client):
    payload = {
        "name": "Noah Singh",
        "email": "noah@suncrest.edu",
        "role": "student",
        "college_id": "suncrest",
        "activity_id": "su-creative",
    }

    create_response = client.post("/registrations", json=payload)
    registration_id = create_response.json()["registration"]["id"]

    delete_response = client.delete(f"/registrations/{registration_id}")
    assert delete_response.status_code == 200
    assert "Unregistered" in delete_response.json()["message"]

    activities_response = client.get("/activities", params={"college_id": "suncrest"})
    activity = next(a for a in activities_response.json()["activities"] if a["id"] == "su-creative")
    assert payload["email"] not in activity["participants"]


def test_delete_unknown_registration_returns_404(client):
    response = client.delete("/registrations/missing-id")
    assert response.status_code == 404
    assert response.json()["detail"] == "Registration not found"


def test_get_registrations_filters_by_college(client):
    first_payload = {
        "name": "Alex Rivera",
        "email": "alex@northbridge.edu",
        "role": "student",
        "college_id": "northbridge",
        "activity_id": "nb-data-story",
    }
    second_payload = {
        "name": "Sara Nguyen",
        "email": "sara@lakeside.edu",
        "role": "college",
        "college_id": "lakeside",
        "activity_id": "li-product",
    }

    client.post("/registrations", json=first_payload)
    client.post("/registrations", json=second_payload)

    response = client.get("/registrations", params={"college_id": "lakeside"})

    assert response.status_code == 200
    registrations = response.json()["registrations"]
    assert len(registrations) == 1
    assert registrations[0]["college_id"] == "lakeside"
