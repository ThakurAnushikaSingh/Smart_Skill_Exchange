from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from supabase import create_client, Client
from dotenv import load_dotenv
import os
load_dotenv()

app = Flask(__name__)
app.secret_key = "your_secret_key"

# Initialize Supabase client
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        data = request.form if request.form else request.json
        name = data["name"]
        email = data["email"]
        password = data["password"]
        gender = data.get("gender", "")
        bio = data.get("bio", "")
        password_hash = generate_password_hash(password)
        res = supabase.table("users").insert({
            "name": name,
            "email": email,
            "password_hash": password_hash,
            "gender": gender,
            "bio": bio
        }).execute()
        if res.data:
            user_id = res.data[0]["id"]
            session["user_id"] = user_id
            session["name"] = name
            return redirect(url_for("add_skill_page"))
        else:
            return "Registration failed", 400
    return render_template("register.html")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        data = request.form if request.form else request.json
        email = data["email"]
        password = data["password"]
        res = supabase.table("users").select("*").eq("email", email).execute()
        if res.data:
            user = res.data[0]
            if check_password_hash(user["password_hash"], password):
                session["user_id"] = user["id"]
                session["name"] = user["name"]
                return redirect(url_for('home'))
            else:
                return "Invalid credentials ❌"
        else:
            return "Invalid credentials ❌"
    return render_template("login.html")

@app.route('/profile')
def profile():
    if 'user_id' not in session:
        return redirect(url_for('home'))
    user_id = session['user_id']
    res = supabase.table("users") \
        .select("*") \
        .eq("id", user_id) \
        .execute()
    user = res.data[0]
    return render_template("profile.html", user=user)

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

@app.route('/transactions')
def transactions():
    if 'user_id' not in session:
        return redirect(url_for('home'))
    user_id = session['user_id']
    res = supabase.table("transactions") \
        .select("*") \
        .or_(f"from_user.eq.{user_id},to_user.eq.{user_id}") \
        .execute()
    return render_template("transactions.html", data=res.data)

@app.route('/add_skill')
@app.route('/add-skill')
def add_skill_page():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('add_skill.html')

@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/skills')
def skills_list():
    # Example: fetch all skills from supabase
    skills = supabase.table("skills").select("*").execute().data
    return render_template('skill_list.html', skills=skills)

@app.route('/skill-requests', methods=['GET', 'POST'])
def skill_requests():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        # Handle skill request form submission here
        pass
    # Example: fetch all skills from supabase
    skills = supabase.table("skills").select("*").execute().data
    return render_template('skill_requests.html', skills=skills)

@app.route('/sessions', methods=['GET', 'POST'])
def sessions_page():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    # Example: fetch all sessions from supabase
    sessions = supabase.table("sessions").select("*").execute().data
    skills = supabase.table("skills").select("*").execute().data
    return render_template('sessions.html', sessions=sessions, skills=skills)

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('home'))
    return redirect(url_for('login'))

# Add other routes and logic as needed

if __name__ == "__main__":
    app.run(debug=True)