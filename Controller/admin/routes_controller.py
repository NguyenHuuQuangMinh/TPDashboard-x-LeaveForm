from flask import Blueprint, session, redirect, url_for, request, render_template, flash, jsonify
from Controller.decorators import admin_required
from Model.admin.routes import Routes

routes_bp = Blueprint('routes', __name__)

@routes_bp.before_request
@admin_required
def before_all():
    pass

@routes_bp.route('/admin/routes')
def route_page():
    name = request.args.get('name', '').strip()
    window_type = request.args.get('window_type', '').strip()
    page = request.args.get('page', 1, type=int)
    per_page = 10
    routes,total = Routes.get_all_routes(name,window_type,page,per_page)
    total_pages = (total + per_page - 1) // per_page

    return render_template(
        'admin/manager/route/routes.html',
        routes=routes,
        page=page,
        name=name,
        window_type=window_type,
        total=total,
        total_pages=total_pages
    )

@routes_bp.route('/partial/routes/<int:route_id>')
def partial_route(route_id):

    route = Routes.get_by_id(route_id)
    parents = Routes.get_parent_routes()
    return render_template(
        'admin/manager/route/route_edit.html',
        route=route,
        parents=parents
    )

@routes_bp.route('/partial/routes/<int:route_id>/update', methods=['POST'])
def update_route(route_id):
    data = {

        "name":
            request.form.get("route_name"),

        "path":
            request.form.get("route_path"),

        "icon":
            request.form.get("icon"),

        "window_type":
            request.form.get("window_type"),

        "sort_order":
            request.form.get("sort_order"),

        "is_active":
            request.form.get("is_active") == "true",

        "parent_id":
            request.form.get("parent_id") or 0

    }
    update = Routes.update_by_id(route_id,data)
    if update:

        flash(
            f'✅ Route "{data["name"]}" updated successfully.',
            'success'
        )

    else:

        flash(
            f'⚠️ Route "{data["name"]}" does not exist or has already been deleted.',
            'warning'
        )
    return redirect(
        url_for('routes.route_page')
    )

@routes_bp.route('/routes/<int:route_id>/delete',methods=['POST'])
def delete_route(route_id):

    delete = Routes.delete(route_id)
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
        url_for('routes.route_page')
    )

@routes_bp.route('/partial/routes/create')
def route_create_form():
    parents = Routes.get_parent_routes()
    return render_template('admin/manager/route/create_form.html',parents=parents)

@routes_bp.route('/routes/create', methods=['POST'])
def create_route():
    data = {

        "name":
            request.form.get("route_name"),

        "path":
            request.form.get("route_path"),

        "icon":
            request.form.get("icon"),

        "window_type":
            request.form.get("window_type"),

        "sort_order":
            request.form.get("sort_order"),

        "is_active":
            request.form.get("is_active") == "true",

        "parent_id":
            request.form.get("parent_id") or 0
    }
    created = Routes.insertRoutes(data)

    if created:

        flash(
            f'✅ Created route "{data["name"]}" successfully',
            'success'
        )

    else:

        flash(
            f'❌ Failed to create route "{data["name"]}"',
            'error'
        )

    return redirect(url_for('routes.route_page'))


