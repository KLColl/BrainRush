"""
Покращена конфігурація pytest з правильною ізоляцією
"""
import pytest
import os
import tempfile
from app import create_app
from app.db import models

@pytest.fixture(scope='function')
def app():
    """Fixture для створення тестового Flask застосунку"""
    db_fd, db_path = tempfile.mkstemp()
    
    app = create_app()
    app.config.update({
        'TESTING': True,
        'SECRET_KEY': 'test-secret-key',
        'WTF_CSRF_ENABLED': False,
        'LOGIN_DISABLED': False
    })
    
    original_db_path = models.DB_PATH
    models.DB_PATH = db_path
    
    with app.app_context():
        models.init_db()
    
    yield app
    
    # Cleanup
    with app.app_context():
        try:
            conn = models.get_db_connection()
            conn.close()
        except:
            pass
    
    try:
        os.close(db_fd)
        os.unlink(db_path)
    except:
        pass
    
    models.DB_PATH = original_db_path


@pytest.fixture
def client(app):
    """Fixture для тестового клієнта"""
    return app.test_client()


@pytest.fixture
def test_user(app):
    """Fixture для створення тестового користувача"""
    with app.app_context():
        user_id = models.create_user("testuser", "password123")
        user = models.get_user_by_id(user_id)
        return {
            "id": user["id"],
            "username": user["username"],
            "password": "password123"
        }


@pytest.fixture
def authenticated_client(client, test_user):
    """Fixture для авторизованого клієнта"""
    client.post('/auth/login', data={
        'username': test_user["username"],
        'password': test_user["password"]
    })
    return client


@pytest.fixture
def admin_user(app):
    """Fixture для користувача-адміністратора"""
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
def authenticated_admin(client, admin_user):
    """Fixture для авторизованого адміна"""
    client.post('/auth/login', data={
        'username': admin_user["username"],
        'password': admin_user["password"]
    })
    return client


@pytest.fixture
def rich_user(app):
    """Fixture для користувача з багатьма монетами"""
    with app.app_context():
        user_id = models.create_user("richuser", "password123")
        models.set_user_coins(user_id, 1000)
        user = models.get_user_by_id(user_id)
        return {
            "id": user["id"],
            "username": user["username"],
            "password": "password123"
        }


@pytest.fixture
def sample_feedback(app, test_user):
    """Fixture для створення тестового відгуку"""
    with app.app_context():
        feedback_id = models.add_feedback(
            user_id=test_user["id"],
            name=test_user["username"],
            email="",
            message="Test feedback message"
        )
        return models.get_feedback(feedback_id)

@pytest.fixture
def sample_game_results(app, test_user):
    """Fixture: додає кілька результатів ігор для test_user (100,200,300 очок)."""
    with app.app_context():
        from app.db import models
        # створюємо 3 результати, які використовуються в тесті
        models.save_game_result(test_user["id"], "arithmetic", "easy", 100, 30.0, 1)
        models.save_game_result(test_user["id"], "color_rush", "medium", 200, 45.0, 1)
        models.save_game_result(test_user["id"], "sequence_recall", "hard", 300, 60.0, 1)
    return True

@pytest.fixture
def shop_items(app):
    """Fixture для отримання товарів магазину"""
    with app.app_context():
        return models.get_all_shop_items()