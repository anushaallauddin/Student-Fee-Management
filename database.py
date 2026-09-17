import sqlite3

def create_database():

    conn = sqlite3.connect("fees.db")
    cursor = conn.cursor()

    # Students table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            subject TEXT,
            monthly_fee REAL
        )
    """)

    # Payments table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER,
            month TEXT,
            year INTEGER,
            amount REAL,
            status TEXT,
            payment_date TEXT,
            FOREIGN KEY (student_id) REFERENCES students(id)
        )
    """)

    # Check whether year column already exists
    cursor.execute("PRAGMA table_info(payments)")
    columns = [column[1] for column in cursor.fetchall()]

    if "year" not in columns:
        cursor.execute(
            "ALTER TABLE payments ADD COLUMN year INTEGER"
        )

    conn.commit()
    conn.close()
