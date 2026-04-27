from flask import Blueprint, render_template, request, redirect, session
from services.auth_service import register_user, login_user

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/")
def landing():
    return render_template("landing.html")

@auth_bp.route("/auth")
def auth_page():
    return render_template("auth.html")

@auth_bp.route("/register", methods=["POST"])
def register():
    data = dict(request.form)
    result = register_user(data)

    if "error" in result:
        return result["error"]

    return redirect("/auth")

@auth_bp.route("/login", methods=["POST"])
def login():
    email = request.form["email"]
    password = request.form["password"]

    result = login_user(email, password)

    if "error" in result:
        return result["error"]

    session["user"] = result["user"]
    return redirect("/home")

@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect("/")