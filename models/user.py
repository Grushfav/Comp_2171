from abc import ABC, abstractmethod
from typing import Dict, Optional
import hashlib

class User(ABC):
    def __init__(self, user_id: int, username: str, password: str, 
                 first_name: str, last_name: str, email: str, role: str):
        self._user_id = user_id
        self._username = username
        self._password = self._hash_password(password)
        self._first_name = first_name
        self._last_name = last_name
        self._email = email
        self._role = role
        self._is_logged_in = False

    def _hash_password(self, password: str) -> str:
        return hashlib.sha256(password.encode()).hexdigest()

    def login(self, password: str) -> bool:
        if self._password == self._hash_password(password):
            self._is_logged_in = True
            return True
        return False

    def logout(self) -> None:
        self._is_logged_in = False

    def change_password(self, old_password: str, new_password: str) -> bool:
        if self._password == self._hash_password(old_password):
            self._password = self._hash_password(new_password)
            return True
        return False

    def update_profile(self, updates: Dict[str, str]) -> bool:
        valid_fields = {'first_name', 'last_name', 'email'}
        for field, value in updates.items():
            if field in valid_fields:
                setattr(self, f'_{field}', value)
        return True

    def get_profile(self) -> Dict[str, str]:
        return {
            'user_id': self._user_id,
            'username': self._username,
            'first_name': self._first_name,
            'last_name': self._last_name,
            'email': self._email,
            'role': self._role
        }

    @property
    def user_id(self) -> int:
        return self._user_id

    @property
    def role(self) -> str:
        return self._role 