from flask import Blueprint, render_template, session, redirect

user_bp = Blueprint("user", __name__)

@user_bp.route("/home")
def home():
    if "user" not in session:
        return redirect("/login")

    return render_template("home.html", user=session["user"])


@user_bp.route("/profile")
def profile():
    if "user" not in session:
        return redirect("/login")

    return render_template("profile.html", user=session["user"])