from flask_login import UserMixin

class UserObject(UserMixin):
    def __init__(self, row):
        self.id = row["id"]
        self.username = row["username"]
        self.password_hash = row["password_hash"]
        self.role = row["role"]
        self.created_at = row["created_at"]

    @property
    def is_admin(self):
        return self.role == 'admin'
