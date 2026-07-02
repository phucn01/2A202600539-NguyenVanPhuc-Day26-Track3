import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "school.db"

ALLOWED_TABLES = {"students", "courses", "enrollments"}

ALLOWED_COLUMNS = {
    "students": {"id", "name", "cohort", "email"},
    "courses": {"id", "name", "description"},
    "enrollments": {"id", "student_id", "course_id", "score"},
}

AGGREGATE_FUNCTIONS = {"count", "sum", "avg", "min", "max"}


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def validate_table(table: str):
    if table not in ALLOWED_TABLES:
        raise ValueError(f"Unknown table '{table}'. Allowed: {sorted(ALLOWED_TABLES)}")


def validate_column(table: str, column: str):
    if column not in ALLOWED_COLUMNS[table]:
        raise ValueError(
            f"Unknown column '{column}' in table '{table}'. "
            f"Allowed: {sorted(ALLOWED_COLUMNS[table])}"
        )


def search(
    table: str,
    filters: dict | None = None,
    order_by: str | None = None,
    order_dir: str = "asc",
    limit: int = 100,
    offset: int = 0,
) -> list[dict]:
    validate_table(table)
    query = f"SELECT * FROM {table}"
    params: list = []

    if filters:
        conditions = []
        for col, val in filters.items():
            validate_column(table, col)
            conditions.append(f"{col} = ?")
            params.append(val)
        query += " WHERE " + " AND ".join(conditions)

    if order_by:
        validate_column(table, order_by)
        direction = "DESC" if order_dir.strip().lower() == "desc" else "ASC"
        query += f" ORDER BY {order_by} {direction}"

    query += f" LIMIT {min(limit, 500)} OFFSET {max(offset, 0)}"

    with get_connection() as conn:
        rows = conn.execute(query, params).fetchall()
        return [dict(row) for row in rows]


def insert(table: str, data: dict) -> dict:
    validate_table(table)
    if not data:
        raise ValueError("Insert data cannot be empty.")

    for col in data:
        validate_column(table, col)

    columns = ", ".join(data.keys())
    placeholders = ", ".join("?" for _ in data)
    query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"

    with get_connection() as conn:
        cursor = conn.execute(query, list(data.values()))
        conn.commit()
        return {"inserted_id": cursor.lastrowid, "table": table}


def aggregate(
    table: str,
    function: str,
    column: str,
    group_by: str | None = None,
) -> list[dict]:
    validate_table(table)
    func = function.lower()
    if func not in AGGREGATE_FUNCTIONS:
        raise ValueError(
            f"Unsupported aggregate function '{function}'. Allowed: {sorted(AGGREGATE_FUNCTIONS)}"
        )
    validate_column(table, column)

    if group_by:
        validate_column(table, group_by)
        query = (
            f"SELECT {group_by}, {func}({column}) AS result "
            f"FROM {table} GROUP BY {group_by}"
        )
    else:
        query = f"SELECT {func}({column}) AS result FROM {table}"

    with get_connection() as conn:
        rows = conn.execute(query).fetchall()
        return [dict(row) for row in rows]


def get_full_schema() -> dict:
    with get_connection() as conn:
        tables = {}
        for table in sorted(ALLOWED_TABLES):
            cursor = conn.execute(f"PRAGMA table_info({table})")
            tables[table] = [
                {
                    "name": row["name"],
                    "type": row["type"],
                    "notnull": bool(row["notnull"]),
                    "pk": bool(row["pk"]),
                }
                for row in cursor.fetchall()
            ]
        return tables


def get_table_schema(table: str) -> list[dict]:
    validate_table(table)
    with get_connection() as conn:
        cursor = conn.execute(f"PRAGMA table_info({table})")
        return [
            {
                "name": row["name"],
                "type": row["type"],
                "notnull": bool(row["notnull"]),
                "pk": bool(row["pk"]),
            }
            for row in cursor.fetchall()
        ]
