from datetime import datetime, time, timedelta
from typing import Optional

class Attendance:
    def __init__(self, attendance_id: int, student_id: int, course_id: int,
                 attendance_date: datetime):
        self._attendance_id = attendance_id
        self._student_id = student_id
        self._course_id = course_id
        self._attendance_date = attendance_date
        self._sign_in_time: Optional[datetime] = None
        self._sign_out_time: Optional[datetime] = None
        self._is_late = False
        self._status = "absent"  # absent, present, late

    def sign_in(self, current_time: datetime, expected_time: time) -> None:
        self._sign_in_time = current_time
        self._status = "present"
        
        # Convert current_time to time object for comparison
        current_time_only = current_time.time()
        
        # Check if late
        if current_time_only > expected_time:
            self._is_late = True
            self._status = "late"

    def sign_out(self, time: datetime) -> None:
        self._sign_out_time = time

    def get_attendance_record(self) -> dict:
        return {
            'attendance_id': self._attendance_id,
            'student_id': self._student_id,
            'course_id': self._course_id,
            'date': self._attendance_date,
            'sign_in_time': self._sign_in_time,
            'sign_out_time': self._sign_out_time,
            'status': self._status,
            'is_late': self._is_late
        } 