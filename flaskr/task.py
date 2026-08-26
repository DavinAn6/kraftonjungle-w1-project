print("### RUNNING task.py ###")

from flask import Flask, render_template, jsonify, request
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime
app = Flask(__name__)

# Connects to local MongoDB. Database: "w1_project", Collection: "tasks".
client = MongoClient("mongodb://localhost:27017/")
db = client["w1_project"]
tasks_col = db["tasks"]



@app.route("/dashboard")
def dashboard():
    projects = list(db.project_info.find())
    return render_template("dashboard.html", projects=projects)



@app.route("/api/tasks/<project_id>", methods=["GET"])
def get_tasks(project_id):
    tasks = list(tasks_col.find({"project_id": project_id}))
    return jsonify([serialize_task(t) for t in tasks])

def serialize_task(task):
    task["_id"] = str(task["_id"])
    return task





@app.route("/api/tasks", methods=["POST"])
def add_task():
    data = request.get_json()

    task = {
        "project_id": data["project_id"],
        "agenda": data["agenda"],
        "due_date": data["due_date"],
        "owner": data["owner"],
        "status": data.get("status", "Not Started"),
        "created_at": datetime.utcnow()
    }

    result = tasks_col.insert_one(task)
    task["_id"] = result.inserted_id

    return jsonify(serialize_task(task)), 201



if __name__ == '__main__':
   app.run('0.0.0.0', port=5000, debug=True)
