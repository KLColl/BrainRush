from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required

games_bp = Blueprint("games", __name__, url_prefix="/games")

@games_bp.route("/")
@login_required
def games_list():
    games = [
        {"name": "Arithmetic", "url": url_for("arithmetic.arithmetic_game")},        
        {"name": "Sequence Recall", "url": url_for("sequence_recall.sequence_recall_game")},  
        {"name": "Color Rush", "url": url_for("color_rush.color_rush_game")},
        {"name": "Tapping Memory", "url": url_for("tapping_memory.tapping_memory_game")}
    ]
    return render_template("games.html", games=games)