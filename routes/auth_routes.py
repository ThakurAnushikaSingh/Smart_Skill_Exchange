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
        return render_template("auth.html", auth_error=result["error"], active_form="register"), 400

    return render_template("auth.html", auth_success="Registration successful. Please login.")


@auth_bp.route("/login", methods=["POST"])
def login():
    email = request.form.get("email", "")
    password = request.form.get("password", "")

    result = login_user(email, password)

    if "error" in result:
        return render_template("auth.html", auth_error=result["error"], active_form="login"), 400

    session["user"] = result["user"]
    session.permanent = True
    return redirect("/home")


@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect("/")
