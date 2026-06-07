from flask import Blueprint, session, redirect, url_for, request, render_template, flash, jsonify
from datetime import datetime
from Model.Leave_form.leave_service import LeaveRequest
from Service.leave_service import (
    calculate_leave_days,
    leave_amounts_from_type,
    calculate_leave_balance,
    get_leave_summary
)
from user_agents import parse as parse_ua
leave_bp = Blueprint('leave', __name__)

@leave_bp.route('/')
def leave_public():
    return render_template('user/leave-form/leave_public.html')

@leave_bp.route('/leave/<int:uid>')
def leave_public_detail(uid):
    session['leave_public_uid'] = uid
    data = get_leave_summary(uid)

    meta = data["meta"]
    entries = data["entries"]

    if not meta:
        return render_template(
            "user/leave-form/leave_public.html",
            error="Employee ID not found.",
            uid=uid
        )

    balance = calculate_leave_balance(meta, entries)

    ua_string = request.headers.get("User-Agent", "")
    user_agent = parse_ua(ua_string)

    template = (
        "user/leave-form/leave_detail_public_mobile.html"
        if user_agent.is_mobile or user_agent.is_tablet
        else "user/leave-form/leave_public.html"
    )

    return render_template(
        template,
        meta=meta,
        entries=entries,
        uid=uid,
        view_only=True,
        error=None,
        **balance
    )

@leave_bp.route('/leave/save-row', methods=['POST'])
def leave_save_row():

    try:
        user_id = int(
            session.get('leave_public_uid')
            or request.form.get('target_uid')
        )
        entry_id = int(
            request.form.get('entry_id')
        )
        leave = LeaveRequest.get_by_id(
            entry_id,
            user_id
        )

        if not leave:
            raise ValueError(
                'Leave request not found.'
            )

        if leave["status"] == "approved":
            raise ValueError(
                'Approved requests cannot be modified.'
            )

        leave_type = (
                request.form.get("leave_type")
                or ""
        ).strip()
        print(leave_type)
        date_from = request.form.get("date_from")
        date_to = request.form.get("date_to")

        date_from_dt = (
            datetime.strptime(
                date_from,
                "%Y-%m-%d"
            ).date()
            if date_from else None
        )

        date_to_dt = (
            datetime.strptime(
                date_to,
                "%Y-%m-%d"
            ).date()
            if date_to else None
        )

        days = float(
            request.form.get("days")
            or 0
        )

        amounts = leave_amounts_from_type(
            leave_type,
            days
        )

        data = {

            "date_from":
                date_from_dt,

            "date_to":
                date_to_dt,

            "notes":
                request.form.get("notes") or "",
            "type":
                leave_type,
            **amounts
        }

        LeaveRequest.update_by_id(
            entry_id,
            user_id,
            data
        )

        return jsonify({
            "ok": True,
            "message": "Leave request updated successfully."
        })

    except Exception as e:

        return jsonify({
            "ok": False,
            "error": str(e)
        }), 500

@leave_bp.route('/leave/add', methods=['POST'])
def leave_add():

    try:
        user_id = int(
            session.get('leave_public_uid')
            or request.form.get('target_uid')
        )
        leave_type = (
            request.form.get('leave_type')
            or ''
        ).strip()

        if not leave_type:
            raise ValueError(
                'Please select leave type.'
            )

        if not LeaveRequest.user_exists(user_id):
            raise ValueError(
                'User not found.'
            )

        date_from = request.form.get('date_from')
        date_to = request.form.get('date_to')

        days = calculate_leave_days(
            date_from,
            date_to
        )

        amounts = leave_amounts_from_type(
            leave_type,
            days
        )

        data = {

            "carry_over":
                float(
                    request.form.get(
                        "carry_over"
                    ) or 0
                ),

            "entitle_contract":
                float(
                    request.form.get(
                        "entitle_contract"
                    ) or 0
                ),

            "date_from":
                date_from,

            "date_to":
                date_to,

            "notes":
                request.form.get(
                    "notes"
                ) or "",

            **amounts
        }

        new_id = LeaveRequest.create(
            user_id,
            data
        )

        return jsonify({
            "ok": True,
            "id": new_id,
            "message":
                "Leave request created successfully."
        })

    except Exception as e:

        return jsonify({
            "ok": False,
            "error": str(e)
        }), 400

@leave_bp.route('/leave/delete/<int:entry_id>', methods=['POST'])
def leave_delete(entry_id):
    """[USER] Xóa dòng pending của chính mình."""

    user_id = int(session.get('leave_public_uid') or request.form.get('target_uid'))

    try:

        ok = LeaveRequest.delete_leave_entry_user(entry_id, user_id)

        if not ok:
            return jsonify({
                'ok': False,
                'error': 'Cannot delete this row.'
            }), 400

        return jsonify({
            'ok': True,
            "message": "Row deleted successfully."
        })

    except Exception as ex:

        return jsonify({
            'ok': False,
            'error': str(ex)
        }), 500

