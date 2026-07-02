import json
from typing import Optional

from fastmcp import FastMCP

import db
import init_db

mcp = FastMCP("sqlite-lab")

# Ensure DB exists on startup
init_db.init()


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------

@mcp.tool()
def search(
    table: str,
    filters: Optional[dict] = None,
    order_by: Optional[str] = None,
    order_dir: str = "asc",
    limit: int = 100,
    offset: int = 0,
) -> list[dict]:
    """Search rows in a database table with optional filters, ordering, and pagination.

    Args:
        table: Table name — one of students, courses, enrollments.
        filters: Optional dict of {column: value} pairs (equality only).
        order_by: Optional column name to sort results by.
        order_dir: Sort direction — "asc" (default) or "desc".
        limit: Maximum number of rows to return (default 100, max 500).
        offset: Number of rows to skip for pagination (default 0).
    """
    return db.search(table, filters, order_by, order_dir, limit, offset)


@mcp.tool()
def insert(table: str, data: dict) -> dict:
    """Insert a new row into a database table.

    Args:
        table: Table name — one of students, courses, enrollments.
        data: Dict of {column: value} for the new row (id is auto-assigned).
    """
    return db.insert(table, data)


@mcp.tool()
def aggregate(
    table: str,
    function: str,
    column: str,
    group_by: Optional[str] = None,
) -> list[dict]:
    """Compute an aggregate statistic over a table column.

    Args:
        table: Table name — one of students, courses, enrollments.
        function: Aggregate function — one of count, sum, avg, min, max.
        column: Column to apply the function to.
        group_by: Optional column to group results by.
    """
    return db.aggregate(table, function, column, group_by)


# ---------------------------------------------------------------------------
# Resources
# ---------------------------------------------------------------------------

@mcp.resource("schema://database")
def full_schema() -> str:
    """Full schema for all tables in the database."""
    return json.dumps(db.get_full_schema(), indent=2)


@mcp.resource("schema://table/{table_name}")
def table_schema(table_name: str) -> str:
    """Schema for a single named table."""
    return json.dumps(db.get_table_schema(table_name), indent=2)


# ---------------------------------------------------------------------------

if __name__ == "__main__":
    mcp.run()
