from flask import Flask, render_template, jsonify, request
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime
import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

app = Flask(__name__)

# Connects to local MongoDB. Database: "w1_project", Collection: "tasks".
client = MongoClient(os.getenv("MONGODB_URI"))
db = client["mini_project"]
tasks_col = db["tasks"]



@app.route("/dashboard")
def dashboard():
    projects = list(db.project_info.find())
    return render_template("dashboard.html", projects=projects)



@app.route("/api/tasks/<project_id>", methods=["GET"])
def get_tasks(project_id):
    tasks = list(tasks_col.find({"project_id": ObjectId(project_id)}))
    return jsonify([serialize_task(t) for t in tasks])




@app.route("/api/tasks", methods=["POST"])
def add_task():
    data = request.get_json()

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






@app.route("/api/tasks", methods=["DELETE"])
def delete_tasks():
    data = request.get_json()
    ids = [ObjectId(i) for i in data["task_ids"]]
    tasks_col.delete_many({"_id": {"$in": ids}})
    return jsonify({"deleted": len(ids)}), 200





@app.route("/api/tasks/<task_id>", methods=["PATCH"])
def update_task(task_id):
    data = request.get_json()

    # only update fields that were actually sent
    allowed_fields = ["agenda", "due_date", "owner", "status"]
    updates = {k: v for k, v in data.items() if k in allowed_fields}

    tasks_col.update_one(
        {"_id": ObjectId(task_id)},
        {"$set": updates}
    )

    return jsonify({"updated": True}), 200




if __name__ == '__main__':
   app.run('0.0.0.0', port=5000, debug=True)
