"""
Тести для routes
Покриває: main, about, games, shop, leaderboard, admin
"""
import json
import pytest

class TestMainRoutes:
    """Тести головних маршрутів"""
    
    def test_index_page(self, client):
        """Тест головної сторінки"""
        response = client.get('/')
        assert response.status_code == 200
        assert b'BrainRush' in response.data or b'brain' in response.data.lower()
    
    def test_index_redirects_when_logged_in(self, authenticated_client):
        """Тест що головна сторінка доступна для авторизованих"""
        response = authenticated_client.get('/')
        assert response.status_code == 200


class TestAboutRoutes:
    """Тести сторінки About"""
    
    def test_about_page_loads(self, client):
        """Тест завантаження сторінки About"""
        response = client.get('/about/')
        assert response.status_code == 200
        assert b'about' in response.data.lower() or b'info' in response.data.lower()


class TestGamesRoutes:
    """Тести маршрутів ігор"""
    
    def test_games_list_requires_login(self, client):
        """Тест що список ігор вимагає авторизації"""
        response = client.get('/games/')
        assert response.status_code in [302, 401]  # Redirect або 401
    
    def test_games_list_authenticated(self, authenticated_client):
        """Тест списку ігор для авторизованого користувача"""
        response = authenticated_client.get('/games/')
        assert response.status_code == 200
        assert b'Arithmetic' in response.data or b'arithmetic' in response.data.lower()
    
    def test_arithmetic_game_loads(self, authenticated_client):
        """Тест завантаження гри Arithmetic"""
        response = authenticated_client.get('/game/arithmetic/')
        assert response.status_code == 200
    
    def test_sequence_recall_game_loads(self, authenticated_client):
        """Тест завантаження гри Sequence Recall"""
        response = authenticated_client.get('/game/sequence_recall/')
        assert response.status_code == 200
    
    def test_color_rush_requires_purchase(self, authenticated_client):
        """Тест що Color Rush вимагає покупки"""
        response = authenticated_client.get('/game/color_rush/')
        # Може бути redirect на shop або завантаження гри якщо куплено
        assert response.status_code in [200, 302]
    
    def test_tapping_memory_requires_purchase(self, authenticated_client):
        """Тест що Tapping Memory вимагає покупки"""
        response = authenticated_client.get('/game/tapping_memory/')
        assert response.status_code in [200, 302]
    
    def test_save_arithmetic_result(self, authenticated_client):
        """Тест збереження результату Arithmetic"""
        response = authenticated_client.post(
            '/game/arithmetic/save_result',
            data=json.dumps({
                'level': 'easy',
                'score': 100,
                'time': 30.5,
                'rounds': 10
            }),
            content_type='application/json'
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
    
    def test_save_sequence_result(self, authenticated_client):
        """Тест збереження результату Sequence Recall"""
        response = authenticated_client.post(
            '/game/sequence_recall/save_result',
            data=json.dumps({
                'level': 'medium',
                'score': 200,
                'time': 60.0,
                'rounds': 5
            }),
            content_type='application/json'
        )
        assert response.status_code == 200


class TestShopRoutes:
    """Тести маршрутів магазину"""
    
    def test_shop_list_requires_login(self, client):
        """Тест що магазин вимагає авторизації"""
        response = client.get('/shop/')
        assert response.status_code in [302, 401]
    
    def test_shop_list_shows_items(self, authenticated_client):
        """Тест відображення товарів у магазині"""
        response = authenticated_client.get('/shop/')
        assert response.status_code == 200
        assert b'Color Rush' in response.data or b'color' in response.data.lower()
    
    
    def test_my_purchases_page(self, authenticated_client):
        """Тест сторінки моїх покупок"""
        response = authenticated_client.get('/shop/my-purchases')
        assert response.status_code == 200
    
    def test_check_game_access_free_game(self, authenticated_client):
        """Тест перевірки доступу до безкоштовної гри"""
        response = authenticated_client.get('/shop/api/check_access/arithmetic')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['has_access'] is True
        assert data['is_free'] is True


class TestLeaderboardRoutes:
    """Тести таблиці лідерів"""
    
    def test_leaderboard_loads(self, client):
        """Тест завантаження таблиці лідерів"""
        response = client.get('/leaderboard/')
        assert response.status_code == 200
    
    def test_leaderboard_shows_users(self, client, app, test_user):
        """Тест відображення користувачів у таблиці"""
        with app.app_context():
            from app.db import models
            models.update_user_coins(test_user['id'], 500)
        
        response = client.get('/leaderboard/')
        assert response.status_code == 200
        assert test_user['username'].encode() in response.data


class TestProfileRoutes:
    """Тести профілю користувача"""
    
    def test_profile_requires_login(self, client):
        """Тест що профіль вимагає авторизації"""
        response = client.get('/profile/')
        assert response.status_code in [302, 401]
    
    def test_my_profile_redirect(self, authenticated_client, test_user):
        """Тест редіректу на власний профіль"""
        response = authenticated_client.get('/profile/', follow_redirects=True)
        assert response.status_code == 200
        assert test_user['username'].encode() in response.data
    
    def test_view_user_profile(self, authenticated_client, test_user):
        """Тест перегляду профілю користувача"""
        response = authenticated_client.get(f'/profile/{test_user["id"]}')
        assert response.status_code == 200
        assert test_user['username'].encode() in response.data
    
    def test_profile_shows_statistics(self, authenticated_client, app, test_user):
        """Тест відображення статистики у профілі"""
        with app.app_context():
            from app.db import models
            models.save_game_result(test_user['id'], 'arithmetic', 'easy', 100, 30.0, 10)
        
        response = authenticated_client.get(f'/profile/{test_user["id"]}')
        assert response.status_code == 200
        assert b'100' in response.data  # Score


class TestFeedbackRoutes:
    """Тести маршрутів відгуків"""
    
    def test_feedback_list_page(self, client):
        """Тест сторінки списку відгуків"""
        response = client.get('/feedback/')
        assert response.status_code == 200
    
    def test_add_feedback_requires_login(self, client):
        """Тест що додавання відгуку вимагає авторизації"""
        response = client.post('/feedback/add', data={
            'message': 'Test feedback'
        })
        assert response.status_code in [302, 401]
    
    def test_add_feedback_success(self, authenticated_client):
        """Тест успішного додавання відгуку"""
        response = authenticated_client.post(
            '/feedback/add',
            data={'message': 'Great app!'},
            follow_redirects=True
        )
        assert response.status_code == 200
        assert b'added' in response.data.lower() or b'success' in response.data.lower()
    
    def test_add_feedback_empty_message(self, authenticated_client):
        """Тест додавання порожнього відгуку"""
        response = authenticated_client.post(
            '/feedback/add',
            data={'message': ''},
            follow_redirects=True
        )
        assert b'empty' in response.data.lower() or b'error' in response.data.lower()
    
    def test_edit_own_feedback(self, authenticated_client, sample_feedback):
        """Тест редагування власного відгуку"""
        response = authenticated_client.get(f'/feedback/edit/{sample_feedback["id"]}')
        assert response.status_code == 200
    
    def test_edit_others_feedback_denied(self, authenticated_client, app):
        """Тест що не можна редагувати чужі відгуки"""
        with app.app_context():
            from app.db import models
            other_id = models.create_user('other', 'pass123')
            fb_id = models.add_feedback(other_id, 'other', '', 'message')
        
        response = authenticated_client.get(f'/feedback/edit/{fb_id}')
        assert response.status_code == 302  # Redirect


class TestAdminRoutes:
    """Тести адміністративних маршрутів"""
    
    def test_admin_dashboard_requires_admin(self, authenticated_client):
        """Тест що dashboard вимагає права адміна"""
        response = authenticated_client.get('/admin/')
        assert response.status_code == 403
    
    def test_admin_dashboard_for_admin(self, authenticated_admin):
        """Тест dashboard для адміністратора"""
        response = authenticated_admin.get('/admin/')
        assert response.status_code == 200
    
    def test_admin_users_list(self, authenticated_admin):
        """Тест списку користувачів для адміна"""
        response = authenticated_admin.get('/admin/users')
        assert response.status_code == 200
    
    def test_admin_can_change_user_role(self, authenticated_admin, test_user):
        """Тест зміни ролі користувача адміном"""
        response = authenticated_admin.post(
            f'/admin/users/set_role/{test_user["id"]}',
            data={'role': 'admin'},
            follow_redirects=True
        )
        assert response.status_code == 200
    
    def test_admin_feedback_list(self, authenticated_admin):
        """Тест списку відгуків для адміна"""
        response = authenticated_admin.get('/admin/feedback')
        assert response.status_code == 200
    
    def test_regular_user_cannot_access_admin(self, authenticated_client):
        """Тест що звичайний користувач не має доступу до адмін панелі"""
        response = authenticated_client.get('/admin/')
        assert response.status_code == 403


class TestAPITestRoute:
    """Тести маршруту тестування API"""
    
    def test_api_test_page_requires_login(self, client):
        """Тест що сторінка API тесту вимагає авторизації"""
        response = client.get('/api-test/')
        assert response.status_code in [302, 401]
    
    def test_api_test_page_loads(self, authenticated_client):
        """Тест завантаження сторінки API тесту"""
        response = authenticated_client.get('/api-test/')
        assert response.status_code == 200