from flask import Blueprint,session,redirect,url_for,request, render_template,flash
from Controller.decorators import login_required

user_bp = Blueprint('user', __name__)

@user_bp.before_request
@login_required
def before_all():
    pass

@user_bp.route('/home',methods=['GET', 'POST'])
def home():
    if session.get('is_admin') == 1:
        session['is_admin'] = 0

    return render_template("user/home.html")