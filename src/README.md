# Mergington High School Activities API

A super simple FastAPI application that allows students to view and sign up for extracurricular activities.

## Features

- View all available extracurricular activities
- Sign up for activities

## Getting Started

1. Install the dependencies:

   ```
   pip install -r requirements.txt
   ```

2. Create the local teacher credentials file:

   ```
   cp src/teachers.example.json src/teachers.json
   ```

   Replace the example `password_hash` with a hash generated for the teacher's password:

   ```
   python -c "import hashlib,secrets; p=input('Teacher password: '); s=secrets.token_bytes(16); print('pbkdf2_sha256$310000$'+s.hex()+'$'+hashlib.pbkdf2_hmac('sha256',p.encode(),s,310000).hex())"
   ```

   `src/teachers.json` is ignored by Git. You can add multiple entries to its `teachers` array. For deployment, configure a persistent session signing key:

   ```
   export SESSION_SECRET="$(python -c 'import secrets; print(secrets.token_urlsafe(32))')"
   ```

   Set `SESSION_COOKIE_SECURE=true` only when serving the app over HTTPS. Leave it unset for local HTTP development.

3. Run the application:

   ```
   uvicorn src.app:app --reload
   ```

4. Open your browser and go to:
   - API documentation: http://localhost:8000/docs
   - Alternative documentation: http://localhost:8000/redoc

## API Endpoints

| Method | Endpoint                                                          | Description                                                         |
| ------ | ----------------------------------------------------------------- | ------------------------------------------------------------------- |
| GET    | `/activities`                                                     | Get all activities with their details and current participant count |
| POST   | `/auth/login`                                                     | Log in as a teacher using a JSON username/password body              |
| GET    | `/auth/me`                                                        | Get the current teacher session status                               |
| POST   | `/auth/logout`                                                    | Log out the current teacher                                          |
| POST   | `/activities/{activity_name}/signup?email=student@mergington.edu` | Teacher-only student registration                                    |
| DELETE | `/activities/{activity_name}/unregister?email=student@mergington.edu` | Teacher-only student unregistration                                |

## Data Model

The application uses a simple data model with meaningful identifiers:

1. **Activities** - Uses activity name as identifier:

   - Description
   - Schedule
   - Maximum number of participants allowed
   - List of student emails who are signed up

2. **Students** - Uses email as identifier:
   - Name
   - Grade level

All activity and participant data is stored in memory, which means it will be reset when the server restarts. Teacher credentials are loaded from `src/teachers.json`; passwords must use the documented PBKDF2-SHA256 format. Public visitors can view activities and participants, while only logged-in teachers can register or unregister students.

Run the authentication tests with:

```
python -m unittest discover -s tests
```
