from functools import wraps
from flask import abort
from flask_login import current_user, login_required

def admin_required(f):
    """
    Декоратор для маршрутів доступних тільки адмінам
    Returns:
        403 якщо користувач не адмін
    """
    @wraps(f)
    @login_required
    def decorated_view(*args, **kwargs):
        if not current_user.is_admin:
            abort(403)
        return f(*args, **kwargs)
    return decorated_view
