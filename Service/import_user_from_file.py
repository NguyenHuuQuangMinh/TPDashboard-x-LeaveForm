import pandas as pd

from sqlalchemy import text

from config import engine

from Service.security_code import generate_security

REQUIRED_COLUMNS = {
    "Username",
    "PasswordHash",
    "FullName"
}
def import_users_from_file(file_stream, filename):

    try:
        df = _read_import_file(file_stream, filename)
        _validate_columns(df)

    except Exception as e:
        return {"ok": False, "error": str(e)}

    result = {
        "inserted": 0,
        "updated": 0,
        "skipped": 0,
        "errors": []
    }

    for index, row in df.iterrows():
        row_num = index + 2

        try:
            with engine.begin() as conn:
                payload, row_id = _build_user_payload(row)
                payload["department_id"] = _get_department_id(conn, payload["department"])
                if row_id:
                    action = _upsert_by_id(conn, payload, row_id)
                else:
                    action = _upsert_by_username(conn, payload)

            result[action] += 1

        except Exception as e:
            result["skipped"] += 1
            result["errors"].append(f"Row {row_num}: {e}")

    _reset_user_sequence()

    return {"ok": True, **result}

def _read_import_file(file_stream, filename):
    if filename.endswith(".csv"):
        df = pd.read_csv(file_stream)
    else:
        df = pd.read_excel(file_stream)

    df.columns = df.columns.str.strip()
    return df

def _validate_columns(df):
    missing = REQUIRED_COLUMNS - set(df.columns)

    if missing:
        raise ValueError("Missing required columns: " + ", ".join(missing))

def _build_user_payload(row):

    username = str(row.get("Username") or "").strip()
    fullname = str(row.get("FullName") or "").strip()

    if not username or not fullname:
        raise ValueError("Username or FullName is empty")

    row_id = _int(row, "Id")

    return {
        "username": username,
        "password_hash": str(row.get("PasswordHash") or "").strip(),
        "full_name": fullname,
        "job_title": _val(row, "Job_title"),
        "img": _val(row, "Img"),
        "status": _int(row, "Status", 1),
        "online": _bool(row, "Online", False),
        "role_id": _int(row, "RoleId", 2),
        "working_location": _val(row, "working_location"),
        "joining_date": _date(row, "joining_date"),
        "year": _int(row, "year"),
        "department": _val(row, "department"),
        "report_to": _val(row, "report_to"),
        "to_email": _val(row, "to_email"),
        "cc_email": _val(row, "cc_email"),

        "security": _val(row, "Security") or generate_security(),

        "entitle_contract": _int(row, "entitle_contract", 0),
        "carry_over": _int(row, "carry_over", 0),
    }, row_id

def _upsert_by_id(conn, payload, row_id):

    exists = conn.execute(
        text('SELECT 1 FROM "Users" WHERE "Id" = :id'),
        {"id": row_id}
    ).fetchone()

    if exists:
        _update_user(conn, payload, "Id = :id", {"id": row_id})
        return "updated"

    _insert_user(conn, payload, include_id=True, row_id=row_id)
    _sync_leave_balance(conn, row_id, payload)
    return "inserted"

def _upsert_by_username(conn, payload):

    exists = conn.execute(
        text('SELECT "Id" FROM "Users" WHERE "Username" = :username'),
        {"username": payload["username"]}
    ).fetchone()

    if exists:
        _update_user(conn, payload, '"Username" = :username', payload)
        user_id = conn.execute(
            text('SELECT "Id" FROM "Users" WHERE "Username" = :username'),
            {"username": payload["username"]}
        ).scalar()

        _sync_leave_balance(conn, user_id, payload)
        return "updated"

    _insert_user(conn, payload, include_id=False)

    user_id = conn.execute(
        text('SELECT "Id" FROM "Users" WHERE "Username" = :username'),
        {"username": payload["username"]}
    ).scalar()

    _sync_leave_balance(conn, user_id, payload)

    return "inserted"

