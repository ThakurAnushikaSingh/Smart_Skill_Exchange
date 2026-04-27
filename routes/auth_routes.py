from flask import Blueprint, render_template, request, redirect, session
from services.auth_service import register_user, login_user

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/")
def landing():
    if "user" in session:
        return redirect("/home")
    return render_template("landing.html")


@auth_bp.route("/auth")
def auth_page():
    if "user" in session:
        return redirect("/home")
    return render_template("auth.html")


@auth_bp.route("/register", methods=["POST"])
def register():
    data = dict(request.form)
    result = register_user(data)

    if "error" in result:
        return result["error"], 400

    return render_template("auth.html", registration_user_id=result["user"]["id"])


@auth_bp.route("/login", methods=["POST"])
def login():
    user_id = request.form.get("user_id", "")
    email = request.form.get("email", "")

    result = login_user(user_id, email)

    if "error" in result:
        return result["error"], 400

    session["user"] = result["user"]
    session.permanent = True
    return redirect("/home")


@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect("/")
