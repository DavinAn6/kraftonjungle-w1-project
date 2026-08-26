import importlib.util
import os
import sys
import types
import unittest
from pathlib import Path

from bson import ObjectId
from flask import Flask, g


USER_ID = ObjectId()
USER = {"_id": USER_ID, "name": "tester", "email": "tester@example.com"}


class FakeUsers:
    def create_index(self, *args, **kwargs):
        return None

    def find_one(self, query):
        return USER if query.get("_id") == USER_ID else None


class FakeDB:
    def get_collection(self, name):
        assert name == "users"
        return FakeUsers()


db_module = types.ModuleType("db")
db_module.get_db = FakeDB
sys.modules["db"] = db_module
os.environ["JWT_SECRET_KEY"] = "test-secret-key-that-is-long-enough"

auth_path = Path(__file__).parents[1] / "flaskr" / "auth.py"
spec = importlib.util.spec_from_file_location("auth_under_test", auth_path)
auth = importlib.util.module_from_spec(spec)
spec.loader.exec_module(auth)


class LoginRequiredTest(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)

        @self.app.get("/private")
        @auth.login_required
        def private():
            return g.user["email"]

        self.client = self.app.test_client()

    def test_valid_sub_loads_current_user(self):
        self.client.set_cookie("access_token", auth.generate_token(USER_ID))
        response = self.client.get("/private")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_data(as_text=True), USER["email"])

    def test_unknown_sub_is_rejected(self):
        self.client.set_cookie("access_token", auth.generate_token(ObjectId()))
        response = self.client.get("/private")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.headers["Location"], "/login")


if __name__ == "__main__":
    unittest.main()
