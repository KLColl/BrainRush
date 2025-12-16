import sqlite3
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
import os

DB_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "instance", "brainrush.db")
)

def get_db_connection():
    """Створення підключення до бази даних SQLite"""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH, detect_types=sqlite3.PARSE_DECLTYPES)
    conn.row_factory = sqlite3.Row
    return conn

# -----------------------
# ІНІЦІАЛІЗАЦІЯ
# -----------------------
def init_db():
    """Ініціалізація бази даних з усіма необхідними таблицями"""
    conn = get_db_connection()
    cur = conn.cursor()

    # Таблиця користувачів
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL DEFAULT 'user',
        balance INTEGER NOT NULL DEFAULT 0,
        coins INTEGER NOT NULL DEFAULT 300,
        theme TEXT NOT NULL DEFAULT 'light',
        current_avatar TEXT DEFAULT 'default',
        login_streak INTEGER DEFAULT 0,
        last_login_date TEXT,
        created_at TEXT NOT NULL
    )
    """)

    # Таблиця результатів ігор
    cur.execute("""
    CREATE TABLE IF NOT EXISTS game_results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        game_name TEXT NOT NULL,
        level TEXT NOT NULL,
        score INTEGER NOT NULL,
        time_spent REAL NOT NULL,
        rounds INTEGER NOT NULL DEFAULT 1,
        coins_earned INTEGER NOT NULL DEFAULT 0,
        created_at TEXT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )
    """)

    # Таблиця відгуків
    cur.execute("""
    CREATE TABLE IF NOT EXISTS feedback (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        name TEXT,
        email TEXT,
        message TEXT NOT NULL,
        created_at TEXT NOT NULL,
        updated_at TEXT,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )
    """)

    # Таблиця товарів магазину
    cur.execute("""
    CREATE TABLE IF NOT EXISTS shop_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        item_type TEXT NOT NULL,
        name TEXT NOT NULL,
        description TEXT,
        price INTEGER NOT NULL,
        is_active INTEGER NOT NULL DEFAULT 1,
        created_at TEXT NOT NULL
    )
    """)

    # Таблиця покупок користувачів
    cur.execute("""
    CREATE TABLE IF NOT EXISTS user_purchases (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        item_id INTEGER NOT NULL,
        purchased_at TEXT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (item_id) REFERENCES shop_items(id)
    )
    """)

    # Таблиця транзакцій
    cur.execute("""
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        amount INTEGER NOT NULL,
        transaction_type TEXT NOT NULL,
        description TEXT,
        created_at TEXT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )
    """)

    # Створення індексів для оптимізації
    cur.execute("CREATE INDEX IF NOT EXISTS idx_game_results_user_id ON game_results (user_id)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_game_results_game_name ON game_results (game_name)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_user_purchases_user_id ON user_purchases (user_id)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_transactions_user_id ON transactions (user_id)")

    # Додавання початкових товарів у магазин
    cur.execute("SELECT COUNT(*) FROM shop_items")
    if cur.fetchone()[0] == 0:
        default_items = [
            ('game', 'Color Rush', 'Test your color recognition speed', 50, 1),
            ('game', 'Tapping Memory', 'Remember and repeat the sequence', 75, 1),
            ('theme', 'Dark Theme Pro', 'Premium dark theme with custom colors', 100, 1),
            ('avatar', 'Golden Brain', 'Exclusive golden brain avatar', 200, 1),
        ]
        cur.executemany(
            "INSERT INTO shop_items (item_type, name, description, price, is_active, created_at) VALUES (?, ?, ?, ?, ?, ?)",
            [(t, n, d, p, a, datetime.utcnow().isoformat()) for t, n, d, p, a in default_items]
        )

    conn.commit()
    conn.close()

# -----------------------
# КОРИСТУВАЧІ
# -----------------------
def create_user(username: str, password: str):
    """Створення нового користувача з початковим балансом монет"""
    conn = get_db_connection()
    cur = conn.cursor()
    password_hash = generate_password_hash(password)
    cur.execute(
        "INSERT INTO users (username, password_hash, coins, created_at) VALUES (?, ?, ?, ?)",
        (username, password_hash, 300, datetime.utcnow().isoformat())
    )
    conn.commit()
    user_id = cur.lastrowid
    conn.close()
    return user_id

def get_user_by_username(username: str):
    """Отримати користувача за іменем (регістронезалежний пошук)"""
    conn = get_db_connection()
    user = conn.execute("SELECT * FROM users WHERE LOWER(username) = LOWER(?)", (username,)).fetchone()
    conn.close()
    return user

def get_user_by_id(user_id: int):
    """Отримати користувача за ID"""
    conn = get_db_connection()
    user = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    conn.close()
    return user

def set_user_role(user_id: int, role: str):
    """Встановити роль користувача (user/admin)"""
    conn = get_db_connection()
    conn.execute("UPDATE users SET role = ? WHERE id = ?", (role, user_id))
    conn.commit()
    conn.close()

def verify_user_password(user_row, password: str) -> bool:
    """Перевірити пароль користувача"""
    if not user_row:
        return False
    return check_password_hash(user_row["password_hash"], password)

def set_user_coins(user_id, new_amount):
    """Встановлює баланс монет користувача на конкретне значення (Критично для тестування)"""
    conn = get_db_connection()
    conn.execute("UPDATE users SET coins = ? WHERE id = ?", (new_amount, user_id))
    conn.commit()
    conn.close()

def update_user_coins(user_id: int, amount: int, description: str = ""):
    """Оновити баланс монет користувача та записати транзакцію"""
    conn = get_db_connection()
    conn.execute("UPDATE users SET coins = coins + ? WHERE id = ?", (amount, user_id))
    conn.execute(
        "INSERT INTO transactions (user_id, amount, transaction_type, description, created_at) VALUES (?, ?, ?, ?, datetime('now'))",
        (user_id, amount, "coins_update", description)
    )
    conn.commit()
    conn.close()

def get_user_coins(user_id: int):
    """Отримати поточний баланс монет користувача"""
    conn = get_db_connection()
    result = conn.execute("SELECT coins FROM users WHERE id = ?", (user_id,)).fetchone()
    conn.close()
    return result["coins"] if result else 0

def update_user_theme(user_id: int, theme: str):
    """Оновити тему користувача (light/dark)"""
    conn = get_db_connection()
    conn.execute("UPDATE users SET theme = ? WHERE id = ?", (theme, user_id))
    conn.commit()
    conn.close()

    # -----------------------
# МАГАЗИН
# -----------------------
def get_all_shop_items():
    """Отримати всі активні товари магазину"""
    conn = get_db_connection()
    items = conn.execute("SELECT * FROM shop_items WHERE is_active = 1 ORDER BY item_type, price").fetchall()
    conn.close()
    return items

def get_shop_item(item_id: int):
    """Отримати конкретний товар за ID"""
    conn = get_db_connection()
    item = conn.execute("SELECT * FROM shop_items WHERE id = ?", (item_id,)).fetchone()
    conn.close()
    return item

def user_has_purchased(user_id: int, item_id: int):
    """Перевірити, чи користувач вже купив товар"""
    conn = get_db_connection()
    result = conn.execute(
        "SELECT COUNT(*) as cnt FROM user_purchases WHERE user_id = ? AND item_id = ?",
        (user_id, item_id)
    ).fetchone()
    conn.close()
    return result["cnt"] > 0

def purchase_item(user_id: int, item_id: int):
    """Купити товар (перевірка балансу та унікальності покупки)"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Перевірка існування товару
    item = conn.execute("SELECT * FROM shop_items WHERE id = ?", (item_id,)).fetchone()
    if not item:
        conn.close()
        return False, "Item not found"
    
    # Перевірка балансу користувача
    user_coins = conn.execute("SELECT coins FROM users WHERE id = ?", (user_id,)).fetchone()["coins"]
    if user_coins < item["price"]:
        conn.close()
        return False, "Not enough coins"
    
    # Перевірка повторної покупки
    if user_has_purchased(user_id, item_id):
        conn.close()
        return False, "Already purchased"
    
    # Виконання покупки
    cur.execute("UPDATE users SET coins = coins - ? WHERE id = ?", (item["price"], user_id))
    cur.execute(
        "INSERT INTO user_purchases (user_id, item_id, purchased_at) VALUES (?, ?, ?)",
        (user_id, item_id, datetime.utcnow().isoformat())
    )
    cur.execute(
        "INSERT INTO transactions (user_id, amount, transaction_type, description, created_at) VALUES (?, ?, ?, ?, ?)",
        (user_id, -item["price"], "purchase", f"Purchased {item['name']}", datetime.utcnow().isoformat())
    )
    
    conn.commit()
    conn.close()
    return True, "Purchase successful"

