import sqlite3
from typing import List, Dict, Any, Optional
from contextlib import contextmanager

class DBManager:
    def __init__(self, db_path: str):
        self._db_path = db_path

    @contextmanager
    def get_connection(self):
        conn = sqlite3.connect(self._db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    def initialize_db(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Create Users table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    first_name TEXT NOT NULL,
                    last_name TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    role TEXT NOT NULL
                )
            ''')

            # Create Students table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS students (
                    student_id INTEGER PRIMARY KEY,
                    user_id INTEGER,
                    contact_number TEXT,
                    emergency_contact TEXT,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            ''')

            # Create Courses table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS courses (
                    course_id INTEGER PRIMARY KEY,
                    course_name TEXT NOT NULL,
                    description TEXT,
                    start_date TEXT NOT NULL,
                    end_date TEXT NOT NULL,
                    location TEXT,
                    max_capacity INTEGER
                )
            ''')

            # Create Attendance table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS attendance (
                    attendance_id INTEGER PRIMARY KEY,
                    student_id INTEGER,
                    course_id INTEGER,
                    attendance_date TEXT NOT NULL,
                    sign_in_time TEXT,
                    sign_out_time TEXT,
                    status TEXT,
                    is_late BOOLEAN,
                    FOREIGN KEY (student_id) REFERENCES students (student_id),
                    FOREIGN KEY (course_id) REFERENCES courses (course_id)
                )
            ''')

            conn.commit() 