from config import engine
from sqlalchemy import text
class Routes:
    @staticmethod
    def get_all_routes(name = None, window_type= None, page = 1, limit = 10):
        offset = (page-1)*limit

        where_clause = []
        params = {
            "limit": limit,
            "offset": offset
        }

        if name:
            where_clause.append("LOWER(name) LIKE LOWER(:name)")
            params["name"] = f"%{name}%"

        if window_type:
            where_clause.append("window_type = :window_type")
            params["window_type"] = window_type

        where_sql = ""
        if where_clause:
            where_sql = "WHERE " + " AND ".join(where_clause)

        count_sql = text(f"""
                SELECT COUNT(*)
                FROM system_routes
                {where_sql}
            """)

        sql = text(f"""
                    SELECT
                        id,
                        name,
                        path,
                        icon,
                        window_type,
                        is_active
                    FROM system_routes
                    {where_sql}
                    ORDER BY id
                    LIMIT :limit
                    OFFSET :offset
            """)

        with engine.connect() as conn:
            total = conn.execute(count_sql, params).scalar()

            routes = conn.execute(sql,params).mappings().all()

        return routes, total

    @staticmethod
    def get_sidebar_routes():
        sql = text("""
            SELECT
                id,
                name,
                path,
                icon,
                parent_id,
                sort_order,
                window_type
            FROM system_routes
            WHERE is_active = true
            ORDER BY parent_id, sort_order
        """)

        with engine.connect() as conn:
            routes = conn.execute(sql).mappings().all()
        return routes

    @staticmethod
    def get_by_id(route_id):
        sql = text("""
            SELECT id,
                name,
                path,
                icon,
                parent_id,
                sort_order,
                window_type,
                is_active
            FROM system_routes
            WHERE id = :id
        """)
        with engine.connect() as conn:
            result = conn.execute(sql, {"id": route_id}).mappings().first()
        return result

    @staticmethod
    def update_by_id(route_id, data):
        sql = text("""
            UPDATE system_routes
            SET 
                name = :name,
                path = :path,
                icon = :icon,
                window_type = :window_type,
                sort_order = :sort_order,
                is_active = :is_active,
                parent_id = :parent_id
            WHERE id = :id
        """)
        with engine.begin() as conn:
            result = conn.execute(
                sql,
                {
                    "id": route_id,
                    **data
                }
            ).rowcount
        return result > 0

    @staticmethod
    def delete(route_id):
        sql = text("""
            DELETE FROM system_routes
            WHERE id = :id
        """)
        with engine.begin() as conn:
            result = conn.execute(sql, {"id": route_id}).rowcount
        return result > 0

    @staticmethod
    def insertRoutes(data):
        sql = text("""
                INSERT INTO system_routes
                (name, path, icon, window_type, sort_order, is_active, parent_id)
                VALUES
                (:name, :path, :icon, :window_type, :sort_order, :is_active, :parent_id)
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
    def get_parent_routes():
        sql = text("""
            SELECT id, name, window_type
            FROM system_routes
            WHERE parent_id = 0
            ORDER BY name
        """)

        with engine.connect() as conn:
            return conn.execute(sql).mappings().all()