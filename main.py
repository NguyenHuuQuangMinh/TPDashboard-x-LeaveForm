from Controller.Auth_Controller import auth_bp
from Controller.Admin_Controller import admin_bp
from Controller.User_Controller import user_bp
from app_factory import base_app
from waitress import serve

app = base_app()

app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(user_bp)

# serve(app, host="0.0.0.0", port=8888)
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8888, debug=True)
