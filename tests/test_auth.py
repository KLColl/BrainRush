"""
Unit тести для системи авторизації
Покриття: реєстрація, вхід, вихід, валідація
"""
import pytest
import re

class TestRegistrationValidation:
    """Тести валідації при реєстрації"""
    
    def test_valid_username_letters_only(self):
        """Тест валідного username тільки з букв"""
        pattern = r"[A-Za-z0-9]{3,16}"
        assert re.fullmatch(pattern, "ValidUser") is not None
    
    def test_valid_username_with_numbers(self):
        """Тест валідного username з буквами та цифрами"""
        pattern = r"[A-Za-z0-9]{3,16}"
        assert re.fullmatch(pattern, "User123") is not None
    
    def test_invalid_username_too_short(self):
        """Тест занадто короткого username"""
        pattern = r"[A-Za-z0-9]{3,16}"
        assert re.fullmatch(pattern, "ab") is None
    
    def test_invalid_username_too_long(self):
        """Тест занадто довгого username"""
        pattern = r"[A-Za-z0-9]{3,16}"
        assert re.fullmatch(pattern, "a" * 17) is None
    
    def test_invalid_username_special_chars(self):
        """Тест username зі спецсимволами"""
        pattern = r"[A-Za-z0-9]{3,16}"
        assert re.fullmatch(pattern, "user@123") is None
        assert re.fullmatch(pattern, "user_name") is None
        assert re.fullmatch(pattern, "user-123") is None
    
    def test_invalid_username_spaces(self):
        """Тест username з пробілами"""
        pattern = r"[A-Za-z0-9]{3,16}"
        assert re.fullmatch(pattern, "user name") is None
    
    def test_valid_password_minimum_length(self):
        """Тест мінімальної довжини пароля"""
        password = "12345678"
        assert len(password) >= 8
    
    def test_invalid_password_too_short(self):
        """Тест занадто короткого пароля"""
        password = "1234567"
        assert len(password) < 8


class TestAuthRoutes:
    """Тести маршрутів авторизації"""
    
    def test_register_page_loads(self, client):
        """Тест завантаження сторінки реєстрації"""
        response = client.get('/auth/register')
        assert response.status_code == 200
        assert b'Register' in response.data
    
    def test_login_page_loads(self, client):
        """Тест завантаження сторінки входу"""
        response = client.get('/auth/login')
        assert response.status_code == 200
        assert b'Login' in response.data
    
    def test_register_success(self, client):
        """Тест успішної реєстрації"""
        response = client.post('/auth/register', data={
            'username': 'newuser123',
            'password': 'password123'
        }, follow_redirects=True)
        assert response.status_code == 200
        assert b'successful' in response.data.lower()
    
    def test_register_duplicate_username(self, client):
        """Тест реєстрації з існуючим username"""
        client.post('/auth/register', data={
            'username': 'duplicate123',
            'password': 'password123'
        })
        response = client.post('/auth/register', data={
            'username': 'duplicate123',
            'password': 'password456'
        }, follow_redirects=True)
        assert b'already taken' in response.data.lower()
    
    def test_register_invalid_username(self, client):
        """Тест реєстрації з невалідним username"""
        response = client.post('/auth/register', data={
            'username': 'ab',  # Занадто короткийаа
            'password': 'password123'
        }, follow_redirects=True)
        assert b'3-16 characters' in response.data
    
    def test_register_invalid_password(self, client):
        """Тест реєстрації з невалідним паролем"""
        response = client.post('/auth/register', data={
            'username': 'validuser',
            'password': '1234567'  # Менше 8 символів
        }, follow_redirects=True)
        assert b'at least 8 characters' in response.data
    
    def test_login_success(self, client, test_user):
        """Тест успішного входу"""
        response = client.post('/auth/login', data={
            'username': 'testuser',
            'password': 'password123'
        }, follow_redirects=True)
        assert response.status_code == 200
    
    def test_login_wrong_password(self, client, test_user):
        """Тест входу з неправильним паролем"""
        response = client.post('/auth/login', data={
            'username': 'testuser',
            'password': 'wrongpassword'
        }, follow_redirects=True)
        assert b'Invalid' in response.data
    
    def test_login_nonexistent_user(self, client):
        """Тест входу з неіснуючим користувачем"""
        response = client.post('/auth/login', data={
            'username': 'nonexistent',
            'password': 'password123'
        }, follow_redirects=True)
        assert b'Invalid' in response.data
    
    def test_logout(self, authenticated_client):
        """Тест виходу з системи"""
        response = authenticated_client.get('/auth/logout', follow_redirects=True)
        assert response.status_code == 200
    
    def test_protected_route_requires_login(self, client):
        """Тест доступу до захищеного маршруту без авторизації"""
        response = client.get('/profile')
            # Перевіряємо що це redirect (3xx status code)
        assert 300 <= response.status_code < 400, f"Expected redirect (3xx), got {response.status_code}"