from typing import List, Dict, Optional
from datetime import datetime
from models.student import Student
from models.course import Course
from models.attendance import Attendance
from db.db_manager import DBManager

class AttendanceController:
    def __init__(self, db_manager: DBManager):
        self._db_manager = db_manager

    def record_attendance(self, student_id: int, course_id: int) -> bool:
        try:
            with self._db_manager.get_connection() as conn:
                cursor = conn.cursor()
                now = datetime.now()
                
                # Create new attendance record
                cursor.execute('''
                    INSERT INTO attendance (student_id, course_id, attendance_date)
                    VALUES (?, ?, ?)
                ''', (student_id, course_id, now.date()))
                
                attendance_id = cursor.lastrowid
                
                # Record sign-in time
                cursor.execute('''
                    UPDATE attendance 
                    SET sign_in_time = ?, status = ?
                    WHERE attendance_id = ?
                ''', (now.time(), 'present', attendance_id))
                
                conn.commit()
                return True
        except Exception as e:
            print(f"Error recording attendance: {e}")
            return False

    def get_student_attendance(self, student_id: int) -> List[Dict]:
        try:
            with self._db_manager.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT a.*, c.course_name
                    FROM attendance a
                    JOIN courses c ON a.course_id = c.course_id
                    WHERE a.student_id = ?
                    ORDER BY a.attendance_date DESC
                ''', (student_id,))
                
                return [dict(row) for row in cursor.fetchall()]
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