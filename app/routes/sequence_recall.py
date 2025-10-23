from flask import Blueprint, render_template, request, jsonify
from flask_login import current_user, login_required
from app.models.game_result import GameResult 
from app.gamesDB import db 

sequence_recall_bp = Blueprint("sequence_recall", __name__, url_prefix="/game/sequence_recall")

@sequence_recall_bp.route("/")
@login_required
def sequence_recall_game():
    return render_template("games/sequence_recall.html")

@sequence_recall_bp.route("/save_result", methods=["POST"])
@login_required
def save_sequence_result():
    data = request.get_json()
    if not data:
        return jsonify({"status": "error", "message": "No JSON"}), 400

    result = GameResult(
        user_id = current_user.id,
        game_name = "sequence_recall",
        level = data.get("level", "unknown"),
        score = int(data.get("score", 0)),
        time_spent = float(data.get("time", 0.0)),
        rounds = int(data.get("rounds", 1)) 
    )
    
    db.session.add(result)
    db.session.commit()
    return jsonify({"status": "success", "message": "Result saved"})