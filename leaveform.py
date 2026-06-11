from Controller.Leaveform.leave_form_Controller import leave_bp
from app_factory import base_app
from waitress import serve

app = base_app()

app.register_blueprint(leave_bp)

# serve(app, host="0.0.0.0", port=8888)
# if __name__ == "__main__":
#     app.run(
#         host="0.0.0.0",
#         port=8000,
#         debug=True
#     )
