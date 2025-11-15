from flask import Blueprint, render_template, request, jsonify
from flask_login import current_user, login_required
from app.db.models import save_game_result


arithmetic_bp = Blueprint("arithmetic", __name__, url_prefix="/game/arithmetic")

@arithmetic_bp.route("/")
@login_required
def arithmetic_game():
    return render_template("games/arithmetic.html")

@arithmetic_bp.route("/save_result", methods=["POST"])
@login_required
def save_result():
    data = request.get_json()
    print(data)
    if not data:
        return jsonify({"status:":"error", "message":"No JSON"}), 400

    save_game_result(
        user_id = current_user.id,
        game_name = "arithmetic",
        level = data.get("level", "unknown"),
        score = int(data.get("score", 0)),
        time_spent = float(data.get("time", 0.0)),
        rounds = int(data.get("rounds", 1)) 
    )
    print(current_user.id, data.get("level", "unknown"), int(data.get("score", 0)), float(data.get("time", 0.0)))
    
    try:
        return jsonify({"status": "success", "message": "Result saved successfully"})
    except Exception as e:
        print(f"Error saving result: {e}")
        return jsonify({"status": "error", "message": "Database error"}), 500