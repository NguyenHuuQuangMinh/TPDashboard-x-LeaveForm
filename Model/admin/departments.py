from config import engine
from sqlalchemy import text
class Departments:
    @staticmethod
    def get_all_departments(name = None, status=None, page = 1, limit = 10):
        offset = (page-1)*limit

        where_clause = []
        params = {
            "limit": limit,
            "offset": offset
        }

        if name:
            where_clause.append('LOWER(name) LIKE LOWER(:name)')
            params["name"] = f"%{name}%"
        if status:
            where_clause.append('status = :status')
            params["status"] = status
        where_sql = ""
        if where_clause:
            where_sql = "WHERE " + " AND ".join(where_clause)

        count_sql = text(f"""
                SELECT COUNT(*)
                FROM "Departments"
                {where_sql}
            """)

        sql = text(f"""
                    SELECT
                        id,
                        name,
                        status
                    FROM "Departments"
                    {where_sql}
                    ORDER BY id
                    LIMIT :limit
                    OFFSET :offset
            """)

        with engine.connect() as conn:
            total = conn.execute(count_sql, params).scalar()

            results = conn.execute(sql,params).mappings().all()

        return results, total

    @staticmethod
    def get_by_id(dpm_id):
        sql = text("""
            SELECT
                id,
                name,
                status
            FROM "Departments"
            WHERE id = :id
        """)
        with engine.connect() as conn:
            result = conn.execute(sql, {"id": dpm_id}).mappings().first()
        return result

    @staticmethod
    def update_by_id(dpm_id, data):
        sql = text("""
            UPDATE "Departments"
            SET 
                name = :name,
                status = :status
            WHERE id = :id
        """)
        with engine.begin() as conn:
            result = conn.execute(
                sql,
                {
                    "id": dpm_id,
                    **data
                }
            ).rowcount
        return result > 0

    @staticmethod
    def delete(dpm_id):
        sql = text("""
            DELETE FROM "Departments"
            WHERE id = :id
        """)
        with engine.begin() as conn:
            result = conn.execute(sql, {"id": dpm_id}).rowcount
        return result > 0

    @staticmethod
    def insertDpm(data):
        sql = text("""
                INSERT INTO "Departments"
                (name, status)
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