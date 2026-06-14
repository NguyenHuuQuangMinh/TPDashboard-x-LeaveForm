from flask import Blueprint, session, redirect, url_for, request, render_template, flash, jsonify, abort
from Controller.decorators import admin_required
from Model.admin.user_mng import User_mng
from Model.Utils.password_helper import hash_password
from Service.security_code import generate_security

user_mng_bp = Blueprint('user_manager', __name__)

@user_mng_bp.before_request
@admin_required
def before_all():
    pass

@user_mng_bp.route('/admin/users')
def user_mng_page():
    name = request.args.get('name', '').strip()
    role = request.args.get('role', '').strip()
    dpm =  request.args.get('dpm', '').strip()
    status = request.args.get('status', '').strip()
    page = request.args.get('page', 1, type=int)
    per_page = 10
    users,total = User_mng.get_all_users(name,role,dpm,status,page,per_page)
    total_pages = (total + per_page - 1) // per_page
    all_dpm = User_mng.get_all_dpm()
    all_role = User_mng.get_all_role()
    return render_template(
        'admin/manager/user/users.html',
        users=users,
        page=page,
        name=name,
        role=role,
        dpm=dpm,
        all_dpm=all_dpm,
        all_role=all_role,
        status=status,
        total=total,
        total_pages=total_pages
    )

@user_mng_bp.route('/partial/users/<string:user_id>')
def user_edit(user_id):

    user = User_mng.get_by_id(user_id)
    roles = User_mng.get_all_role()
    dpms = User_mng.get_all_dpm()
    return render_template(
        'admin/manager/user/user_edit.html',
        user=user,
        roles=roles,
        dpms=dpms
    )

@user_mng_bp.route('/partial/users/<string:user_id>/update', methods=['POST'])
def update_user(user_id):

    user = User_mng.get_by_id(user_id)

    if not user:
        flash("⚠️ User does not exist.", "warning")
        return redirect(url_for('user_manager.user_mng_page'))

    fields = [
        "FullName",
        "working_location",
        "RoleId",
        "DepartmentId",
        "Job_title",
        "report_to",
        "to_email",
        "cc_email",
        "Status",
        "Security"
    ]

    data = {}

    # Chỉ lấy những field thực sự thay đổi
    for field in fields:
        new_value = request.form.get(field)

        if str(new_value or "") != str(user.get(field) or ""):
            data[field] = new_value

    # Password
    password = request.form.get("PasswordHash")

    if password:
        data["PasswordHash"] = hash_password(password)
        print(f'{data["PasswordHash"]}')

    # Không có gì thay đổi
    if not data:
        flash(
            f'ℹ️ No changes detected for "{user["FullName"]}".',
            'info'
        )
        return redirect(url_for('user_manager.user_mng_page'))
    update = User_mng.update_by_id(user_id, data)

    if update:
        flash(
            f'✅ User "{user["FullName"]}" updated successfully.',
            'success'
        )
    else:
        flash(
            f'⚠️ Failed to update "{user["FullName"]}".',
            'warning'
        )

    return redirect(
        url_for('user_manager.user_mng_page')
    )

@user_mng_bp.route('/users/<string:user_id>/delete',methods=['POST'])
def delete_user(user_id):

    delete = User_mng.delete(user_id)
    if delete:

        flash(
            "✅ Deleted successfully.",
            "success"
        )

    else:

        flash(
            "⚠️ User not found.",
            "warning"
        )

    return redirect(
        url_for('user_manager.user_mng_page')
    )

@user_mng_bp.route('/partial/users/create')
def user_create_form():
    roles = User_mng.get_all_role()
    dpms = User_mng.get_all_dpm()
    return render_template('admin/manager/user/create_form.html',
                           roles=roles,
                           dpms=dpms)

@user_mng_bp.route('/users/create', methods=['POST'])
def create_user():
    data = {
        "id":
            request.form.get("Id"),
        "Username":
            request.form.get("Username"),

        "FullName":
            request.form.get("FullName"),

        "working_location":
            request.form.get("working_location"),

        "RoleId":
            request.form.get("RoleId"),

        "DepartmentId":
            request.form.get("DepartmentId"),

        "Job_title":
            request.form.get("Job_title"),

        "report_to":
            request.form.get("report_to"),

        "to_email":
            request.form.get("to_email"),

        "cc_email":
            request.form.get("cc_email"),

        "PasswordHash":
            hash_password(request.form.get("PasswordHash")),

        "Status":
            request.form.get("Status"),
        "Security":
            generate_security()
    }
    created = User_mng.insertUser(data)

    if created:

        flash(
            f'✅ Created user "{data["Username"]}" successfully',
            'success'
        )

    else:

        flash(
            f'❌ Failed to create user "{data["Username"]}"',
            'error'
        )

    return redirect(url_for('user_manager.user_mng_page'))



