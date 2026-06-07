from flask import Blueprint, session, redirect, url_for, request, render_template, flash, jsonify
from Controller.decorators import admin_required
from Model.admin.departments import Departments

dpm_bp = Blueprint('departments', __name__)

@dpm_bp.before_request
@admin_required
def before_all():
    pass

@dpm_bp.route('/admin/departments')
def dpm_page():
    name = request.args.get('name', '').strip()
    status = request.args.get('status', '').strip()
    page = request.args.get('page', 1, type=int)
    per_page = 10
    dpms,total = Departments.get_all_departments(name, status,page,per_page)
    total_pages = (total + per_page - 1) // per_page

    return render_template(
        'admin/manager/department/department.html',
        dpms=dpms,
        page=page,
        name=name,
        status = status,
        total=total,
        total_pages=total_pages
    )

@dpm_bp.route('/partial/departments/<int:dpm_id>')
def partial_dpm(dpm_id):
    dpms = Departments.get_by_id(dpm_id)
    return render_template(
        'admin/manager/department/department_edit.html',
        dpms=dpms
    )

@dpm_bp.route('/partial/departments/<int:dpm_id>/update', methods=['POST'])
def update_dpm(dpm_id):
    data = {

        "name":
            request.form.get("name"),

        "status":
            request.form.get("status")

    }
    update = Departments.update_by_id(dpm_id,data)
    if update:

        flash(
            f'✅ Departments "{data["name"]}" updated successfully.',
            'success'
        )

    else:

        flash(
            f'⚠️ Departments "{data["name"]}" does not exist or has already been deleted.',
            'warning'
        )
    return redirect(
        url_for('departments.dpm_page')
    )

@dpm_bp.route('/departments/<int:dpm_id>/delete',methods=['POST'])
def delete_dpm(dpm_id):

    delete = Departments.delete(dpm_id)
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
        url_for('departments.dpm_page')
    )

@dpm_bp.route('/partial/departments/create')
def dpm_create_form():
    return render_template('admin/manager/department/create_form.html')

@dpm_bp.route('/departments/create', methods=['POST'])
def create_dpm():
    data = {

        "name":
            request.form.get("name"),
        "status":
            request.form.get("status")
    }
    created = Departments.insertDpm(data)

    if created:

        flash(
            f'✅ Created departments "{data["name"]}" successfully',
            'success'
        )

    else:

        flash(
            f'❌ Failed to create departments "{data["name"]}"',
            'error'
        )

    return redirect(url_for('departments.dpm_page'))



