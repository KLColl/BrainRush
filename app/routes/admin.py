from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.utils.decorators import admin_required
from app.db.models import get_db_connection, get_user_by_id, set_user_role, get_feedbacks, get_feedback, update_feedback, delete_feedback

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

@admin_bp.route("/")
@admin_required
def admin_dashboard():
    return render_template("admin/dashboard.html")

@admin_bp.route("/users")
@admin_required
def admin_users():
    conn = get_db_connection()
    users = conn.execute("SELECT * FROM users ORDER BY id").fetchall()
    conn.close()
    return render_template("admin/users.html", users=users)

@admin_bp.route("/users/set_role/<int:user_id>", methods=["POST"])
@admin_required
def admin_set_role(user_id):
    role = request.form.get("role")
    if role not in ("user", "admin"):
        flash("Invalid role")
        return redirect(url_for("admin.admin_users"))

    set_user_role(user_id, role)
    flash("Role updated!")
    return redirect(url_for("admin.admin_users"))


@admin_bp.route("/feedback")
@admin_required
def admin_feedback_list():
    feedbacks = get_feedbacks()
    return render_template("admin/feedback_list.html", feedbacks=feedbacks)

@admin_bp.route("/feedback/edit/<int:fid>", methods=["GET", "POST"])
@admin_required
def admin_feedback_edit(fid):
    fb = get_feedback(fid)

    if not fb:
        flash("Feedback not found")
        return redirect(url_for("admin.admin_feedback_list"))

    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        message = request.form["message"]
        update_feedback(fid, name, email, message)
        flash("Feedback updated")
        return redirect(url_for("admin.admin_feedback_list"))

    return render_template("admin/feedback_edit.html", f=fb)

@admin_bp.route("/feedback/delete/<int:fid>", methods=["POST"])
@admin_required
def admin_feedback_delete(fid):
    delete_feedback(fid)
    flash("Feedback deleted")
    return redirect(url_for("admin.admin_feedback_list"))