def get_user_purchases(user_id: int):
    """Отримати історію покупок користувача"""
    conn = get_db_connection()
    purchases = conn.execute("""
        SELECT si.* FROM shop_items si
        JOIN user_purchases up ON si.id = up.item_id
        WHERE up.user_id = ?
        ORDER BY up.purchased_at DESC
    """, (user_id,)).fetchall()
    conn.close()
    return purchases

# -----------------------
# CRUD ОПЕРАЦІЇ З ВІДГУКАМИ
# -----------------------
def add_feedback(user_id, name, email, message):
    """Додати новий відгук"""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO feedback (user_id, name, email, message, created_at)
        VALUES (?, ?, ?, ?, ?)
    """, (user_id, name, email, message, datetime.utcnow().isoformat()))
    conn.commit()
    fid = cur.lastrowid
    conn.close()
    return fid

def get_feedbacks(limit=200):
    """Отримати всі відгуки з обмеженням"""
    conn = get_db_connection()
    rows = conn.execute("""
        SELECT * FROM feedback
        ORDER BY created_at DESC
        LIMIT ?
    """, (limit,)).fetchall()
    conn.close()
    return rows

def get_feedback(feedback_id):
    """Отримати конкретний відгук за ID"""
    conn = get_db_connection()
    row = conn.execute("SELECT * FROM feedback WHERE id = ?", (feedback_id,)).fetchone()
    conn.close()
    return row

def update_feedback(feedback_id, name, email, message):
    """Оновити існуючий відгук"""
    conn = get_db_connection()
    conn.execute("""
        UPDATE feedback
        SET name = ?, email = ?, message = ?, updated_at = ?
        WHERE id = ?
    """, (name, email, message, datetime.utcnow().isoformat(), feedback_id))
    conn.commit()
    conn.close()

def delete_feedback(feedback_id):
    """Видалити відгук"""
    conn = get_db_connection()
    conn.execute("DELETE FROM feedback WHERE id = ?", (feedback_id,))
    conn.commit()
    conn.close()

# -----------------------
# РЕЗУЛЬТАТИ ІГОР
# -----------------------
def save_game_result(user_id: int, game_name: str, level: str, score: int, time_spent: float, rounds: int = 1):
    """Зберегти результат гри та нарахувати монети (1 монета за 10 очок)"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Розрахунок зарахованих монет
    coins_earned = max(1, score // 10)
    
    cur.execute(
        """
        INSERT INTO game_results (user_id, game_name, level, score, time_spent, rounds, coins_earned, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (user_id, game_name, level, score, time_spent, rounds, coins_earned, datetime.utcnow().isoformat())
    )
    
    # Нарахування монет користувачу
    cur.execute("UPDATE users SET coins = coins + ? WHERE id = ?", (coins_earned, user_id))
    
    # Запис транзакції
    cur.execute(
        "INSERT INTO transactions (user_id, amount, transaction_type, description, created_at) VALUES (?, ?, ?, ?, ?)",
        (user_id, coins_earned, "game_reward", f"Earned in {game_name}", datetime.utcnow().isoformat())
    )
    
    conn.commit()
    conn.close()
    return coins_earned

def get_distinct_games_for_user(user_id: int):
    """Отримати список унікальних ігор користувача"""
    conn = get_db_connection()
    rows = conn.execute("SELECT DISTINCT game_name FROM game_results WHERE user_id = ?", (user_id,)).fetchall()
    conn.close()
    return [r["game_name"] for r in rows]

def get_stats_for_game(user_id: int, game_name: str):
    """Отримати статистику користувача для конкретної гри"""
    conn = get_db_connection()
    rows = conn.execute(
        """
        SELECT level, rounds,
               COUNT(id) AS rounds_played,
               SUM(score) AS total_score,
               AVG(time_spent) AS avg_time,
               SUM(coins_earned) AS total_coins
        FROM game_results
        WHERE user_id = ? AND LOWER(game_name) = LOWER(?)
        GROUP BY level, rounds
        """,
        (user_id, game_name)
    ).fetchall()
    conn.close()
    return rows

def get_total_games(user_id: int):
    """Отримати загальну кількість зіграних ігор"""
    conn = get_db_connection()
    value = conn.execute("SELECT COUNT(*) as cnt FROM game_results WHERE user_id = ?", (user_id,)).fetchone()["cnt"]
    conn.close()
    return value

def get_total_points(user_id: int):
    """Отримати загальну кількість очок користувача"""
    conn = get_db_connection()
    value = conn.execute("SELECT COALESCE(SUM(score), 0) AS s FROM game_results WHERE user_id = ?", (user_id,)).fetchone()["s"]
    conn.close()
    return value

def get_total_coins_earned(user_id: int):
    """Отримати загальну кількість зароблених монет"""
    conn = get_db_connection()
    value = conn.execute("SELECT COALESCE(SUM(coins_earned), 0) AS c FROM game_results WHERE user_id = ?", (user_id,)).fetchone()["c"]
    conn.close()
    return value

# -----------------------
# ТРАНЗАКЦІЇ
# -----------------------
def get_user_transactions(user_id: int, limit=50):
    """Отримати історію транзакцій користувача"""
    conn = get_db_connection()
    transactions = conn.execute("""
        SELECT * FROM transactions
        WHERE user_id = ?
        ORDER BY created_at DESC
        LIMIT ?
    """, (user_id, limit)).fetchall()
    conn.close()
    return transactions

# -----------------------
# LEADERBOARDS
# -----------------------
def get_global_leaderboard(limit=10):
    """Топ користувачів за монетами"""
    conn = get_db_connection()
    rows = conn.execute(
        "SELECT username, coins, current_avatar FROM users ORDER BY coins DESC LIMIT ?", 
        (limit,)
    ).fetchall()
    conn.close()
    return rows

def get_game_leaderboard(game_name, limit=10):
    """Топ кращих результатів у конкретній грі"""
    conn = get_db_connection()
    rows = conn.execute("""
        SELECT u.username, u.current_avatar, MAX(gr.score) as max_score
        FROM game_results gr
        JOIN users u ON gr.user_id = u.id
        WHERE gr.game_name = ?
        GROUP BY u.id
        ORDER BY max_score DESC
        LIMIT ?
    """, (game_name, limit)).fetchall()
    conn.close()
    return rows

# -----------------------
# DAILY BONUS
# -----------------------
def check_daily_bonus(user_id):
    """Перевірка та нарахування щоденного бонусу"""
    conn = get_db_connection()
    user = conn.execute("SELECT last_login_date, login_streak FROM users WHERE id = ?", (user_id,)).fetchone()
    
    today = datetime.utcnow().date().isoformat()
    last_login = user["last_login_date"]
    streak = user["login_streak"] or 0
    bonus_amount = 0
    message = None

    if last_login != today:
        # Якщо останній вхід був вчора - збільшуємо стрік
        last_date = datetime.strptime(last_login, "%Y-%m-%d").date() if last_login else None
        yesterday = datetime.utcnow().date() - timedelta(days=1)
        
        if last_date == yesterday:
            streak += 1
        else:
            streak = 1 # Скидання стріку, якщо пропустив день
            
        # Нарахування (10 + 5 за кожен день стріку, макс 50)
        bonus_amount = min(10 + (streak * 5), 50)
        
        conn.execute("""
            UPDATE users 
            SET coins = coins + ?, login_streak = ?, last_login_date = ? 
            WHERE id = ?
        """, (bonus_amount, streak, today, user_id))
        
        conn.execute("""
            INSERT INTO transactions (user_id, amount, transaction_type, description, created_at) 
            VALUES (?, ?, 'daily_bonus', ?, ?)
        """, (user_id, bonus_amount, f"Daily bonus (Day {streak})", datetime.utcnow().isoformat()))
        
        conn.commit()
        message = f"Daily Bonus! +{bonus_amount} coins (Streak: {streak} days)"
    
    conn.close()
    return message

# -----------------------
# AVATAR
# -----------------------
def equip_avatar(user_id, avatar_name):
    """Встановити активний аватар"""
    conn = get_db_connection()
    conn.execute("UPDATE users SET current_avatar = ? WHERE id = ?", (avatar_name, user_id))
    conn.commit()
    conn.close()

# -----------------------
# SETTINGS
# -----------------------
def change_user_password(user_id, new_password_hash):
    """Змінити пароль користувача"""
    conn = get_db_connection()
    conn.execute("UPDATE users SET password_hash = ? WHERE id = ?", (new_password_hash, user_id))
    conn.commit()
    conn.close()

def delete_user_account(user_id):
    """Повне видалення акаунту"""
    conn = get_db_connection()
    # SQLite з FK constraints ON має видалити каскадно, але для надійності:
    conn.execute("DELETE FROM game_results WHERE user_id = ?", (user_id,))
    conn.execute("DELETE FROM user_purchases WHERE user_id = ?", (user_id,))
    conn.execute("DELETE FROM transactions WHERE user_id = ?", (user_id,))
    conn.execute("DELETE FROM feedback WHERE user_id = ?", (user_id,))
    conn.execute("DELETE FROM users WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()