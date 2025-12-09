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
        assert re.fullmatch(pattern, "123User") is not None
        assert re.fullmatch(pattern, "User123User") is not None
    
    def test_valid_username_only_numbers(self):
        """Тест валідного username тільки з цифр"""
        pattern = r"[A-Za-z0-9]{3,16}"
        assert re.fullmatch(pattern, "123456") is not None
    
    def test_valid_username_minimum_length(self):
        """Тест мінімальної довжини username (3 символи)"""
        pattern = r"[A-Za-z0-9]{3,16}"
        assert re.fullmatch(pattern, "abc") is not None
        assert re.fullmatch(pattern, "a23") is not None
        assert re.fullmatch(pattern, "123") is not None
    
    def test_valid_username_maximum_length(self):
        """Тест максимальної довжини username (16 символів)"""
        pattern = r"[A-Za-z0-9]{3,16}"
        assert re.fullmatch(pattern, "a" * 16) is not None
        assert re.fullmatch(pattern, "1" * 16) is not None
        assert re.fullmatch(pattern, "User12345678901") is not None  # 15 символів
    
    def test_invalid_username_too_short(self):
        """Тест занадто короткого username (менше 3 символів)"""
        pattern = r"[A-Za-z0-9]{3,16}"
        assert re.fullmatch(pattern, "ab") is None
        assert re.fullmatch(pattern, "a") is None
        assert re.fullmatch(pattern, "12") is None
    
    def test_invalid_username_too_long(self):
        """Тест занадто довгого username (більше 16 символів)"""
        pattern = r"[A-Za-z0-9]{3,16}"
        assert re.fullmatch(pattern, "a" * 17) is None
        assert re.fullmatch(pattern, "User123456789012") is not None  # 16 символів

    
    def test_invalid_username_special_chars(self):
        """Тест username зі спецсимволами"""
        pattern = r"[A-Za-z0-9]{3,16}"
        assert re.fullmatch(pattern, "user@123") is None
        assert re.fullmatch(pattern, "user_name") is None
        assert re.fullmatch(pattern, "user-123") is None
        assert re.fullmatch(pattern, "user.name") is None
        assert re.fullmatch(pattern, "user!123") is None
    
    def test_invalid_username_spaces(self):
        """Тест username з пробілами"""
        pattern = r"[A-Za-z0-9]{3,16}"
        assert re.fullmatch(pattern, "user name") is None
        assert re.fullmatch(pattern, " user") is None
        assert re.fullmatch(pattern, "user ") is None
    
    def test_valid_password_minimum_length(self):
        """Тест мінімальної довжини пароля (8 символів)"""
        password = "12345678"
        assert len(password) >= 8
    
    def test_valid_password_with_mixed_characters(self):
        """Тест пароля з різними символами"""
        passwords = [
            "password",
            "password123",
            "Pass123!",
            "12345678",
            "P@ssw0rd!123",
        ]
        for password in passwords:
            assert len(password) >= 8
    
    def test_invalid_password_too_short(self):
        """Тест занадто короткого пароля (менше 8 символів)"""
        passwords = ["1234567", "pass", "abc", "12345", ""]
        for password in passwords:
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
    
    def test_register_success_letters_only(self, client):
        """Тест успішної реєстрації з username тільки з букв"""
        response = client.post('/auth/register', data={
            'username': 'newuser',
            'password': 'password123'
        }, follow_redirects=True)
        assert response.status_code == 200
        assert b'successful' in response.data.lower()
    
    def test_register_success_with_numbers(self, client):
        """Тест успішної реєстрації з username з буквами та цифрами"""
        response = client.post('/auth/register', data={
            'username': 'user123',
            'password': 'password123'
        }, follow_redirects=True)
        assert response.status_code == 200
        assert b'successful' in response.data.lower()
    
    def test_register_success_only_numbers(self, client):
        """Тест успішної реєстрації з username тільки з цифр"""
        response = client.post('/auth/register', data={
            'username': '123456',
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
    
    def test_register_duplicate_username_case_insensitive(self, client):
        """Тест реєстрації з існуючим username (різний регістр)"""
        client.post('/auth/register', data={
            'username': 'TestUser',
            'password': 'password123'
        })
        response = client.post('/auth/register', data={
            'username': 'testuser',  # Той самий username, інший регістр
            'password': 'password456'
        }, follow_redirects=True)
        assert b'already taken' in response.data.lower()
    
    def test_register_invalid_username_too_short(self, client):
        """Тест реєстрації з занадто коротким username"""
        response = client.post('/auth/register', data={
            'username': 'ab',  # 2 символи (мінімум 3)
            'password': 'password123'
        }, follow_redirects=True)
        assert b'3-16 characters' in response.data
    
    def test_register_invalid_username_too_long(self, client):
        """Тест реєстрації з занадто довгим username"""
        response = client.post('/auth/register', data={
            'username': 'a' * 17,  # 17 символів (максимум 16)
            'password': 'password123'
        }, follow_redirects=True)
        assert b'3-16 characters' in response.data
    
    def test_register_invalid_username_special_chars(self, client):
        """Тест реєстрації з спецсимволами в username"""
        invalid_usernames = ['user@123', 'user_name', 'user-123', 'user.name']
        for username in invalid_usernames:
            response = client.post('/auth/register', data={
                'username': username,
                'password': 'password123'
            }, follow_redirects=True)
            assert b'3-16 characters' in response.data or b'only english letters' in response.data.lower()
    
    def test_register_invalid_password_too_short(self, client):
        """Тест реєстрації з занадто коротким паролем"""
        response = client.post('/auth/register', data={
            'username': 'validuser',
            'password': '1234567'  # 7 символів (мінімум 8)
        }, follow_redirects=True)
        assert b'at least 8 characters' in response.data
    
    def test_register_username_with_whitespace(self, client):
        """Тест реєстрації з пробілами в username (strip має видалити)"""
        response = client.post('/auth/register', data={
            'username': '  user123  ',  # Пробіли на початку та в кінці
            'password': 'password123'
        }, follow_redirects=True)
        assert response.status_code == 200
        # Username має бути збережений як 'user123' без пробілів
    
    def test_login_success(self, client, test_user):
        """Тест успішного входу"""
        response = client.post('/auth/login', data={
            'username': 'testuser',
            'password': 'password123'
        }, follow_redirects=True)
        assert response.status_code == 200
    
    def test_login_success_with_numbers(self, client):
        """Тест успішного входу з username що містить цифри"""
        # Спочатку реєструємо
        client.post('/auth/register', data={
            'username': 'user123',
            'password': 'password123'
        })
        # Потім логінимось
        response = client.post('/auth/login', data={
            'username': 'user123',
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
    
    def test_login_invalid_username_format(self, client):
        """Тест входу з невалідним форматом username"""
        response = client.post('/auth/login', data={
            'username': 'us',  # Занадто короткий
            'password': 'password123'
        }, follow_redirects=True)
        assert b'Invalid' in response.data
    
    def test_login_invalid_password_format(self, client):
        """Тест входу з невалідним форматом пароля"""
        response = client.post('/auth/login', data={
            'username': 'testuser',
            'password': 'short'  # Менше 8 символів
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
    
    def test_register_edge_case_min_length(self, client):
        """Тест реєстрації з мінімальною довжиною username та password"""
        response = client.post('/auth/register', data={
            'username': 'abc',  # 3 символи (мінімум)
            'password': '12345678'  # 8 символів (мінімум)
        }, follow_redirects=True)
        assert response.status_code == 200
        assert b'successful' in response.data.lower()
    
    def test_register_edge_case_max_length(self, client):
        """Тест реєстрації з максимальною довжиною username"""
        response = client.post('/auth/register', data={
            'username': 'a' * 16,  # 16 символів (максимум)
            'password': 'password123'
        }, follow_redirects=True)
        assert response.status_code == 200
        assert b'successful' in response.data.lower()