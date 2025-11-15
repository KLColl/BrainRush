from flask import Blueprint, render_template, request, jsonify
from flask_login import current_user, login_required
from app.db.models import save_game_result


color_rush_bp = Blueprint("color_rush", __name__, url_prefix="/game/color_rush")

@color_rush_bp.route("/")
@login_required
def color_rush_game():
    return render_template("games/color_rush.html")

@color_rush_bp.route("/save_result", methods=["POST"])
@login_required
def save_color_rush_result():
    data = request.get_json()
    
    if not data:
        return jsonify({"status": "error", "message": "No JSON data received"}), 400

    save_game_result(
        user_id = current_user.id,
        game_name = "color_rush",
        level = data.get("level", "unknown"),
        score = int(data.get("score", 0)),
        time_spent = float(data.get("time", 0.0)),
        rounds = int(data.get("rounds", 10)) 
    )
    
    try:
        return jsonify({"status": "success", "message": "Result saved successfully"})
    except Exception as e:
        print(f"Error saving result: {e}")
        return jsonify({"status": "error", "message": "Database error"}), 500