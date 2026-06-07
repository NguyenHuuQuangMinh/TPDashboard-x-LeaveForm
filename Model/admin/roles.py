from config import engine
from sqlalchemy import text
class Roles:
    @staticmethod
    def get_all_roles(name = None, status=None, page = 1, limit = 10):
        offset = (page-1)*limit

        where_clause = []
        params = {
            "limit": limit,
            "offset": offset
        }

        if name:
            where_clause.append('LOWER("Rolename") LIKE LOWER(:name)')
            params["name"] = f"%{name}%"
        if status:
            where_clause.append('Status = :status')
            params["status"] = status
        where_sql = ""
        if where_clause:
            where_sql = "WHERE " + " AND ".join(where_clause)

        count_sql = text(f"""
                SELECT COUNT(*)
                FROM "Roles"
                {where_sql}
            """)

        sql = text(f"""
                    SELECT
                        "RoleId",
                        "Rolename",
                        "Status"
                    FROM "Roles"
                    {where_sql}
                    ORDER BY "RoleId"
                    LIMIT :limit
                    OFFSET :offset
            """)

        with engine.connect() as conn:
            total = conn.execute(count_sql, params).scalar()

            roles = conn.execute(sql,params).mappings().all()

        return roles, total

    @staticmethod
    def get_by_id(role_id):
        sql = text("""
            SELECT
                "RoleId",
                "Rolename",
                "Status"
            FROM "Roles"
            WHERE "RoleId" = :id
        """)
        with engine.connect() as conn:
            result = conn.execute(sql, {"id": role_id}).mappings().first()
        return result

    @staticmethod
    def update_by_id(roles_id, data):
        sql = text("""
            UPDATE "Roles"
            SET 
                "Rolename" = :name,
                "Status" = :status
            WHERE "RoleId" = :id
        """)
        with engine.begin() as conn:
            result = conn.execute(
                sql,
                {
                    "id": roles_id,
                    **data
                }
            ).rowcount
        return result > 0

    @staticmethod
    def delete(role_id):
        sql = text("""
            DELETE FROM "Roles"
            WHERE "RoleId" = :id
        """)
        with engine.begin() as conn:
            result = conn.execute(sql, {"id": role_id}).rowcount
        return result > 0

    @staticmethod
    def insertRole(data):
        sql = text("""
                INSERT INTO "Roles"
                ("Rolename", "Status")
                VALUES
                (:name, :status)
            """)
        with engine.begin() as conn:
            result = conn.execute(
                sql,
                {
                    **data
                }
            ).rowcount
        return result > 0