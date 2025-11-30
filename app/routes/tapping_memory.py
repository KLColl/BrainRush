"""
BrainRush Tapping Memory Game Routes
Маршрути для гри Tapping Memory
"""

from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import current_user, login_required
from app.db.models import save_game_result, get_all_shop_items, user_has_purchased

tapping_memory_bp = Blueprint("tapping_memory", __name__, url_prefix="/game/tapping_memory")

def check_game_access(game_name):
    """Перевірка доступу користувача до гри"""
    free_games = ["arithmetic", "sequence_recall"]
    
    if game_name in free_games:
        return True
    
    # Знаходимо гру в магазині
    shop_items = get_all_shop_items()
    for item in shop_items:
        if item["item_type"] == "game" and item["name"].lower().replace(" ", "_") == game_name:
            return user_has_purchased(current_user.id, item["id"])
    
    return False

@tapping_memory_bp.route("/")
@login_required
def tapping_memory_game():
    """Відображення гри Tapping Memory (потрібна покупка)"""
    # Перевіряємо доступ
    if not check_game_access("tapping_memory"):
        flash("You need to purchase this game from the shop first!", "warning")
        return redirect(url_for("shop.shop_list"))
    
    return render_template("games/tapping_memory.html")

@tapping_memory_bp.route("/save_result", methods=["POST"])
@login_required
def save_result():
    """Збереження результату гри та нарахування монет"""
    data = request.get_json()
    print(data)
    if not data:
        return jsonify({"status": "error", "message": "No JSON data received"}), 400

    coins_earned = save_game_result(
        user_id = current_user.id,
        game_name = "tapping_memory",
        level = data.get("level", "unknown"),
        score = int(data.get("score", 0)),
        time_spent = float(data.get("time", 0.0)),
        rounds = int(data.get("rounds", 1)) 
    )
    
    try:
        return jsonify({
            "status": "success",
            "message": "Result saved successfully",
            "coins_earned": coins_earned
        })
    except Exception as e:
        print(f"Error saving result: {e}")
        return jsonify({"status": "error", "message": "Database error"}), 500