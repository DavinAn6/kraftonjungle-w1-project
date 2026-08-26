from flask import Blueprint, render_template, jsonify, request, make_response
from bson import ObjectId

from datetime import datetime
from db import get_db

from auth import login_required

task = Blueprint("task", __name__)

db = get_db()
tasks_col = db["tasks"]


@task.route("/dashboard")
@login_required
def dashboard():
    name = request.cookies.get("name")
    projects = list(db.project_info.find({"members": name}))
    return render_template("dashboard.html", projects=projects, name=name)


@task.route("/api/tasks/<project_id>", methods=["GET"])
@login_required
def get_tasks(project_id):
    tasks = list(tasks_col.find({"project_id": ObjectId(project_id)}))
    return jsonify([serialize_task(t) for t in tasks])









@task.route("/api/tasks", methods=["POST"])
@login_required
def add_task():
    data = request.get_json()


    # Validation Check —————————————————————————————————————————————
    # 1) Is the request actually contain JSON data? Or did someone send empty or broken request?
    if not data: 
        return jsonify({"error": "Invalid request"}), 400

    # 2) Are all the fields filled out by the user?
    required = ["project_id", "agenda", "due_date", "owner"]
    missing = [f for f in required if not data.get(f)]
    if missing:
        return jsonify({"error": f"Missing fields: {', '.join(missing)}"}), 400
    
    # 3) Is project_id properly formatted? 
    # If project_id can't be converted to ObjectId, it's not valid format
    try:
        project_oid = ObjectId(data["project_id"])
    except Exception:
        return jsonify({"error": "Invalid project id"}), 400
    
    # 4) Does project exist? Might not exist even if project_id does
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

    # only update fields that were actually sent
    allowed_fields = ["agenda", "due_date", "owner", "status"]
    updates = {k: v for k, v in data.items() if k in allowed_fields}

    tasks_col.update_one({"_id": ObjectId(task_id)}, {"$set": updates})

    return jsonify({"updated": True}), 200


if __name__ == "__main__":
    task.run("0.0.0.0", port=5000, debug=True)
