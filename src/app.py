"""College learning platform API with role-based registrations."""

from datetime import datetime, timezone
from uuid import uuid4

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import os
from pathlib import Path
from pydantic import BaseModel

app = FastAPI(
    title="Campus Learning Hub API",
    description="API for college and student learning registrations",
)

# Mount the static files directory
current_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=os.path.join(Path(__file__).parent,
          "static")), name="static")

class RegistrationRequest(BaseModel):
    name: str
    email: str
    role: str
    college_id: str
    activity_id: str


SUPPORTED_ROLES = {"college", "student"}

colleges = {
    "northbridge": {
        "name": "Northbridge College",
        "city": "Boston",
        "focus": "Engineering and Applied Sciences",
    },
    "lakeside": {
        "name": "Lakeside Institute",
        "city": "Chicago",
        "focus": "Business and Leadership",
    },
    "suncrest": {
        "name": "Suncrest University",
        "city": "San Diego",
        "focus": "Arts and Digital Media",
    },
}

activities = {
    "nb-ai-lab": {
        "id": "nb-ai-lab",
        "title": "AI Foundations Lab",
        "college_id": "northbridge",
        "description": "Hands-on machine learning fundamentals and model evaluation.",
        "schedule": "Mon and Wed, 4:00 PM - 5:30 PM",
        "max_participants": 24,
        "participants": [],
    },
    "nb-data-story": {
        "id": "nb-data-story",
        "title": "Data Storytelling Studio",
        "college_id": "northbridge",
        "description": "Communicate data insights through visuals and narrative.",
        "schedule": "Fri, 2:30 PM - 4:00 PM",
        "max_participants": 20,
        "participants": [],
    },
    "li-product": {
        "id": "li-product",
        "title": "Product Strategy Sprint",
        "college_id": "lakeside",
        "description": "Build product roadmaps with customer-first thinking.",
        "schedule": "Tue, 3:00 PM - 4:30 PM",
        "max_participants": 26,
        "participants": [],
    },
    "li-negotiation": {
        "id": "li-negotiation",
        "title": "Negotiation Masterclass",
        "college_id": "lakeside",
        "description": "Practice practical negotiation and stakeholder alignment.",
        "schedule": "Thu, 5:00 PM - 6:15 PM",
        "max_participants": 18,
        "participants": [],
    },
    "su-creative": {
        "id": "su-creative",
        "title": "Creative Coding Workshop",
        "college_id": "suncrest",
        "description": "Blend design and code for interactive digital art.",
        "schedule": "Wed, 1:00 PM - 3:00 PM",
        "max_participants": 16,
        "participants": [],
    },
    "su-film": {
        "id": "su-film",
        "title": "Film Critique Circle",
        "college_id": "suncrest",
        "description": "Analyze cinematic storytelling, pacing, and visual language.",
        "schedule": "Fri, 4:00 PM - 5:30 PM",
        "max_participants": 14,
        "participants": [],
    },
}

users = {}
registrations = {}


def build_dummy_feedback(name: str, role: str, college_name: str, activity_title: str) -> str:
    role_label = "college representative" if role == "college" else "student"
    return (
        f"Dummy feedback: {name} registered as a {role_label} for {activity_title} at "
        f"{college_name}. Engagement level: excellent."
    )


def serialize_registration(registration: dict) -> dict:
    college = colleges[registration["college_id"]]
    activity = activities[registration["activity_id"]]
    return {
        **registration,
        "college_name": college["name"],
        "activity_title": activity["title"],
    }


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/colleges")
def get_colleges():
    return {
        "colleges": [
            {
                "id": college_id,
                **college_data,
            }
            for college_id, college_data in colleges.items()
        ]
    }


@app.get("/activities")
def get_activities(college_id: str | None = None):
    activity_items = []
    for activity in activities.values():
        if college_id and activity["college_id"] != college_id:
            continue
        activity_items.append(activity)
    return {"activities": activity_items}


@app.get("/registrations")
def get_registrations(college_id: str | None = None):
    registration_items = []
    for registration in registrations.values():
        if college_id and registration["college_id"] != college_id:
            continue
        registration_items.append(serialize_registration(registration))
    return {"registrations": registration_items}


@app.post("/registrations")
def create_registration(payload: RegistrationRequest):
    role = payload.role.strip().lower()
    if role not in SUPPORTED_ROLES:
        raise HTTPException(status_code=400, detail="Role must be either 'college' or 'student'")

    if payload.college_id not in colleges:
        raise HTTPException(status_code=404, detail="College not found")

    if payload.activity_id not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    activity = activities[payload.activity_id]
    if activity["college_id"] != payload.college_id:
        raise HTTPException(status_code=400, detail="Activity does not belong to selected college")

    if len(activity["participants"]) >= activity["max_participants"]:
        raise HTTPException(status_code=400, detail="Activity has reached max participants")

    duplicate = next(
        (
            reg
            for reg in registrations.values()
            if reg["email"] == payload.email
            and reg["role"] == role
            and reg["college_id"] == payload.college_id
            and reg["activity_id"] == payload.activity_id
        ),
        None,
    )
    if duplicate:
        raise HTTPException(status_code=400, detail="Registration already exists")

    existing_user = users.get(payload.email)
    if existing_user and existing_user["role"] != role:
        raise HTTPException(status_code=400, detail="Email is already used with a different role")

    users[payload.email] = {
        "name": payload.name.strip(),
        "email": payload.email.strip(),
        "role": role,
        "college_id": payload.college_id,
    }

    college_name = colleges[payload.college_id]["name"]
    feedback = build_dummy_feedback(payload.name.strip(), role, college_name, activity["title"])

    registration_id = str(uuid4())
    registration = {
        "id": registration_id,
        "name": payload.name.strip(),
        "email": payload.email.strip(),
        "role": role,
        "college_id": payload.college_id,
        "activity_id": payload.activity_id,
        "dummy_feedback": feedback,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    registrations[registration_id] = registration

    if payload.email not in activity["participants"]:
        activity["participants"].append(payload.email)

    return {
        "message": "Registration successful",
        "registration": serialize_registration(registration),
    }


@app.delete("/registrations/{registration_id}")
def delete_registration(registration_id: str):
    if registration_id not in registrations:
        raise HTTPException(status_code=404, detail="Registration not found")

    registration = registrations.pop(registration_id)
    activity = activities[registration["activity_id"]]

    if registration["email"] in activity["participants"]:
        has_other_registration = any(
            reg["email"] == registration["email"] and reg["activity_id"] == registration["activity_id"]
            for reg in registrations.values()
        )
        if not has_other_registration:
            activity["participants"].remove(registration["email"])

    return {"message": f"Unregistered {registration['email']} from {activity['title']}"}
