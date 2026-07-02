"""Smoke-test: exercises all tools and resources without starting a real MCP transport."""

import json
import sys
import time
import traceback

import init_db
import db


def run(label: str, fn) -> bool:
    try:
        result = fn()
        preview = json.dumps(result, ensure_ascii=False)[:200]
        print(f"[OK]   {label}")
        print(f"       {preview}\n")
        return True
    except Exception:
        print(f"[FAIL] {label}")
        traceback.print_exc()
        print()
        return False


def expect_error(fn) -> str:
    try:
        fn()
        raise AssertionError("Expected ValueError but none was raised")
    except ValueError as exc:
        return f"Caught expected error: {exc}"


def main():
    print("=" * 60)
    print("Initializing database")
    print("=" * 60)
    init_db.init()
    print()

    checks = []

    print("--- search ---")
    checks.append(run("search students in cohort A1",
        lambda: db.search("students", {"cohort": "A1"})))
    checks.append(run("search all courses",
        lambda: db.search("courses")))
    checks.append(run("search enrollments with limit 3",
        lambda: db.search("enrollments", limit=3)))

    print("--- insert ---")
    unique_email = f"test_{int(time.time())}@school.edu"
    checks.append(run("insert new student",
        lambda: db.insert("students", {
            "name": "Test User", "cohort": "A3", "email": unique_email
        })))

    print("--- aggregate ---")
    checks.append(run("count all students",
        lambda: db.aggregate("students", "count", "id")))
    checks.append(run("avg score across all enrollments",
        lambda: db.aggregate("enrollments", "avg", "score")))
    checks.append(run("avg score grouped by course_id",
        lambda: db.aggregate("enrollments", "avg", "score", group_by="course_id")))

    print("--- resources ---")
    checks.append(run("full database schema",
        lambda: db.get_full_schema()))
    checks.append(run("schema for table: students",
        lambda: db.get_table_schema("students")))
    checks.append(run("schema for table: enrollments",
        lambda: db.get_table_schema("enrollments")))

    print("--- validation errors (all expected to fail) ---")
    checks.append(run("reject unknown table",
        lambda: expect_error(lambda: db.search("hackers"))))
    checks.append(run("reject unknown column in filter",
        lambda: expect_error(lambda: db.search("students", {"password": "x"}))))
    checks.append(run("reject empty insert",
        lambda: expect_error(lambda: db.insert("students", {}))))
    checks.append(run("reject unknown column in insert",
        lambda: expect_error(lambda: db.insert("students", {
            "name": "X", "cohort": "A1", "email": "x@y.com", "admin": True
        }))))
    checks.append(run("reject bad aggregate function",
        lambda: expect_error(lambda: db.aggregate("students", "drop", "id"))))
    checks.append(run("reject schema for unknown table",
        lambda: expect_error(lambda: db.get_table_schema("secrets"))))

    passed = sum(checks)
    total = len(checks)
    print("=" * 60)
    print(f"Result: {passed}/{total} checks passed")
    print("=" * 60)
    sys.exit(0 if passed == total else 1)


if __name__ == "__main__":
    main()
