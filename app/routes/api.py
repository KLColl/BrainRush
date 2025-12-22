from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from functools import wraps
from app.db.models import (
    get_user_by_id,
    get_all_shop_items,
    get_shop_item,
    purchase_item,
    get_user_purchases,
    get_user_coins,
    get_feedbacks,
    add_feedback,
    get_feedback,
    update_feedback,
    delete_feedback,
    save_game_result,
    get_stats_for_game,
    get_total_games,
    get_total_points,
    get_total_coins_earned,
    get_distinct_games_for_user,
    get_user_transactions
)

api_bp = Blueprint("api", __name__, url_prefix="/api/v1")

# Декоратор для API автентифікації
def api_login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            # Залишаємо повідомлення англійською для клієнта, коментар українською
            return jsonify({"error": "Authentication required"}), 401
        return f(*args, **kwargs)
    return decorated_function

# Обробка помилок
@api_bp.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Resource not found"}), 404

@api_bp.errorhandler(400)
def bad_request(error):
    return jsonify({"error": "Bad request"}), 400

@api_bp.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500

# -----------------------
# ЕНДПОІНТИ КОРИСТУВАЧА
# -----------------------
@api_bp.route("/user/profile", methods=["GET"])
@api_login_required
def get_user_profile():
    """Отримати профіль поточного користувача"""
    user = get_user_by_id(current_user.id)
    return jsonify({
        "id": user["id"],
        "username": user["username"],
        "role": user["role"],
        "coins": user["coins"],
        "theme": user["theme"],
        "total_games": get_total_games(current_user.id),
        "total_points": get_total_points(current_user.id),
        "total_coins_earned": get_total_coins_earned(current_user.id),
        "created_at": user["created_at"]
    }), 200

