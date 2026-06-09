from flask import Flask,session
import os
from flask_wtf import CSRFProtect
from flask_wtf.csrf import generate_csrf
from Model.admin.routes import Routes
csrf = CSRFProtect()
def base_app():
    app = Flask(__name__)
    app.secret_key = os.getenv('FLASK_SECRET_KEY')
    csrf.init_app(app)
    @app.context_processor
    def inject_global_data():
        role_id = session.get("role")
        return {
            "csrf_token": generate_csrf,
            "sidebar_routes": Routes.get_sidebar_routes(role_id)
        }

    @app.context_processor
    def inject_helpers():
        return {
            "get_route_name": lambda endpoint, routes: next(
                (r["name"] for r in routes if r["path"] == endpoint),
                None
            )
        }

    app.config.update(
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SECURE=False,
        SESSION_COOKIE_SAMESITE='Lax'
    )
    return app