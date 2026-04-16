from flask import Flask
import os
from flask_wtf import CSRFProtect
from flask_wtf.csrf import generate_csrf
csrf = CSRFProtect()
def base_app():
    app = Flask(__name__)
    app.secret_key = os.getenv('FLASK_SECRET_KEY')
    csrf.init_app(app)
    @app.context_processor
    def inject_csrf():
        return dict(csrf_token=generate_csrf)

    return app