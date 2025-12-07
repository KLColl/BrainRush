"""
Integration тести для API користувача
Тестування складної взаємодії між компонентами
"""
import json
import pytest

class TestUserProfileAPI:
    """Тести для endpoints профілю користувача"""
    
    def test_get_profile_authenticated(self, authenticated_client, test_user, sample_game_results):
        """Тест отримання профілю авторизованого користувача"""
        response = authenticated_client.get('/api/v1/user/profile')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        # Перевірка структури відповіді
        assert 'id' in data
        assert 'username' in data
        assert 'coins' in data
        assert 'total_games' in data
        assert 'total_points' in data
        
        # Перевірка даних
        assert data['username'] == test_user['username']
        assert data['total_games'] == 3  # З sample_game_results
        assert data['total_points'] == 600  # 100 + 200 + 300
    
    def test_get_profile_unauthenticated(self, client):
        """Тест отримання профілю без авторизації"""
        response = client.get('/api/v1/user/profile')
        assert response.status_code == 401
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_get_user_by_id(self, authenticated_client, test_user):
        """Тест отримання користувача за ID"""
        response = authenticated_client.get(f'/api/v1/user/{test_user["id"]}')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        assert data['id'] == test_user['id']
        assert data['username'] == test_user['username']
        assert 'password_hash' not in data  # Приватна інформація
    
    def test_get_nonexistent_user(self, authenticated_client):
        """Тест отримання неіснуючого користувача"""
        response = authenticated_client.get('/api/v1/user/99999')
        assert response.status_code == 404
        data = json.loads(response.data)
        assert 'error' in data


class TestThemeAPI:
    """Тести для зміни теми"""
    
    def test_update_theme_to_dark(self, authenticated_client):
        """Тест зміни теми на темну"""
        response = authenticated_client.post(
            '/api/v1/user/theme',
            data=json.dumps({'theme': 'dark'}),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['theme'] == 'dark'
    
    def test_update_theme_to_light(self, authenticated_client):
        """Тест зміни теми на світлу"""
        response = authenticated_client.post(
            '/api/v1/user/theme',
            data=json.dumps({'theme': 'light'}),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['theme'] == 'light'
    
    def test_update_theme_invalid(self, authenticated_client):
        """Тест зміни теми на невалідне значення"""
        response = authenticated_client.post(
            '/api/v1/user/theme',
            data=json.dumps({'theme': 'invalid'}),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_update_theme_missing_data(self, authenticated_client):
        """Тест зміни теми без передачі даних"""
        response = authenticated_client.post(
            '/api/v1/user/theme',
            data=json.dumps({}),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_update_theme_unauthenticated(self, client):
        """Тест зміни теми без авторизації"""
        response = client.post(
            '/api/v1/user/theme',
            data=json.dumps({'theme': 'dark'}),
            content_type='application/json'
        )
        
        assert response.status_code == 401


class TestUserStatsAPI:
    """Тести для статистики користувача"""
    
    def test_profile_with_multiple_games(self, authenticated_client, test_user, app):
        """Тест профілю з кількома зіграними іграми"""
        with app.app_context():
            from app.db import models
            # Додаємо різні ігри
            models.save_game_result(test_user["id"], "arithmetic", "easy", 50, 20.0, 5)
            models.save_game_result(test_user["id"], "color_rush", "medium", 150, 45.0, 10)
            models.save_game_result(test_user["id"], "sequence_recall", "hard", 300, 120.0, 15)
        
        response = authenticated_client.get('/api/v1/user/profile')
        data = json.loads(response.data)
        
        assert data['total_games'] == 3
        assert data['total_points'] == 500
        assert data['total_coins_earned'] > 0
    
    def test_profile_coins_accumulation(self, authenticated_client, test_user, app):
        """Тест накопичення монет через гру"""
        with app.app_context():
            from app.db import models
            initial_coins = models.get_user_coins(test_user["id"])
            
            # Граємо і заробляємо монети
            models.save_game_result(test_user["id"], "arithmetic", "easy", 100, 30.0, 10)
            
            final_coins = models.get_user_coins(test_user["id"])
        
        response = authenticated_client.get('/api/v1/user/profile')
        data = json.loads(response.data)
        
        assert data['coins'] > initial_coins
        assert data['total_coins_earned'] == 10  # 100 / 10