from flask import Blueprint, render_template, redirect, request
from bson.objectid import ObjectId
from db import get_db
import json

db = get_db()
projects = db["projects"]

detail = Blueprint("detail",__name__)
@detail.route("/projects/<project_id>")
def project_detail(project_id):
    project = projects.find_one({"_id": ObjectId(project_id)})
    if not project:
        return "삭제된 프로젝트입니다."
    return render_template("project_detail.html", project=project)
    
@detail.route("/projects/<project_id>/delete", methods = ["post"])
def delete_project(project_id):
    projects.delete_one({"_id": ObjectId(project_id)})
    return redirect("/")

@detail.route("/projects/<project_id>/edit", methods=["GET", "POST"])
def edit_project(project_id):
    if request.method == "POST":
        members_json = request.form.get("members")
        members = json.loads(members_json) if members_json else []
        updated_project = {
            "title": request.form.get("title"),
            "team": request.form.get("team"),
            "description": request.form.get("description"),
            "start_date": request.form.get("start_date"),
            "end_date": request.form.get("end_date"),
            "members": members,
        }
        projects.update_one({"_id": ObjectId(project_id)}, {"$set": updated_project})
        return redirect(f"/projects/{project_id}")
    project = projects.find_one({"_id": ObjectId(project_id)})
    return render_template("create.html", project=project, form_action=f"/projects/{project_id}/edit")