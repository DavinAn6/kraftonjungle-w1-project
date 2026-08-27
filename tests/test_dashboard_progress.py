import importlib.util
import sys
import types
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from bson import ObjectId
from flask import Flask, g


projects = Mock()
tasks = Mock()
db_module = types.ModuleType("db")
db_module.get_db = lambda: {"projects": projects, "tasks": tasks}
auth_module = types.ModuleType("auth")
auth_module.login_required = lambda view: view
sys.modules["db"] = db_module
sys.modules["auth"] = auth_module

task_path = Path(__file__).parents[1] / "flaskr" / "task.py"
spec = importlib.util.spec_from_file_location("task_under_test", task_path)
task_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(task_module)


class DashboardProgressTest(unittest.TestCase):
    def setUp(self):
        projects.reset_mock()
        tasks.reset_mock()
        tasks.count_documents.side_effect = None

    def test_progress_uses_completed_task_ratio(self):
        project = {"_id": ObjectId()}
        projects.find.return_value = [project]
        tasks.count_documents.side_effect = [4, 3]

        with Flask(__name__).test_request_context(), patch.object(
            task_module, "render_template", return_value="dashboard"
        ):
            g.user = {"name": "tester", "email": "tester@example.com"}
            self.assertEqual(task_module.dashboard(), "dashboard")

        self.assertEqual(project["progress"], 75)

    def test_task_fields_are_validated_and_updated(self):
        task_id = ObjectId()
        project_id = ObjectId()
        tasks.find_one.return_value = {"_id": task_id, "project_id": project_id}
        tasks.update_one.return_value = Mock(matched_count=1)
        projects.find_one.return_value = {
            "_id": project_id,
            "members": [{"name": "tester", "email": "tester@example.com"}],
        }
        app = Flask(__name__)

        with app.test_request_context(
            f"/api/tasks/{task_id}", method="PATCH", json={"agenda": "   "}
        ):
            g.user = {"email": "tester@example.com"}
            _, status = task_module.update_task(str(task_id))
        self.assertEqual(status, 400)
        tasks.update_one.assert_not_called()

        with app.test_request_context(
            f"/api/tasks/{task_id}", method="PATCH", json={"agenda": "  수정된 태스크  "}
        ):
            g.user = {"email": "tester@example.com"}
            _, status = task_module.update_task(str(task_id))
        self.assertEqual(status, 200)
        tasks.update_one.assert_called_once_with(
            {"_id": task_id}, {"$set": {"agenda": "수정된 태스크"}}
        )

        tasks.update_one.reset_mock()
        with app.test_request_context(
            f"/api/tasks/{task_id}", method="PATCH", json={"owner": "outsider"}
        ):
            g.user = {"email": "tester@example.com"}
            _, status = task_module.update_task(str(task_id))
        self.assertEqual(status, 400)
        tasks.update_one.assert_not_called()

    def test_get_tasks_returns_project_members(self):
        project_id = ObjectId()
        members = [{"name": "tester", "email": "tester@example.com"}]
        projects.find_one.return_value = {"_id": project_id, "members": members}
        tasks.find.return_value = []
        app = Flask(__name__)

        with app.test_request_context(f"/api/tasks/{project_id}"):
            g.user = {"email": "tester@example.com"}
            response = task_module.get_tasks(str(project_id))

        self.assertEqual(response.get_json(), {"members": members, "tasks": []})


if __name__ == "__main__":
    unittest.main()