def _insert_user(conn, payload, include_id=False, row_id=None):

    columns = [
        '"Username"',
        '"PasswordHash"',
        '"FullName"',
        '"Job_title"',
        '"Img"',
        '"Status"',
        '"Online"',
        '"RoleId"',
        '"working_location"',
        '"joining_date"',
        '"year"',
        '"department"',
        '"report_to"',
        '"to_email"',
        '"cc_email"',
        '"Security"',
        '"DepartmentId"'
    ]

    values = [
        ":username",
        ":password_hash",
        ":full_name",
        ":job_title",
        ":img",
        ":status",
        ":online",
        ":role_id",
        ":working_location",
        ":joining_date",
        ":year",
        ":department",
        ":report_to",
        ":to_email",
        ":cc_email",
        ":security",
        ":department_id"
    ]

    if include_id:
        columns.insert(0, '"Id"')
        values.insert(0, ":id")
        payload = {**payload, "id": row_id}

    conn.execute(
        text(f"""
            INSERT INTO "Users"
            ({",".join(columns)})
            VALUES
            ({",".join(values)})
        """),
        payload
    )

def _update_user(conn, payload, condition, extra_params=None):

    params = payload.copy()
    if extra_params:
        params.update(extra_params)

    conn.execute(
        text(f"""
            UPDATE "Users"
            SET
                "Username" = :username,
                "PasswordHash" = :password_hash,
                "FullName" = :full_name,
                "Job_title" = :job_title,
                "Img" = :img,
                "Status" = :status,
                "Online" = :online,
                "RoleId" = :role_id,
                "working_location" = :working_location,
                "joining_date" = :joining_date,
                "year" = :year,
                "department" = :department,
                "report_to" = :report_to,
                "to_email" = :to_email,
                "cc_email" = :cc_email,
                "DepartmentId" = :department_id,
                "Security" = :security 
            WHERE {condition}
        """),
        params
    )

def _int(row, key, default=None):

    value = row.get(key)

    if pd.isna(value) or value == "":
        return default

    try:
        return int(value)
    except:
        return default

def _val(row, key):

    value = row.get(key)

    if pd.isna(value) or value is None:
        return None

    return str(value).strip()

def _bool(row, key, default=False):

    value = row.get(key)

    if pd.isna(value):
        return default

    if str(value).lower() in ["true", "1", "yes"]:
        return True

    if str(value).lower() in ["false", "0", "no"]:
        return False

    return default

def _date(row, key):

    value = row.get(key)

    if pd.isna(value) or not value:
        return None

    try:
        return pd.to_datetime(value).date()
    except:
        return None

def _reset_user_sequence():

    with engine.begin() as conn:

        conn.execute(
            text("""
                SELECT setval(
                    pg_get_serial_sequence(
                        '"Users"',
                        'Id'
                    ),
                    COALESCE(
                        (
                            SELECT MAX("Id")
                            FROM "Users"
                        ),
                        1
                    )
                )
            """)
        )

def _sync_leave_balance(conn, user_id, payload):

    year = payload.get("year")
    if not year:
        return

    entitle = payload.get("entitle_contract", 0)
    carry = payload.get("carry_over", 0)

    exists = conn.execute(text("""
        SELECT id
        FROM leave_requests
        WHERE user_id = :uid
          AND EXTRACT(YEAR FROM date_from) = :year
          AND type = 'annual'
        ORDER BY id DESC
        LIMIT 1
    """), {
        "uid": user_id,
        "year": year
    }).fetchone()

    # ─────────────────────────
    # UPDATE
    # ─────────────────────────
    if exists:

        conn.execute(text("""
            UPDATE leave_requests
            SET
                entitle_contract = :entitle,
                carry_over       = :carry,
                updated_at       = NOW()
            WHERE id = :id
        """), {
            "id": exists[0],
            "entitle": entitle,
            "carry": carry
        })

    # ─────────────────────────
    # INSERT
    # ─────────────────────────
    else:

        conn.execute(text("""
            INSERT INTO leave_requests (
                user_id,
                entitle_contract,
                carry_over,
                annual_leave,
                sick_leave,
                maternity_leave,
                pregnancy_leave,
                personal_leave,
                compensate_leave,
                unpaid_leave,
                date_from,
                date_to,
                status,
                type,
                created_at,
                updated_at
            )
            VALUES (
                :user_id,
                :entitle,
                :carry,
                0,0,0,0,0,0,0,
                make_date(:year,1,1),
                make_date(:year,12,31),
                'approved',
                'annual',
                NOW(),
                NOW()
            )
        """), {
            "user_id": user_id,
            "entitle": entitle,
            "carry": carry,
            "year": year
        })

def _get_department_id(conn, name):
    if not name:
        return None

    return conn.execute(text("""
        SELECT id
        FROM "Departments"
        WHERE name = :name
        LIMIT 1
    """), {"name": name}).scalar()