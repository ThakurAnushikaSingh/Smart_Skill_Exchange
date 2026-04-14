from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from supabase import create_client, Client

# 🔐 Supabase Config
url = "https://qftsuqmhwnfqzudmhfee.supabase.co"
key = "sb_publishable_X0N493XXYH7z0b9mYKGrkw_6CD0PeJm"

supabase: Client = create_client(url, key)

app = Flask(__name__)
app.secret_key = "supersecretkey"


# -------------------- HELPERS --------------------

def _user_map():
    users = supabase.table("users").select("*").execute().data or []
    return {u["user_id"]: u for u in users}


def _skill_map():
    skills = supabase.table("skills").select("*").execute().data or []
    return {s["skill_id"]: s for s in skills}


# -------------------- PAGES --------------------

@app.route("/")
def home():
    return render_template("index.html")


@app.route('/add-skill')
def add_skill_page():
    return render_template("add_skill.html")


@app.route('/request-skill')
def request_skill_page():
    if 'user_id' not in session:
        return redirect(url_for('home'))

    sessions_data = supabase.table("sessions").select("*").execute().data or []
    available_sessions = [s for s in sessions_data if not s.get("learner_id")]

    return render_template(
        "request_skill.html",
        sessions_data=available_sessions,
        current_user_id=session['user_id']
    )


@app.route('/complete-session-page')
def complete_session_page():
    return render_template("complete_session.html")


@app.route('/certificates')
def certificates():
    if 'user_id' not in session:
        return redirect(url_for('home'))

    user_id = session['user_id']

    res = supabase.table("certifications") \
        .select("*") \
        .eq("user_id", user_id) \
        .execute()

    certs = res.data or []

    return render_template("certificates.html", certs=certs)


# -------------------- USERS --------------------

@app.route("/users", methods=["POST"])
def add_user():
    data = request.form if request.form else request.json

    res = supabase.table("users").insert({
        "name": data["name"],
        "email": data["email"]
    }).execute()

    return jsonify(res.data)


@app.route("/users", methods=["GET"])
def get_users():
    res = supabase.table("users").select("*").execute()
    return jsonify(res.data)


# -------------------- SKILLS --------------------

@app.route('/skills', methods=['POST'])
def add_skill():
    data = request.form if request.form else request.json

    res = supabase.table("skills").insert({
        "skill_name": data["skill_name"]
    }).execute()

    return jsonify(res.data)


@app.route("/skills", methods=["GET"])
def get_skills():
    res = supabase.table("skills").select("*").execute()
    return jsonify(res.data)


# -------------------- USER SKILLS --------------------

@app.route("/user-skills", methods=["POST"])
def map_user_skill():
    data = request.form if request.form else request.json

    res = supabase.table("user_skills").insert({
        "user_id": int(data["user_id"]),
        "skill_id": int(data["skill_id"]),
        "proficiency_level": data.get("proficiency_level", "Beginner")
    }).execute()

    return jsonify(res.data)


# -------------------- BOOKING / REQUEST FLOW --------------------

@app.route('/request_skill', methods=['POST'])
def request_skill():
    if 'user_id' not in session:
        return redirect(url_for('home'))

    data = request.form if request.form else request.json
    learner_id = int(session['user_id'])
    session_id = int(data['session_id'])

    try:
        supabase.rpc("create_booking_request", {
            "p_session_id": session_id,
            "p_learner_id": learner_id
        }).execute()
    except Exception as exc:
        return f"Unable to create booking request: {exc}"

    return redirect(url_for('view_sessions'))


@app.route('/manage-requests')
def manage_requests():
    if 'user_id' not in session:
        return redirect(url_for('home'))

    teacher_id = session['user_id']
    sessions_data = supabase.table("sessions").select("*").eq("teacher_id", teacher_id).execute().data or []
    bookings = supabase.table("bookings").select("*").eq("status", "Pending").execute().data or []
    users = _user_map()
    skills = _skill_map()

    session_by_id = {s['session_id']: s for s in sessions_data}

    incoming = []
    for b in bookings:
        current_session = session_by_id.get(b.get("session_id"))
        if not current_session:
            continue
        incoming.append({
            "booking_id": b.get("booking_id"),
            "session_id": current_session.get("session_id"),
            "learner_id": b.get("learner_id"),
            "learner_name": users.get(b.get("learner_id"), {}).get("name", "Unknown Learner"),
            "skill_name": skills.get(current_session.get("skill_id"), {}).get("skill_name", current_session.get("skill_name", "Skill")),
            "session_date": current_session.get("session_date"),
            "session_time": current_session.get("session_time")
        })

    return render_template("manage_requests.html", incoming=incoming)


