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


if __name__ == "__main__":
    unittest.main()
