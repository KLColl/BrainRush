# Звіт про тестування BrainRush API

**Дата створення:** 22.12.2025  
**Дата оновлення:** 22.12.2025

---

## Огляд API

BrainRush API надає RESTful інтерфейс для взаємодії з платформою когнітивних тренувань. API підтримує операції з користувачами, магазином, відгуками та статистикою ігор.

**Base URL:** `http://localhost:5000/api/v1`

**Документація:** `http://localhost:5000/api/docs` (Swagger UI)

**Автентифікація:** Cookie-based authentication (Flask session)

---

## Endpoints API

### 1. Отримати профіль користувача

- **URL:** `/api/v1/user/profile`
- **Метод:** `GET`
- **Опис:** Повертає повну інформацію про профіль авторизованого користувача
- **Автентифікація:** Обов'язкова

**Приклад запиту:**
```http
GET /api/v1/user/profile HTTP/1.1
Host: localhost:5000
Cookie: session=...
```

**Приклад відповіді:**
```json
{
  "id": 1,
  "username": "testuser",
  "role": "user",
  "coins": 450,
  "theme": "dark",
  "total_games": 15,
  "total_points": 2340,
  "total_coins_earned": 234,
  "created_at": "2025-12-01T10:30:00"
}
```

**Скріншот з Postman:**  
![Get User Profile](screenshots/user_profile.png)

---

### 2. Отримати користувача за ID

- **URL:** `/api/v1/user/{user_id}`
- **Метод:** `GET`
- **Опис:** Повертає публічну інформацію про користувача за його ID
- **Автентифікація:** Обов'язкова

**Параметри:**
- `user_id` (path) - ID користувача (integer)

**Приклад запиту:**
```http
GET /api/v1/user/5 HTTP/1.1
Host: localhost:5000
Cookie: session=...
```

**Приклад відповіді:**
```json
{
  "id": 5,
  "username": "player123",
  "total_games": 25,
  "total_points": 4500,
  "created_at": "2025-11-15T14:20:00"
}
```

**Скріншот з Postman:**  
![Get User by ID](screenshots/user_by_id.png)

---

### 3. Змінити тему користувача

- **URL:** `/api/v1/user/theme`
- **Метод:** `POST`
- **Опис:** Змінює тему інтерфейсу користувача (світла/темна)
- **Автентифікація:** Обов'язкова

**Приклад запиту:**
```json
{
  "theme": "dark"
}
```

**Приклад відповіді:**
```json
{
  "success": true,
  "theme": "dark"
}
```

**Скріншот з Postman:**  
![Update Theme](screenshots/update_theme.png)

---

### 4. Отримати всі товари магазину

- **URL:** `/api/v1/shop/items`
- **Метод:** `GET`
- **Опис:** Повертає список всіх активних товарів у магазині з інформацією про покупки користувача
- **Автентифікація:** Обов'язкова

**Приклад відповіді:**
```json
{
  "items": [
    {
      "id": 1,
      "item_type": "game",
      "name": "Color Rush",
      "description": "Test your color recognition speed",
      "price": 50,
      "is_purchased": false,
      "created_at": "2025-12-01T10:00:00"
    },
    {
      "id": 2,
      "item_type": "theme",
      "name": "Dark Theme Pro",
      "description": "Premium dark theme",
      "price": 100,
      "is_purchased": true,
      "created_at": "2025-12-01T10:00:00"
    }
  ],
  "user_coins": 450
}
```

**Скріншот з Postman:**  
![Get Shop Items](screenshots/shop_items.png)

---

### 5. Купити товар

- **URL:** `/api/v1/shop/purchase/{item_id}`
- **Метод:** `POST`
- **Опис:** Здійснює покупку товару з магазину
- **Автентифікація:** Обов'язкова

**Параметри:**
- `item_id` (path) - ID товару (integer)

**Приклад успішної відповіді:**
```json
{
  "success": true,
  "message": "Purchase successful",
  "remaining_coins": 400
}
```

**Приклад помилки (недостатньо монет):**
```json
{
  "success": false,
  "error": "Not enough coins"
}
```

**Скріншот з Postman:**  
![Purchase Item](screenshots/purchase_item.png)

---

### 6. Отримати історію покупок

- **URL:** `/api/v1/shop/purchases`
- **Метод:** `GET`
- **Опис:** Повертає список усіх покупок користувача
- **Автентифікація:** Обов'язкова

**Приклад відповіді:**
```json
{
  "purchases": [
    {
      "id": 1,
      "name": "Color Rush",
      "item_type": "game",
      "price": 50
    },
    {
      "id": 3,
      "name": "Dark Theme Pro",
      "item_type": "theme",
      "price": 100
    }
  ]
}
```

**Скріншот з Postman:**  
![Get Purchases](screenshots/purchases.png)

---

### 7. Отримати всі відгуки

- **URL:** `/api/v1/feedback`
- **Метод:** `GET`
- **Опис:** Повертає список відгуків користувачів
- **Автентифікація:** Обов'язкова

**Query параметри:**
- `limit` (опціонально) - Кількість відгуків (default: 50)

**Приклад відповіді:**
```json
{
  "feedback": [
    {
      "id": 1,
      "user_id": 5,
      "name": "player123",
      "email": "",
      "message": "Чудовий додаток!",
      "created_at": "2025-12-15T12:30:00",
      "updated_at": null
    }
  ],
  "count": 1
}
```

**Скріншот з Postman:**  
![Get Feedback](screenshots/feedback_list.png)

---

### 8. Створити новий відгук

- **URL:** `/api/v1/feedback`
- **Метод:** `POST`
- **Опис:** Створює новий відгук від користувача
- **Автентифікація:** Обов'язкова

