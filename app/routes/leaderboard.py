from flask import Blueprint, render_template
from app.db.models import get_global_leaderboard, get_game_leaderboard

leaderboard_bp = Blueprint("leaderboard", __name__, url_prefix="/leaderboard")

@leaderboard_bp.route("/")
def leaderboard_list():
    global_top = get_global_leaderboard()
    arithmetic_top = get_game_leaderboard("arithmetic")
    color_top = get_game_leaderboard("color_rush")
    sequence_top = get_game_leaderboard("sequence_recall")
    tapping_top = get_game_leaderboard("tapping_memory")
    
    return render_template("leaderboard.html", 
                           global_top=global_top,
                           arithmetic_top=arithmetic_top,
                           color_top=color_top,
                           sequence_top=sequence_top,
                           tapping_top=tapping_top)