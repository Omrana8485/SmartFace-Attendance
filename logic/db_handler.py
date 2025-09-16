# logic/db_ops.py
############### IMPORTS ###############
import sqlite3
from datetime import date

############## CONSTANTS ##############

DB_PATH = "data/facetrack.db"

############## FUNCTIONS ##############

# Function: add_student
# Purpose: Insert a new student's data into the students table in the database
def add_student(name, roll, department, email, phone, photo_path):
    try:
        # Connect to database
        connect = sqlite3.connect(DB_PATH)
        cursor = connect.cursor()

        # Insert student record
        cursor.execute("""
            INSERT INTO students (name, roll, department, email, phone, photo_path)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (name, roll, department, email, phone, photo_path))

        # Commit and close
        connect.commit()
        connect.close()

        return True, "Student added successfully."

    except sqlite3.IntegrityError as e:
        # Likely duplicate roll number
        return False, f"Integrity error: {e}"

    except Exception as e:
        return False, f"Error: {e}"

#######################################

# Function: get_all_students
# Purpose: Return a list of all students from the students table
def get_all_students():
    try:
        connect = sqlite3.connect(DB_PATH)
        cursor = connect.cursor()

        cursor.execute(
            "SELECT id, name, roll, department, email, phone, photo_path FROM students"
        )
        rows = cursor.fetchall()
        connect.close()

        students = []
        for r in rows:
            students.append(
                {
                    "id": r[0],
                    "name": r[1],
                    "roll": r[2],
                    "department": r[3],
                    "email": r[4],
                    "phone": r[5],
                    "photo_path": r[6],
                }
            )

        return True, students

    except Exception as e:
        return False, f"Error: {e}"

#######################################

# Function: get_student_by_roll
# Purpose: Fetch a single student record by roll number
def get_student_by_roll(roll):
    try:
        connect = sqlite3.connect(DB_PATH)
        cursor = connect.cursor()

        cursor.execute(
            "SELECT id, name, roll, department, email, phone, photo_path FROM students WHERE roll = ?",
            (roll,),
        )
        row = cursor.fetchone()
        connect.close()

        if not row:
            return False, "Student not found."

        student = {
            "id": row[0],
            "name": row[1],
            "roll": row[2],
            "department": row[3],
            "email": row[4],
            "phone": row[5],
            "photo_path": row[6],
        }
        return True, student

    except Exception as e:
        return False, f"Error: {e}"

#######################################

# Function: update_student
# Purpose: Update a student's details identified by roll number.
#          Only fields provided (not None) will be updated.
def update_student(roll, name = None, department = None, email = None, phone = None, photo_path = None):
    try:
        updates = []
        params = []

        if name is not None:
            updates.append("name = ?")
            params.append(name)
        if department is not None:
            updates.append("department = ?")
            params.append(department)
        if email is not None:
            updates.append("email = ?")
            params.append(email)
        if phone is not None:
            updates.append("phone = ?")
            params.append(phone)
        if photo_path is not None:
            updates.append("photo_path = ?")
            params.append(photo_path)

        if not updates:
            return False, "No fields to update."

        params.append(roll)  # WHERE roll = ?

        sql = "UPDATE students SET " + ", ".join(updates) + " WHERE roll = ?"

        connect = sqlite3.connect(DB_PATH)
        cursor = connect.cursor()
        cursor.execute(sql, tuple(params))
        connect.commit()
        changed = cursor.rowcount
        connect.close()

        if changed == 0:
            return False, "No student found with that roll number."
        return True, "Student updated successfully."

    except sqlite3.IntegrityError as e:
        return False, f"Integrity error: {e}"
    except Exception as e:
        return False, f"Error: {e}"

#######################################

# Function: delete_student
# Purpose: Delete a student by roll. Optionally remove their attendance too.
def delete_student(roll, delete_attendance = False):
    try:
        connect = sqlite3.connect(DB_PATH)
        cursor = connect.cursor()

        # find id
        cursor.execute("SELECT id FROM students WHERE roll = ?", (roll,))
        row = cursor.fetchone()
        if not row:
            connect.close()
            return False, "Student not found."

        student_id = row[0]

        if delete_attendance:
            cursor.execute("DELETE FROM attendance WHERE student_id = ?", (student_id,))

        cursor.execute("DELETE FROM students WHERE id = ?", (student_id,))
        connect.commit()
        connect.close()
        return True, "Student deleted successfully."

    except Exception as e:
        return False, f"Error: {e}"

#######################################

# Function: mark_attendance
# Purpose: Mark attendance for a student (by roll) with status 'Present' or 'Absent'
def mark_attendance(roll, status = "Present"):
    try:
        if status not in ("Present", "Absent"):
            return False, "Invalid status. Use 'Present' or 'Absent'."

        connect = sqlite3.connect(DB_PATH)
        cursor = connect.cursor()

        # get student id
        cursor.execute("SELECT id FROM students WHERE roll = ?", (roll,))
        row = cursor.fetchone()
        if not row:
            connect.close()
            return False, "Student not found."

        student_id = row[0]

        # Check if attendance already marked today
        cursor.execute("""
            SELECT COUNT(*) FROM attendance 
            WHERE student_id = ? AND date(timestamp) = date('now') AND status = ?
        """, (student_id, status))
        
        existing_count = cursor.fetchone()[0]
        if existing_count > 0:
            connect.close()
            return False, f"Attendance already marked today for this student."

        cursor.execute(
            "INSERT INTO attendance (student_id, status) VALUES (?, ?)",
            (student_id, status),
        )
        connect.commit()
        connect.close()
        return True, "Attendance marked successfully."

    except Exception as e:
        return False, f"Error: {e}"

#######################################

# Function: clean_duplicate_attendance
# Purpose: Remove duplicate attendance records for the same student on the same day
def clean_duplicate_attendance():
    try:
        connect = sqlite3.connect(DB_PATH)
        cursor = connect.cursor()
        
        # Find and remove duplicate attendance records
        cursor.execute("""
            DELETE FROM attendance 
            WHERE id NOT IN (
                SELECT MIN(id) 
                FROM attendance 
                WHERE date(timestamp) = date('now')
                GROUP BY student_id, status
            ) AND date(timestamp) = date('now')
        """)
        
        deleted_count = cursor.rowcount
        connect.commit()
        connect.close()
        
        return True, f"Cleaned {deleted_count} duplicate attendance records."
        
    except Exception as e:
        return False, f"Error cleaning duplicates: {e}"

#######################################

# Function: get_attendance_by_date
# Purpose: Return attendance records for a specific date (YYYY-MM-DD). Defaults to today.
def get_attendance_by_date(target_date=None):
    try:
        if target_date is None:
            target_date = date.today().isoformat()  # 'YYYY-MM-DD'

        connect = sqlite3.connect(DB_PATH)
        cursor = connect.cursor()

        cursor.execute(
            """
            SELECT a.id, s.name, s.roll, s.department, a.timestamp, a.status
            FROM attendance a
            JOIN students s ON a.student_id = s.id
            WHERE date(a.timestamp) = ?
            ORDER BY a.timestamp DESC
            """,
            (target_date,),
        )
        rows = cursor.fetchall()
        connect.close()

        records = []
        for r in rows:
            records.append(
                {
                    "attendance_id": r[0],
                    "name": r[1],
                    "roll": r[2],
                    "department": r[3],
                    "timestamp": r[4],
                    "status": r[5],
                }
            )

        return True, records

    except Exception as e:
        return False, f"Error: {e}"

#######################################

# Function: get_attendance_by_student
# Purpose: Return attendance history for a student identified by roll
def get_attendance_by_student(roll):
    try:
        connect = sqlite3.connect(DB_PATH)
        cursor = connect.cursor()

        cursor.execute(
            """
            SELECT a.id, a.timestamp, a.status
            FROM attendance a
            JOIN students s ON a.student_id = s.id
            WHERE s.roll = ?
            ORDER BY a.timestamp DESC
            """,
            (roll,),
        )
        rows = cursor.fetchall()
        connect.close()

        history = []
        for r in rows:
            history.append({"attendance_id": r[0], "timestamp": r[1], "status": r[2]})

        return True, history

    except Exception as e:
        return False, f"Error: {e}"

#######################################

# Function: clear_all_data
# Purpose: Clear all data from the database and reset the project
def clear_all_data():
    try:
        connect = sqlite3.connect(DB_PATH)
        cursor = connect.cursor()
        
        # Clear all attendance records
        cursor.execute("DELETE FROM attendance")
        attendance_deleted = cursor.rowcount
        
        # Clear all student records
        cursor.execute("DELETE FROM students")
        students_deleted = cursor.rowcount
        
        # Reset auto-increment counters
        cursor.execute("DELETE FROM sqlite_sequence WHERE name = 'students'")
        cursor.execute("DELETE FROM sqlite_sequence WHERE name = 'attendance'")
        
        connect.commit()
        connect.close()
        
        return True, f"Cleared {students_deleted} students and {attendance_deleted} attendance records."
        
    except Exception as e:
        return False, f"Error clearing data: {e}"

#######################################

# Function: reset_project_structure
# Purpose: Reset the project to initial state by recreating database and folders
def reset_project_structure():
    try:
        import os
        
        # Recreate database with fresh schema
        from logic import database
        
        # Recreate necessary folders
        folders = ["data", "data/images", "data/attendance", "dataset", "model"]
        for folder in folders:
            if not os.path.exists(folder):
                os.makedirs(folder, exist_ok=True)
        
        return True, "Project structure reset successfully."
        
    except Exception as e:
        return False, f"Error resetting project: {e}"

    