from flask import Blueprint, abort, g, render_template, redirect, request
from bson.objectid import ObjectId
from auth import login_required
from db import get_db
import json

db = get_db()
projects = db["projects"]
tasks = db["tasks"]

detail = Blueprint("detail", __name__)


def get_project_for_user(project_id):
    if not ObjectId.is_valid(project_id):
        abort(404)
    project = projects.find_one(
        {"_id": ObjectId(project_id), "members.email": g.user["email"]}
    )
    if not project:
        abort(404)
    return project


@detail.route("/projects/<project_id>")
@login_required
def project_detail(project_id):
    project = get_project_for_user(project_id)
    return render_template("project_detail.html", project=project)


@detail.route("/projects/<project_id>/delete", methods=["POST"])
@login_required
def delete_project(project_id):
    project = get_project_for_user(project_id)
    result = projects.delete_one({"_id": project["_id"]})
    if result.deleted_count:
        tasks.delete_many({"project_id": project["_id"]})
    return redirect("/")


@detail.route("/projects/<project_id>/edit", methods=["GET", "POST"])
@login_required
def edit_project(project_id):
    project = get_project_for_user(project_id)
    if request.method == "POST":
        members_json = request.form.get("members")
        try:
            members = json.loads(members_json) if members_json else []
        except json.JSONDecodeError:
            return "Invalid members", 400

        if not isinstance(members, list) or any(
            not isinstance(member, dict)
            or not isinstance(member.get("name"), str)
            or not isinstance(member.get("email"), str)
            for member in members
        ):
            return "Invalid members", 400

        current_member = {"name": g.user["name"], "email": g.user["email"]}
        if not any(member["email"] == current_member["email"] for member in members):
            members.append(current_member)

        updated_project = {
            "title": request.form.get("title"),
            "team": request.form.get("team"),
            "description": request.form.get("description"),
            "start_date": request.form.get("start_date"),
            "end_date": request.form.get("end_date"),
            "members": members,
        }
        projects.update_one({"_id": project["_id"]}, {"$set": updated_project})
        return redirect(f"/projects/{project_id}")
    return render_template(
        "create.html",
        project=project,
        form_action=f"/projects/{project_id}/edit",
    )
