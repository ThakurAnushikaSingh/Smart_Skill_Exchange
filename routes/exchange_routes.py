from flask import Blueprint, redirect, render_template, request, session, jsonify

from services.exchange_service import (
    add_skill_to_user,
    complete_learning_session,
    create_learning_session,
    get_certifications,
    get_dashboard_context,
    get_transactions,
    join_learning_session,
    request_skill,
    get_skill_requests,
)

exchange_bp = Blueprint("exchange", __name__)


def require_auth():
    if "user" not in session:
        return None, redirect("/auth")
    return session["user"], None


@exchange_bp.route("/my-dashboard")
def my_dashboard():
    user, resp = require_auth()
    if resp:
        return resp
    context = get_dashboard_context(user)
    context["skill_requests"] = get_skill_requests(user)
    return render_template("dashboard.html", user=user, **context)


@exchange_bp.route("/user-skills/add", methods=["POST"])
def add_user_skill():
    user, resp = require_auth()
    if resp:
        return resp
    result = add_skill_to_user(user, dict(request.form) or (request.get_json(silent=True) or {}))
    if result.get("error"):
        return jsonify(result), 400
    return jsonify(result), 201


@exchange_bp.route("/skill-requests", methods=["GET", "POST"])
def skill_requests_route():
    user, resp = require_auth()
    if resp:
        return resp

    if request.method == "POST":
        payload = dict(request.form) or (request.get_json(silent=True) or {})
        result = request_skill(user, payload.get("skill_id"))
        if result.get("error"):
            return jsonify(result), 400

    context = get_dashboard_context(user)
    requests = get_skill_requests(user)
    return render_template(
        "skill_requests.html",
        user=user,
        skills=context["skills_catalog"],
        skill_requests=requests,
    )


@exchange_bp.route("/sessions", methods=["GET"])
def sessions_page():
    user, resp = require_auth()
    if resp:
        return resp
    context = get_dashboard_context(user)
    return render_template("sessions.html", user=user, sessions=context["sessions"], skills=context["skills_catalog"])


@exchange_bp.route("/sessions", methods=["POST"])
def create_session_route():
    user, resp = require_auth()
    if resp:
        return resp
    payload = dict(request.form) or (request.get_json(silent=True) or {})
    result = create_learning_session(user, payload)
    if result.get("error"):
        return jsonify(result), 400
    return redirect("/sessions")


@exchange_bp.route("/sessions/<session_id>/join", methods=["POST"])
def join_session_route(session_id):
    user, resp = require_auth()
    if resp:
        return resp
    result = join_learning_session(user, session_id)
    if result.get("error"):
        return jsonify(result), 400
    return redirect("/sessions")


@exchange_bp.route("/sessions/complete", methods=["POST"])
def complete_session_form_route():
    user, resp = require_auth()
    if resp:
        return resp
    session_id = request.form.get("session_id", "")
    result = complete_learning_session(user, session_id)
    if result.get("error"):
        return result["error"], 400

    # refresh user state quickly for credits on UI
    session["user"] = {**session["user"], "credits": session["user"].get("credits", 0)}
    return redirect("/transactions")


@exchange_bp.route("/sessions/<session_id>/complete", methods=["POST"])
def complete_session_route(session_id):
    user, resp = require_auth()
    if resp:
        return resp
    result = complete_learning_session(user, session_id)
    if result.get("error"):
        return jsonify(result), 400
    return jsonify(result), 200


@exchange_bp.route("/sessions/<session_id>/live")
def live_session_page(session_id):
    user, resp = require_auth()
    if resp:
        return resp
    return render_template("live_session.html", user=user, session_id=session_id)


@exchange_bp.route("/transactions")
def transactions_page():
    user, resp = require_auth()
    if resp:
        return resp
    return render_template("transactions.html", user=user, transactions=get_transactions(user))


@exchange_bp.route("/certifications")
def certifications_page():
    user, resp = require_auth()
    if resp:
        return resp
    return render_template("certifications.html", user=user, certifications=get_certifications(user))
