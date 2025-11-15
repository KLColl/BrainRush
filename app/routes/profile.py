from turtle import st
from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from flask_login import login_required, current_user
from app.db.models import get_user_by_id, get_distinct_games_for_user, get_stats_for_game, get_total_games, get_total_points

profile_bp = Blueprint("profile", __name__, url_prefix="/profile")

@profile_bp.route("/")
@login_required
def my_profile():
    return redirect(url_for("profile.user_profile", user_id=current_user.id))

@profile_bp.route("/<int:user_id>")
@login_required
def user_profile(user_id):
    user_row = get_user_by_id(user_id)
    if not user_row:
        abort(404)

    games_list = get_distinct_games_for_user(user_id)
    selected_game = request.args.get("game")
    stats_by_game = []

    if selected_game:
        stats_by_game = get_stats_for_game(user_id, selected_game)

    total_games = get_total_games(user_id)
    total_points = get_total_points(user_id)
    
    return render_template(
        "profile.html",
        user=user_row,
        total_games=total_games,
        total_points=total_points,
        games_list=games_list,
        selected_game=selected_game,
        stats_by_game=stats_by_game
    )