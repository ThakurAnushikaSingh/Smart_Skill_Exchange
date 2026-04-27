from flask import Blueprint, render_template, request, redirect, session
from services.skill_service import fetch_skills, create_skill

skill_bp = Blueprint("skill", __name__)


@skill_bp.route("/skills")
def skills():
    skills = fetch_skills()
    return render_template("skill_list.html", skills=skills)


@skill_bp.route("/add-skill", methods=["GET", "POST"])
def add_skill():
    if "user" not in session:
        return redirect("/auth")

    if request.method == "POST":
        data = dict(request.form)
        create_skill(data)
        skill_name = data.get("name") or data.get("skill_name") or "Your skill"
        return render_template("skill_success.html", skill_name=skill_name)

    return render_template("add_skill.html")
