import re
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required, login_user, logout_user
from app.db.models import create_user, get_user_by_username, verify_user_password, get_user_by_id
from app.models.user_obj import UserObject


auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]

        if not re.fullmatch(r"[A-Za-z0-9]{3,16}", username):
            flash(
                "Username must contain only English letters and digits, length 3-16 characters.",
                "warning"
            )
            return redirect(url_for("auth.register"))

        if len(password) < 8:
            flash("Password must be at least 8 characters long.", "warning")
            return redirect(url_for("auth.register"))

        if get_user_by_username(username):
            flash("This username is already taken.")
            return redirect(url_for("auth.register"))

        user_id = create_user(username, password)
        flash("Registration successful! Please log in.", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/register.html")

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user_row = get_user_by_username(username)

        if not user_row or not verify_user_password(user_row, password):
            flash("Invalid username or password.", "error")
            return redirect(url_for("auth.login"))

        user_obj = UserObject(user_row)
        login_user(user_obj)
        return redirect(url_for("main.index"))

    return render_template("auth/login.html")

@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))