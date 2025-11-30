from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.db.models import add_feedback, delete_feedback, get_feedback, get_feedbacks, update_feedback

feedback_bp = Blueprint("feedback", __name__, url_prefix="/feedback")

@feedback_bp.route("/", methods=["GET"])
def feedback_list():
    feedbacks = get_feedbacks()
    return render_template("feedback/list.html", feedbacks=feedbacks)


@feedback_bp.route("/add", methods=["POST"])
@login_required
def feedback_add():
    message = request.form.get("message", "").strip()

    if not message:
        flash("The message cannot be empty", "error")
        return redirect(url_for("feedback.feedback_list"))

    add_feedback(
        user_id=current_user.id,
        name=current_user.username,
        email="",
        message=message
    )

    flash("Feedback has been added!", "success")
    return redirect(url_for("feedback.feedback_list"))

@feedback_bp.route("/edit/<int:fid>", methods=["GET", "POST"])
@login_required
def feedback_edit(fid):
    fb = get_feedback(fid)

    if not fb:
        flash("Feedback not found", "error")
        return redirect(url_for("feedback.feedback_list"))

    # Перевірка прав доступу - тільки автор може редагувати
    if fb["user_id"] != current_user.id:
        flash("You cannot edit someone else's feedback!", "error")
        return redirect(url_for("feedback.feedback_list"))

    if request.method == "POST":
        message = request.form.get("message", "").strip()
        if not message:
            flash("Message cannot be empty", "error")
            return render_template("feedback/edit.html", f=fb)
            
        update_feedback(fid, fb["name"], fb["email"], message)
        flash("Feedback has been updated!", "success")
        return redirect(url_for("feedback.feedback_list"))

    return render_template("feedback/edit.html", f=fb)


@feedback_bp.route("/delete/<int:fid>", methods=["POST"])
@login_required
def feedback_delete(fid):
    fb = get_feedback(fid)

    if not fb:
        flash("Feedback not found", "error")
        return redirect(url_for("feedback.feedback_list"))

    # Перевірка прав доступу - тільки автор або адміністратор можуть видаляти
    if current_user.role != "admin" and fb["user_id"] != current_user.id:
        flash("You cannot delete someone else's feedback!", "error")
        return redirect(url_for("feedback.feedback_list"))

    delete_feedback(fid)
    flash("Feedback has been deleted.", "success")
    return redirect(url_for("feedback.feedback_list"))