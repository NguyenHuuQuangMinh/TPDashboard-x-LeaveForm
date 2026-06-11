from config import engine
from sqlalchemy import text
from decimal import Decimal

def _float_row(row):
    row = dict(row)

    for k, v in row.items():
        if isinstance(v, Decimal):
            row[k] = float(v)

    return row

class LeaveRequest:
    @staticmethod
    def get_leave_entries(user_id, security_code):
        sql = text("""
            SELECT
                lr.id,
                lr.date_from,
                lr.date_to,
                lr.annual_leave,
                lr.sick_leave,
                lr.maternity_leave,
                lr.pregnancy_leave,
                lr.personal_leave,
                lr.compensate_leave,
                lr.unpaid_leave,
                lr.notes,
                lr.status,
                lr.created_at,
                lr.carry_over,
                lr.entitle_contract,
                lr.type
            FROM leave_requests lr INNER JOIN "Users" u ON u."Id" = lr.user_id
            WHERE lr.user_id = :uid AND u."Security" = :security_code
              AND EXTRACT(YEAR FROM lr.date_from) = EXTRACT(YEAR FROM CURRENT_DATE)
            ORDER BY lr.date_from ASC
        """)

        with engine.connect() as conn:
            rows = conn.execute(
                sql,
                {"uid": user_id,
                 "security_code": security_code}
            ).mappings().all()

        return [_float_row(row) for row in rows]

    @staticmethod
    def get_all_leave_summary():
        sql = text("""
            SELECT
                lr.user_id,
                u."Username" AS username,
                u."FullName" AS full_name,
                u."report_to" AS report_to,
                u."PasswordHash" AS security_code,
                SUM(annual_leave) AS total_annual,
                SUM(sick_leave) AS total_sick,
                SUM(unpaid_leave) AS total_unpaid,
                COUNT(*) AS total_entries
            FROM leave_requests lr
            JOIN "Users" u
                ON u."Id" = lr.user_id
            WHERE EXTRACT(YEAR FROM lr.date_from)
                = EXTRACT(YEAR FROM CURRENT_DATE)
            GROUP BY
                lr.user_id,
                u."Username",
                u."FullName",
                u."report_to",
                u."PasswordHash"
        """)

        with engine.connect() as conn:
            return conn.execute(sql).mappings().all()

    @staticmethod
    def get_leave_meta(user_id, security_code):
        sql = text("""
            SELECT
                u."Username"         AS username,
                u."FullName"         AS full_name,
                u."Job_title"        AS job_title,
                u."working_location" AS working_location,
                u."joining_date"     AS joining_date,
                u."department"       AS department,
                u."report_to"        AS report_to,
                lr.carry_over,
                lr.entitle_contract
            FROM "Users" u
            LEFT JOIN leave_requests lr
                ON u."Id" = lr.user_id
            WHERE u."Id" = :uid AND u."Security" = :security_code
              AND EXTRACT(YEAR FROM lr.date_from) = EXTRACT(YEAR FROM CURRENT_DATE)
            ORDER BY lr.created_at ASC
            LIMIT 1
        """)

        with engine.connect() as conn:
            row = conn.execute(
                sql,
                {"uid": user_id,
                 "security_code": security_code}
            ).mappings().first()

        if not row:
            return {}

        meta = dict(row)
        meta["carry_over"] = float(meta.get("carry_over") or 0)
        meta["entitle_contract"] = float(meta.get("entitle_contract") or 0)

        return meta

    @staticmethod
    def get_by_id(entry_id, user_id):
        sql = text("""
            SELECT
                id,
                user_id,
                status
            FROM leave_requests
            WHERE id = :eid
              AND user_id = :uid
        """)

        with engine.connect() as conn:
            result = conn.execute(
                sql,
                {
                    "eid": entry_id,
                    "uid": user_id
                }
            ).mappings().first()

        return result

    @staticmethod
    def update_by_id(entry_id, user_id, data):
        sql = text("""
            UPDATE leave_requests
            SET
                date_from        = :date_from,
                date_to          = :date_to,

                annual_leave     = :annual_leave,
                sick_leave       = :sick_leave,
                maternity_leave  = :maternity_leave,
                pregnancy_leave  = :pregnancy_leave,
                personal_leave   = :personal_leave,
                compensate_leave = :compensate_leave,
                unpaid_leave     = :unpaid_leave,

                notes            = :notes,
                type             = :type,
                updated_at       = NOW()

            WHERE id = :eid
              AND user_id = :uid
        """)

        with engine.begin() as conn:
            result = conn.execute(
                sql,
                {
                    "eid": entry_id,
                    "uid": user_id,
                    **data
                }
            ).rowcount

        return result > 0

    @staticmethod
    def user_exists(user_id):

        sql = text("""
            SELECT 1
            FROM "Users"
            WHERE "Id" = :id
        """)

        with engine.connect() as conn:
            result = conn.execute(
                sql,
                {"id": user_id}
            ).scalar()

        return bool(result)

    @staticmethod
    def create(user_id, data):

        sql = text("""
            INSERT INTO leave_requests (

                user_id,
                carry_over,
                entitle_contract,

                date_from,
                date_to,

                annual_leave,
                sick_leave,
                maternity_leave,
                pregnancy_leave,
                personal_leave,
                compensate_leave,
                unpaid_leave,

                notes,
                status

            )
            VALUES (

                :user_id,
                :carry_over,
                :entitle_contract,

                :date_from,
                :date_to,

                :annual_leave,
                :sick_leave,
                :maternity_leave,
                :pregnancy_leave,
                :personal_leave,
                :compensate_leave,
                :unpaid_leave,

                :notes,
                'pending'
            )
            RETURNING id
        """)

        with engine.begin() as conn:
            result = conn.execute(
                sql,
                {
                    "user_id": user_id,
                    **data
                }
            ).scalar()

        return result

    @staticmethod
    def delete_leave_entry_user(entry_id, user_id):
        """[USER] Xóa dòng pending của chính mình."""
        sql = text("""
                DELETE FROM leave_requests
                WHERE id = :eid
                  AND user_id = :uid
                  AND status = 'pending'
            """)
        with engine.begin() as conn:
            result = conn.execute(sql,{
                'eid': entry_id,
                'uid': user_id
            })

            return result.rowcount > 0