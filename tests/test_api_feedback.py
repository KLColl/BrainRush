"""
Integration тести для API відгуків
Тестування CRUD операцій та прав доступу
"""
import json
import pytest

class TestFeedbackListAPI:
    """Тести для отримання списку відгуків"""
    
    def test_get_empty_feedback(self, authenticated_client):
        """Тест порожнього списку відгуків"""
        response = authenticated_client.get('/api/v1/feedback')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'feedback' in data
        assert 'count' in data
        assert data['count'] == 0
    
    def test_get_feedback_list(self, authenticated_client, sample_feedback):
        """Тест отримання списку відгуків"""
        response = authenticated_client.get('/api/v1/feedback')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        assert data['count'] > 0
        assert len(data['feedback']) > 0
        
        # Перевірка структури
        fb = data['feedback'][0]
        assert 'id' in fb
        assert 'message' in fb
        assert 'created_at' in fb
    
    def test_get_feedback_with_limit(self, authenticated_client, app, test_user):
        """Тест обмеження кількості відгуків"""
        # Створюємо багато відгуків
        with app.app_context():
            from app.db import models
            for i in range(10):
                models.add_feedback(
                    test_user["id"],
                    test_user["username"],
                    "",
                    f"Message {i}"
                )
        
        response = authenticated_client.get('/api/v1/feedback?limit=5')
        data = json.loads(response.data)
        
        assert len(data['feedback']) == 5


class TestFeedbackCRUD:
    """Тести CRUD операцій для відгуків"""
    
    def test_create_feedback(self, authenticated_client):
        """Тест створення відгуку"""
        response = authenticated_client.post(
            '/api/v1/feedback',
            data=json.dumps({'message': 'Great app!'}),
            content_type='application/json'
        )
        
        assert response.status_code == 201
        data = json.loads(response.data)
        
        assert data['success'] is True
        assert 'feedback_id' in data
        assert data['feedback_id'] > 0
    
    def test_create_feedback_empty_message(self, authenticated_client):
        """Тест створення відгуку з порожнім повідомленням"""
        response = authenticated_client.post(
            '/api/v1/feedback',
            data=json.dumps({'message': ''}),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_create_feedback_missing_message(self, authenticated_client):
        """Тест створення відгуку без повідомлення"""
        response = authenticated_client.post(
            '/api/v1/feedback',
            data=json.dumps({}),
            content_type='application/json'
        )
        
        assert response.status_code == 400
    
    def test_get_feedback_by_id(self, authenticated_client, sample_feedback):
        """Тест отримання відгуку за ID"""
        response = authenticated_client.get(f'/api/v1/feedback/{sample_feedback["id"]}')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        assert data['id'] == sample_feedback['id']
        assert data['message'] == sample_feedback['message']
    
    def test_get_nonexistent_feedback(self, authenticated_client):
        """Тест отримання неіснуючого відгуку"""
        response = authenticated_client.get('/api/v1/feedback/99999')
        
        assert response.status_code == 404
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_update_own_feedback(self, authenticated_client, sample_feedback):
        """Тест оновлення власного відгуку"""
        new_message = "Updated message"
        response = authenticated_client.put(
            f'/api/v1/feedback/{sample_feedback["id"]}',
            data=json.dumps({'message': new_message}),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        
        # Перевіряємо що оновилось
        get_response = authenticated_client.get(f'/api/v1/feedback/{sample_feedback["id"]}')
        updated_data = json.loads(get_response.data)
        assert updated_data['message'] == new_message
    
    def test_update_feedback_empty_message(self, authenticated_client, sample_feedback):
        """Тест оновлення з порожнім повідомленням"""
        response = authenticated_client.put(
            f'/api/v1/feedback/{sample_feedback["id"]}',
            data=json.dumps({'message': ''}),
            content_type='application/json'
        )
        
        assert response.status_code == 400
    
    def test_delete_own_feedback(self, authenticated_client, sample_feedback):
        """Тест видалення власного відгуку"""
        response = authenticated_client.delete(f'/api/v1/feedback/{sample_feedback["id"]}')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        
        # Перевіряємо що видалено
        get_response = authenticated_client.get(f'/api/v1/feedback/{sample_feedback["id"]}')
        assert get_response.status_code == 404


class TestFeedbackPermissions:
    """Тести прав доступу до відгуків"""
    
    def test_update_others_feedback_denied(self, authenticated_client, app):
        """Тест оновлення чужого відгуку (має бути заборонено)"""
        # Створюємо відгук від іншого користувача
        with app.app_context():
            from app.db import models
            other_user_id = models.create_user("otheruser123", "password123")
            feedback_id = models.add_feedback(
                other_user_id,
                "otheruser123",
                "",
                "Other user's feedback"
            )
        
        response = authenticated_client.put(
            f'/api/v1/feedback/{feedback_id}',
            data=json.dumps({'message': 'Hacked!'}),
            content_type='application/json'
        )
        
        assert response.status_code == 403
    
    def test_delete_others_feedback_denied(self, authenticated_client, app):
        """Тест видалення чужого відгуку (має бути заборонено)"""
        with app.app_context():
            from app.db import models
            other_user_id = models.create_user("otheruser456", "password123")
            feedback_id = models.add_feedback(
                other_user_id,
                "otheruser456",
                "",
                "Other user's feedback"
            )
        
        response = authenticated_client.delete(f'/api/v1/feedback/{feedback_id}')
        
        assert response.status_code == 403
    
    def test_admin_can_delete_any_feedback(self, client, admin_user, sample_feedback):
        """Тест що адмін може видаляти будь-які відгуки"""
        # Логінимось як адмін
        client.post('/auth/login', data={
            'username': admin_user['username'],
            'password': admin_user['password']
        })
        
        response = client.delete(f'/api/v1/feedback/{sample_feedback["id"]}')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True