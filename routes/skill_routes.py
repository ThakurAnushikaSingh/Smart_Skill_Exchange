from flask import Blueprint, render_template, request, redirect, session, flash

from services.exchange_service import add_skill_to_user
from services.skill_service import fetch_skills

skill_bp = Blueprint("skill", __name__)


@skill_bp.route("/skills")
def skills():
    skills = fetch_skills()
    return render_template("skill_list.html", skills=skills)


@skill_bp.route("/add-skill", methods=["GET", "POST"])
def add_skill():
    if "user" not in session:
        return redirect("/auth")
<<<<<<< HEAD

=======
>>>>>>> 26eef87ce471af82a0c8b5d4d6fbb30f3d918d72

    if request.method == "POST":
        data = dict(request.form)
        result = add_skill_to_user(session["user"], data)
        if result.get("error"):
            flash(result["error"], "error")
            return redirect("/add-skill")

        skill_name = data.get("name") or data.get("skill_name") or "Your skill"
        flash(f"{skill_name} added successfully.", "success")
        return render_template("skill_success.html", skill_name=skill_name)

<<<<<<< HEAD
    return render_template("add_skill.html", skills=fetch_skills())


=======
    return render_template("add_skill.html")
>>>>>>> 26eef87ce471af82a0c8b5d4d6fbb30f3d918d72
