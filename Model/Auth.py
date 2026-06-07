from sqlalchemy import text
from config import engine

class AuthModel:
    @staticmethod
    def authenticate(username):
        query = text("""SELECT u."Id"       AS id,
                            u."Username" AS username,
                            u."RoleId"   AS role_id,
                            u."DepartmentId" AS department_id,
                            u."Online"   AS online,
                            u."Status"   AS status,
                            u."Job_title" AS job_title,
                            r."Status"   AS role_status,
                            u."PasswordHash" AS password_hash
                     FROM "Users" u
                              JOIN "Roles" r ON u."RoleId" = r."RoleId"
                     WHERE LOWER(u."Username") = LOWER(:username)""")

        with engine.connect() as conn:
            result = conn.execute(query, {"username": username}).fetchone()
        return result
