from flask import Blueprint,session,redirect,url_for,request, render_template,flash
from Controller.decorators import admin_required

admin_bp = Blueprint('admin', __name__)

@admin_bp.before_request
@admin_required
def before_all():
    pass
@admin_bp.route('/admin')
def dashboard():
    if session.get('is_admin') == 0:
        session['is_admin'] = 1
    return render_template("admin/dashboard.html")
