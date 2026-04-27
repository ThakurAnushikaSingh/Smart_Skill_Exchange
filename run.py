from flask import Flask
from routes.auth_routes import auth_bp
from routes.user_routes import user_bp
from routes.skill_routes import skill_bp
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# 🔐 IMPORTANT FIX
app.secret_key = os.getenv("SECRET_KEY") or "fallback_secret"

app.register_blueprint(auth_bp)
app.register_blueprint(user_bp)
app.register_blueprint(skill_bp)

if __name__ == "__main__":
    app.run(debug=True)