# =============================================================================
# app/routes/main.py — Dashboard principal
# =============================================================================

from flask import Blueprint, render_template
from flask_login import login_required, current_user
from sqlalchemy import func
from app.extensions import db
from app.models import Iniciativa, CompromisoOperativo, ProblemaIPR, AlertaIPR

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
@login_required
def dashboard():
    """Dashboard principal según rol del usuario."""

    # Estadísticas generales
    stats = get_stats(current_user)

    # Compromisos del usuario
    mis_compromisos = CompromisoOperativo.query.filter(
        CompromisoOperativo.responsable_id == current_user.id,
        CompromisoOperativo.estado.in_(['PENDIENTE', 'EN_PROGRESO'])
    ).order_by(CompromisoOperativo.fecha_limite).limit(10).all()

    # Compromisos vencidos (para jefes y admin)
    compromisos_vencidos = []
    if current_user.puede_verificar_compromisos():
        from datetime import date
        compromisos_vencidos = CompromisoOperativo.query.filter(
            CompromisoOperativo.estado.in_(['PENDIENTE', 'EN_PROGRESO']),
            CompromisoOperativo.fecha_limite < date.today()
        ).order_by(CompromisoOperativo.fecha_limite).limit(10).all()

    # Alertas activas
    alertas = AlertaIPR.query.filter(
        AlertaIPR.activa == True
    ).order_by(AlertaIPR.nivel.desc(), AlertaIPR.generada_en.desc()).limit(10).all()

    # IPR con problemas
    ipr_con_problemas = Iniciativa.query.filter(
        Iniciativa.tiene_problemas_abiertos == True
    ).limit(10).all()

    return render_template('dashboard/index.html',
                           stats=stats,
                           mis_compromisos=mis_compromisos,
                           compromisos_vencidos=compromisos_vencidos,
                           alertas=alertas,
                           ipr_con_problemas=ipr_con_problemas)


def get_stats(usuario):
    """Obtiene estadísticas según el rol del usuario."""
    stats = {}

    # Base query según permisos
    if usuario.puede_ver_todas_ipr():
        # Admin ve todo
        iniciativas_query = Iniciativa.query
        compromisos_query = CompromisoOperativo.query
        problemas_query = ProblemaIPR.query
    else:
        # Jefes y encargados ven sus IPR asignadas y compromisos
        iniciativas_query = Iniciativa.query.filter(
            Iniciativa.responsable_id == usuario.id
        )
        compromisos_query = CompromisoOperativo.query.filter(
            CompromisoOperativo.responsable_id == usuario.id
        )
        problemas_query = ProblemaIPR.query.filter(
            ProblemaIPR.detectado_por_id == usuario.id
        )

    # Contar
    stats['total_ipr'] = iniciativas_query.count()
    stats['ipr_con_problemas'] = iniciativas_query.filter(
        Iniciativa.tiene_problemas_abiertos == True
    ).count()

    stats['compromisos_pendientes'] = compromisos_query.filter(
        CompromisoOperativo.estado.in_(['PENDIENTE', 'EN_PROGRESO'])
    ).count()

    from datetime import date
    stats['compromisos_vencidos'] = compromisos_query.filter(
        CompromisoOperativo.estado.in_(['PENDIENTE', 'EN_PROGRESO']),
        CompromisoOperativo.fecha_limite < date.today()
    ).count()

    stats['problemas_abiertos'] = problemas_query.filter(
        ProblemaIPR.estado.in_(['ABIERTO', 'EN_GESTION'])
    ).count()

    stats['alertas_activas'] = AlertaIPR.query.filter(AlertaIPR.activa == True).count()

    return stats
