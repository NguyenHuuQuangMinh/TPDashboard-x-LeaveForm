from flask import Blueprint, session, redirect, url_for, request, render_template, flash, jsonify
from Controller.decorators import admin_required
from Model.admin.roles import Roles

role_bp = Blueprint('role', __name__)

@role_bp.before_request
@admin_required
def before_all():
    pass

@role_bp.route('/admin/roles')
def role_page():
    name = request.args.get('name', '').strip()
    status = request.args.get('status', '').strip()
    page = request.args.get('page', 1, type=int)
    per_page = 10
    roles,total = Roles.get_all_roles(name, status,page,per_page)
    total_pages = (total + per_page - 1) // per_page

    return render_template(
        'admin/manager/role/roles.html',
        roles=roles,
        page=page,
        name=name,
        status = status,
        total=total,
        total_pages=total_pages
    )

@role_bp.route('/partial/roles/<int:role_id>')
def partial_role(role_id):
    role = Roles.get_by_id(role_id)
    return render_template(
        'admin/manager/role/role_edit.html',
        role=role
    )

@role_bp.route('/partial/roles/<int:role_id>/update', methods=['POST'])
def update_role(role_id):
    data = {

        "name":
            request.form.get("name"),

        "status":
            request.form.get("status")

    }
    update = Roles.update_by_id(role_id,data)
    if update:

        flash(
            f'✅ Role "{data["name"]}" updated successfully.',
            'success'
        )

    else:

        flash(
            f'⚠️ Role "{data["name"]}" does not exist or has already been deleted.',
            'warning'
        )
    return redirect(
        url_for('role.role_page')
    )

@role_bp.route('/roles/<int:role_id>/delete',methods=['POST'])
def delete_role(role_id):

    delete = Roles.delete(role_id)
    if delete:

        flash(
            "✅ Deleted successfully.",
            "success"
        )

    else:

        flash(
            "⚠️ Route not found.",
            "warning"
        )

    return redirect(
        url_for('role.role_page')
    )

@role_bp.route('/partial/roles/create')
def route_create_form():
    return render_template('admin/manager/role/create_form.html')

@role_bp.route('/roles/create', methods=['POST'])
def create_role():
    data = {

        "name":
            request.form.get("name"),
        "status":
            request.form.get("status")
    }
    created = Roles.insertRole(data)

    if created:

        flash(
            f'✅ Created role "{data["name"]}" successfully',
            'success'
        )

    else:

        flash(
            f'❌ Failed to create role "{data["name"]}"',
            'error'
        )

    return redirect(url_for('role.role_page'))



