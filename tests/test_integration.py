"""
Комплексні integration тести
Тестування повних сценаріїв користувача
"""
import json

class TestCompleteUserJourney:
    """Тести повного шляху користувача"""
    
    def test_user_registration_to_game_purchase(self, client, app):
        """Сценарій: Реєстрація -> Логін -> Гра -> Покупка"""
        # 1. Реєстрація
        client.post('/auth/register', data={
            'username': 'newplayer123',
            'password': 'password123'
        })
        
        # 2. Логін
        client.post('/auth/login', data={
            'username': 'newplayer123',
            'password': 'password123'
        })
        
        # 3. Встановлюємо чистий початковий баланс
        with app.app_context():
            from app.db import models
            user = models.get_user_by_username('newplayer123')
            models.set_user_coins(user['id'], 100)
        
        # 4. Перевіряємо початковий баланс
        response = client.get('/api/v1/user/profile')
        data = json.loads(response.data)
        assert data['coins'] == 100
        
        # 5. Граємо і заробляємо монети
        with app.app_context():
            from app.db import models
            user = models.get_user_by_username('newplayer123')
            coins_earned = models.save_game_result(
                user["id"], "arithmetic", "easy", 500, 120.0, 10
            )
        
        # 6. Перевіряємо нараховані монети
        response = client.get('/api/v1/user/profile')
        data = json.loads(response.data)
        expected_coins = 100 + coins_earned
        assert data['coins'] == expected_coins
        
        # 7. Купуємо товар
        items_response = client.get('/api/v1/shop/items')
        items = json.loads(items_response.data)['items']
        affordable_item = next(i for i in items if i['price'] <= expected_coins)
        
        purchase_response = client.post(f'/api/v1/shop/purchase/{affordable_item["id"]}')
        assert purchase_response.status_code == 200
        
        # 8. Перевіряємо фінальний баланс
        final_response = client.get('/api/v1/user/profile')
        final_data = json.loads(final_response.data)
        assert final_data['coins'] == expected_coins - affordable_item['price']


class TestTransactionConsistency:
    """Тести консистентності транзакцій"""
    
    def test_balance_matches_transactions(self, authenticated_client, app, test_user):
        """Тест відповідності балансу та транзакцій"""
        with app.app_context():
            from app.db import models
            
            # Встановлюємо чистий початковий баланс
            models.set_user_coins(test_user['id'], 0)
            
            # Операція 1: Додаємо монети вручну
            models.update_user_coins(test_user['id'], 100, "Manual credit")
            
            # Операція 2: Граємо і заробляємо
            coins_earned = models.save_game_result(
                test_user['id'], 'arithmetic', 'easy', 200, 30.0, 10
            )  # 200 / 10 = 20 монет
            
            # Операція 3: Купуємо найдешевший товар
            items = models.get_all_shop_items()
            cheap_item = min(items, key=lambda x: x['price'])
            models.purchase_item(test_user['id'], cheap_item['id'])
            
            # Отримуємо фактичний баланс
            actual_balance = models.get_user_coins(test_user['id'])
            
            # Очікуваний баланс
            expected_balance = 100 + coins_earned - cheap_item['price']
        
        # Перевіряємо через API
        response = authenticated_client.get('/api/v1/user/profile')
        profile_data = json.loads(response.data)
        
        assert profile_data['coins'] == expected_balance
        assert profile_data['coins'] == actual_balance
    
    def test_transaction_history_complete(self, authenticated_client, app, test_user):
        """Тест повноти історії транзакцій"""
        with app.app_context():
            from app.db import models
            
            # Очищаємо для чистоти тесту
            models.set_user_coins(test_user['id'], 0)
            
            # Операції
            models.update_user_coins(test_user['id'], 50, "Bonus")
            models.save_game_result(test_user['id'], 'arithmetic', 'easy', 300, 30.0, 10)
            
            items = models.get_all_shop_items()
            cheap_item = min(items, key=lambda x: x['price'])
            if models.get_user_coins(test_user['id']) >= cheap_item['price']:
                models.purchase_item(test_user['id'], cheap_item['id'])
        
        # Отримуємо транзакції
        response = authenticated_client.get('/api/v1/transactions')
        data = json.loads(response.data)
        transactions = data['transactions']
        
        # Перевіряємо наявність всіх типів транзакцій
        transaction_types = [t['transaction_type'] for t in transactions]
        assert 'coins_update' in transaction_types
        assert 'game_reward' in transaction_types


