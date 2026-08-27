from flask import Blueprint, g, render_template, jsonify, request
from bson import ObjectId

from db import get_db

from auth import login_required

task = Blueprint("task", __name__)

db = get_db()
tasks_col = db["tasks"]
projects_col = db["projects"]
TASK_STATUSES = {"not-started", "in-progress", "done"}


def find_member_project(project_id):
    return projects_col.find_one({"_id": project_id, "members.email": g.user["email"]})


@task.route("/dashboard")
@login_required
def dashboard():
    """현재 사용자가 참여 중인 프로젝트 대시보드입니다."""
    projects = list(projects_col.find({"members.email": g.user["email"]}))
    return render_template("dashboard.html", projects=projects, name=g.user["name"])


@task.route("/api/tasks/<project_id>", methods=["GET"])
@login_required
def get_tasks(project_id):
    """Task 대시보드에 들어갈 내용입니다.

    1. 주 프로젝트의 ObjectId로 구분합니다.
    """
    if not ObjectId.is_valid(project_id):
        return jsonify({"error": "Invalid project id"}), 400

    project_oid = ObjectId(project_id)
    project = find_member_project(project_oid)
    if not project:
        return jsonify({"error": "Project not found"}), 404

    tasks = list(tasks_col.find({"project_id": project_oid}))
    return jsonify(
        {
            "members": project.get("members", []),
            "tasks": [serialize_task(t) for t in tasks],
        }
    )


@task.route("/api/tasks", methods=["POST"])
@login_required
def add_task():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "Invalid request"}), 400

    required = ["project_id", "agenda", "due_date", "owner"]
    missing = [f for f in required if not data.get(f)]
    if missing:
        return jsonify({"error": f"Missing fields: {', '.join(missing)}"}), 400

    status = data.get("status", "not-started")
    if status not in TASK_STATUSES:
        return jsonify({"error": "Invalid status"}), 400

    try:
        project_oid = ObjectId(data["project_id"])
    except Exception:
        return jsonify({"error": "Invalid project id"}), 400

    project = find_member_project(project_oid)
    if not project:
        return jsonify({"error": "Project not found"}), 404

    task = {
        "project_id": ObjectId(data["project_id"]),
        "agenda": data["agenda"],
        "due_date": data["due_date"],
        "owner": data["owner"],
        "status": status,
    }

    result = tasks_col.insert_one(task)
    task["_id"] = result.inserted_id

    return jsonify(serialize_task(task)), 201


def serialize_task(task):
    task["_id"] = str(task["_id"])
    task["project_id"] = str(task["project_id"])
    return task


@task.route("/api/tasks", methods=["DELETE"])
@login_required
def delete_tasks():
    data = request.get_json(silent=True) or {}
    task_ids = data.get("task_ids")
    if (
        not isinstance(task_ids, list)
        or not task_ids
        or any(not ObjectId.is_valid(task_id) for task_id in task_ids)
    ):
        return jsonify({"error": "Invalid task ids"}), 400

    ids = list({ObjectId(task_id) for task_id in task_ids})
    task_docs = list(tasks_col.find({"_id": {"$in": ids}}))
    if len(task_docs) != len(ids) or any(
        not find_member_project(task_doc["project_id"]) for task_doc in task_docs
    ):
        return jsonify({"error": "Task not found"}), 404

    result = tasks_col.delete_many({"_id": {"$in": ids}})
    return jsonify({"deleted": result.deleted_count}), 200


@task.route("/api/tasks/<task_id>", methods=["PATCH"])
@login_required
def update_task(task_id):
    if not ObjectId.is_valid(task_id):
        return jsonify({"error": "Invalid task id"}), 400

    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "Invalid request"}), 400

    allowed_fields = ["agenda", "due_date", "owner", "status"]
    updates = {k: v for k, v in data.items() if k in allowed_fields}
    if not updates:
        return jsonify({"error": "No valid fields"}), 400
    if "status" in updates and updates["status"] not in TASK_STATUSES:
        return jsonify({"error": "Invalid status"}), 400

    task_doc = tasks_col.find_one({"_id": ObjectId(task_id)})
    if not task_doc or not find_member_project(task_doc["project_id"]):
        return jsonify({"error": "Task not found"}), 404

    result = tasks_col.update_one({"_id": ObjectId(task_id)}, {"$set": updates})
    if result.matched_count == 0:
        return jsonify({"error": "Task not found"}), 404

    return jsonify({"updated": True}), 200
