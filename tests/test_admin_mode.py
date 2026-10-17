import hashlib
import json
import os
import tempfile
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

from src import app as app_module


class AdminModeTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.credentials_path = Path(self.temp_dir.name) / "teachers.json"
        salt = b"test-salt-for-admin-mode"
        password_hash = hashlib.pbkdf2_hmac(
            "sha256", b"test-password", salt, 100_000
        ).hex()
        self.credentials_path.write_text(
            json.dumps({
                "teachers": [{
                    "username": "teacher",
                    "password_hash": f"pbkdf2_sha256$100000${salt.hex()}${password_hash}",
                }]
            }),
            encoding="utf-8",
        )
        self.previous_credentials_path = os.environ.get("TEACHERS_FILE")
        os.environ["TEACHERS_FILE"] = str(self.credentials_path)
        app_module.activities["Test Activity"] = {
            "description": "Test activity",
            "schedule": "Mondays",
            "max_participants": 3,
            "participants": [],
        }
        self.client = TestClient(app_module.app)

    def tearDown(self):
        app_module.activities.pop("Test Activity", None)
        if self.previous_credentials_path is None:
            os.environ.pop("TEACHERS_FILE", None)
        else:
            os.environ["TEACHERS_FILE"] = self.previous_credentials_path
        self.temp_dir.cleanup()

    def test_public_can_view_activities_but_cannot_change_participants(self):
        self.assertEqual(self.client.get("/activities").status_code, 200)
        signup = self.client.post(
            "/activities/Test%20Activity/signup",
            params={"email": "student@example.edu"},
        )
        unregister = self.client.delete(
            "/activities/Test%20Activity/unregister",
            params={"email": "student@example.edu"},
        )
        self.assertEqual(signup.status_code, 401)
        self.assertEqual(unregister.status_code, 401)

    def test_teacher_can_sign_up_and_unregister_students(self):
        login = self.client.post(
            "/auth/login",
            json={"username": "teacher", "password": "test-password"},
        )
        self.assertEqual(login.status_code, 200)

        signup = self.client.post(
            "/activities/Test%20Activity/signup",
            params={"email": "student@example.edu"},
        )
        unregister = self.client.delete(
            "/activities/Test%20Activity/unregister",
            params={"email": "student@example.edu"},
        )
        self.assertEqual(signup.status_code, 200)
        self.assertEqual(unregister.status_code, 200)

    def test_invalid_teacher_password_is_rejected(self):
        response = self.client.post(
            "/auth/login",
            json={"username": "teacher", "password": "wrong-password"},
        )
        self.assertEqual(response.status_code, 401)


if __name__ == "__main__":
    unittest.main()