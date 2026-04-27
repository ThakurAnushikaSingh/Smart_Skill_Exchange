from flask import Flask
from flask import session, redirect, url_for, flash
from config.supabase import supabase
from routes.auth_routes import auth_bp
from routes.user_routes import user_bp
from routes.skill_routes import skill_bp

def create_app():
    app = Flask(__name__)
    app.secret_key = supabase.secret_key  # Loaded from .env

    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(skill_bp)

    @app.errorhandler(404)
    def not_found(e):
        return "404 Not Found", 404

    @app.errorhandler(500)
    def server_error(e):
        return "500 Internal Server Error", 500

    return app
