from flask import Blueprint, render_template, request, jsonify
from flask_login import current_user, login_required
from app.models.game_result import GameResult
from app.gamesDB import db

tapping_memory_bp = Blueprint("tapping_memory", __name__, url_prefix="/game/tapping_memory")

@tapping_memory_bp.route("/")
@login_required
def tapping_memory_game():
    return render_template("games/tapping_memory.html")

@tapping_memory_bp.route("/save_result", methods=["POST"])
@login_required
def save_result():
    data = request.get_json()
    print(data)
    if not data:
        return jsonify({"status:":"error", "message":"No JSON"}), 400

    result = GameResult(
        user_id = current_user.id,
        game_name = "tapping_memory",
        level = data.get("level", "unknown"),
        score = int(data.get("score", 0)),
        time_spent = float(data.get("time", 0.0)),
        rounds = int(data.get("rounds", 1)) 
    )
    print(result.user_id, result.level, result.score, result.time_spent)
    db.session.add(result)
    db.session.commit()
    return jsonify("status", "success")