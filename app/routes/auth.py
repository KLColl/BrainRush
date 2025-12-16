import re
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required, login_user, logout_user
from app.db.models import create_user, get_user_by_username, verify_user_password, get_user_by_id, check_daily_bonus
from app.models.user_obj import UserObject


auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    """
    GET: Показати форму реєстрації
    POST: Обробити дані форми
    """
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]

        # Валідація username: тільки англійські букви та цифри, 3-16 символів
        if not re.fullmatch(r"[A-Za-z0-9]{3,16}", username):
            flash(
                "Username must contain only English letters and digits, length 3-16 characters.",
                "warning"
            )
            return redirect(url_for("auth.register"))

        # Валідація паролю: мінімум 8 символів
        if len(password) < 8:
            flash("Password must be at least 8 characters long.", "warning")
            return redirect(url_for("auth.register"))

        # Перевірка унікальності username (регістронезалежна)
        if get_user_by_username(username):
            flash("This username is already taken.", "warning")
            return redirect(url_for("auth.register"))

        # Створення користувача (пароль автоматично хешується в create_user)
        user_id = create_user(username, password)
        flash("Registration successful! Please log in.", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/register.html")

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """
    GET: Показати форму входу
    POST: Перевірити credentials та створити сесію
    """
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]
        
        if not re.fullmatch(r"[A-Za-z0-9]{3,16}", username):
            flash("Invalid username format.", "error")
            return redirect(url_for("auth.login"))
        
        if len(password) < 8:
            flash("Invalid password format.", "error")
            return redirect(url_for("auth.login"))
        
        # Отримання користувача з БД (регістронезалежний пошук)
        user_row = get_user_by_username(username)

        # Перевірка існування та пароля
        if not user_row or not verify_user_password(user_row, password):
            flash("Invalid username or password.", "error")
            return redirect(url_for("auth.login"))

        # Створення UserObject та старт сесії через Flask-Login
        user_obj = UserObject(user_row)
        login_user(user_obj)

        # Перевірка бонусу
        bonus_msg = check_daily_bonus(user_obj.id)
        if bonus_msg:
            flash(bonus_msg, "success")
            
        return redirect(url_for("main.index"))

    return render_template("auth/login.html")

@auth_bp.route("/logout")
@login_required
def logout():
    """
    Вихід з системи
    Знищує сесію користувача через Flask-Login та перенаправляє на сторінку входу
    """
    logout_user()
    return redirect(url_for("auth.login"))