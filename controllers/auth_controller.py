from typing import Optional, Dict
from models.student import Student
from models.user import User
from db.db_manager import DBManager
from datetime import datetime

class AuthController:
    def __init__(self, db_manager: DBManager):
        self._db_manager = db_manager
        self._current_user = None

    def signup(self, username: str, password: str, first_name: str, 
               last_name: str, email: str, role: str, 
               contact_number: str = None, emergency_contact: str = None) -> bool:
        try:
            with self._db_manager.get_connection() as conn:
                cursor = conn.cursor()
                
                # Check if username already exists
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

                # If role is student, add student details
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

    def login(self, username: str, password: str) -> Optional[Dict]:
        try:
            with self._db_manager.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT * FROM users WHERE username = ? AND password = ?
                ''', (username, password))
                
                user = cursor.fetchone()
                if user:
                    self._current_user = dict(user)
                    return self._current_user
                return None

        except Exception as e:
            print(f"Error during login: {e}")
            return None

    def get_current_user(self) -> Optional[Dict]:
        return self._current_user

    def is_admin(self) -> bool:
        return self._current_user and self._current_user['role'].lower() == 'admin'

    def logout(self) -> None:
        self._current_user = None 