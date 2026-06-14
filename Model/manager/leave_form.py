from config import engine
from sqlalchemy import text
from Service.import_user_from_file import import_users_from_file
import io
import openpyxl
class Leave:
    @staticmethod
    def get_all_leave_summary():
        sql = text("""
                        SELECT
                            lr.user_id,

                            u."Username"      AS username,
                            u."FullName"      AS full_name,
                            u."report_to"     AS report_to,
                            d.name            AS department,
                            u."Security"      AS security,

                            SUM(lr.annual_leave) AS total_annual,
                            SUM(lr.sick_leave)   AS total_sick,
                            SUM(lr.unpaid_leave) AS total_unpaid,

                            COUNT(*) AS total_entries

                        FROM leave_requests lr

                        JOIN "Users" u
                            ON u."Id" = lr.user_id
                        JOIN "Departments" d
                            ON d.id = u."DepartmentId"
                        WHERE
                            EXTRACT(YEAR FROM lr.date_from)
                            =
                            EXTRACT(YEAR FROM CURRENT_DATE)

                        GROUP BY
                            lr.user_id,
                            u."Username",
                            u."FullName",
                            u."report_to",
                            u."PasswordHash",
                            d.name,
                            u."Security"

                        ORDER BY
                            u."FullName"
                    """)
        with engine.connect() as conn:
            results = conn.execute(
                sql
            ).mappings().all()
        return results

    @staticmethod
    def get_pending_for_admin():
        sql = text("""
                        SELECT
                            lr.id,
                            lr.user_id,

                            lr.date_from,
                            lr.date_to,

                            lr.annual_leave,
                            lr.sick_leave,
                            lr.maternity_leave,
                            lr.pregnancy_leave,
                            lr.personal_leave,
                            lr.compensate_leave,
                            lr.unpaid_leave,
                            lr.type,
                            lr.notes,
                            lr.status,
                            lr.created_at,

                            lr.carry_over,
                            lr.entitle_contract,

                            u."Username"         AS username,
                            u."FullName"         AS full_name,
                            u."Job_title"        AS job_title,
                            u."working_location" AS working_location,
                            u."DepartmentId"     AS department_id,
                            d.name            AS department,
                            lr.type             AS leave_type
                        FROM leave_requests lr 

                        JOIN "Users" u
                            ON u."Id" = lr.user_id

                        Join "Departments" d
                            ON u."DepartmentId"  = d.id
                        WHERE lr.status = 'pending'

                        ORDER BY lr.created_at DESC
                    """)
        with engine.connect() as conn:
            results = conn.execute(
                sql
            ).mappings().all()
        return results

    @staticmethod
    def get_department_leave_summary(department_id):
        sql = text("""
                        SELECT
                            lr.user_id,

                            u."Username"      AS username,
                            u."FullName"      AS full_name,
                            u."report_to"     AS report_to,
                            d.name            AS department,
                            u."Security"      AS security,
                            SUM(lr.annual_leave) AS total_annual,
                            SUM(lr.sick_leave)   AS total_sick,
                            SUM(lr.unpaid_leave) AS total_unpaid,

                            COUNT(*) AS total_entries

                        FROM leave_requests lr

                        JOIN "Users" u
                            ON u."Id" = lr.user_id
                        JOIN "Departments" d
                            ON d.id = u."DepartmentId"

                        WHERE
                            EXTRACT(YEAR FROM lr.date_from)
                            =
                            EXTRACT(YEAR FROM CURRENT_DATE)

                            AND u."DepartmentId" = :dept_id

                        GROUP BY
                            lr.user_id,
                            u."Username",
                            u."FullName",
                            u."report_to",
                            u."PasswordHash",
                            u."DepartmentId",
                            d.name,
                            u."Security"

                        ORDER BY
                            u."FullName"
                    """)
        with engine.connect() as conn:
            results = conn.execute(
                sql
                ,
                {
                    "dept_id": department_id
                }
            ).mappings().all()
        return results

    @staticmethod
    def get_pending_for_department(department_id,id):
        sql = text("""
                        SELECT
                            lr.id,
                            lr.user_id,

                            lr.date_from,
                            lr.date_to,

                            lr.annual_leave,
                            lr.sick_leave,
                            lr.maternity_leave,
                            lr.pregnancy_leave,
                            lr.personal_leave,
                            lr.compensate_leave,
                            lr.unpaid_leave,
                            lr.type,
                            lr.notes,
                            lr.status,
                            lr.created_at,

                            lr.carry_over,
                            lr.entitle_contract,

                            u."Username"         AS username,
                            u."FullName"         AS full_name,
                            u."Job_title"        AS job_title,
                            u."working_location" AS working_location,
                            u."DepartmentId"     AS department_id,
                            d.name            AS department,
                            lr.type             AS leave_type
                        FROM leave_requests lr

                        JOIN "Users" u
                            ON u."Id" = lr.user_id
                        Join "Departments" d
                            ON u."DepartmentId"  = d.id
                        WHERE
                            lr.status = 'pending'
                            AND u."DepartmentId" = :dept_id
                            AND u."Id" != :id

                        ORDER BY lr.created_at DESC
                    """)

        with engine.connect() as conn:
            results = conn.execute(
                sql,
                {
                    "dept_id": department_id,
                    "id": id
                }
            ).mappings().all()
        return results

    @staticmethod
    def get_leave_summary(user_id):
        meta_sql = text("""
                    SELECT
                        u."Username"         AS username,
                        u."FullName"         AS full_name,
                        u."Job_title"        AS job_title,
                        u."working_location" AS working_location,
                        u."joining_date"     AS joining_date,
                        u."DepartmentId"       AS department,
                        u."report_to"        AS report_to,
                        lr.carry_over,
                        lr.entitle_contract
                    FROM "Users" u
                    LEFT JOIN leave_requests lr ON u."Id" = lr.user_id
                    WHERE u."Id" = :uid
                      AND EXTRACT(YEAR FROM lr.date_from) = EXTRACT(YEAR FROM CURRENT_DATE)
                    ORDER BY lr.created_at ASC
                    LIMIT 1
                """)

        entries_raw_sql = text("""
                    SELECT
                        id, date_from, date_to,
                        annual_leave, sick_leave, maternity_leave,
                        pregnancy_leave, personal_leave, compensate_leave,
                        unpaid_leave, notes, status, created_at,
                        carry_over, entitle_contract
                    FROM leave_requests
                    WHERE user_id = :uid
                      AND EXTRACT(YEAR FROM date_from) = EXTRACT(YEAR FROM CURRENT_DATE)
                    ORDER BY date_from ASC
                """)
        with engine.connect() as conn:
            meta_row = conn.execute(
                meta_sql
                ,
                {"uid": user_id},
            ).mappings().first()

            entries_raw = conn.execute(
                entries_raw_sql
                ,
                {"uid": user_id},
            ).mappings().all()

        return meta_row, entries_raw

    @staticmethod
    def get_request_department(entry_id):
        sql = text("""
                SELECT u."DepartmentId"
                FROM leave_requests lr
                JOIN "Users" u ON u."Id" = lr.user_id
                WHERE lr.id = :eid
            """)

        with engine.connect() as conn:
            row = conn.execute(sql, {"eid": entry_id}).mappings().first()

        return row["DepartmentId"] if row else None

    @staticmethod
    def reject_leave_entry(entry_id, note=None):
        sql = text("""
              UPDATE leave_requests
              SET status     = 'rejected',
                  notes      = COALESCE(:note, notes),
                  updated_at = NOW()
              WHERE id = :id
          """)

        with engine.begin() as conn:
            result = conn.execute(sql, {"id": entry_id, "note": note})

        return result.rowcount >0

    @staticmethod
    def approve_leave_entry(entry_id):
        sql = text("UPDATE leave_requests SET status = 'approved', updated_at = NOW() WHERE id = :id")
        with engine.begin() as conn:
            result = conn.execute(
                sql
                ,
                {'id': entry_id},
            )
        return result.rowcount > 0

    @staticmethod
    def generate_import_template():
        wb = openpyxl.Workbook()

        ws = wb.active
        ws.title = "Users"

        headers = [
            "Id",
            "Username",
            "PasswordHash",
            "FullName",
            "Job_title",
            "Status",
            "RoleId",
            "working_location",
            "joining_date",
            "year",
            "department",
            "report_to",
            "to_email",
            "cc_email",
            "entitle_contract",
            "carry_over",
            "Security"
        ]

        ws.append(headers)

        # Example data
        ws.append([
            "SG000",
            "tran.my",
            "password123",
            "Tran My",
            "Reporter",
            1,
            2,
            "2/29 Quach Van Tuan",
            "2024-08-26",
            2026,
            "Systems",
            "BM",
            "tran.my@company.com",
            "hr@company.com",
            12,
            1,
            ""
        ])

        buffer = io.BytesIO()

        wb.save(buffer)

        buffer.seek(0)

        return buffer

    @staticmethod
    def import_users(file):
        print(file)
        if not file or file.filename == '':
            return {
                "ok": False,
                "error": "Please select an Excel or CSV file."
            }

        filename = file.filename.lower()

        if not (
                filename.endswith(".xlsx")
                or filename.endswith(".xls")
                or filename.endswith(".csv")
        ):
            return {
                "ok": False,
                "error": "Only .xlsx, .xls or .csv files are supported."
            }

        return import_users_from_file(
            file.stream,
            filename
        )