@api_bp.route("/user/<int:user_id>", methods=["GET"])
@api_login_required
def get_user(user_id):
    """Отримати дані користувача за його ID"""
    user = get_user_by_id(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify({
        "id": user["id"],
        "username": user["username"],
        "total_games": get_total_games(user_id),
        "total_points": get_total_points(user_id),
        "created_at": user["created_at"]
    }), 200

# -----------------------
# ЕНДПОІНТИ МАГАЗИНУ
# -----------------------
@api_bp.route("/shop/items", methods=["GET"])
@api_login_required
def get_shop_items():
    """Отримати список усіх доступних товарів у магазині"""
    items = get_all_shop_items()
    user_purchases = get_user_purchases(current_user.id)
    purchased_ids = [p["id"] for p in user_purchases]

    result = []
    for item in items:
        result.append({
            "id": item["id"],
            "item_type": item["item_type"],
            "name": item["name"],
            "description": item["description"],
            "price": item["price"],
            "is_purchased": item["id"] in purchased_ids,
            "created_at": item["created_at"]
        })

    return jsonify({
        "items": result,
        "user_coins": get_user_coins(current_user.id)
    }), 200

@api_bp.route("/shop/item/<int:item_id>", methods=["GET"])
@api_login_required
def get_item(item_id):
    """Отримати детальну інформацію про конкретний товар"""
    item = get_shop_item(item_id)
    if not item:
        return jsonify({"error": "Item not found"}), 404

    return jsonify({
        "id": item["id"],
        "item_type": item["item_type"],
        "name": item["name"],
        "description": item["description"],
        "price": item["price"],
        "is_active": item["is_active"],
        "created_at": item["created_at"]
    }), 200

@api_bp.route("/shop/purchase/<int:item_id>", methods=["POST"])
@api_login_required
def api_purchase_item(item_id):
    """Здійснити покупку товару"""
    success, message = purchase_item(current_user.id, item_id)

    if success:
        return jsonify({
            "success": True,
            "message": message,
            "remaining_coins": get_user_coins(current_user.id)
        }), 200
    else:
        return jsonify({
            "success": False,
            "error": message
        }), 400

@api_bp.route("/shop/purchases", methods=["GET"])
@api_login_required
def get_purchases():
    """Отримати історію куплених товарів користувача"""
    purchases = get_user_purchases(current_user.id)

    result = []
    for p in purchases:
        result.append({
            "id": p["id"],
            "name": p["name"],
            "item_type": p["item_type"],
            "price": p["price"]
        })

    return jsonify({"purchases": result}), 200

# -----------------------
# ЕНДПОІНТИ ВІДГУКІВ
# -----------------------
@api_bp.route("/feedback", methods=["GET"])
@api_login_required
def api_get_feedbacks():
    """Отримати список усіх відгуків з можливістю лімітування"""
    limit = request.args.get("limit", 50, type=int)
    feedbacks = get_feedbacks(limit)

    result = []
    for fb in feedbacks:
        result.append({
            "id": fb["id"],
            "user_id": fb["user_id"],
            "name": fb["name"],
            "email": fb["email"],
            "message": fb["message"],
            "created_at": fb["created_at"],
            "updated_at": fb["updated_at"]
        })

    return jsonify({"feedback": result, "count": len(result)}), 200

@api_bp.route("/feedback/<int:feedback_id>", methods=["GET"])
@api_login_required
def api_get_feedback(feedback_id):
    """Отримати конкретний відгук за його ідентифікатором"""
    fb = get_feedback(feedback_id)
    if not fb:
        return jsonify({"error": "Feedback not found"}), 404

    return jsonify({
        "id": fb["id"],
        "user_id": fb["user_id"],
        "name": fb["name"],
        "email": fb["email"],
        "message": fb["message"],
        "created_at": fb["created_at"],
        "updated_at": fb["updated_at"]
    }), 200

@api_bp.route("/feedback", methods=["POST"])
@api_login_required
def api_create_feedback():
    """Створити новий відгук від імені поточного користувача"""
    data = request.get_json()

    if not data or "message" not in data:
        return jsonify({"error": "Message is required"}), 400

    message = data["message"].strip()
    if not message:
        return jsonify({"error": "Message cannot be empty"}), 400

    feedback_id = add_feedback(
        user_id=current_user.id,
        name=current_user.username,
        email="",
        message=message
    )

    return jsonify({
        "success": True,
        "feedback_id": feedback_id,
        "message": "Feedback successfully created"
    }), 201

@api_bp.route("/feedback/<int:feedback_id>", methods=["PUT"])
@api_login_required
def api_update_feedback(feedback_id):
    """Оновити текст існуючого відгуку"""
    fb = get_feedback(feedback_id)
    if not fb:
        return jsonify({"error": "Feedback not found"}), 404

    # Перевірка прав: власник відгуку або адміністратор
    if fb["user_id"] != current_user.id and current_user.role != "admin":
        return jsonify({"error": "Access forbidden"}), 403

    data = request.get_json()
    if not data or "message" not in data:
        return jsonify({"error": "Message is required"}), 400

    message = data["message"].strip()
    if not message:
        return jsonify({"error": "Message cannot be empty"}), 400

    update_feedback(feedback_id, fb["name"], fb["email"], message)

    return jsonify({
        "success": True,
        "message": "Feedback successfully updated"
    }), 200

@api_bp.route("/feedback/<int:feedback_id>", methods=["DELETE"])
@api_login_required
def api_delete_feedback(feedback_id):
    """Видалити відгук із системи"""
    fb = get_feedback(feedback_id)
    if not fb:
        return jsonify({"error": "Feedback not found"}), 404

    # Перевірка прав: власник відгуку або адміністратор
    if fb["user_id"] != current_user.id and current_user.role != "admin":
        return jsonify({"error": "Access forbidden"}), 403

    delete_feedback(feedback_id)

    return jsonify({
        "success": True,
        "message": "Feedback successfully deleted"
    }), 200

# -----------------------
# ЕНДПОІНТИ СТАТИСТИКИ
# -----------------------
@api_bp.route("/stats/games", methods=["GET"])
@api_login_required
def get_user_games():
    """Отримати список унікальних назв ігор, у які грав користувач"""
    games = get_distinct_games_for_user(current_user.id)
    return jsonify({"games": games}), 200

@api_bp.route("/stats/game/<game_name>", methods=["GET"])
@api_login_required
def get_game_stats(game_name):
    """Отримати детальну статистику проходження конкретної гри"""
    stats = get_stats_for_game(current_user.id, game_name)

    result = []
    for s in stats:
        result.append({
            "level": s["level"],
            "rounds": s["rounds"],
            "rounds_played": s["rounds_played"],
            "total_score": s["total_score"],
            "avg_time": round(s["avg_time"], 2),
            "total_coins": s["total_coins"]
        })

    return jsonify({"game": game_name, "stats": result}), 200

@api_bp.route("/transactions", methods=["GET"])
@api_login_required
def get_transactions():
    """Отримати історію нарахувань та списань монет користувача"""
    limit = request.args.get("limit", 50, type=int)
    transactions = get_user_transactions(current_user.id, limit)

    result = []
    for t in transactions:
        result.append({
            "id": t["id"],
            "amount": t["amount"],
            "transaction_type": t["transaction_type"],
            "description": t["description"],
            "created_at": t["created_at"]
        })

    return jsonify({"transactions": result, "count": len(result)}), 200

@api_bp.route("/user/theme", methods=["POST"])
@api_login_required
def update_theme():
    """Змінити налаштування теми інтерфейсу користувача (light/dark)"""
    data = request.get_json()

    if not data or "theme" not in data:
        return jsonify({"error": "Theme is required"}), 400

    theme = data["theme"]
    if theme not in ["light", "dark"]:
        return jsonify({"error": "Invalid theme"}), 400

    from app.db.models import update_user_theme
    update_user_theme(current_user.id, theme)

    return jsonify({
        "success": True,
        "theme": theme
    }), 200