**Приклад запиту:**
```json
{
  "message": "Чудовий додаток для тренування мозку!"
}
```

**Приклад відповіді:**
```json
{
  "success": true,
  "feedback_id": 10,
  "message": "Відгук успішно створено"
}
```

**Скріншот з Postman:**  
![Create Feedback](screenshots/create_feedback.png)

---

### 9. Оновити відгук

- **URL:** `/api/v1/feedback/{feedback_id}`
- **Метод:** `PUT`
- **Опис:** Оновлює існуючий відгук (тільки власний або адміністратор)
- **Автентифікація:** Обов'язкова

**Параметри:**
- `feedback_id` (path) - ID відгуку (integer)

**Приклад запиту:**
```json
{
  "message": "Оновлений текст відгуку"
}
```

**Приклад відповіді:**
```json
{
  "success": true,
  "message": "Відгук успішно оновлено"
}
```

**Скріншот з Postman:**  
![Update Feedback](screenshots/update_feedback.png)

---

### 10. Видалити відгук

- **URL:** `/api/v1/feedback/{feedback_id}`
- **Метод:** `DELETE`
- **Опис:** Видаляє відгук (тільки власний або адміністратор)
- **Автентифікація:** Обов'язкова

**Параметри:**
- `feedback_id` (path) - ID відгуку (integer)

**Приклад відповіді:**
```json
{
  "success": true,
  "message": "Відгук успішно видалено"
}
```

**Скріншот з Postman:**  
![Delete Feedback](screenshots/delete_feedback.png)

---

### 11. Отримати список ігор користувача

- **URL:** `/api/v1/stats/games`
- **Метод:** `GET`
- **Опис:** Повертає список ігор, у які грав користувач
- **Автентифікація:** Обов'язкова

**Приклад відповіді:**
```json
{
  "games": [
    "arithmetic",
    "color_rush",
    "sequence_recall"
  ]
}
```

**Скріншот з Postman:**  
![Get User Games](screenshots/user_games.png)

---

### 12. Отримати статистику гри

- **URL:** `/api/v1/stats/game/{game_name}`
- **Метод:** `GET`
- **Опис:** Повертає детальну статистику для конкретної гри
- **Автентифікація:** Обов'язкова

**Параметри:**
- `game_name` (path) - Назва гри (string)

**Приклад відповіді:**
```json
{
  "game": "arithmetic",
  "stats": [
    {
      "level": "easy",
      "rounds": 10,
      "rounds_played": 5,
      "total_score": 450,
      "avg_time": 12.5,
      "total_coins": 45
    },
    {
      "level": "medium",
      "rounds": 10,
      "rounds_played": 3,
      "total_score": 680,
      "avg_time": 18.3,
      "total_coins": 68
    }
  ]
}
```

**Скріншот з Postman:**  
![Get Game Stats](screenshots/game_stats.png)

---

### 13. Отримати історію транзакцій

- **URL:** `/api/v1/transactions`
- **Метод:** `GET`
- **Опис:** Повертає історію всіх транзакцій користувача
- **Автентифікація:** Обов'язкова

**Query параметри:**
- `limit` (опціонально) - Кількість транзакцій (default: 50)

**Приклад відповіді:**
```json
{
  "transactions": [
    {
      "id": 15,
      "amount": 45,
      "transaction_type": "game_reward",
      "description": "Earned in arithmetic",
      "created_at": "2025-12-20T15:30:00"
    },
    {
      "id": 14,
      "amount": -50,
      "transaction_type": "purchase",
      "description": "Purchased Color Rush",
      "created_at": "2025-12-19T10:15:00"
    }
  ],
  "count": 2
}
```

**Скріншот з Postman:**  
![Get Transactions](screenshots/transactions.png)

## Обробка помилок

API використовує стандартні HTTP коди стану для позначення успіху або помилки запиту.

### Коди відповідей

#### 2xx - Успіх
- **200 OK** - Запит успішно оброблено
- **201 Created** - Ресурс успішно створено (використовується при створенні відгуків)

#### 4xx - Помилки клієнта
- **400 Bad Request**
    - Некоректний формат даних у запиті
    - Відсутні обов'язкові поля
    - Порожнє повідомлення у відгуку
    - Приклад: `{"error": "Повідомлення не може бути порожнім"}`

- **401 Unauthorized**
    - Відсутня автентифікація
    - Неавторизований доступ до захищених endpoints
    - Приклад: `{"error": "Потрібна автентифікація"}`

- **403 Forbidden**
    - Недостатньо прав для виконання операції
    - Спроба редагувати чужий відгук
    - Приклад: `{"error": "Доступ заборонено"}`

- **404 Not Found**
    - Запитуваний ресурс не знайдено
    - Неіснуючий ID користувача, товару, відгуку
    - Приклад: `{"error": "Користувача не знайдено"}`

#### 5xx - Помилки сервера
- **500 Internal Server Error**
    - Непередбачена помилка на сервері
    - Помилка бази даних
    - Приклад: `{"error": "Внутрішня помилка сервера"}`

### Формат помилок

Всі помилки повертаються у JSON форматі:

```json
{
  "error": "Опис помилки",
  "success": false  // для деяких endpoints
}
```

### Приклади обробки помилок

**Недостатньо монет для покупки:**
```json
{
  "success": false,
  "error": "Not enough coins"
}
```

**Товар вже придбано:**
```json
{
  "success": false,
  "error": "Already purchased"
}
```

**Товар не знайдено:**
```json
{
  "error": "Товар не знайдено"
}
```

## Додаткова інформація

**Swagger UI:** Доступний за адресою `http://localhost:5000/api/docs`

**Postman колекція:** Доступна у файлі `BrainRush_API.postman_collection.json`

**OpenAPI специфікація:** Доступна у файлі `swagger.yaml`

---