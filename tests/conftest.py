"""
Конфігурація pytest та спільні fixtures
Використовується для підготовки тестового середовища
"""
import pytest
import os
import tempfile
from app import create_app
from app.db import models

@pytest.fixture
def app():
    """
    Fixture для створення тестового Flask застосунку
    Використовує окрему тестову БД для ізоляції
    """
    # Створюємо тимчасовий файл для БД
    db_fd, db_path = tempfile.mkstemp()
    
    app = create_app()
    app.config.update({
        'TESTING': True,
        'SECRET_KEY': 'test-secret-key',
        'WTF_CSRF_ENABLED': False,
        'LOGIN_DISABLED': False
    })
    
    # Перевизначаємо шлях до БД
    original_db_path = models.DB_PATH
    models.DB_PATH = db_path
    
    with app.app_context():
        models.init_db()
    
    yield app
    
    # Teardown: видаляємо тестову БД
    # Закриваємо всі з'єднання перед видаленням
    with app.app_context():
        conn = models.get_db_connection()
        conn.close()
    
    try:
        os.close(db_fd)
        os.unlink(db_path)
    except (OSError, PermissionError):
        # Якщо не вдається видалити - ігноруємо
        pass
    
    models.DB_PATH = original_db_path


@pytest.fixture
def client(app):
    """
    Fixture для тестового клієнта
    Дозволяє робити HTTP запити до застосунку
    """
    return app.test_client()


@pytest.fixture
def runner(app):
    """
    Fixture для CLI runner
    Використовується для тестування консольних команд
    """
    return app.test_cli_runner()


@pytest.fixture
def test_user(app):
    """
    Fixture для створення тестового користувача
    Повертає словник з даними користувача
    """
    with app.app_context():
        user_id = models.create_user("testuser", "password123")
        user = models.get_user_by_id(user_id)
        return {
            "id": user["id"],
            "username": user["username"],
            "password": "password123"  # Зберігаємо для логіну
        }


@pytest.fixture
def authenticated_client(client, test_user):
    """
    Fixture для авторизованого клієнта
    Автоматично виконує логін перед тестами
    """
    client.post('/auth/login', data={
        'username': test_user["username"],
        'password': test_user["password"]
    })
    return client


@pytest.fixture
def admin_user(app):
    """
    Fixture для створення користувача-адміністратора
    """
    with app.app_context():
        user_id = models.create_user("admin", "adminpass123")
        models.set_user_role(user_id, "admin")
        user = models.get_user_by_id(user_id)
        return {
            "id": user["id"],
            "username": user["username"],
            "password": "adminpass123",
            "role": user["role"]
        }


@pytest.fixture
def rich_user(app):
    """
    Fixture для користувача з багатьма монетами
    Використовується для тестування покупок
    """
    with app.app_context():
        user_id = models.create_user("richuser", "password123")
        models.update_user_coins(user_id, 1000)  # Додаємо 1000 монет
        user = models.get_user_by_id(user_id)
        return {
            "id": user["id"],
            "username": user["username"],
            "password": "password123"
        }


@pytest.fixture
def sample_game_results(app, test_user):
    """
    Fixture для створення тестових результатів ігор
    """
    with app.app_context():
        results = [
            models.save_game_result(
                test_user["id"], "arithmetic", "easy", 100, 30.0, 10
            ),
            models.save_game_result(
                test_user["id"], "arithmetic", "medium", 200, 60.0, 10
            ),
            models.save_game_result(
                test_user["id"], "color_rush", "hard", 300, 90.0, 10
            )
        ]
        return results


@pytest.fixture
def sample_feedback(app, test_user):
    """
    Fixture для створення тестового відгуку
    """
    with app.app_context():
        feedback_id = models.add_feedback(
            user_id=test_user["id"],
            name=test_user["username"],
            email="",
            message="Test feedback message"
        )
        return models.get_feedback(feedback_id)


@pytest.fixture(autouse=True)
def reset_db(app):
    """
    Автоматичне очищення БД після кожного тесту
    autouse=True означає, що fixture виконується завжди
    """
    yield
    # Код teardown виконується після кожного тесту
    # Безпечне очищення з обробкою помилок
    try:
        with app.app_context():
            conn = models.get_db_connection()
            try:
                conn.execute("DELETE FROM game_results")
                conn.execute("DELETE FROM feedback")
                conn.execute("DELETE FROM user_purchases")
                conn.execute("DELETE FROM transactions")
                conn.execute("DELETE FROM users WHERE username != 'testuser'")
                conn.commit()
            except Exception as e:
                print(f"Warning: Database cleanup failed: {e}")
            finally:
                conn.close()
    except Exception as e:
        print(f"Warning: Could not reset database: {e}")