# Campus Learning Hub API

This FastAPI app provides role-based learning registrations for any college.

## Features

- Multi-college activity catalog
- Registration as `student` or `college`
- Server-generated dummy feedback for every successful registration
- Registration listing and unregister support

## Getting Started

1. Install dependencies from the repository root:

   ```
   pip install -r requirements.txt
   ```

2. Run the API from the repository root:

   ```
   uvicorn src.app:app --reload
   ```

3. Open:
   - App UI: http://localhost:8000/static/index.html
   - API docs: http://localhost:8000/docs

## API Endpoints

| Method | Endpoint | Description |
| ------ | -------- | ----------- |
| GET | `/colleges` | List available colleges |
| GET | `/activities?college_id=northbridge` | List activities (optionally by college) |
| GET | `/registrations?college_id=northbridge` | List registrations (optionally by college) |
| POST | `/registrations` | Create role-based registration with dummy feedback |
| DELETE | `/registrations/{registration_id}` | Remove a registration |

## Example Registration Request

```json
{
  "name": "Aisha Khan",
  "email": "aisha@northbridge.edu",
  "role": "student",
  "college_id": "northbridge",
  "activity_id": "nb-ai-lab"
}
```

## Run Tests

```
pytest -q
```
