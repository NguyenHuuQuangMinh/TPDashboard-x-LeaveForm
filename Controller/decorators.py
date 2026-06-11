from functools import wraps
from flask import session, redirect, url_for, abort, request
from Model.admin.roles import Roles

PARENT_PERMISSION = {
    "permission.user_edit": "permission.user_mng_page",
    "permission.update_user": "permission.user_mng_page",
    "permission.delete_user": "permission.user_mng_page",
    "permission.create_user": "permission.user_mng_page",
    "permission.user_create_form": "permission.user_mng_page",
}

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))

        if session.get('role') != 1:
            abort(403)  # Forbidden
        return f(*args, **kwargs)
    return decorated_function

def admin_or_manager_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))

        if session.get('role') not in (1, 3):
            abort(403)

        return f(*args, **kwargs)
    return decorated_function



def role_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):

        # Chưa login
        if "user_id" not in session:
            return redirect(url_for("auth.login"))

        role_id = session.get("role")
        endpoint = PARENT_PERMISSION.get(
            request.endpoint,
            request.endpoint
        )
        # Kiểm tra bảng role_permissions
        has_permission = Roles.check_permission(
            role_id,
            endpoint
        )

        if not has_permission:
            abort(403)

        return f(*args, **kwargs)

    return decorated_function