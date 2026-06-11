from flask import Blueprint, session, redirect, url_for, request, render_template, flash, jsonify, send_file, abort
from Controller.decorators import admin_or_manager_required
from Model.manager.leave_form import Leave
from Service.leave_service import (_float_row, calc_used_leave, calc_total)
from datetime import datetime
leave_mng_bp = Blueprint('leave', __name__)

@leave_mng_bp.before_request
@admin_or_manager_required
def before_all():
    pass

@leave_mng_bp.route('/manager/leave-overview')
def manager_leave_overview():
    id = session.get('user_id')
    role = session.get('role')
    department_id = session.get(
        'department'
    )
    print('dpm:', department_id)
    print('role:', role)
    if role == 1 or (role == 3 and department_id == 5):

        rows = [
            dict(r)
            for r in Leave.get_all_leave_summary()
        ]

        pending_entries = [
            _float_row(r)
            for r in Leave.get_pending_for_admin()
        ]

        title = 'All Departments'

    else:



        rows = [
            dict(r)
            for r in Leave.get_department_leave_summary(
                department_id
            )
        ]

        pending_entries = [
            _float_row(r)
            for r in Leave.get_pending_for_department(
                department_id,id
            )
        ]

        title = f'Department {department_id}'

    return render_template(
        'user/manager_leave_overview.html',
        rows=rows,
        pending_entries=pending_entries,
        title=title,
        role=role,
        now=datetime.now()
    )

@leave_mng_bp.route('/manager/leave', methods=['GET'])
def leave():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for("auth.login"))
    meta_row, entries_raw = Leave.get_leave_summary(user_id)

    # ---- META CLEAN ----
    meta = dict(meta_row) if meta_row else {}
    meta["carry_over"] = float(meta.get("carry_over") or 0)
    meta["entitle_contract"] = float(meta.get("entitle_contract") or 0)

    # ---- ENTRIES CLEAN ----
    entries = [_float_row(e) for e in entries_raw]

    # ---- BUSINESS LOGIC (nhẹ, vẫn để controller ok trong MVC) ----
    total_avail = meta["carry_over"] + meta["entitle_contract"]

    al_used = sum(
        float(
            e.get("annual_leave")
            or e.get("sick_leave")
            or e.get("maternity_leave")
            or e.get("pregnancy_leave")
            or e.get("personal_leave")
            or e.get("compensate_leave")
            or e.get("unpaid_leave")
            or 0
        )
        for e in entries
    )

    remaining = total_avail - al_used

    return render_template(
        "user/leave.html",
        entries=entries,
        meta=meta,
        total_avail=total_avail,
        al_used=al_used,
        remaining=remaining,
        username=session.get("username"),
        job=session.get("job"),
    )

@leave_mng_bp.route('/manager/leave/<int:target_user_id>', methods=['GET'])
def manager_leave_detail(target_user_id):
    role       = session.get('role')
    id_department = session.get('department')

    meta, entries_raw = Leave.get_leave_summary(target_user_id)
    if role == 3 and id_department !=5 and meta.get('department') != id_department:
        abort(403)

    entries = [_float_row(e) for e in entries_raw]

    total_avail = calc_total(meta)
    al_used = calc_used_leave(entries)
    remaining = total_avail - al_used

    return render_template(
        "user/leave.html",
        entries=entries,
        meta=meta,
        total_avail=total_avail,
        al_used=al_used,
        remaining=remaining,
        username=session.get('username'),
        job=session.get('job'),
        view_only=True
    )

@leave_mng_bp.route('/manager/reject/<int:entry_id>', methods=['POST'])
def manager_reject(entry_id):
    role = session.get('role')
    department = session.get('department')

    request_dept = Leave.get_request_department(entry_id)

    if not request_dept:
        flash('Đơn không tồn tại.', 'error')
        return redirect(url_for('leave.manager_leave_overview') + '?tab=pending')
    if role != 1 and role == 3:
        if request_dept != department:
            flash('Không có quyền từ chối đơn này.', 'error')
            return redirect(url_for('leave.manager_leave_overview') + '?tab=pending')

    note = request.form.get('note') or ''

    rows_affected = Leave.reject_leave_entry(entry_id, note)
    if rows_affected:
        flash('✗ Đã từ chối đơn.', 'success')
    else:
        flash('Không tìm thấy đơn hoặc đã bị xử lý.', 'error')
    return redirect(url_for('leave.manager_leave_overview') + '?tab=pending')

@leave_mng_bp.route('/manager/approve/<int:entry_id>', methods=['POST'])
def manager_approve(entry_id):
    role = session.get('role')
    department = session.get('department')

    # ❗ check department ownership
    request_dept = Leave.get_request_department(entry_id)

    if not request_dept:
        flash('Đơn không tồn tại.', 'error')
        return redirect(url_for('leave.manager_leave_overview') + '?tab=pending')
    if role != 1 and role == 3:
        if request_dept != department:
            flash('Không có quyền duyệt đơn này.', 'error')
            return redirect(url_for('leave.manager_leave_overview') + '?tab=pending')

    # approve
    results = Leave.approve_leave_entry(entry_id)
    if results:
        flash('✅ Đã duyệt đơn thành công.', 'success')
    else:
        flash('Không tìm thấy đơn hoặc đã bị xử lý.', 'error')

    return redirect(url_for('leave.manager_leave_overview') + '?tab=pending')

@leave_mng_bp.route("/manager/users/import/template")
def users_import_template():

    file = Leave.generate_import_template()

    return send_file(
        file,
        mimetype=(
            "application/"
            "vnd.openxmlformats-officedocument"
            ".spreadsheetml.sheet"
        ),
        as_attachment=True,
        download_name="users_import_template.xlsx"
    )

@leave_mng_bp.route('/manager/users/import', methods=['POST'])
def users_import():
    result = Leave.import_users(
        request.files.get("import_file")
    )
    if not result["ok"]:

        flash(
            f"❌ {result['error']}",
            "error"
        )

        return redirect(
            url_for("leave.manager_leave_overview")
        )

    message = (
        f"✅ Import completed: "
        f"{result['inserted']} inserted, "
        f"{result['updated']} updated"
    )

    if result["skipped"]:

        message += (
            f", {result['skipped']} skipped"
        )

    flash(
        message,
        "success"
    )

    for error in result.get("errors", [])[:5]:

        flash(
            f"⚠️ {error}",
            "error"
        )

    return redirect(
        url_for("leave.manager_leave_overview")
    )