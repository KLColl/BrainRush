from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from flask_login import login_required, current_user, logout_user
from werkzeug.security import generate_password_hash
from app.db.models import (
    get_user_by_id, 
    get_distinct_games_for_user, 
    get_stats_for_game, 
    get_total_games, 
    get_total_points,
    get_user_purchases,
    equip_avatar,
    change_user_password,
    delete_user_account
)

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

    # Статистика
    games_list = get_distinct_games_for_user(user_id)
    selected_game = request.args.get("game")
    stats_by_game = []
    if selected_game:
        stats_by_game = get_stats_for_game(user_id, selected_game)

    total_games = get_total_games(user_id)
    total_points = get_total_points(user_id)
    
    # Отримуємо доступні аватари (куплені + стандартний)
    available_avatars = ['default']
    purchases = get_user_purchases(user_id)
    for p in purchases:
        if p['item_type'] == 'avatar':
            available_avatars.append(p['id'])

    return render_template(
        "profile.html",
        user=user_row,
        total_games=total_games,
        total_points=total_points,
        games_list=games_list,
        selected_game=selected_game,
        stats_by_game=stats_by_game,
        available_avatars=available_avatars,
        is_own_profile=(current_user.id == user_id)
    )

@profile_bp.route("/settings", methods=["POST"])
@login_required
def settings():
    action = request.form.get("action")
    
    # Зміна аватара
    if action == "change_avatar":
        avatar = request.form.get("avatar")
        # Тут бажано додати перевірку, чи куплений цей аватар
        equip_avatar(current_user.id, avatar)
        flash("Avatar updated successfully!", "success")
        
    # Зміна пароля
    elif action == "change_password":
        new_pass = request.form.get("new_password")
        confirm_pass = request.form.get("confirm_password")
        
        if not new_pass or len(new_pass) < 8:
            flash("Password must be at least 8 characters long.", "error")
        elif new_pass != confirm_pass:
            flash("Passwords do not match.", "error")
        else:
            hashed = generate_password_hash(new_pass)
            change_user_password(current_user.id, hashed)
            flash("Password changed successfully.", "success")
            
    # Видалення акаунту
    elif action == "delete_account":
        confirm_text = request.form.get("confirm_delete")
        if confirm_text == "DELETE":
            delete_user_account(current_user.id)
            logout_user()
            flash("Your account has been deleted.", "info")
            return redirect(url_for("main.index"))
        else:
            flash("Please type 'DELETE' to confirm account deletion.", "error")
            
    return redirect(url_for("profile.my_profile"))