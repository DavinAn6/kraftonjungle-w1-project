from flask import Blueprint, render_template, jsonify, request
from bson import ObjectId

from db import get_db

from auth import login_required

task = Blueprint("task", __name__)

db = get_db()
tasks_col = db["tasks"]


@task.route("/dashboard")
@login_required
def dashboard():
    """대시보드입니다.
    쿠키에 적힌 사용자명 기반으로 이름을 바꿔서 보여줍니다.

    """
    name = request.cookies.get("name")
    projects = list(db.project_info.find({"members": name}))
    return render_template("dashboard.html", projects=projects, name=name)


@task.route("/api/tasks/<project_id>", methods=["GET"])
@login_required
def get_tasks(project_id):
    """Task 대시보드에 들어갈 내용입니다.

    1. 주 프로젝트의 ObjectId로 구분합니다.
    """
    tasks = list(tasks_col.find({"project_id": ObjectId(project_id)}))
    return jsonify([serialize_task(t) for t in tasks])


@task.route("/api/tasks", methods=["POST"])
@login_required
def add_task():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid request"}), 400

    required = ["project_id", "agenda", "due_date", "owner"]
    missing = [f for f in required if not data.get(f)]
    if missing:
        return jsonify({"error": f"Missing fields: {', '.join(missing)}"}), 400

    try:
        project_oid = ObjectId(data["project_id"])
    except Exception:
        return jsonify({"error": "Invalid project id"}), 400

    project = db.project_info.find_one({"_id": project_oid})
    if not project:
        return jsonify({"error": "Project not found"}), 404

    task = {
        "project_id": ObjectId(data["project_id"]),
        "agenda": data["agenda"],
        "due_date": data["due_date"],
        "owner": data["owner"],
        "status": data.get("status", "Not Started"),
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
    data = request.get_json()
    ids = [ObjectId(i) for i in data["task_ids"]]
    tasks_col.delete_many({"_id": {"$in": ids}})
    return jsonify({"deleted": len(ids)}), 200


@task.route("/api/tasks/<task_id>", methods=["PATCH"])
@login_required
def update_task(task_id):
    data = request.get_json()

    allowed_fields = ["agenda", "due_date", "owner", "status"]
    updates = {k: v for k, v in data.items() if k in allowed_fields}

    tasks_col.update_one({"_id": ObjectId(task_id)}, {"$set": updates})

    return jsonify({"updated": True}), 200
