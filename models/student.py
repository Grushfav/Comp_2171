from typing import List, Dict, Optional
from datetime import datetime
from .user import User

class Student(User):
    def __init__(self, user_id: int, username: str, password: str,
                 first_name: str, last_name: str, email: str,
                 student_id: int, contact_number: str, 
                 emergency_contact: str):
        super().__init__(user_id, username, password, first_name, 
                        last_name, email, role="student")
        self._student_id = student_id
        self._contact_number = contact_number
        self._emergency_contact = emergency_contact
        self._enrolled_courses: List[int] = []

    def register_for_course(self, course_id: int) -> bool:
        if course_id not in self._enrolled_courses:
            self._enrolled_courses.append(course_id)
            return True
        return False

    def drop_course(self, course_id: int) -> bool:
        if course_id in self._enrolled_courses:
            self._enrolled_courses.remove(course_id)
            return True
        return False

    def view_enrolled_courses(self) -> List[int]:
        return self._enrolled_courses.copy()

    def sign_in(self, course_id: int) -> datetime:
        if course_id in self._enrolled_courses:
            return datetime.now()
        raise ValueError("Student not enrolled in this course")

    def sign_out(self, course_id: int) -> datetime:
        if course_id in self._enrolled_courses:
            return datetime.now()
        raise ValueError("Student not enrolled in this course")

    @property
    def student_id(self) -> int:
        return self._student_id 