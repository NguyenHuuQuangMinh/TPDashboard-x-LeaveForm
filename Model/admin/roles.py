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

    @staticmethod
    def get_role_permissions(role_id):

        sql = """
            SELECT route_id
            FROM role_route_permissions
            WHERE role_id = :role_id
            AND can_view = true
        """
        with engine.connect() as conn:
            rows = conn.execute(
                text(sql),
                {"role_id": role_id}
            ).fetchall()

        return {r.route_id for r in rows}

    @staticmethod
    def get_all_routes_permissions():

        sql = """
            SELECT
                id,
                name,
                window_type
            FROM system_routes
            ORDER BY window_type, name
        """
        with engine.connect() as conn:

            results = conn.execute(
                text(sql)
            ).mappings().all()

        admin_routes = []
        user_routes = []

        for row in results:

            if (row["window_type"] or "").lower() == "admin":
                admin_routes.append(row)

            else:
                user_routes.append(row)

        return {
            "admin_routes": admin_routes,
            "user_routes": user_routes
        }

    @staticmethod
    def save_role_permissions(
            role_id,
            route_ids
    ):
        try:

            sql_turnoff_role = """
                UPDATE role_route_permissions
                SET can_view = false
                WHERE role_id = :role_id
            """

            sql_update_insert_per = """
                INSERT INTO role_route_permissions
                (
                    role_id,
                    route_id,
                    can_view
                )
                VALUES
                (
                    :role_id,
                    :route_id,
                    true
                )
                ON CONFLICT
                (
                    role_id,
                    route_id
                )
                DO UPDATE
                SET can_view = true
            """

            route_ids = [int(x) for x in route_ids]

            affected_rows = 0

            with engine.begin() as conn:

                result = conn.execute(
                    text(sql_turnoff_role),
                    {
                        "role_id": role_id
                    }
                )

                affected_rows += result.rowcount

                for route_id in route_ids:
                    result = conn.execute(
                        text(sql_update_insert_per),
                        {
                            "role_id": role_id,
                            "route_id": route_id
                        }
                    )

                    affected_rows += result.rowcount

            return {
                "ok": True,
                "affected_rows": affected_rows
            }

        except Exception as ex:

            return {
                "ok": False,
                "error": str(ex)
            }