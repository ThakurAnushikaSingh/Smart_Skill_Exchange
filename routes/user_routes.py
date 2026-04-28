from flask import Blueprint, render_template, session, redirect
from services.skill_service import fetch_my_skills

user_bp = Blueprint("user", __name__)


@user_bp.route("/home")
def home():
    if "user" not in session:
        return redirect("/auth")

    return render_template("home.html", user=session["user"])


@user_bp.route("/profile")
def profile():
    if "user" not in session:
        return redirect("/auth")

    user = session["user"]
    my_skills = fetch_my_skills(user)
    return render_template("profile.html", user=user, my_skills=my_skills)
