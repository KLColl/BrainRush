from flask_login import UserMixin

"""
UserObject для Flask-Login
Обгортка над даними користувача з БД
"""
class UserObject(UserMixin):
    def __init__(self, row):
        self.id = row["id"]
        self.username = row["username"]
        self.password_hash = row["password_hash"]
        self.role = row["role"]
        self.coins = row["coins"] if "coins" in row.keys() else 0
        self.theme = row["theme"] if "theme" in row.keys() else "light"
        self.created_at = row["created_at"]

    @property
    def is_admin(self):
        return self.role == 'admin'