@app.route('/bookings/<int:booking_id>/accept', methods=['POST'])
def accept_request(booking_id):
    if 'user_id' not in session:
        return redirect(url_for('home'))

    meeting_url = request.form.get('meeting_url', '').strip()

    try:
        supabase.rpc("accept_booking_request", {
            "p_booking_id": booking_id,
            "p_teacher_id": int(session['user_id']),
            "p_meeting_url": meeting_url
        }).execute()
    except Exception as exc:
        return f"Unable to accept request: {exc}"

    return redirect(url_for('view_sessions'))


@app.route('/bookings/<int:booking_id>/reject', methods=['POST'])
def reject_request(booking_id):
    if 'user_id' not in session:
        return redirect(url_for('home'))

    try:
        supabase.rpc("reject_booking_request", {
            "p_booking_id": booking_id,
            "p_teacher_id": int(session['user_id'])
        }).execute()
    except Exception as exc:
        return f"Unable to reject request: {exc}"

    return redirect(url_for('manage_requests'))


# -------------------- SESSIONS VIEW --------------------

@app.route('/sessions')
def view_sessions():
    sessions = supabase.table("sessions").select("*").execute().data or []
    users = _user_map()
    skills = _skill_map()
    bookings = supabase.table("bookings").select("*").execute().data or []

    accepted_booking_by_session = {
        b.get("session_id"): b
        for b in bookings
        if b.get("status") == "Accepted"
    }

    enriched = []
    for s in sessions:
        accepted = accepted_booking_by_session.get(s.get("session_id"))
        learner_id = s.get("learner_id") or (accepted or {}).get("learner_id")
        teacher = users.get(s.get("teacher_id"), {})
        learner = users.get(learner_id, {}) if learner_id else {}
        skill = skills.get(s.get("skill_id"), {})
        enriched.append({
            **s,
            "teacher_name": s.get("teacher_name") or teacher.get("name", "Unknown Teacher"),
            "learner_name": s.get("learner_name") or learner.get("name"),
            "skill_name": s.get("skill_name") or skill.get("skill_name", "Skill"),
            "booking_status": s.get("booking_status") or (accepted or {}).get("status"),
            "meeting_url": s.get("meeting_url"),
        })

    return render_template(
        "sessions.html",
        sessions=enriched,
        current_user_id=session.get('user_id')
    )


@app.route('/learn/<int:session_id>')
def learn(session_id):
    if 'user_id' not in session:
        return redirect(url_for('home'))

    current_session = supabase.table("sessions").select("*").eq("session_id", session_id).execute().data
    if not current_session:
        return "Session not found."

    s = current_session[0]

    if not s.get("meeting_url"):
        return "Meeting link will be available once the teacher accepts the request."

    return render_template("learn.html", session_data=s, current_user_id=session['user_id'])


# -------------------- LOGIN --------------------

@app.route('/login', methods=['POST'])
def login():
    user_id = int(request.form['user_id'])
    email = request.form['email']

    res = supabase.table("users") \
        .select("*") \
        .eq("user_id", user_id) \
        .eq("email", email) \
        .execute()

    if res.data:
        user = res.data[0]
        session['user_id'] = user['user_id']
        session['name'] = user['name']
        return redirect(url_for('home'))
    return "Invalid credentials ❌"


# -------------------- LOGOUT --------------------

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))


# -------------------- PROFILE --------------------

@app.route('/profile')
def profile():
    if 'user_id' not in session:
        return redirect(url_for('home'))

    user_id = session['user_id']

    res = supabase.table("users") \
        .select("*") \
        .eq("user_id", user_id) \
        .execute()

    user = res.data[0]
    return render_template("profile.html", user=user)


# -------------------- TRANSACTIONS --------------------

@app.route('/transactions')
def transactions():
    if 'user_id' not in session:
        return redirect(url_for('home'))

    user_id = session['user_id']

    res = supabase.table("transactions") \
        .select("*") \
        .or_(f"learner_id.eq.{user_id},trainer_id.eq.{user_id}") \
        .execute()

    return render_template("transactions.html", data=res.data)


# -------------------- COMPLETE SESSION --------------------

@app.route('/complete_session', methods=['POST'])
def complete_session():
    if 'user_id' not in session:
        return redirect(url_for('home'))

    data = request.form if request.form else request.json

    session_id = int(data['session_id'])
    learner_id = int(data['learner_id'])
    trainer_id = int(data['trainer_id'])
    skill_id = int(data['skill_id'])
    credits = int(data['credits'])

    try:
        supabase.rpc("complete_session_atomic", {
            "p_session_id": session_id,
            "p_learner_id": learner_id,
            "p_trainer_id": trainer_id,
            "p_skill_id": skill_id,
            "p_credits": credits
        }).execute()
    except Exception as exc:
        return f"Unable to complete session: {exc}"

    return redirect(url_for('home'))


# -------------------- CACHE FIX --------------------

@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-store'
    return response


# -------------------- RUN --------------------

if __name__ == "__main__":
    app.run(debug=True)
