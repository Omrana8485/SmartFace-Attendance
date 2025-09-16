# logic/database.py
############### IMPORTS ###############
import sqlite3
import os

# Create data directory if it doesn't exist
if not os.path.exists("data"):
    os.makedirs("data")

# Connect to (or create) the SQLite database
connect = sqlite3.connect("data/facetrack.db")
cursor = connect.cursor()

# Create a table to store student information
cursor.execute("""
    CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        roll TEXT UNIQUE NOT NULL,
        department TEXT,
        email TEXT,
        phone TEXT,
        photo_path TEXT
    );
""")

# Drop and recreate table if schema is different
cursor.execute("DROP TABLE IF EXISTS students")
cursor.execute("""
    CREATE TABLE students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        roll TEXT UNIQUE NOT NULL,
        department TEXT,
        email TEXT,
        phone TEXT,
        photo_path TEXT
    );
""")

# Drop and recreate attendance table
cursor.execute("DROP TABLE IF EXISTS attendance")
cursor.execute("""
    CREATE TABLE attendance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        status TEXT CHECK(status IN ('Present', 'Absent')),
        FOREIGN KEY(student_id) REFERENCES students(id)
    );
""")

# Save changes and close the connection
connect.commit()
connect.close()

print("Database and tables created successfully.")
