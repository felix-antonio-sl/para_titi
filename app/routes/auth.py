# =============================================================================
# app/routes/auth.py — Autenticación
# =============================================================================

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app.models import Usuario

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Inicio de sesión."""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        usuario = Usuario.query.filter_by(username=username, activo=True).first()

        if usuario and usuario.check_password(password):
            login_user(usuario, remember=request.form.get('remember'))
            next_page = request.args.get('next')
            flash('Sesión iniciada correctamente.', 'success')
            return redirect(next_page or url_for('main.dashboard'))

        flash('Usuario o contraseña incorrectos.', 'error')

    return render_template('auth/login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    """Cerrar sesión."""
    logout_user()
    flash('Sesión cerrada.', 'info')
    return redirect(url_for('auth.login'))
