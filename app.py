from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from supabase import create_client, Client

# 🔐 Supabase Config
url = "https://qftsuqmhwnfqzudmhfee.supabase.co"
key = "sb_publishable_X0N493XXYH7z0b9mYKGrkw_6CD0PeJm" 

supabase: Client = create_client(url, key)

app = Flask(__name__)
app.secret_key = "supersecretkey"

# -------------------- PAGES --------------------

@app.route("/")
def home():
    return render_template("index.html")

@app.route('/add-skill')
def add_skill_page():
    return render_template("add_skill.html")

@app.route('/request-skill')
def request_skill_page():
    return render_template("request_skill.html")

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

    certs = res.data

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

# -------------------- SESSIONS VIEW --------------------

@app.route('/sessions')
def view_sessions():
    sessions = supabase.table("sessions").select("*").execute().data
    users = supabase.table("users").select("*").execute().data
    skills = supabase.table("skills").select("*").execute().data
    bookings = supabase.table("bookings").select("*").execute().data

    return render_template("sessions.html",
                           sessions=sessions,
                           users=users,
                           skills=skills,
                           bookings=bookings)

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
    else:
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

    # 1️⃣ Check trainer certification
    cert = supabase.table("certifications") \
        .select("*") \
        .eq("user_id", trainer_id) \
        .eq("skill_id", skill_id) \
        .eq("role", "TRAINER") \
        .execute()

    if not cert.data:
        return "Trainer is not certified ❌"

    # 2️⃣ Update booking status
    supabase.table("bookings") \
        .update({"status": "Completed"}) \
        .eq("session_id", session_id) \
        .execute()

    # 3️⃣ Insert transaction
    supabase.table("transactions").insert({
        "session_id": session_id,
        "learner_id": learner_id,
        "trainer_id": trainer_id,
        "credits_transferred": credits
    }).execute()

    # 4️⃣ Update credits manually
    # learner - credits
    learner = supabase.table("users").select("credits").eq("user_id", learner_id).execute().data[0]
    trainer = supabase.table("users").select("credits").eq("user_id", trainer_id).execute().data[0]

    supabase.table("users").update({
        "credits": learner["credits"] - credits
    }).eq("user_id", learner_id).execute()

    supabase.table("users").update({
        "credits": trainer["credits"] + credits
    }).eq("user_id", trainer_id).execute()

    # 5️⃣ Add certification if not exists
    existing = supabase.table("certifications") \
        .select("*") \
        .eq("user_id", learner_id) \
        .eq("skill_id", skill_id) \
        .execute()

    if not existing.data:
        supabase.table("certifications").insert({
            "user_id": learner_id,
            "skill_id": skill_id,
            "role": "LEARNER"
        }).execute()

    return redirect(url_for('home'))

# -------------------- CACHE FIX --------------------

@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-store'
    return response

# -------------------- RUN --------------------

if __name__ == "__main__":
    app.run(debug=True)