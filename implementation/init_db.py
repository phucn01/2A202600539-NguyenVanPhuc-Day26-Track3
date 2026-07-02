import sqlite3
import db


def init():
    with sqlite3.connect(str(db.DB_PATH)) as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS students (
                id      INTEGER PRIMARY KEY AUTOINCREMENT,
                name    TEXT NOT NULL,
                cohort  TEXT NOT NULL,
                email   TEXT UNIQUE NOT NULL
            );

            CREATE TABLE IF NOT EXISTS courses (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                name        TEXT NOT NULL,
                description TEXT
            );

            CREATE TABLE IF NOT EXISTS enrollments (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id  INTEGER NOT NULL REFERENCES students(id),
                course_id   INTEGER NOT NULL REFERENCES courses(id),
                score       REAL
            );
        """)

        conn.executemany(
            "INSERT OR IGNORE INTO students (name, cohort, email) VALUES (?, ?, ?)",
            [
                ("Alice Nguyen", "A1", "alice@school.edu"),
                ("Bob Tran",     "A1", "bob@school.edu"),
                ("Carol Le",     "A2", "carol@school.edu"),
                ("David Pham",   "A2", "david@school.edu"),
                ("Eva Hoang",    "A1", "eva@school.edu"),
            ],
        )

        conn.executemany(
            "INSERT OR IGNORE INTO courses (name, description) VALUES (?, ?)",
            [
                ("Python Basics",    "Introduction to Python programming"),
                ("Data Structures",  "Algorithms and data structures"),
                ("Machine Learning", "Intro to ML with scikit-learn"),
            ],
        )

        conn.executemany(
            "INSERT OR IGNORE INTO enrollments (student_id, course_id, score) VALUES (?, ?, ?)",
            [
                (1, 1, 88.5),
                (1, 2, 92.0),
                (2, 1, 75.0),
                (3, 2, 85.5),
                (3, 3, 90.0),
                (4, 1, 70.0),
                (4, 3, 95.0),
                (5, 2, 88.0),
                (5, 3, 82.0),
            ],
        )
        conn.commit()

    print(f"Database initialized at {db.DB_PATH}")


if __name__ == "__main__":
    init()
