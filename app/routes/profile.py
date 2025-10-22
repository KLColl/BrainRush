from turtle import st
from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from flask_login import login_required, current_user
from sqlalchemy import func
from app.models.user import User
from app.models.game_result import GameResult

from app.models.user import db

profile_bp = Blueprint("profile", __name__, url_prefix="/profile")

@profile_bp.route("/")
@login_required
def my_profile():
    return redirect(url_for("profile.user_profile", user_id=current_user.id))

@profile_bp.route("/<int:user_id>")
@login_required
def user_profile(user_id):
    user = User.query.get(user_id)
    if not user:
        abort(404)

    games_list = db.session.query(GameResult.game_name)\
        .filter_by(user_id=user.id)\
        .distinct()\
        .all()
    games_list = [game.game_name for game in games_list]

    selected_game = request.args.get("game")
    stats_by_game = []

    if selected_game:
        stats_by_game = db.session.query(
            GameResult.game_name,
            GameResult.level,
            GameResult.rounds,
            func.count(GameResult.id).label("rounds_played"),
            func.sum(GameResult.score).label("total_score"),
            func.avg(GameResult.time_spent).label("avg_time")
        ).filter(
            GameResult.user_id==user.id,
            GameResult.game_name.ilike(selected_game)
        ).group_by(
            GameResult.level,
            GameResult.rounds
        ).all()

    total_games = len(current_user.results)
    total_points = sum(result.score for result in current_user.results)
    
    return render_template(
        "profile.html",
        user=user,
        total_games=total_games,
        total_points=total_points,
        games_list=games_list,
        selected_game=selected_game,
        stats_by_game=stats_by_game
    )