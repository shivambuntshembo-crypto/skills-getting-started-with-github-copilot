def test_registration_creates_record_and_feedback(client):
    payload = {
        "name": "Aisha Khan",
        "email": "aisha@northbridge.edu",
        "role": "student",
        "college_id": "northbridge",
        "activity_id": "nb-ai-lab",
    }

    response = client.post("/registrations", json=payload)

    assert response.status_code == 200
    body = response.json()
    assert body["message"] == "Registration successful"
    assert "Dummy feedback:" in body["registration"]["dummy_feedback"]
    assert body["registration"]["role"] == "student"

    activities_response = client.get("/activities", params={"college_id": "northbridge"})
    activity = next(a for a in activities_response.json()["activities"] if a["id"] == "nb-ai-lab")
    assert payload["email"] in activity["participants"]


def test_registration_rejects_duplicate(client):
    payload = {
        "name": "Mina Carter",
        "email": "mina@northbridge.edu",
        "role": "student",
        "college_id": "northbridge",
        "activity_id": "nb-ai-lab",
    }

    first = client.post("/registrations", json=payload)
    second = client.post("/registrations", json=payload)

    assert first.status_code == 200
    assert second.status_code == 400
    assert second.json()["detail"] == "Registration already exists"


def test_registration_rejects_invalid_role(client):
    payload = {
        "name": "Jordan Blake",
        "email": "jordan@northbridge.edu",
        "role": "mentor",
        "college_id": "northbridge",
        "activity_id": "nb-ai-lab",
    }

    response = client.post("/registrations", json=payload)

    assert response.status_code == 400
    assert response.json()["detail"] == "Role must be either 'college' or 'student'"


def test_registration_rejects_college_activity_mismatch(client):
    payload = {
        "name": "Rina Lopez",
        "email": "rina@lakeside.edu",
        "role": "college",
        "college_id": "lakeside",
        "activity_id": "nb-ai-lab",
    }

    response = client.post("/registrations", json=payload)

    assert response.status_code == 400
    assert response.json()["detail"] == "Activity does not belong to selected college"
