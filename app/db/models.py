import sqlite3
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import os

DB_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "instance", "brainrush.db")
)

def get_db_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH, detect_types=sqlite3.PARSE_DECLTYPES)
    conn.row_factory = sqlite3.Row
    return conn

# -----------------------
# INITIALIZATION
# -----------------------
def init_db():
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL DEFAULT 'user',
        balance INTEGER NOT NULL DEFAULT 0,
        created_at TEXT NOT NULL
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS game_results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        game_name TEXT NOT NULL,
        level TEXT NOT NULL,
        score INTEGER NOT NULL,
        time_spent REAL NOT NULL,
        rounds INTEGER NOT NULL DEFAULT 1,
        created_at TEXT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )
    """)

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

    cur.execute("CREATE INDEX IF NOT EXISTS idx_game_results_user_id ON game_results (user_id)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_game_results_game_name ON game_results (game_name)")

    conn.commit()
    conn.close()

# -----------------------
# USERS
# -----------------------
def create_user(username: str, password: str):
    conn = get_db_connection()
    cur = conn.cursor()
    password_hash = generate_password_hash(password)
    cur.execute(
        "INSERT INTO users (username, password_hash, created_at) VALUES (?, ?, ?)",
        (username, password_hash, datetime.utcnow().isoformat())
    )
    conn.commit()
    user_id = cur.lastrowid
    conn.close()
    return user_id

def get_user_by_username(username: str):
    conn = get_db_connection()
    user = conn.execute("SELECT * FROM users WHERE LOWER(username) = LOWER(?)", (username,)).fetchone()
    conn.close()
    return user

def get_user_by_id(user_id: int):
    conn = get_db_connection()
    user = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    conn.close()
    return user

def set_user_role(user_id: int, role: str):
    conn = get_db_connection()
    conn.execute("UPDATE users SET role = ? WHERE id = ?", (role, user_id))
    conn.commit()
    conn.close()

def verify_user_password(user_row, password: str) -> bool:
    if not user_row:
        return False
    return check_password_hash(user_row["password_hash"], password)

# -----------------------
# CRUD FEEDBACK OPERATIONS
# -----------------------

def add_feedback(user_id, name, email, message):
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
    conn = get_db_connection()
    rows = conn.execute("""
        SELECT * FROM feedback
        ORDER BY created_at DESC
        LIMIT ?
    """, (limit,)).fetchall()
    conn.close()
    return rows


def get_feedback(feedback_id):
    conn = get_db_connection()
    row = conn.execute("SELECT * FROM feedback WHERE id = ?", (feedback_id,)).fetchone()
    conn.close()
    return row


def update_feedback(feedback_id, name, email, message):
    conn = get_db_connection()
    conn.execute("""
        UPDATE feedback
        SET name = ?, email = ?, message = ?, updated_at = ?
        WHERE id = ?
    """, (name, email, message, datetime.utcnow().isoformat(), feedback_id))
    conn.commit()
    conn.close()


def delete_feedback(feedback_id):
    conn = get_db_connection()
    conn.execute("DELETE FROM feedback WHERE id = ?", (feedback_id,))
    conn.commit()
    conn.close()

# -----------------------
# GAME RESULTS
# -----------------------
def save_game_result(user_id: int, game_name: str, level: str, score: int, time_spent: float, rounds: int = 1):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO game_results (user_id, game_name, level, score, time_spent, rounds, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (user_id, game_name, level, score, time_spent, rounds, datetime.utcnow().isoformat())
    )
    conn.commit()
    conn.close()

def get_distinct_games_for_user(user_id: int):
    conn = get_db_connection()
    rows = conn.execute("SELECT DISTINCT game_name FROM game_results WHERE user_id = ?", (user_id,)).fetchall()
    conn.close()
    return [r["game_name"] for r in rows]

def get_stats_for_game(user_id: int, game_name: str):
    conn = get_db_connection()
    rows = conn.execute(
        """
        SELECT level, rounds,
               COUNT(id) AS rounds_played,
               SUM(score) AS total_score,
               AVG(time_spent) AS avg_time
        FROM game_results
        WHERE user_id = ? AND LOWER(game_name) = LOWER(?)
        GROUP BY level, rounds
        """,
        (user_id, game_name)
    ).fetchall()
    conn.close()
    return rows

def get_total_games(user_id: int):
    conn = get_db_connection()
    value = conn.execute("SELECT COUNT(*) as cnt FROM game_results WHERE user_id = ?", (user_id,)).fetchone()["cnt"]
    conn.close()
    return value

def get_total_points(user_id: int):
    conn = get_db_connection()
    value = conn.execute("SELECT COALESCE(SUM(score), 0) AS s FROM game_results WHERE user_id = ?", (user_id,)).fetchone()["s"]
    conn.close()
    return value
