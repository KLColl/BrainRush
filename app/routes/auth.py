import re
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required, login_user, logout_user
from app.models.user import User
from app.gamesDB import db


auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]

        if not re.fullmatch(r"[A-Za-z]{1,16}", username):
            flash("Username must contain only English letters and be up to 16 characters long.")
            return redirect(url_for("auth.register"))

        if User.query.filter(db.func.lower(User.username) == username.lower()).first():
            flash("This username is already taken.")
            return redirect(url_for("auth.register"))

        new_user = User(username=username)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        flash("Registration successful! Please log in.")

    return render_template("auth/register.html")

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = User.query.filter(db.func.lower(User.username) == username.lower()).first()
        if not user or not user.check_password(password):
            flash("Invalid username or password.")
            return redirect(url_for("auth.login"))

        login_user(user)
        return redirect(url_for("main.index"))

    return render_template("auth/login.html")

@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))