from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required

games_bp = Blueprint("games", __name__, url_prefix="/games")

@games_bp.route("/")
@login_required
def games_list():
    games = [
        {"name": "Arithmetic", "url": url_for("arithmetic.arithmetic_game")}        
    ]
    return render_template("games.html", games=games)