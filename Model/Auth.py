from sqlalchemy import text
from config import get_postgres_engine

class AuthModel:
    @staticmethod
    def authenticate(username, password):
        engine = get_postgres_engine()
        query = text("""SELECT u."Id"       AS id,
                            u."Username" AS username,
                            u."RoleId"   AS role_id,
                            u."Online"   AS online,
                            u."Status"   AS status,
                            u."Job_title" AS job_title,
                            r."Status"   AS role_status
                     FROM "Users" u
                              JOIN "Roles" r ON u."RoleId" = r."RoleId"
                     WHERE LOWER(u."Username") = LOWER(:username)
                       AND u."PasswordHash" = :password""")

        with engine.connect() as conn:
            result = conn.execute(query, {"username": username, "password": password}).fetchone()
        return result
