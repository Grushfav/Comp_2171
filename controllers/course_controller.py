from typing import List, Dict, Optional
from datetime import datetime
from db.db_manager import DBManager

class CourseController:
    def __init__(self, db_manager: DBManager):
        self._db_manager = db_manager

    def create_course(self, course_name: str, description: str, 
                     start_date: str, end_date: str, 
                     location: str, max_capacity: int) -> bool:
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