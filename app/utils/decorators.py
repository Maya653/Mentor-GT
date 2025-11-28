from functools import wraps
from flask import redirect, url_for, flash
from flask_login import current_user

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Debes iniciar sesión', 'warning')
            return redirect(url_for('auth.login'))
        if not current_user.es_admin():
            flash('No tienes permisos de administrador', 'danger')
            return redirect(url_for('docente.dashboard'))
        return f(*args, **kwargs)
    return decorated_function

def profesor_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Debes iniciar sesión', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def docente_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Debes iniciar sesión', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