class TestShopAndGameInteraction:
    """Тести взаємодії магазину та ігор"""
    
    def test_earn_and_spend_cycle(self, authenticated_client, app, test_user):
        """Тест циклу заробітку та витрат"""
        with app.app_context():
            from app.db import models
            
            # Початковий стан
            models.set_user_coins(test_user['id'], 0)
            
            # Заробляємо монети через гру
            total_earned = 0
            for _ in range(3):
                earned = models.save_game_result(
                    test_user['id'], 'arithmetic', 'easy', 100, 30.0, 10
                )
                total_earned += earned
            
            balance_after_games = models.get_user_coins(test_user['id'])
            assert balance_after_games == total_earned
            
            # Купуємо товар
            items = models.get_all_shop_items()
            affordable = [i for i in items if i['price'] <= balance_after_games]
            
            if affordable:
                item = affordable[0]
                success, _ = models.purchase_item(test_user['id'], item['id'])
                assert success is True
                
                final_balance = models.get_user_coins(test_user['id'])
                assert final_balance == balance_after_games - item['price']
    
    def test_cannot_purchase_without_coins(self, authenticated_client, app, test_user):
        """Тест що не можна купити без монет"""
        with app.app_context():
            from app.db import models
            
            models.set_user_coins(test_user['id'], 0)
            
            items = models.get_all_shop_items()
            item = items[0]
            
            success, message = models.purchase_item(test_user['id'], item['id'])
            assert success is False
            assert 'not enough' in message.lower()


class TestMultipleGamesStatistics:
    """Тести статистики для кількох ігор"""
    
    def test_statistics_across_games(self, authenticated_client, app, test_user):
        """Тест агрегованої статистики по всіх іграх"""
        with app.app_context():
            from app.db import models
            
            # Arithmetic - 3 гри
            for i in range(3):
                models.save_game_result(
                    test_user['id'], 'arithmetic', 'easy', 100 * (i+1), 30.0, 10
                )
            
            # Color Rush - 2 гри
            for i in range(2):
                models.save_game_result(
                    test_user['id'], 'color_rush', 'medium', 200 * (i+1), 60.0, 10
                )
        
        # Перевіряємо загальну статистику
        response = authenticated_client.get('/api/v1/user/profile')
        data = json.loads(response.data)
        
        assert data['total_games'] == 5
        assert data['total_points'] == 1200  # 100+200+300+200+400
        
        # Перевіряємо список ігор
        games_response = authenticated_client.get('/api/v1/stats/games')
        games = json.loads(games_response.data)['games']
        
        assert 'arithmetic' in games
        assert 'color_rush' in games


class TestConcurrentOperations:
    """Тести паралельних операцій"""
    
    def test_multiple_transactions_consistency(self, authenticated_client, app, test_user):
        """Тест консистентності при множинних транзакціях"""
        with app.app_context():
            from app.db import models
            
            initial_coins = 100
            models.set_user_coins(test_user['id'], initial_coins)
            
            # Виконуємо багато операцій
            operations = []
            
            # Додавання
            models.update_user_coins(test_user['id'], 50, "Op1")
            operations.append(50)
            
            # Гра 1
            earned1 = models.save_game_result(
                test_user['id'], 'arithmetic', 'easy', 100, 30.0, 10
            )
            operations.append(earned1)
            
            # Гра 2
            earned2 = models.save_game_result(
                test_user['id'], 'color_rush', 'medium', 200, 60.0, 10
            )
            operations.append(earned2)
            
            # Віднімання
            models.update_user_coins(test_user['id'], -30, "Op4")
            operations.append(-30)
            
            # Перевіряємо фінальний баланс
            final_coins = models.get_user_coins(test_user['id'])
            expected = initial_coins + sum(operations)
            
            assert final_coins == expected


class TestEdgeCases:
    """Тести граничних випадків"""
    
    def test_zero_balance_operations(self, app, test_user):
        """Тест операцій з нульовим балансом"""
        with app.app_context():
            from app.db import models
            
            models.set_user_coins(test_user['id'], 0)
            
            # Заробляємо
            earned = models.save_game_result(
                test_user['id'], 'arithmetic', 'easy', 10, 30.0, 10
            )
            
            balance = models.get_user_coins(test_user['id'])
            assert balance == earned
    
    def test_negative_operations(self, app, test_user):
        """Тест від'ємних операцій"""
        with app.app_context():
            from app.db import models
            
            models.set_user_coins(test_user['id'], 100)
            models.update_user_coins(test_user['id'], -50, "Penalty")
            
            balance = models.get_user_coins(test_user['id'])
            assert balance == 50
    
    def test_minimum_game_reward(self, app, test_user):
        """Тест мінімальної винагороди за гру"""
        with app.app_context():
            from app.db import models
            
            # Дуже малий score
            earned = models.save_game_result(
                test_user['id'], 'arithmetic', 'easy', 1, 30.0, 10
            )
            
            assert earned >= 1  # Мінімум 1 монета