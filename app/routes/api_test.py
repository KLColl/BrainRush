from flask import Blueprint, render_template
from flask_login import login_required

api_test_bp = Blueprint("api_test", __name__, url_prefix="/api-test")

@api_test_bp.route("/")
@login_required
def api_test_page():
    return render_template("api_test.html")