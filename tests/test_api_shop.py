"""
Integration тести для API магазину
Тестування покупок, транзакцій та балансу монет
"""
import json
import pytest

class TestShopItemsAPI:
    """Тести для отримання товарів"""
    
    def test_get_shop_items(self, authenticated_client):
        """Тест отримання списку товарів"""
        response = authenticated_client.get('/api/v1/shop/items')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        assert 'items' in data
        assert 'user_coins' in data
        assert len(data['items']) > 0
        
        # Перевірка структури товарів
        item = data['items'][0]
        assert 'id' in item
        assert 'name' in item
        assert 'price' in item
        assert 'item_type' in item
        assert 'is_purchased' in item
    
    def test_get_shop_items_with_purchases(self, authenticated_client, app, test_user):
        """Тест відображення куплених товарів"""
        with app.app_context():
            from app.db import models
            items = models.get_all_shop_items()
            item = items[0]
            
            # Купуємо товар
            models.update_user_coins(test_user["id"], item["price"])
            models.purchase_item(test_user["id"], item["id"])
        
        response = authenticated_client.get('/api/v1/shop/items')
        data = json.loads(response.data)
        
        # Перевіряємо що товар позначений як куплений
        purchased_items = [i for i in data['items'] if i['is_purchased']]
        assert len(purchased_items) > 0
    
    def test_get_single_item(self, authenticated_client, app):
        """Тест отримання окремого товару"""
        with app.app_context():
            from app.db import models
            items = models.get_all_shop_items()
            item_id = items[0]["id"]
        
        response = authenticated_client.get(f'/api/v1/shop/item/{item_id}')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['id'] == item_id


class TestPurchaseAPI:
    """Тести для покупки товарів"""
    
    def test_purchase_item_success(self, authenticated_client, app, test_user):
        """Тест успішної покупки"""
        with app.app_context():
            from app.db import models
            items = models.get_all_shop_items()
            item = items[0]
            
            # Додаємо достатньо монет
            models.update_user_coins(test_user["id"], item["price"])
            initial_coins = models.get_user_coins(test_user["id"])
        
        response = authenticated_client.post(f'/api/v1/shop/purchase/{item["id"]}')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        assert data['success'] is True
        assert data['remaining_coins'] == initial_coins - item["price"]
    
    def test_purchase_insufficient_coins(self, authenticated_client, app, test_user):
        """Тест покупки без достатньої кількості монет"""
        with app.app_context():
            from app.db import models
            items = models.get_all_shop_items()
            expensive_item = max(items, key=lambda x: x["price"])
        
            models.set_user_coins(test_user["id"], expensive_item["price"] - 1)
            
        response = authenticated_client.post(
            f'/api/v1/shop/purchase/{expensive_item["id"]}'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'not enough' in data['error'].lower()
    
    def test_purchase_duplicate_item(self, authenticated_client, app, test_user):
        """Тест повторної покупки товару"""
        with app.app_context():
            from app.db import models
            items = models.get_all_shop_items()
            item = items[0]
            
            # Купуємо товар вперше
            models.update_user_coins(test_user["id"], item["price"] * 2)
            models.purchase_item(test_user["id"], item["id"])
        
        # Намагаємось купити вдруге
        response = authenticated_client.post(f'/api/v1/shop/purchase/{item["id"]}')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'already' in data['error'].lower()
    
    def test_purchase_nonexistent_item(self, authenticated_client):
        """Тест покупки неіснуючого товару"""
        response = authenticated_client.post('/api/v1/shop/purchase/99999')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False


class TestPurchaseHistoryAPI:
    """Тести для історії покупок"""
    
    def test_get_empty_purchases(self, authenticated_client):
        """Тест порожньої історії покупок"""
        response = authenticated_client.get('/api/v1/shop/purchases')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'purchases' in data
        assert len(data['purchases']) == 0
    
    def test_get_purchases_with_history(self, authenticated_client, app, test_user):
        """Тест історії з покупками"""
        with app.app_context():
            from app.db import models
            items = models.get_all_shop_items()[:2]  # Перші 2 товари
            
            # Купуємо товари
            for item in items:
                models.update_user_coins(test_user["id"], item["price"])
                models.purchase_item(test_user["id"], item["id"])
        
        response = authenticated_client.get('/api/v1/shop/purchases')
        data = json.loads(response.data)
        
        assert len(data['purchases']) == 2
        
        # Перевірка структури
        purchase = data['purchases'][0]
        assert 'id' in purchase
        assert 'name' in purchase
        assert 'price' in purchase


class TestShopTransactionsIntegration:
    """Integration тести для транзакцій магазину"""
    
    def test_purchase_creates_transaction(self, authenticated_client, app, test_user):
        """Тест створення транзакції при покупці"""
        with app.app_context():
            from app.db import models
            items = models.get_all_shop_items()
            item = items[0]
            
            models.update_user_coins(test_user["id"], item["price"])
        
        # Купуємо товар
        authenticated_client.post(f'/api/v1/shop/purchase/{item["id"]}')
        
        # Перевіряємо транзакції
        response = authenticated_client.get('/api/v1/transactions')
        data = json.loads(response.data)
        
        # Знаходимо транзакцію покупки
        purchase_transaction = next(
            (t for t in data['transactions'] if t['transaction_type'] == 'purchase'),
            None
        )
        
        assert purchase_transaction is not None
        assert purchase_transaction['amount'] == -item["price"]
    
    def test_coins_balance_after_purchase(self, authenticated_client, app, test_user):
        """Тест балансу монет після покупки"""
        with app.app_context():
            from app.db import models
            items = models.get_all_shop_items()
            item = items[0]
            
            initial_coins = 200
            models.set_user_coins(test_user["id"], initial_coins)
        
        # Купуємо товар
        authenticated_client.post(f'/api/v1/shop/purchase/{item["id"]}')
        
        # Перевіряємо баланс
        response = authenticated_client.get('/api/v1/user/profile')
        data = json.loads(response.data)
        
        expected_coins = initial_coins - item["price"]
        assert data['coins'] == expected_coins