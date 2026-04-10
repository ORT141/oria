"""
RBAC Security Decorators for ORIA.
Uses session-based auth (session['user_id']).
"""
from functools import wraps
from flask import session, redirect, url_for, abort, g
from models import db, User


def login_required(f):
    """Ensure the user is logged in via session."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = session.get('user_id')
        if not user_id:
            return redirect(url_for('auth.login'))

        user = db.session.get(User, user_id)
        if not user:
            session.clear()
            return redirect(url_for('auth.login'))

        g.user = user
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    """Ensure the user has 'admin' or 'superadmin' role."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = session.get('user_id')
        if not user_id:
            return redirect(url_for('auth.login'))

        user = db.session.get(User, user_id)
        if not user:
            session.clear()
            return redirect(url_for('auth.login'))

        if not user.is_admin:
            abort(403)

        g.user = user
        return f(*args, **kwargs)
    return decorated_function


def superadmin_required(f):
    """Ensure the user has the 'superadmin' role."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = session.get('user_id')
        if not user_id:
            return redirect(url_for('auth.login'))

        user = db.session.get(User, user_id)
        if not user:
            session.clear()
            return redirect(url_for('auth.login'))

        if not user.is_superadmin:
            abort(403)

        g.user = user
        return f(*args, **kwargs)
    return decorated_function
