from flask import Blueprint,session,redirect,url_for,request, render_template,flash
from Model.Auth import AuthModel
from Model.Utils.password_helper import verify_password
auth_bp = Blueprint('auth', __name__)
@auth_bp.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    role = session.get('role')

    if role == 1:
        return redirect(url_for('admin.dashboard'))
    else:
        return redirect(url_for('user.home'))

@auth_bp.route('/login',methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        role = session.get('role')
        return redirect(
            url_for('admin.dashboard') if role == 1
            else url_for('user.home')
        )
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        remember = request.form.get('remember')
        user = AuthModel.authenticate(username)
        if not username or not password:
            flash(
                "❌ Please enter both username and password.",
                "error"
            )
            return redirect(url_for('auth.login'))

        if user and int(user.status) == 0:
            flash(
                "🚫 Your account has been locked.",
                "error"
            )
            return redirect(url_for('auth.login'))

        if user and int(user.role_status) == 0:
            flash(
                "🚫 Your permissions have been disabled.",
                "error"
            )
            return redirect(url_for('auth.login'))

        if not user or not verify_password(password, user.password_hash):
            flash(
                "❌ Invalid username or password.",
                "error"
            )
            return redirect(url_for('auth.login'))
        else:
            session.clear()
            session['user_id'] = user.id
            session['username'] = user.username
            session['role'] = user.role_id
            session['job'] = user.job_title
            session['department'] = user.department_id
            if(user.role_id == 1):
                session['is_admin'] = 1
            if remember:
                session.permanent = True
            else:
                session.permanent = False
            # UserModel.update_online(user.id, True)
            flash(
                f'🎉 Welcome back, {user.username}! You have logged in successfully.',
                'success'
            )
            if user.role_id == 1:
                return redirect(url_for('admin.dashboard'))
            else:
                return redirect(url_for('user.home'))
    return render_template('login/login.html', error=error)

@auth_bp.route('/logout')
def logout():
    user_id = session.get('user_id')
    if user_id:
        session.clear()
    return redirect(url_for('auth.login'))