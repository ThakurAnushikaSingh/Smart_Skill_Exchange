from flask import Blueprint, render_template, request, redirect, session, flash, url_for
from services.auth_service import register_user, login_user

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/")
def landing():
    if "user" in session:
<<<<<<< HEAD
        return redirect(url_for("user.home"))
=======
        return redirect("/home")
>>>>>>> 26eef87ce471af82a0c8b5d4d6fbb30f3d918d72
    return render_template("landing.html")


@auth_bp.route("/auth")
def auth_page():
    if "user" in session:
<<<<<<< HEAD
        return redirect(url_for("user.home"))
    return render_template("auth.html")


=======
        return redirect("/home")
    return render_template("auth.html")




@auth_bp.route("/login", methods=["GET"])
def login_page_redirect():
    return redirect("/auth")


@auth_bp.route("/register", methods=["GET"])
def register_page_redirect():
    return redirect("/auth")

>>>>>>> 26eef87ce471af82a0c8b5d4d6fbb30f3d918d72
@auth_bp.route("/register", methods=["POST"])
def register():
    data = dict(request.form)
    result = register_user(data)

    if "error" in result:
        flash(result["error"], "error")
        return render_template("auth.html", active_form="register"), 400

    flash("Registration successful. Please login.", "success")
    return redirect(url_for("auth.auth_page"))


@auth_bp.route("/login", methods=["POST"])
def login():
    email = request.form.get("email", "")
    password = request.form.get("password", "")

    result = login_user(email, password)

    if "error" in result:
        flash(result["error"], "error")
        return render_template("auth.html", active_form="login"), 400

    session["user"] = result["user"]
    session.permanent = True
    flash(f"Welcome back, {result['user'].get('name', 'User')}!", "success")
    return redirect(url_for("user.home"))

@auth_bp.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "success")
<<<<<<< HEAD
    return redirect(url_for("auth.landing"))
=======
    return redirect("/")
>>>>>>> 26eef87ce471af82a0c8b5d4d6fbb30f3d918d72
