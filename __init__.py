import os

from flask import Flask

from routes.auth_routes import auth_bp
from routes.user_routes import user_bp
from routes.skill_routes import skill_bp
from routes.exchange_routes import exchange_bp


def create_app():
    app = Flask(__name__)

    secret_key = os.getenv("FLASK_SECRET_KEY") or os.getenv("SECRET_KEY")
    if not secret_key:
        raise RuntimeError(
            "Missing Flask secret key. Set FLASK_SECRET_KEY (or SECRET_KEY) in your environment/.env."
        )
    app.secret_key = secret_key

    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(skill_bp)
    app.register_blueprint(exchange_bp)

    @app.errorhandler(404)
    def not_found(e):
        return "404 Not Found", 404

    @app.errorhandler(500)
    def server_error(e):
        return "500 Internal Server Error", 500

    return app
