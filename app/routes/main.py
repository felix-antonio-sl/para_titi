# =============================================================================
# app/routes/main.py — Dashboard principal
# =============================================================================

from flask import Blueprint, render_template
from flask_login import login_required, current_user
from sqlalchemy import func
from app.extensions import db
from app.models import Iniciativa, CompromisoOperativo, ProblemaIPR, AlertaIPR

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
@login_required
def dashboard():
    """Dashboard principal según rol del usuario."""

    # Estadísticas generales
    stats = get_stats(current_user)

    # Compromisos del usuario
    mis_compromisos = (
        CompromisoOperativo.query.filter(
            CompromisoOperativo.responsable_id == current_user.id,
            CompromisoOperativo.estado.in_(["PENDIENTE", "EN_PROGRESO"]),
        )
        .order_by(CompromisoOperativo.fecha_limite)
        .limit(10)
        .all()
    )

    # Compromisos vencidos (para jefes y admin)
    compromisos_vencidos = []
    if current_user.puede_verificar_compromisos():
        from datetime import date

        compromisos_vencidos = (
            CompromisoOperativo.query.filter(
                CompromisoOperativo.estado.in_(["PENDIENTE", "EN_PROGRESO"]),
                CompromisoOperativo.fecha_limite < date.today(),
            )
            .order_by(CompromisoOperativo.fecha_limite)
            .limit(10)
            .all()
        )

    # Alertas activas
    alertas = (
        AlertaIPR.query.filter(AlertaIPR.activa == True)
        .order_by(AlertaIPR.nivel.desc(), AlertaIPR.generada_en.desc())
        .limit(10)
        .all()
    )

    # IPR con problemas
    ipr_con_problemas = (
        Iniciativa.query.filter(Iniciativa.tiene_problemas_abiertos == True)
        .limit(10)
        .all()
    )

    return render_template(
        "dashboard/index.html",
        stats=stats,
        mis_compromisos=mis_compromisos,
        compromisos_vencidos=compromisos_vencidos,
        alertas=alertas,
        ipr_con_problemas=ipr_con_problemas,
    )


@main_bp.route("/dashboard/ejecutivo")
@login_required
def dashboard_ejecutivo():
    """
    Dashboard Ejecutivo para Gobernador Regional.
    Vista estratégica con KPIs de ERD, cartera IPR y alertas críticas.
    """
    from app.services.dashboard_service import DashboardService
    from app.services.kpi_service import KPIService

    # Solo Gobernador, Admin Sistema o Admin Regional pueden ver
    if not current_user.puede_ver_todas_ipr():
        from flask import abort

        abort(403)

    # Datos del dashboard ejecutivo
    resumen_jefatura = DashboardService.get_dashboard_jefatura()
    resumen_dipir = DashboardService.get_dashboard_dipir()

    # KPIs estratégicos (si disponibles)
    try:
        kpis_erd = KPIService.get_kpis_erd()
    except Exception:
        kpis_erd = {}

    # Alertas críticas consolidadas
    alertas_criticas = DashboardService.get_alertas_activas(
        limite=15, nivel_minimo="ALTO"
    )

    # Compromisos vencidos por división
    compromisos_por_division = DashboardService.get_compromisos_vencidos_por_division()

    return render_template(
        "dashboard/ejecutivo.html",
        resumen=resumen_jefatura,
        cartera=resumen_dipir,
        kpis_erd=kpis_erd,
        alertas_criticas=alertas_criticas,
        compromisos_por_division=compromisos_por_division,
    )


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
    stats["total_ipr"] = iniciativas_query.count()
    stats["ipr_con_problemas"] = iniciativas_query.filter(
        Iniciativa.tiene_problemas_abiertos == True
    ).count()

    stats["compromisos_pendientes"] = compromisos_query.filter(
        CompromisoOperativo.estado.in_(["PENDIENTE", "EN_PROGRESO"])
    ).count()

    from datetime import date

    stats["compromisos_vencidos"] = compromisos_query.filter(
        CompromisoOperativo.estado.in_(["PENDIENTE", "EN_PROGRESO"]),
        CompromisoOperativo.fecha_limite < date.today(),
    ).count()

    stats["problemas_abiertos"] = problemas_query.filter(
        ProblemaIPR.estado.in_(["ABIERTO", "EN_GESTION"])
    ).count()

    stats["alertas_activas"] = AlertaIPR.query.filter(AlertaIPR.activa == True).count()

    return stats
