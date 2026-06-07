from datetime import datetime, timedelta
from Model.Leave_form.leave_service import LeaveRequest
from decimal import Decimal

_LEAVE_AMOUNT_COLS = (
    "annual_leave",
    "sick_leave",
    "maternity_leave",
    "pregnancy_leave",
    "personal_leave",
    "compensate_leave",
    "unpaid_leave",
)

_LEAVE_TYPE_COLUMN = {
    "annual_carry": "annual_leave",
    "annual": "annual_leave",
    "sick": "sick_leave",
    "maternity": "maternity_leave",
    "marriage": "personal_leave",
    "paternity": "pregnancy_leave",
    "personal": "personal_leave",
    "compensate": "compensate_leave",
    "unpaid": "unpaid_leave",
}

LEAVE_FIELDS = [
    "annual_leave",
    "sick_leave",
    "maternity_leave",
    "pregnancy_leave",
    "personal_leave",
    "compensate_leave",
    "unpaid_leave",
]

def _float_row(row):
    row = dict(row)

    for k, v in row.items():
        if isinstance(v, Decimal):
            row[k] = float(v)

    return row


def get_leave_summary(user_id):
    meta = LeaveRequest.get_leave_meta(user_id)
    entries = LeaveRequest.get_leave_entries(user_id)

    return {
        "meta": meta,
        "entries": entries
    }

def calculate_leave_balance(meta, entries):
        total_avail = (
                float(meta.get("carry_over") or 0)
                + float(meta.get("entitle_contract") or 0)
        )

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

        return {
            "total_avail": total_avail,
            "al_used": al_used,
            "remaining": total_avail - al_used
        }

def calculate_leave_days(date_from, date_to):

        if not date_from or not date_to:
            return 0

        if isinstance(date_from, str):
            date_from = datetime.strptime(
                date_from,
                "%Y-%m-%d"
            ).date()

        if isinstance(date_to, str):
            date_to = datetime.strptime(
                date_to,
                "%Y-%m-%d"
            ).date()

        if date_to < date_from:
            return 0

        total = 0
        current = date_from

        while current <= date_to:

            weekday = current.weekday()

            # Monday=0 ... Sunday=6

            # Sunday
            if weekday == 6:
                pass

            # Saturday
            elif weekday == 5:
                total += 0.5

            # Monday -> Friday
            else:
                total += 1

            current = current.replace(day=current.day) + timedelta(days=1)

        return total

def leave_amounts_from_type(leave_type, days):
        """Chuyển leave_type + số ngày thành dict amount."""
        amounts = {c: 0.0 for c in _LEAVE_AMOUNT_COLS}
        lt = (leave_type or '').strip()
        if not lt:
            return amounts
        col = _LEAVE_TYPE_COLUMN.get(lt)
        if not col:
            raise ValueError(f'Loại nghỉ không hợp lệ: {leave_type!r}')
        amounts[col] = float(days or 0)
        return amounts

def calc_used_leave(entries):
    return sum(
        sum(float(e.get(f) or 0) for f in LEAVE_FIELDS)
        for e in entries
    )


def calc_total(meta):
    return float(meta.get("carry_over") or 0) + float(meta.get("entitle_contract") or 0)