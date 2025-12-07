"""
Unit тести для моделей бази даних
Покриття: створення користувачів, валідація, операції з БД
"""
import pytest
from app.db import models

class TestUserModel:
    """Тести для моделі User"""
    
    def test_create_user_success(self, app):
        """Тест успішного створення користувача"""
        with app.app_context():
            user_id = models.create_user("testuser", "password123")
            assert user_id is not None
            assert user_id > 0
    
    def test_create_user_duplicate(self, app):
        """Тест створення користувача з існуючим username"""
        with app.app_context():
            models.create_user("duplicate", "password123")
            with pytest.raises(Exception):
                models.create_user("duplicate", "password456")
    
    def test_get_user_by_username(self, app):
        """Тест отримання користувача за username"""
        with app.app_context():
            models.create_user("findme", "password123")
            user = models.get_user_by_username("findme")
            assert user is not None
            assert user["username"] == "findme"
    
    def test_get_user_case_insensitive(self, app):
        """Тест пошуку користувача без урахування регістру"""
        with app.app_context():
            models.create_user("CamelCase", "password123")
            user = models.get_user_by_username("camelcase")
            assert user is not None
            assert user["username"] == "CamelCase"
    
    def test_get_nonexistent_user(self, app):
        """Тест отримання неіснуючого користувача"""
        with app.app_context():
            user = models.get_user_by_username("nonexistent")
            assert user is None
    
    def test_verify_password_correct(self, app):
        """Тест перевірки правильного пароля"""
        with app.app_context():
            models.create_user("passtest", "correct123")
            user = models.get_user_by_username("passtest")
            assert models.verify_user_password(user, "correct123") is True
    
    def test_verify_password_incorrect(self, app):
        """Тест перевірки неправильного пароля"""
        with app.app_context():
            models.create_user("passtest2", "correct123")
            user = models.get_user_by_username("passtest2")
            assert models.verify_user_password(user, "wrong123") is False
    
    def test_update_user_coins(self, app):
        """Тест оновлення балансу монет"""
        with app.app_context():
            user_id = models.create_user("cointest", "password123")
            models.update_user_coins(user_id, 50)
            coins = models.get_user_coins(user_id)
            assert coins == 150  # 100 початкових + 50

    def test_update_user_coins_negative(self, app):
        """Тест віднімання монет"""
        with app.app_context():
            user_id = models.create_user("cointest2", "password123")
            models.update_user_coins(user_id, -30)
            coins = models.get_user_coins(user_id)
            assert coins == 70  # 100 - 30
    
    def test_set_user_role(self, app):
        """Тест зміни ролі користувача"""
        with app.app_context():
            user_id = models.create_user("roletest", "password123")
            models.set_user_role(user_id, "admin")
            user = models.get_user_by_id(user_id)
            assert user["role"] == "admin"


class TestGameResults:
    """Тести для результатів ігор"""
    
    def test_save_game_result(self, app, test_user):
        """Тест збереження результату гри"""
        with app.app_context():
            coins = models.save_game_result(
                user_id=test_user["id"],
                game_name="arithmetic",
                level="easy",
                score=100,
                time_spent=45.5,
                rounds=10
            )
            assert coins == 10  # 100 / 10 = 10 монет
    
    def test_save_game_result_minimum_coins(self, app, test_user):
        """Тест мінімальної кількості монет за гру"""
        with app.app_context():
            coins = models.save_game_result(
                user_id=test_user["id"],
                game_name="arithmetic",
                level="easy",
                score=5,
                time_spent=10.0,
                rounds=1
            )
            assert coins == 1  # Мінімум 1 монета
    
    def test_get_total_games(self, app, test_user):
        """Тест підрахунку загальної кількості ігор"""
        with app.app_context():
            models.save_game_result(test_user["id"], "arithmetic", "easy", 100, 30.0, 1)
            models.save_game_result(test_user["id"], "color_rush", "medium", 200, 60.0, 1)
            total = models.get_total_games(test_user["id"])
            assert total == 2
    
    def test_get_total_points(self, app, test_user):
        """Тест підрахунку загальних очок"""
        with app.app_context():
            models.save_game_result(test_user["id"], "arithmetic", "easy", 100, 30.0, 1)
            models.save_game_result(test_user["id"], "arithmetic", "hard", 250, 90.0, 1)
            total = models.get_total_points(test_user["id"])
            assert total == 350


class TestShop:
    """Тести для магазину"""
    
    def test_get_shop_items(self, app):
        """Тест отримання товарів магазину"""
        with app.app_context():
            items = models.get_all_shop_items()
            assert len(items) > 0
            for item in items:
                assert item["price"] is not None, "Price field is missing"
                assert item["name"] is not None, "Name field is missing"
                assert item["item_type"] is not None, "Item type is missing"
    
    def test_purchase_item_success(self, app, test_user):
        """Тест успішної покупки товару"""
        with app.app_context():
            items = models.get_all_shop_items()
            item = items[0]
            
            # Додаємо достатньо монет
            models.update_user_coins(test_user["id"], item["price"])
            
            success, msg = models.purchase_item(test_user["id"], item["id"])
            assert success is True
            assert "successful" in msg.lower()
    
    def test_purchase_item_insufficient_coins(self, app, test_user):
        """Тест покупки без достатньої кількості монет"""
        with app.app_context():
            items = models.get_all_shop_items()
            expensive_item = max(items, key=lambda x: x["price"])
            
            success, msg = models.purchase_item(test_user["id"], expensive_item["id"])
            assert success is False
            assert "not enough" in msg.lower()
    
    def test_purchase_item_duplicate(self, app, test_user):
        """Тест повторної покупки того ж товару"""
        with app.app_context():
            items = models.get_all_shop_items()
            item = items[0]
            
            models.update_user_coins(test_user["id"], item["price"] * 2)
            models.purchase_item(test_user["id"], item["id"])
            
            success, msg = models.purchase_item(test_user["id"], item["id"])
            assert success is False
            assert "already purchased" in msg.lower()