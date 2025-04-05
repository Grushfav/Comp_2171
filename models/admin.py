from .user import User
from datetime import time

class Admin(User):
    def __init__(self, user_id: int, username: str, password: str,
                 first_name: str, last_name: str, email: str,
                 admin_id: int, department: str):
        super().__init__(user_id, username, password, first_name, 
                        last_name, email, role="admin")
        self._admin_id = admin_id
        self._department = department

    @property
    def admin_id(self) -> int:
        return self._admin_id

    @property
    def department(self) -> str:
        return self._department 