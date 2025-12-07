"""
Комплексні integration тести
Тестування повних сценаріїв користувача
"""
import json
import pytest

class TestCompleteUserJourney:
    """Тести повного шляху користувача"""
    
    def test_user_registration_to_game_purchase(self, client, app):
        """
        Сценарій: Реєстрація -> Гра -> Заробіток монет -> Покупка
        """
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
        
        # 3. Перевіряємо початковий баланс
        response = client.get('/api/v1/user/profile')
        data = json.loads(response.data)
        initial_coins = data['coins']
        assert initial_coins == 100  # Початковий баланс
        
        # 4. Граємо в гру і заробляємо монети
        with app.app_context():
            from app.db import models
            user = models.get_user_by_username('newplayer123')
            models.save_game_result(
                user["id"],
                "arithmetic",
                "easy",
                500,  # 500 очок = 50 монет
                120.0,
                10
            )
        
        # 5. Перевіряємо що монети зараховані
        response = client.get('/api/v1/user/profile')
        data = json.loads(response.data)
        assert data['coins'] == 150  # 100 + 50
        
        # 6. Купуємо щось у магазині
        items_response = client.get('/api/v1/shop/items')
        items = json.loads(items_response.data)['items']
        affordable_item = next(i for i in items if i['price'] <= 150)
        
        purchase_response = client.post(f'/api/v1/shop/purchase/{affordable_item["id"]}')
        purchase_data = json.loads(purchase_response.data)
        
        assert purchase_data['success'] is True
        
        # 7. Перевіряємо фінальний баланс
        final_response = client.get('/api/v1/user/profile')
        final_data = json.loads(final_response.data)
        expected_balance = 150 - affordable_item['price']
        assert final_data['coins'] == expected_balance
    
    def test_game_statistics_accumulation(self, authenticated_client, app, test_user):
        """
        Сценарій: Гра в різні ігри -> Накопичення статистики
        """
        # 1. Граємо в різні ігри
        with app.app_context():
            from app.db import models
            
            # Arithmetic - 3 рази
            for i in range(3):
                models.save_game_result(
                    test_user["id"],
                    "arithmetic",
                    "easy",
                    100 + i * 10,
                    30.0 + i * 5,
                    10
                )
            
            # Color Rush - 2 рази
            for i in range(2):
                models.save_game_result(
                    test_user["id"],
                    "color_rush",
                    "medium",
                    200 + i * 20,
                    60.0 + i * 10,
                    10
                )
        
        # 2. Перевіряємо загальну статистику
        profile_response = authenticated_client.get('/api/v1/user/profile')
        profile_data = json.loads(profile_response.data)
        
        assert profile_data['total_games'] == 5
        
        # 3. Перевіряємо список ігор
        games_response = authenticated_client.get('/api/v1/stats/games')
        games_data = json.loads(games_response.data)
        
        assert 'arithmetic' in games_data['games']
        assert 'color_rush' in games_data['games']
        
        # 4. Перевіряємо статистику по грі
        arithmetic_response = authenticated_client.get('/api/v1/stats/game/arithmetic')
        arithmetic_data = json.loads(arithmetic_response.data)
        
        assert arithmetic_data['game'] == 'arithmetic'
        assert len(arithmetic_data['stats']) > 0


