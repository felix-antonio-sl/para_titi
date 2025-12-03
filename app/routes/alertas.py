# =============================================================================
# app/routes/alertas.py — Gestión de Alertas IPR
# =============================================================================

from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.extensions import db
from app.models import AlertaIPR

alertas_bp = Blueprint('alertas', __name__)


@alertas_bp.route('/')
@login_required
def lista():
    """Lista de alertas activas."""
    page = request.args.get('page', 1, type=int)

    # Filtros
    nivel = request.args.get('nivel')
    tipo = request.args.get('tipo')
    solo_activas = request.args.get('activas', '1') == '1'

    query = AlertaIPR.query

    if solo_activas:
        query = query.filter(AlertaIPR.activa == True)

    if nivel:
        query = query.filter(AlertaIPR.nivel == nivel)

    if tipo:
        query = query.filter(AlertaIPR.tipo == tipo)

    # Ordenar por nivel (crítico primero) y fecha
    query = query.order_by(
        AlertaIPR.nivel.desc(),
        AlertaIPR.generada_en.desc()
    )

    paginacion = query.paginate(page=page, per_page=20, error_out=False)

    return render_template('alertas/lista.html',
                           alertas=paginacion.items,
                           paginacion=paginacion,
                           filtros={
                               'nivel': nivel,
                               'tipo': tipo,
                               'activas': solo_activas
                           })


@alertas_bp.route('/<uuid:id>/atender', methods=['POST'])
@login_required
def atender(id):
    """Marcar alerta como atendida."""
    alerta = AlertaIPR.query.get_or_404(id)
    accion = request.form.get('accion_tomada', '').strip()

    alerta.activa = False
    alerta.atendida_por_id = current_user.id
    alerta.atendida_en = datetime.utcnow()
    alerta.accion_tomada = accion or 'Atendida'

    db.session.commit()

    flash('Alerta atendida.', 'success')

    # Si es HTMX, retornar fragmento vacío o actualizado
    if request.headers.get('HX-Request'):
        return ''

    return redirect(url_for('alertas.lista'))
