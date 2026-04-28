from flask import Blueprint, redirect, render_template, request, session, jsonify, flash
from models.user_model import get_user_by_id
from services.exchange_service import (
    add_skill_to_user,
    complete_learning_session,
    create_learning_session,
    get_certifications,
    get_dashboard_context,
    get_transactions,
    join_learning_session,
    request_skill_with_time,
    get_requests_for_user_skills,
    get_skill_requests_for_user,
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
    return render_template("profile.html", user=user, my_skills=context["my_skills"])


@exchange_bp.route("/share-skill")
def share_skill_page():
    user, resp = require_auth()
    if resp:
        return resp
    requests = get_requests_for_user_skills(user)
    return render_template("share_skill.html", user=user, requests=requests)


@exchange_bp.route("/growth-hub")
def growth_hub():
    user, resp = require_auth()
    if resp:
        return resp
    
    # Refresh user data from DB to ensure credits are up to date
    refreshed = get_user_by_id(user.get("id"))
    if refreshed:
        session["user"] = refreshed
        user = refreshed

    context = get_dashboard_context(user)
    return render_template("growth_hub.html", user=user, sessions=context["sessions"])



@exchange_bp.route("/skill-requests", methods=["POST"])
def create_skill_request_route():
    user, resp = require_auth()
    if resp:
        return resp
    
    skill_id = request.form.get("skill_id")
    suggested_time = request.form.get("suggested_time")
    
    result = request_skill_with_time(user, skill_id, suggested_time)
    if result.get("error"):
        flash(result["error"], "error")
        return redirect("/skills")
        
    flash("Skill request sent! Mentors will see your suggested time.", "success")
    return redirect("/skills")


@exchange_bp.route("/sessions", methods=["POST"])
def create_session_route():
    user, resp = require_auth()
    if resp:
        return resp
    payload = dict(request.form)
    result = create_learning_session(user, payload)
    
    if result.get("error"):
        flash(result["error"], "error")
        return redirect("/share-skill") if payload.get("request_id") else redirect("/sessions")

    flash("Session scheduled successfully.", "success")
    return redirect("/growth-hub")


@exchange_bp.route("/sessions/<session_id>/join", methods=["POST"])
def join_session_route(session_id):
    user, resp = require_auth()
    if resp:
        return resp
    result = join_learning_session(user, session_id)
    if result.get("error"):
        flash(result["error"], "error")
        return redirect("/growth-hub")
    
    flash("You have joined the session.", "success")
    return redirect("/growth-hub")


@exchange_bp.route("/sessions/<session_id>/complete", methods=["POST"])
def complete_session_route(session_id):
    user, resp = require_auth()
    if resp:
        return resp
    result = complete_learning_session(user, session_id)
    if result.get("error"):
        flash(result["error"], "error")
        return redirect("/growth-hub")
    
    # Refresh credits in session
    refreshed = get_user_by_id(user.get("id"))
    if refreshed:
        session["user"] = refreshed
        
    flash("Session marked as completed.", "success")
    return redirect("/growth-hub")


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