class TestShopAndGameInteraction:
    """Тести взаємодії магазину та ігор"""
    
    def test_earn_coins_through_gameplay(self, authenticated_client, app, test_user):
        """Тест заробітку монет через гру"""
        with app.app_context():
            from app.db import models
            initial_coins = models.get_user_coins(test_user["id"])
            
            # Граємо і заробляємо монети
            coins_earned = models.save_game_result(
                test_user["id"],
                "arithmetic",
                "hard",
                300,  # 300 очок = 30 монет
                90.0,
                15
            )
            
            final_coins = models.get_user_coins(test_user["id"])
        
        assert coins_earned == 30
        assert final_coins == initial_coins + 30
        
        # Перевіряємо транзакцію
        transactions_response = authenticated_client.get('/api/v1/transactions')
        transactions = json.loads(transactions_response.data)['transactions']
        
        game_reward = next(
            t for t in transactions
            if t['transaction_type'] == 'game_reward'
        )
        assert game_reward['amount'] == 30
    
    def test_purchase_with_earned_coins(self, authenticated_client, app, test_user):
        """Тест покупки за зароблені монети"""
        with app.app_context():
            from app.db import models
            
            # Заробляємо багато монет
            for _ in range(5):
                models.save_game_result(
                    test_user["id"],
                    "arithmetic",
                    "hard",
                    200,
                    60.0,
                    10
                )
            
            current_coins = models.get_user_coins(test_user["id"])
        
        # Купуємо товар
        items_response = authenticated_client.get('/api/v1/shop/items')
        items = json.loads(items_response.data)['items']
        item_to_buy = items[0]
        
        purchase_response = authenticated_client.post(
            f'/api/v1/shop/purchase/{item_to_buy["id"]}'
        )
        
        assert purchase_response.status_code == 200
        
        # Перевіряємо що монети віднялись
        profile_response = authenticated_client.get('/api/v1/user/profile')
        profile_data = json.loads(profile_response.data)
        
        expected_coins = current_coins - item_to_buy['price']
        assert profile_data['coins'] == expected_coins


class TestDataConsistency:
    """Тести консистентності даних"""
    
    def test_transaction_history_matches_balance(self, authenticated_client, app, test_user):
        """Тест відповідності історії транзакцій балансу"""
        with app.app_context():
            from app.db import models
            
            # Початковий баланс
            initial_balance = models.get_user_coins(test_user["id"])

            # Виконуємо операції
            models.save_game_result(test_user["id"], "arithmetic", "easy", 100, 30.0, 10)
            models.update_user_coins(test_user["id"], 50)
            
            # Купуємо найдешевший товар
            items = models.get_all_shop_items()
            cheap_item = min(items, key=lambda x: x['price'])
            models.update_user_coins(test_user["id"], cheap_item['price'])
            models.purchase_item(test_user["id"], cheap_item['id'])
        
        # Отримуємо транзакції
        transactions_response = authenticated_client.get('/api/v1/transactions')
        transactions = json.loads(transactions_response.data)['transactions']
        
        # Підраховуємо баланс з транзакцій
        calculated_balance = initial_balance
        for t in transactions:
            calculated_balance += t['amount']
        
        
        # Отримуємо реальний баланс
        profile_response = authenticated_client.get('/api/v1/user/profile')
        actual_balance = json.loads(profile_response.data)['coins']
        
        assert calculated_balance == actual_balance, \
        f"Balance mismatch: calculated={calculated_balance}, actual={actual_balance}"
    
    def test_purchase_updates_all_related_data(self, authenticated_client, app, test_user):
        """Тест що покупка оновлює всі пов'язані дані"""
        with app.app_context():
            from app.db import models
            items = models.get_all_shop_items()
            item = items[0]
            
            models.update_user_coins(test_user["id"], item["price"])
            initial_coins = models.get_user_coins(test_user["id"])
        
        # Купуємо товар
        authenticated_client.post(f'/api/v1/shop/purchase/{item["id"]}')
        
        # 1. Перевіряємо баланс
        profile_response = authenticated_client.get('/api/v1/user/profile')
        profile_data = json.loads(profile_response.data)
        assert profile_data['coins'] == initial_coins - item['price']
        
        # 2. Перевіряємо історію покупок
        purchases_response = authenticated_client.get('/api/v1/shop/purchases')
        purchases = json.loads(purchases_response.data)['purchases']
        assert any(p['id'] == item['id'] for p in purchases)
        
        # 3. Перевіряємо транзакції
        transactions_response = authenticated_client.get('/api/v1/transactions')
        transactions = json.loads(transactions_response.data)['transactions']
        purchase_transaction = next(
            t for t in transactions
            if t['transaction_type'] == 'purchase'
        )
        assert purchase_transaction['amount'] == -item['price']
        
        # 4. Перевіряємо що товар позначений як куплений
        items_response = authenticated_client.get('/api/v1/shop/items')
        items_data = json.loads(items_response.data)['items']
        purchased_item = next(i for i in items_data if i['id'] == item['id'])
        assert purchased_item['is_purchased'] is True