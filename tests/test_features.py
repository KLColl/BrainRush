from app.db import models
from datetime import datetime, timedelta

class TestNewFeatures:
    
    def test_daily_bonus(self, app, test_user):
        with app.app_context():
            # Симулюємо логін вчора
            yesterday = (datetime.utcnow() - timedelta(days=1)).date().isoformat()
            conn = models.get_db_connection()
            conn.execute("UPDATE users SET last_login_date = ?, login_streak = 1 WHERE id = ?", 
                         (yesterday, test_user['id']))
            conn.commit()
            conn.close()
            
            # Перевіряємо бонус сьогодні
            msg = models.check_daily_bonus(test_user['id'])
            assert "Daily Bonus" in msg
            
            user = models.get_user_by_id(test_user['id'])
            assert user['login_streak'] == 2
            
    def test_leaderboard(self, app, test_user):
        with app.app_context():
            # Створюємо ще одного юзера з більшою кількістю монет
            rich_id = models.create_user("richguy", "pass")
            models.update_user_coins(rich_id, 500)
            
            top = models.get_global_leaderboard()
            assert len(top) >= 2
            assert top[0]['username'] == "richguy"

    def test_change_password(self, app, test_user):
        with app.app_context():
            from werkzeug.security import generate_password_hash
            new_hash = generate_password_hash("newpass123")
            models.change_user_password(test_user['id'], new_hash)
            
            user = models.get_user_by_id(test_user['id'])
            assert models.verify_user_password(user, "newpass123")

    def test_delete_account(self, app, test_user):
        with app.app_context():
            models.delete_user_account(test_user['id'])
            user = models.get_user_by_id(test_user['id'])
            assert user is None