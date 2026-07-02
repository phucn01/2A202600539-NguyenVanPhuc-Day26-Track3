import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

import db
import init_db


@pytest.fixture(autouse=True)
def fresh_db(tmp_path, monkeypatch):
    monkeypatch.setattr(db, "DB_PATH", tmp_path / "test.db")
    init_db.init()


# ---------------------------------------------------------------------------
# search
# ---------------------------------------------------------------------------

def test_search_returns_all_students():
    rows = db.search("students")
    assert len(rows) == 5


def test_search_filter_by_cohort():
    rows = db.search("students", {"cohort": "A1"})
    assert len(rows) == 3
    assert all(r["cohort"] == "A1" for r in rows)


def test_search_limit():
    rows = db.search("enrollments", limit=3)
    assert len(rows) == 3


def test_search_unknown_table():
    with pytest.raises(ValueError, match="Unknown table"):
        db.search("hackers")


def test_search_unknown_column():
    with pytest.raises(ValueError, match="Unknown column"):
        db.search("students", {"password": "secret"})


# ---------------------------------------------------------------------------
# insert
# ---------------------------------------------------------------------------

def test_insert_student():
    result = db.insert("students", {
        "name": "New Student", "cohort": "B1", "email": "new@school.edu"
    })
    assert "inserted_id" in result
    rows = db.search("students", {"email": "new@school.edu"})
    assert len(rows) == 1
    assert rows[0]["name"] == "New Student"


def test_insert_course():
    result = db.insert("courses", {"name": "DevOps", "description": "CI/CD and containers"})
    assert result["table"] == "courses"
    rows = db.search("courses", {"name": "DevOps"})
    assert len(rows) == 1


def test_insert_empty_raises():
    with pytest.raises(ValueError, match="empty"):
        db.insert("students", {})


def test_insert_unknown_column_raises():
    with pytest.raises(ValueError, match="Unknown column"):
        db.insert("students", {"name": "X", "cohort": "A1", "email": "x@y.com", "admin": True})


def test_insert_unknown_table_raises():
    with pytest.raises(ValueError, match="Unknown table"):
        db.insert("admins", {"name": "hacker"})


# ---------------------------------------------------------------------------
# aggregate
# ---------------------------------------------------------------------------

def test_count_students():
    result = db.aggregate("students", "count", "id")
    assert result[0]["result"] == 5


def test_avg_score():
    result = db.aggregate("enrollments", "avg", "score")
    assert result[0]["result"] is not None
    assert 0 < result[0]["result"] < 100


def test_avg_score_group_by_course():
    result = db.aggregate("enrollments", "avg", "score", group_by="course_id")
    assert len(result) == 3
    assert all("course_id" in r and "result" in r for r in result)


def test_min_score():
    result = db.aggregate("enrollments", "min", "score")
    assert result[0]["result"] == 70.0


def test_max_score():
    result = db.aggregate("enrollments", "max", "score")
    assert result[0]["result"] == 95.0


def test_aggregate_bad_function():
    with pytest.raises(ValueError, match="Unsupported aggregate"):
        db.aggregate("students", "drop", "id")


def test_aggregate_unknown_table():
    with pytest.raises(ValueError, match="Unknown table"):
        db.aggregate("hackers", "count", "id")


def test_aggregate_unknown_column():
    with pytest.raises(ValueError, match="Unknown column"):
        db.aggregate("students", "count", "password")


def test_aggregate_unknown_group_by_column():
    with pytest.raises(ValueError, match="Unknown column"):
        db.aggregate("students", "count", "id", group_by="secret")


# ---------------------------------------------------------------------------
# schema resources
# ---------------------------------------------------------------------------

def test_full_schema_contains_all_tables():
    schema = db.get_full_schema()
    assert set(schema.keys()) == {"students", "courses", "enrollments"}


def test_full_schema_students_columns():
    schema = db.get_full_schema()
    names = [c["name"] for c in schema["students"]]
    assert "id" in names
    assert "name" in names
    assert "cohort" in names
    assert "email" in names


def test_table_schema_students():
    cols = db.get_table_schema("students")
    names = [c["name"] for c in cols]
    assert names == ["id", "name", "cohort", "email"]


def test_table_schema_enrollments():
    cols = db.get_table_schema("enrollments")
    names = [c["name"] for c in cols]
    assert "score" in names
    assert "student_id" in names


def test_table_schema_unknown_raises():
    with pytest.raises(ValueError, match="Unknown table"):
        db.get_table_schema("secrets")
