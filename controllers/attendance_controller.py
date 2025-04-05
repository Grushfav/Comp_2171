from typing import List, Dict, Optional
from datetime import datetime, time, timedelta
from models.student import Student
from models.course import Course
from models.attendance import Attendance
from db.db_manager import DBManager
import sqlite3

class AttendanceController:
    def __init__(self, db_manager: DBManager):
        self._db_manager = db_manager
        self._current_user = None
        self._expected_time = time(9, 0)  # Default expected time: 9:00 AM

    # Authentication Methods
    def login(self, username: str, password: str) -> Optional[Dict]:
        try:
            with self._db_manager.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT u.*, s.student_id, s.contact_number, s.emergency_contact
                    FROM users u 
                    LEFT JOIN students s ON u.user_id = s.user_id 
                    WHERE u.username = ? AND u.password = ?
                ''', (username, password))
                
                user = cursor.fetchone()
                if user:
                    user_dict = dict(user)
                    self._current_user = user_dict
                    
                    if user_dict['role'].lower() == 'student':
                        if user_dict.get('student_id') is None:
                            print("Error: No student record found for this user!")
                            return None
                            
                        # Get today's attendance status
                        attendance = self.get_daily_attendance_status(user_dict['student_id'])
                        
                        welcome_msg = f"\nWelcome, {user_dict['first_name']} {user_dict['last_name']}!"
                        welcome_msg += f"\nStudent ID: {user_dict['student_id']}"
                        
                        if attendance['status'] == 'late':
                            welcome_msg += f"\nNote: You were late today (Arrived at {attendance['sign_in_time']})"
                        elif attendance['status'] == 'absent':
                            welcome_msg += "\nNote: You haven't signed in today yet"
                        elif attendance['status'] == 'present':
                            welcome_msg += f"\nYou're on time today! (Arrived at {attendance['sign_in_time']})"
                        
                        print(welcome_msg)
                        
                    return user_dict
                return None
                
        except Exception as e:
            print(f"Error during login: {e}")
            return None

    def signup(self, username: str, password: str, first_name: str, 
               last_name: str, email: str, role: str, 
               contact_number: str = None, emergency_contact: str = None) -> bool:
        try:
            with self._db_manager.get_connection() as conn:
                cursor = conn.cursor()
                
                # Check if username exists
                cursor.execute('SELECT user_id FROM users WHERE username = ?', (username,))
                if cursor.fetchone():
                    print("Username already exists!")
                    return False

                # Insert user
                cursor.execute('''
                    INSERT INTO users (username, password, first_name, last_name, email, role)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (username, password, first_name, last_name, email, role))
                
                user_id = cursor.lastrowid

                if role.lower() == 'student':
                    cursor.execute('''
                        INSERT INTO students (user_id, contact_number, emergency_contact)
                        VALUES (?, ?, ?)
                    ''', (user_id, contact_number, emergency_contact))

                conn.commit()
                return True
        except Exception as e:
            print(f"Error during signup: {e}")
            return False

    # Course Management Methods
    def create_course(self, course_name: str, description: str, 
                     start_date: str, end_date: str, 
                     location: str, max_capacity: int) -> bool:
        if not self.is_admin():
            print("Unauthorized access!")
            return False
            
        try:
            with self._db_manager.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO courses (course_name, description, start_date, 
                                       end_date, location, max_capacity)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (course_name, description, start_date, end_date, 
                      location, max_capacity))
                conn.commit()
                return True
        except Exception as e:
            print(f"Error creating course: {e}")
            return False

    def list_courses(self) -> List[Dict]:
        try:
            with self._db_manager.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM courses')
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            print(f"Error listing courses: {e}")
            return []

    # Attendance Management Methods
    def set_expected_time(self, new_time: time) -> bool:
        if not self.is_admin():
            return True
        self._expected_time = new_time
        return True

    def enroll_student_in_course(self, student_id: int, course_id: int) -> bool:
        try:
            with self._db_manager.get_connection() as conn:
                cursor = conn.cursor()
                
                # Check if course exists and has space
                cursor.execute('''
                    SELECT max_capacity, 
                           (SELECT COUNT(*) FROM student_courses 
                            WHERE course_id = ?) as current_enrollment
                    FROM courses WHERE course_id = ?
                ''', (course_id, course_id))
                
                result = cursor.fetchone()
                if not result:
                    print("Course not found!")
                    return False
                
                max_capacity = result['max_capacity']
                current_enrollment = result['current_enrollment']
                
                if current_enrollment >= max_capacity:
                    print("Course is full!")
                    return False
                
                # Check if student is already enrolled
                cursor.execute('''
                    SELECT 1 FROM student_courses 
                    WHERE student_id = ? AND course_id = ?
                ''', (student_id, course_id))
                
                if cursor.fetchone():
                    print("Student already enrolled in this course!")
                    return False
                
                # Enroll student
                cursor.execute('''
                    INSERT INTO student_courses (student_id, course_id)
                    VALUES (?, ?)
                ''', (student_id, course_id))
                
                conn.commit()
                return True
                
        except Exception as e:
            print(f"Error enrolling student: {e}")
            return False

    def drop_course(self, student_id: int, course_id: int) -> bool:
        try:
            with self._db_manager.get_connection() as conn:
                cursor = conn.cursor()
                
                # Check if student is enrolled
                cursor.execute('''
                    DELETE FROM student_courses 
                    WHERE student_id = ? AND course_id = ?
                ''', (student_id, course_id))
                
                if cursor.rowcount > 0:
                    conn.commit()
                    return True
                else:
                    print("Student not enrolled in this course!")
                    return False
                
        except Exception as e:
            print(f"Error dropping course: {e}")
            return False

    def set_daily_attendance_time(self, course_id: int, expected_time: time) -> bool:
        if not self.is_admin():
            print("Only admins can set attendance time!")
            return True
            
        try:
            with self._db_manager.get_connection() as conn:
                cursor = conn.cursor()
                
                # First check if course exists
                cursor.execute('SELECT 1 FROM courses WHERE course_id = ?', (course_id,))
                if not cursor.fetchone():
                    print("Course not found!")
                    return False
                
                # Update attendance time for course
                cursor.execute('''
                    UPDATE courses 
                    SET expected_attendance_time = ?
                    WHERE course_id = ?
                ''', (expected_time.strftime('%H:%M'), course_id))
                
                if cursor.rowcount > 0:
                    conn.commit()
                    return True
                else:
                    print("No changes made to course attendance time")
                    return False
                
        except Exception as e:
            print(f"Error setting attendance time: {e}")
            return False

    def record_attendance(self, student_id: int) -> bool:
        try:
            with self._db_manager.get_connection() as conn:
                cursor = conn.cursor()
                now = datetime.now()
                today = now.date()
                
                # Check if already recorded attendance today
                cursor.execute('''
                    SELECT 1 FROM attendance 
                    WHERE student_id = ? AND date(attendance_date) = ?
                ''', (student_id, today))
                
                if cursor.fetchone():
                    print("\nAttendance already recorded for today!")
                    return False
                
                # Get the expected arrival time (school-wide setting)
                expected_time = self._expected_time
                current_time = now.time()
                
                # Record attendance with late status if after expected time
                is_late = current_time > expected_time
                status = 'late' if is_late else 'present'
                
                try:
                    cursor.execute('''
                        INSERT INTO attendance (
                            student_id, attendance_date, 
                            sign_in_time, status, is_late
                        )
                        VALUES (?, ?, ?, ?, ?)
                    ''', (
                        student_id, 
                        today.strftime('%Y-%m-%d'), 
                        current_time.strftime('%H:%M'),
                        status,
                        1 if is_late else 0
                    ))
                    
                    conn.commit()
                    
                    if is_late:
                        print(f"\nMarked as late (Expected: {expected_time.strftime('%H:%M')}, Arrived: {current_time.strftime('%H:%M')})")
                    else:
                        print(f"\nAttendance recorded - On time! ({current_time.strftime('%H:%M')})")
                        
                    return True
                    
                except sqlite3.Error as e:
                    print(f"\nDatabase error: {e}")
                    return False
                    
        except Exception as e:
            print(f"\nError recording attendance: {e}")
            return False

    def generate_late_report(self, start_date: str, end_date: str) -> List[Dict]:
        if not self.is_admin():
            return []
            
        try:
            with self._db_manager.get_connection() as conn:
                cursor = conn.cursor()
                
                # Get all students and their attendance status for the date range
                cursor.execute('''
                    WITH DateRange AS (
                        SELECT date(?) as start_date,
                               date(?) as end_date
                    ),
                    AllStudents AS (
                        SELECT s.student_id, u.first_name, u.last_name
                        FROM students s
                        JOIN users u ON s.user_id = u.user_id
                    )
                    SELECT 
                        s.student_id,
                        s.first_name,
                        s.last_name,
                        date(a.attendance_date) as attendance_date,
                        CASE 
                            WHEN a.attendance_id IS NULL THEN 'Absent'
                            WHEN a.is_late = 1 THEN 'Late'
                            ELSE a.status
                        END as status,
                        a.sign_in_time
                    FROM AllStudents s
                    CROSS JOIN (
                        SELECT date(date('now', 'start of day', '+' || t.i || ' days')) as date
                        FROM (
                            WITH RECURSIVE
                            cnt(i) AS (
                                SELECT 0
                                UNION ALL
                                SELECT i + 1 FROM cnt
                                LIMIT (julianday(?) - julianday(?) + 1)
                            )
                            SELECT i FROM cnt
                        ) t
                        WHERE date >= date(?) AND date <= date(?)
                    ) d
                    LEFT JOIN attendance a ON s.student_id = a.student_id 
                        AND date(a.attendance_date) = d.date
                    WHERE d.date <= date('now')
                    ORDER BY d.date DESC, s.last_name, s.first_name
                ''', (start_date, end_date, end_date, start_date, start_date, end_date))
                
                records = cursor.fetchall()
                return [dict(row) for row in records]
                
        except Exception as e:
            print(f"Error generating attendance report: {e}")
            return []

    # Utility Methods
    def get_current_user(self) -> Optional[Dict]:
        return self._current_user

    def is_admin(self) -> bool:
        return self._current_user and self._current_user['role'].lower() == 'admin'

    def logout(self) -> None:
        self._current_user = None

    def get_student_attendance(self, student_id: int) -> List[Dict]:
        try:
            with self._db_manager.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT a.*
                    FROM attendance a
                    WHERE a.student_id = ?
                    ORDER BY a.attendance_date DESC
                ''', (student_id,))
                
                records = cursor.fetchall()
                return [dict(row) for row in records]
        except Exception as e:
            print(f"Error getting attendance: {e}")
            return []

    def generate_course_report(self, course_id: int) -> Dict:
        try:
            with self._db_manager.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT 
                        COUNT(*) as total_sessions,
                        SUM(CASE WHEN status = 'present' THEN 1 ELSE 0 END) as present_count,
                        SUM(CASE WHEN is_late = 1 THEN 1 ELSE 0 END) as late_count
                    FROM attendance
                    WHERE course_id = ?
                ''', (course_id,))
                
                return dict(cursor.fetchone())
        except Exception as e:
            print(f"Error generating report: {e}")
            return {}

    def get_daily_attendance_status(self, student_id: int) -> Dict:
        """Get student's attendance status for today"""
        try:
            with self._db_manager.get_connection() as conn:
                cursor = conn.cursor()
                today = datetime.now().date()
                
                cursor.execute('''
                    SELECT a.*
                    FROM attendance a
                    WHERE a.student_id = ? AND date(a.attendance_date) = ?
                ''', (student_id, today))
                
                attendance = cursor.fetchone()
                if attendance:
                    return {
                        'status': attendance['status'],
                        'is_late': attendance['is_late'],
                        'sign_in_time': attendance['sign_in_time']
                    }
                return {'status': 'absent'}
                
        except Exception as e:
            print(f"Error getting daily attendance: {e}")
            return {'status': 'unknown'}

    def get_student_details(self, username: str) -> Dict:
        """Get student details including ID and name"""
        try:
            with self._db_manager.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT u.first_name, u.last_name, s.student_id
                    FROM users u
                    JOIN students s ON u.user_id = s.user_id
                    WHERE u.username = ?
                ''', (username,))
                
                student = cursor.fetchone()
                if student:
                    return dict(student)
                return None
                
        except Exception as e:
            print(f"Error getting student details: {e}")
            return None 