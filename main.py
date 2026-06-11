from Controller.Auth_Controller import auth_bp
from Controller.admin.Admin_Controller import admin_bp
from Controller.admin.routes_controller import routes_bp
from Controller.admin.Role_manager import role_bp
from Controller.admin.departments_controller import dpm_bp
from Controller.admin.user_manager import user_mng_bp
from Controller.admin.permission import pms_mng_bp
from Controller.User_Controller import user_bp
from Controller.Partials_Controller import partial_bp
from Controller.manager.Leave_Controller import leave_mng_bp
from Controller.Leaveform.leave_form_Controller import leave_bp
from app_factory import base_app
from waitress import serve

app = base_app()

app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(routes_bp)
app.register_blueprint(role_bp)
app.register_blueprint(dpm_bp)
app.register_blueprint(user_mng_bp)
app.register_blueprint(leave_mng_bp)
app.register_blueprint(user_bp)
app.register_blueprint(partial_bp)
app.register_blueprint(pms_mng_bp)
app.register_blueprint(leave_bp)

# serve(app, host="0.0.0.0", port=8888)
# if __name__ == "__main__":
#     app.run(
#         host="0.0.0.0",
#         port=8888,
#         debug=True
#     )
