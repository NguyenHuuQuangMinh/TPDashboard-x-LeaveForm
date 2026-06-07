from config import engine
from sqlalchemy import text
class User_mng:
    @staticmethod
    def get_all_users(name = None, role = None, department = None, status=None, page = 1, limit = 10):
        offset = (page-1)*limit

        where_clause = []
        params = {
            "limit": limit,
            "offset": offset
        }

        if name:
            where_clause.append('LOWER(u."Username") LIKE LOWER(:name) OR LOWER(u."FullName") LIKE LOWER(:name)')
            params["name"] = f"%{name}%"
        if role:
            where_clause.append('u."RoleId" = :role')
            params["role"] = role
        if department:
            where_clause.append('u."DepartmentId" = :department')
            params["department"] = department
        if status:
            where_clause.append('LOWER(u."Status") = LOWER(:status)')
            params["status"] = status
        if where_clause:
            where_sql = "WHERE " + " AND ".join(where_clause)
        else:
            where_sql = ""

        if where_sql:
            where_sql += ' AND r."Status" = 1 AND d.status = 1'
        else:
            where_sql = 'WHERE r."Status" = 1 AND d.status = 1'

        count_sql = text(f"""
            SELECT COUNT(*)
            FROM "Users" u
            INNER JOIN "Roles" r ON r."RoleId" = u."RoleId"
            INNER JOIN "Departments" d ON d.id = u."DepartmentId"
            {where_sql}
        """)

        sql = text(f"""
                    SELECT
                        u."Id",
                        u."Username",
                        u."FullName",
                        u."Job_title",
                        u."Status",
                        r."Rolename",
                        d.name as "dpm_name"
                    FROM "Users" u INNER JOIN "Roles" r ON r."RoleId" = u."RoleId"
                                   INNER JOIN "Departments" d ON d.id = u."DepartmentId"
                    {where_sql}
                    ORDER BY u."Id"
                    LIMIT :limit
                    OFFSET :offset
            """)

        with engine.connect() as conn:
            total = conn.execute(count_sql, params).scalar()

            results = conn.execute(sql,params).mappings().all()

        return results, total

    @staticmethod
    def get_by_id(user_id):
        sql = text("""
            SELECT
                "Id",
                "FullName",
                "Job_title",
                "report_to",
                "to_email",
                "cc_email",
                "PasswordHash",
                "Status",
                "working_location",
                "RoleId",
                "DepartmentId"
            FROM "Users"
            WHERE "Id" = :id
        """)
        with engine.connect() as conn:
            result = conn.execute(sql, {"id": user_id}).mappings().first()
        return result

    @staticmethod
    def get_all_dpm():
        sql = text("""
                    SELECT DISTINCT
                        id,
                        name
                    FROM "Departments"
                """)
        with engine.connect() as conn:
            results = conn.execute(sql).mappings().all()
        return results

    @staticmethod
    def get_all_role():
        sql = text("""
                        SELECT DISTINCT
                            "RoleId",
                            "Rolename"
                        FROM "Roles"
                    """)
        with engine.connect() as conn:
            results = conn.execute(sql).mappings().all()
        return results

    @staticmethod
    def update_by_id(user_id, data):
        set_clauses = []

        for key in data.keys():
            set_clauses.append(f'"{key}" = :{key}')
        sql = text(f"""
                UPDATE "Users"
                SET {", ".join(set_clauses)}
                WHERE "Id" = :id
            """)

        with engine.begin() as conn:
            result = conn.execute(
                sql,
                {
                    "id": user_id,
                    **data
                }
            ).rowcount
        return result > 0

    @staticmethod
    def delete(user_id):
        sql = text("""
            DELETE FROM "Users"
            WHERE "Id" = :id
        """)
        with engine.begin() as conn:
            result = conn.execute(sql, {"id": user_id}).rowcount
        return result > 0

    @staticmethod
    def insertUser(data):
        sql = text("""
                INSERT INTO "Users"
                ("Username", "FullName", "working_location", "RoleId", "DepartmentId", "Job_title", "report_to","to_email", "cc_email","PasswordHash","Status")
                VALUES
                (:Username, :FullName, :working_location, :RoleId, :DepartmentId, :Job_title, :report_to, :to_email, :cc_email, :PasswordHash, :Status)
            """)
        with engine.begin() as conn:
            result = conn.execute(
                sql,
                {
                    **data
                }
            ).rowcount
        return result > 0