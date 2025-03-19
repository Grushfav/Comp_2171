from typing import List, Dict, Optional
from datetime import datetime

class Course:
    def __init__(self, course_id: int, course_name: str, description: str,
                 start_date: datetime, end_date: datetime, location: str,
                 max_capacity: int):
        self._course_id = course_id
        self._course_name = course_name
        self._description = description
        self._start_date = start_date
        self._end_date = end_date
        self._location = location
        self._max_capacity = max_capacity
        self._enrolled_students: List[int] = []

    def add_student(self, student_id: int) -> bool:
        if len(self._enrolled_students) < self._max_capacity:
            if student_id not in self._enrolled_students:
                self._enrolled_students.append(student_id)
                return True
        return False

    def remove_student(self, student_id: int) -> bool:
        if student_id in self._enrolled_students:
            self._enrolled_students.remove(student_id)
            return True
        return False

    def get_course_details(self) -> Dict:
        return {
            'course_id': self._course_id,
            'course_name': self._course_name,
            'description': self._description,
            'location': self._location,
            'enrolled_count': len(self._enrolled_students),
            'max_capacity': self._max_capacity
        }

    @property
    def course_id(self) -> int:
        return self._course_id 